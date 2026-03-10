from __future__ import annotations

import base64
import io
from typing import Optional, Union

import httpx
import structlog
from PIL import Image, UnidentifiedImageError

from src.models.schemas import AnalysisError

logger = structlog.get_logger(__name__)

_MAX_IMAGE_BYTES = 20 * 1024 * 1024  # 20 MB — limite bloccante
_COMPRESS_THRESHOLD_BYTES = 4 * 1024 * 1024  # 4 MB — soglia ricompressione
_MAX_DIMENSION_PX = 2048  # ridimensiona se supera questa dimensione
_MIN_DIMENSION_WARNING = 300  # warning non bloccante se sotto questa soglia
_SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP", "GIF"}
_DOWNLOAD_TIMEOUT_SECONDS = 10.0  # timeout per download da URL


class ImagePreprocessor:
    """Valida e prepara un'immagine per la pipeline LLM.

    Può ricevere l'immagine come URL pubblico (scaricamento asincrono)
    oppure come bytes già caricati (upload multipart).

    Spec di riferimento: 03_pipeline_classificazione_ai.md, Sezione 4.
    """

    async def validate_and_prepare(
        self,
        image_source: Union[str, bytes],
    ) -> tuple[str, list[AnalysisError]]:
        """Valida l'immagine e la restituisce come stringa base64.

        Args:
            image_source: URL pubblico HTTP/HTTPS dell'immagine (str)
                          oppure bytes dell'immagine (bytes da upload multipart).

        Returns:
            Tupla (image_b64, warnings) dove:
              - image_b64: immagine codificata in base64, pronta per l'API LLM.
              - warnings: lista di AnalysisError non bloccanti (es. risoluzione
                          sotto soglia, GIF convertita al primo frame).

        Raises:
            ValueError: Se l'immagine è illeggibile, corrotta, in formato
                        non supportato, o supera i 20 MB. Errori bloccanti.
        """
        warnings: list[AnalysisError] = []

        raw_bytes = await self._acquire_bytes(image_source)
        self._check_file_size(raw_bytes)
        image, detected_format = self._open_and_validate_format(raw_bytes)

        if detected_format == "GIF":
            image = self._extract_gif_first_frame(image)
            warnings.append(
                AnalysisError(
                    code="W-GIF-FIRST-FRAME",
                    message="GIF detected: only the first frame was processed for classification.",
                    severity="warning",
                )
            )

        self._check_resolution(image, warnings)
        image = self._resize_if_oversized(image)
        image_b64 = self._encode_to_base64(raw_bytes, image, detected_format)

        logger.info(
            "image_preprocessed",
            format=detected_format,
            width=image.width,
            height=image.height,
            base64_len=len(image_b64),
            warnings_count=len(warnings),
        )
        return image_b64, warnings

    # ------------------------------------------------------------------
    # Metodo di compatibilità per callsite che passano image_url / image_bytes separati
    # ------------------------------------------------------------------

    async def validate_and_prepare_from_parts(
        self,
        image_url: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
    ) -> tuple[str, list[AnalysisError]]:
        """Wrapper di compatibilità: accetta image_url e image_bytes come parametri separati.

        Almeno uno dei due deve essere fornito.
        """
        if image_bytes is not None:
            return await self.validate_and_prepare(image_bytes)
        if image_url is not None:
            return await self.validate_and_prepare(image_url)
        raise ValueError("Deve essere fornito image_url oppure image_bytes.")

    # ------------------------------------------------------------------
    # Privati
    # ------------------------------------------------------------------

    async def _acquire_bytes(self, image_source: Union[str, bytes]) -> bytes:
        """Acquisisce i bytes dell'immagine da URL o da upload diretto."""
        if isinstance(image_source, bytes):
            return image_source
        if isinstance(image_source, str) and image_source.lower().startswith("http"):
            return await self._download_image(image_source)
        raise ValueError(
            f"image_source deve essere bytes oppure un URL HTTP/HTTPS valido. "
            f"Ricevuto: {type(image_source).__name__}"
        )

    async def _download_image(self, url: str) -> bytes:
        """Scarica l'immagine dall'URL con timeout e gestione degli errori."""
        logger.debug("image_download_start", url=url)
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=_DOWNLOAD_TIMEOUT_SECONDS,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                content = response.content

            logger.info(
                "image_downloaded",
                url=url,
                content_length=len(content),
                content_type=response.headers.get("content-type", "unknown"),
            )
            return content

        except httpx.TimeoutException as exc:
            raise ValueError(
                f"image_url_unreachable: timeout dopo {_DOWNLOAD_TIMEOUT_SECONDS}s "
                f"scaricando {url}"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ValueError(
                f"image_url_unreachable: HTTP {exc.response.status_code} per {url}"
            ) from exc
        except httpx.RequestError as exc:
            raise ValueError(
                f"image_url_unreachable: errore di rete per {url}: {exc}"
            ) from exc

    def _check_file_size(self, raw_bytes: bytes) -> None:
        """Verifica che la dimensione del file non superi i 20 MB."""
        size_mb = len(raw_bytes) / (1024 * 1024)
        if len(raw_bytes) > _MAX_IMAGE_BYTES:
            raise ValueError(
                f"image_too_large: il file pesa {size_mb:.1f} MB, "
                f"il massimo consentito è {_MAX_IMAGE_BYTES // 1024 // 1024} MB."
            )

    def _open_and_validate_format(
        self, raw_bytes: bytes
    ) -> tuple[Image.Image, str]:
        """Apre l'immagine con Pillow e verifica che il formato sia supportato.

        Esegue verify() per l'integrità, poi riapre per le operazioni successive
        (verify() consuma lo stream interno dell'immagine).

        Returns:
            Tuple (image, detected_format) dove detected_format è in maiuscolo.

        Raises:
            ValueError: Se l'immagine è corrotta o in formato non supportato.
        """
        try:
            img = Image.open(io.BytesIO(raw_bytes))
            img.verify()
        except UnidentifiedImageError as exc:
            raise ValueError(
                "image_unreadable: formato immagine non riconosciuto o file corrotto."
            ) from exc
        except Exception as exc:
            raise ValueError(
                f"image_unreadable: impossibile aprire l'immagine: {exc}"
            ) from exc

        # Riapre dopo verify — lo stream è stato consumato
        img = Image.open(io.BytesIO(raw_bytes))
        detected_format = (img.format or "").upper()

        if detected_format not in _SUPPORTED_FORMATS:
            raise ValueError(
                f"image_unreadable: formato '{detected_format}' non supportato. "
                f"Formati accettati: {', '.join(sorted(_SUPPORTED_FORMATS))}."
            )

        return img, detected_format

    def _extract_gif_first_frame(self, image: Image.Image) -> Image.Image:
        """Estrae il primo frame da un GIF e lo converte in RGB."""
        image.seek(0)
        return image.copy().convert("RGB")

    def _check_resolution(
        self, image: Image.Image, warnings: list[AnalysisError]
    ) -> None:
        """Aggiunge un warning non bloccante se la risoluzione è sotto 300x300."""
        width, height = image.size
        if width < _MIN_DIMENSION_WARNING or height < _MIN_DIMENSION_WARNING:
            warnings.append(
                AnalysisError(
                    code="E-102",
                    message=(
                        f"Risoluzione immagine sotto la soglia consigliata: "
                        f"{width}x{height} px "
                        f"(minimo consigliato {_MIN_DIMENSION_WARNING}x{_MIN_DIMENSION_WARNING} px). "
                        "La qualità della classificazione potrebbe essere ridotta."
                    ),
                    severity="warning",
                )
            )
            logger.warning(
                "image_low_resolution",
                width=width,
                height=height,
                min_recommended=_MIN_DIMENSION_WARNING,
            )

    def _resize_if_oversized(self, image: Image.Image) -> Image.Image:
        """Ridimensiona l'immagine se supera 2048x2048, mantenendo l'aspect ratio."""
        if max(image.size) <= _MAX_DIMENSION_PX:
            return image

        original_size = image.size
        resized = image.copy()
        resized.thumbnail((_MAX_DIMENSION_PX, _MAX_DIMENSION_PX), Image.Resampling.LANCZOS)
        logger.debug(
            "image_resized",
            original_size=original_size,
            new_size=resized.size,
            max_dimension=_MAX_DIMENSION_PX,
        )
        return resized

    def _encode_to_base64(
        self,
        raw_bytes: bytes,
        image: Image.Image,
        detected_format: str,
    ) -> str:
        """Converte l'immagine in stringa base64.

        Se l'immagine è stata ridimensionata o supera la soglia di 4 MB,
        la ricomprime a JPEG quality 85 (o 70 se ancora troppo grande).
        Altrimenti usa i bytes originali per preservare la qualità.
        """
        original_image = Image.open(io.BytesIO(raw_bytes))
        was_resized = image.size != original_image.size

        if not was_resized and len(raw_bytes) <= _COMPRESS_THRESHOLD_BYTES:
            return base64.b64encode(raw_bytes).decode("ascii")

        # Determina il formato di output
        save_format = "JPEG" if detected_format in ("JPEG", "GIF") else detected_format
        encode_image = image.convert("RGB") if save_format == "JPEG" else image

        buffer = io.BytesIO()
        encode_image.save(buffer, format=save_format, quality=85)

        if buffer.tell() > _COMPRESS_THRESHOLD_BYTES:
            buffer = io.BytesIO()
            encode_image.save(buffer, format=save_format, quality=70)
            logger.debug(
                "image_recompressed_quality70",
                final_size_mb=round(buffer.tell() / (1024 * 1024), 2),
            )

        return base64.b64encode(buffer.getvalue()).decode("ascii")
