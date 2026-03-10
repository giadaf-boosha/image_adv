from __future__ import annotations

import asyncio
import base64
import time
from typing import Any

import structlog

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from src.llm.base import (
    BaseLLMClient,
    LLMClientError,
    LLMRateLimitError,
    LLMServerError,
    LLMTimeoutError,
)

logger = structlog.get_logger(__name__)

_RETRYABLE_GOOGLE_EXCEPTIONS = (
    google_exceptions.ResourceExhausted,  # 429 rate limit
    google_exceptions.ServiceUnavailable,  # 503
    google_exceptions.InternalServerError,  # 500
    google_exceptions.DeadlineExceeded,    # timeout
)

_DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
_MAX_RETRIES = 3
_BACKOFF_BASE_SECONDS = 2.0


class GeminiClient(BaseLLMClient):
    """Client asincrono per Google Gemini 2.5 Flash.

    Usa google.generativeai SDK. Il metodo analyze_image gira il modello
    sincrono in un thread executor per non bloccare l'event loop.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = _DEFAULT_MODEL,
        request_timeout_seconds: int = 60,
    ) -> None:
        """
        Args:
            api_key: Google AI API key.
            model_name: Nome del modello Gemini da usare.
            request_timeout_seconds: Timeout per ogni singola chiamata API.
        """
        if not api_key:
            raise LLMClientError("GOOGLE_API_KEY non fornita a GeminiClient")

        genai.configure(api_key=api_key)
        self._model_name = model_name
        self._timeout = request_timeout_seconds
        self._model = genai.GenerativeModel(model_name=model_name)

        logger.info(
            "gemini_client_initialized",
            model=model_name,
            timeout=request_timeout_seconds,
        )

    # ------------------------------------------------------------------
    # Interfaccia pubblica
    # ------------------------------------------------------------------

    async def analyze_image(
        self,
        image_base64: str,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        """Invia immagine + prompt a Gemini e restituisce la risposta testuale.

        Effettua fino a _MAX_RETRIES tentativi con backoff esponenziale sui
        codici di errore recuperabili (rate limit, 5xx, timeout).
        """
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        image_part = self._build_image_part(image_base64)
        last_exc: Exception = RuntimeError("Nessun tentativo eseguito")

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                start_ms = time.monotonic() * 1000
                response = await self._call_model(
                    image_part=image_part,
                    prompt=prompt,
                    generation_config=generation_config,
                )
                elapsed_ms = int(time.monotonic() * 1000 - start_ms)

                logger.info(
                    "gemini_request_success",
                    model=self._model_name,
                    attempt=attempt,
                    elapsed_ms=elapsed_ms,
                )
                return response.text

            except google_exceptions.ResourceExhausted as exc:
                last_exc = LLMRateLimitError(str(exc))
                logger.warning(
                    "gemini_rate_limit",
                    attempt=attempt,
                    max_retries=_MAX_RETRIES,
                    error=str(exc),
                )

            except google_exceptions.DeadlineExceeded as exc:
                last_exc = LLMTimeoutError(str(exc))
                logger.warning(
                    "gemini_timeout",
                    attempt=attempt,
                    max_retries=_MAX_RETRIES,
                    timeout_seconds=self._timeout,
                    error=str(exc),
                )

            except (
                google_exceptions.ServiceUnavailable,
                google_exceptions.InternalServerError,
            ) as exc:
                last_exc = LLMServerError(str(exc))
                logger.warning(
                    "gemini_server_error",
                    attempt=attempt,
                    max_retries=_MAX_RETRIES,
                    error=str(exc),
                )

            except google_exceptions.InvalidArgument as exc:
                # Errore client non recuperabile — non ritentare
                raise LLMClientError(
                    f"Input non valido per Gemini: {exc}"
                ) from exc

            except google_exceptions.PermissionDenied as exc:
                raise LLMClientError(
                    f"API key non autorizzata per Gemini: {exc}"
                ) from exc

            if attempt < _MAX_RETRIES:
                backoff = _BACKOFF_BASE_SECONDS ** attempt
                logger.info(
                    "gemini_retry_backoff",
                    attempt=attempt,
                    backoff_seconds=backoff,
                )
                await asyncio.sleep(backoff)

        raise last_exc

    async def health_check(self) -> bool:
        """Verifica la connettività inviando un messaggio minimo."""
        try:
            model = genai.GenerativeModel(model_name=self._model_name)
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(
                    "ping",
                    generation_config=genai.GenerationConfig(max_output_tokens=5),
                ),
            )
            return bool(response.text)
        except Exception as exc:
            logger.warning("gemini_health_check_failed", error=str(exc))
            return False

    # ------------------------------------------------------------------
    # Helpers privati
    # ------------------------------------------------------------------

    @staticmethod
    def _build_image_part(image_base64: str) -> dict[str, Any]:
        """Costruisce la parte immagine nel formato atteso dall'SDK Gemini."""
        # Decodifica e ri-codifica per validare che sia base64 valido
        try:
            raw_bytes = base64.b64decode(image_base64, validate=True)
        except Exception as exc:
            raise LLMClientError(
                f"image_base64 non è un base64 valido: {exc}"
            ) from exc

        # Rileva MIME type dai magic bytes
        mime_type = _detect_mime_type(raw_bytes)

        return {
            "mime_type": mime_type,
            "data": image_base64,
        }

    async def _call_model(
        self,
        image_part: dict[str, Any],
        prompt: str,
        generation_config: genai.GenerationConfig,
    ) -> Any:
        """Esegue la chiamata sincrona all'SDK in un thread executor."""
        loop = asyncio.get_running_loop()

        def _sync_call() -> Any:
            return self._model.generate_content(
                contents=[image_part, prompt],
                generation_config=generation_config,
                request_options={"timeout": self._timeout},
            )

        return await loop.run_in_executor(None, _sync_call)


# ------------------------------------------------------------------
# Utility module-level
# ------------------------------------------------------------------

def _detect_mime_type(raw_bytes: bytes) -> str:
    """Rileva il MIME type dell'immagine dai magic bytes iniziali."""
    if raw_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if raw_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if raw_bytes[:4] in (b"RIFF", b"WEBP") or raw_bytes[8:12] == b"WEBP":
        return "image/webp"
    if raw_bytes[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    # Default safe fallback
    return "image/jpeg"
