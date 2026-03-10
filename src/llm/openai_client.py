from __future__ import annotations

import asyncio
import base64
import time

import structlog
from openai import AsyncOpenAI, APIStatusError, APITimeoutError, APIConnectionError

from src.llm.base import (
    BaseLLMClient,
    LLMClientError,
    LLMRateLimitError,
    LLMServerError,
    LLMTimeoutError,
)

logger = structlog.get_logger(__name__)

_DEFAULT_MODEL = "gpt-4o"
_MAX_RETRIES = 3
_BACKOFF_BASE_SECONDS = 2.0


class OpenAIClient(BaseLLMClient):
    """Client asincrono per OpenAI GPT-4o.

    Usa AsyncOpenAI per chiamate non bloccanti native.
    L'immagine viene inviata come URL data URI in base64
    all'interno del content array vision.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = _DEFAULT_MODEL,
        request_timeout_seconds: int = 60,
    ) -> None:
        """
        Args:
            api_key: OpenAI API key.
            model_name: Nome del modello da usare (es. "gpt-4o").
            request_timeout_seconds: Timeout per ogni singola chiamata API.
        """
        if not api_key:
            raise LLMClientError("OPENAI_API_KEY non fornita a OpenAIClient")

        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=float(request_timeout_seconds),
            max_retries=0,  # gestione retry manuale con backoff
        )
        self._model_name = model_name
        self._timeout = request_timeout_seconds

        logger.info(
            "openai_client_initialized",
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
        """Invia immagine + prompt a GPT-4o e restituisce la risposta testuale.

        L'immagine viene codificata come data URI base64 nel campo image_url
        del content array, compatibile con la vision API di OpenAI.

        Effettua fino a _MAX_RETRIES tentativi con backoff esponenziale sui
        codici 429, 5xx e timeout.
        """
        # Valida base64 prima di costruire la richiesta
        mime_type = _validate_and_detect_mime(image_base64)
        data_uri = f"data:{mime_type};base64,{image_base64}"

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_uri,
                            "detail": "high",
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]

        last_exc: Exception = RuntimeError("Nessun tentativo eseguito")

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                start_ms = time.monotonic() * 1000
                response = await self._client.chat.completions.create(
                    model=self._model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                elapsed_ms = int(time.monotonic() * 1000 - start_ms)

                content = response.choices[0].message.content
                if content is None:
                    raise LLMServerError(
                        "OpenAI ha restituito un messaggio con content None"
                    )

                logger.info(
                    "openai_request_success",
                    model=self._model_name,
                    attempt=attempt,
                    elapsed_ms=elapsed_ms,
                    finish_reason=response.choices[0].finish_reason,
                    prompt_tokens=response.usage.prompt_tokens if response.usage else None,
                    completion_tokens=response.usage.completion_tokens if response.usage else None,
                )
                return content

            except APITimeoutError as exc:
                last_exc = LLMTimeoutError(str(exc))
                logger.warning(
                    "openai_timeout",
                    attempt=attempt,
                    max_retries=_MAX_RETRIES,
                    timeout_seconds=self._timeout,
                    error=str(exc),
                )

            except APIConnectionError as exc:
                last_exc = LLMServerError(str(exc))
                logger.warning(
                    "openai_connection_error",
                    attempt=attempt,
                    max_retries=_MAX_RETRIES,
                    error=str(exc),
                )

            except APIStatusError as exc:
                if exc.status_code == 429:
                    last_exc = LLMRateLimitError(str(exc))
                    logger.warning(
                        "openai_rate_limit",
                        attempt=attempt,
                        max_retries=_MAX_RETRIES,
                        error=str(exc),
                    )
                elif exc.status_code >= 500:
                    last_exc = LLMServerError(str(exc))
                    logger.warning(
                        "openai_server_error",
                        attempt=attempt,
                        max_retries=_MAX_RETRIES,
                        status_code=exc.status_code,
                        error=str(exc),
                    )
                elif exc.status_code == 401:
                    raise LLMClientError(
                        f"API key OpenAI non valida o non autorizzata: {exc}"
                    ) from exc
                elif exc.status_code == 400:
                    raise LLMClientError(
                        f"Richiesta non valida per OpenAI: {exc}"
                    ) from exc
                else:
                    raise LLMClientError(
                        f"Errore HTTP {exc.status_code} da OpenAI: {exc}"
                    ) from exc

            if attempt < _MAX_RETRIES:
                backoff = _BACKOFF_BASE_SECONDS ** attempt
                logger.info(
                    "openai_retry_backoff",
                    attempt=attempt,
                    backoff_seconds=backoff,
                )
                await asyncio.sleep(backoff)

        raise last_exc

    async def health_check(self) -> bool:
        """Verifica la connettività inviando una richiesta testuale minimale."""
        try:
            response = await self._client.chat.completions.create(
                model=self._model_name,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
                temperature=0.0,
            )
            return bool(response.choices[0].message.content)
        except Exception as exc:
            logger.warning("openai_health_check_failed", error=str(exc))
            return False


# ------------------------------------------------------------------
# Utility module-level
# ------------------------------------------------------------------

def _validate_and_detect_mime(image_base64: str) -> str:
    """Valida che image_base64 sia base64 corretto e rileva il MIME type.

    Raises:
        LLMClientError: se la stringa non è base64 valido.
    """
    try:
        raw_bytes = base64.b64decode(image_base64, validate=True)
    except Exception as exc:
        raise LLMClientError(
            f"image_base64 non è un base64 valido: {exc}"
        ) from exc

    if raw_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if raw_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if raw_bytes[8:12] == b"WEBP":
        return "image/webp"
    if raw_bytes[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    return "image/jpeg"
