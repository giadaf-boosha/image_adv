from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM primario (Google Gemini)
    google_api_key: str = ""
    primary_model: str = "gemini-3.1-flash-image-preview"

    # LLM fallback (OpenAI)
    openai_api_key: str = ""
    fallback_model: str = "gpt-4o"

    # Dati locali
    taxonomy_path: str = "data/taxonomy.json"
    quality_criteria_path: str = "data/quality_criteria.json"
    alerts_log_path: str = "data/new_type_alerts_log.jsonl"

    # Soglie pipeline
    classification_confidence_threshold: float = 0.45
    novelty_trigger_threshold: float = 0.45

    # Timeout LLM (secondi)
    llm_timeout_seconds: int = 45

    # Versione applicazione
    app_version: str = "1.0.0"
