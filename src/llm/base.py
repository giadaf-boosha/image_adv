from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Interfaccia comune per i client LLM multimodali."""

    @abstractmethod
    async def analyze_image(
        self,
        image_base64: str,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        """Invia immagine + prompt al modello e restituisce la risposta testuale.

        Args:
            image_base64: Immagine codificata in base64 (senza prefisso data URI).
            prompt: Testo del prompt utente da affiancare all'immagine.
            temperature: Temperatura per la generazione (0.0 - 1.0).
            max_tokens: Numero massimo di token nell'output.

        Returns:
            Testo della risposta generata dal modello.

        Raises:
            LLMRateLimitError: Quota API superata.
            LLMServerError: Errore lato server (5xx).
            LLMTimeoutError: Timeout della richiesta.
            LLMClientError: Errori di configurazione o input non valido (4xx).
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """Verifica che il client sia configurato e raggiungibile.

        Returns:
            True se l'API risponde correttamente, False altrimenti.
        """


class LLMRateLimitError(Exception):
    """Quota o rate limit API superata."""


class LLMServerError(Exception):
    """Errore interno del server LLM (5xx)."""


class LLMTimeoutError(Exception):
    """Timeout durante la chiamata al modello."""


class LLMClientError(Exception):
    """Errore lato client: configurazione errata, input non valido (4xx)."""
