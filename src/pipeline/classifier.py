from __future__ import annotations

import json
import re
from typing import Optional

import structlog

from src.llm.base import BaseLLMClient
from src.models.schemas import AnalysisError, Classification
from src.models.taxonomy import TaxonomyManager
from src.config import Settings
from src.prompts.classification import build_classification_prompt

logger = structlog.get_logger(__name__)

_CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.45
_MAX_CLASSIFICATIONS = 5


class AdClassifier:
    """RF-01: Classifica il formato creativo di un'immagine pubblicitaria."""

    def __init__(
        self,
        llm_client: BaseLLMClient,
        taxonomy_manager: TaxonomyManager,
        settings: Settings,
    ) -> None:
        self._llm = llm_client
        self._taxonomy = taxonomy_manager
        self._settings = settings

    async def classify(
        self,
        image_b64: str,
        platform_hint: Optional[str] = None,
        vertical_hint: Optional[str] = None,
    ) -> tuple[list[Classification], list[AnalysisError]]:
        """Classifica l'immagine e restituisce le classificazioni sopra soglia.

        Args:
            image_b64: Immagine in base64.
            platform_hint: Piattaforma target (es. "meta", "tiktok").
            vertical_hint: Settore merceologico (es. "beauty", "tech").

        Returns:
            Tuple (classifications, errors) dove:
              - classifications: lista di Classification ordinate per confidence
                decrescente, max 5, con confidence >= 0.45.
              - errors: lista di AnalysisError non bloccanti (es. risposta JSON malformata
                parzialmente recuperata).
        """
        errors: list[AnalysisError] = []

        taxonomy_text = self._taxonomy.build_taxonomy_for_prompt()
        system_prompt = build_classification_prompt(
            taxonomy_text=taxonomy_text,
            platform_hint=platform_hint,
            vertical_hint=vertical_hint,
        )

        logger.info(
            "classifier_start",
            platform_hint=platform_hint,
            vertical_hint=vertical_hint,
        )

        try:
            raw_response = await self._llm.analyze_image(
                image_base64=image_b64,
                prompt=system_prompt,
                temperature=0.2,
                max_tokens=2048,
            )
        except Exception as exc:
            logger.error("classifier_llm_error", error=str(exc))
            errors.append(
                AnalysisError(
                    code="E-LLM-CLASSIFY",
                    message=f"LLM call failed during classification: {exc}",
                    severity="error",
                )
            )
            return [], errors

        classifications, parse_errors = self._parse_response(raw_response)
        errors.extend(parse_errors)

        logger.info(
            "classifier_done",
            total_parsed=len(classifications),
            above_threshold=len(classifications),
            errors_count=len(errors),
        )
        return classifications, errors

    # ------------------------------------------------------------------
    # Privati
    # ------------------------------------------------------------------

    def _parse_response(
        self,
        raw: str,
    ) -> tuple[list[Classification], list[AnalysisError]]:
        """Estrae e valida le classificazioni dalla risposta LLM grezza.

        Gestisce sia la risposta con `classifications` (schema del prompt builder)
        sia con `detected_formats` (schema alternativo del doc 03).
        """
        errors: list[AnalysisError] = []
        cleaned = _strip_markdown_fences(raw)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.warning(
                "classifier_json_parse_error",
                error=str(exc),
                raw_preview=raw[:300],
            )
            errors.append(
                AnalysisError(
                    code="E-JSON-CLASSIFY",
                    message=f"Failed to parse classification response as JSON: {exc}",
                    severity="warning",
                )
            )
            return [], errors

        if data.get("not_advertising_content", False):
            logger.info("classifier_not_advertising_content")
            return [], errors

        # Supporta entrambi gli schema: `classifications` e `detected_formats`
        raw_items = data.get("classifications") or data.get("detected_formats") or []
        if not isinstance(raw_items, list):
            logger.warning(
                "classifier_invalid_response_structure",
                data_keys=list(data.keys()),
            )
            errors.append(
                AnalysisError(
                    code="E-SCHEMA-CLASSIFY",
                    message="Classification response missing 'classifications' or 'detected_formats' array.",
                    severity="warning",
                )
            )
            return [], errors

        classifications: list[Classification] = []
        for item in raw_items:
            try:
                confidence_raw = item.get("confidence", 0.0)
                # Normalizza se il LLM restituisce 0-100 invece di 0.0-1.0
                confidence = float(confidence_raw)
                if confidence > 1.0:
                    confidence = confidence / 100.0

                if confidence < _CLASSIFICATION_CONFIDENCE_THRESHOLD:
                    continue

                cls = Classification(
                    category_id=str(item.get("category_id") or item.get("format_id", "")),
                    category_name=str(item.get("category_name") or item.get("format_name", "")),
                    macro_category_id=int(
                        item.get("macro_category_id", 0)
                    ),
                    macro_category_name=str(
                        item.get("macro_category_name", "")
                    ),
                    confidence=confidence,
                    evidence=str(item.get("evidence") or item.get("reasoning", "")),
                )
                classifications.append(cls)
            except (KeyError, ValueError, TypeError) as exc:
                logger.warning(
                    "classifier_skip_invalid_item",
                    error=str(exc),
                    item=item,
                )
                continue

        classifications.sort(key=lambda c: c.confidence, reverse=True)
        return classifications[:_MAX_CLASSIFICATIONS], errors


def _strip_markdown_fences(text: str) -> str:
    """Rimuove i fence ```json ... ``` se presenti nella risposta LLM."""
    stripped = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", stripped)
    if match:
        return match.group(1).strip()
    return stripped
