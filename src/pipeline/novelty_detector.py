from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Optional

import structlog

from src.llm.base import BaseLLMClient
from src.models.schemas import (
    AnalysisError,
    Classification,
    ClosestKnownType,
    NewTypeAlert,
    ProposedNewType,
)
from src.config import Settings
from src.prompts.novelty import build_novelty_prompt

logger = structlog.get_logger(__name__)

_CONFIDENCE_NOVELTY_PRIORITY_THRESHOLD = 0.65


class NoveltyDetector:
    """RF-03: Rileva se un'immagine rappresenta una tipologia creativa nuova."""

    def __init__(
        self,
        llm_client: BaseLLMClient,
        settings: Settings,
    ) -> None:
        self._llm = llm_client
        self._settings = settings
        self._alert_counter = 0

    async def detect(
        self,
        image_b64: str,
        closest_known_types: Optional[list[Classification]] = None,
        trigger_reason: str = "no_classification_above_threshold",
    ) -> tuple[NewTypeAlert | None, list[AnalysisError]]:
        """Analizza l'immagine per rilevare se è una tipologia creativa nuova.

        Args:
            image_b64: Immagine in base64.
            closest_known_types: Classificazioni con confidence più alta (sotto soglia).
                                 Max 3 vengono passate al prompt come contesto.
            trigger_reason: Motivo che ha attivato il rilevamento.

        Returns:
            Tuple (alert, errors) dove:
              - alert: NewTypeAlert con i dettagli del potenziale nuovo tipo,
                       o None se il LLM ha risposto in modo non parsabile.
              - errors: lista di AnalysisError non bloccanti.
        """
        errors: list[AnalysisError] = []
        closest_list = _build_closest_list(closest_known_types or [])

        system_prompt = build_novelty_prompt(closest_types=closest_list)

        user_message = (
            f"Analyze this advertising image. "
            f"Novelty detection triggered because: {trigger_reason}. "
            f"Determine if this represents a genuinely new creative format "
            f"not covered by the 128 known formats in the taxonomy."
        )

        logger.info(
            "novelty_detector_start",
            trigger_reason=trigger_reason,
            closest_count=len(closest_list),
        )

        try:
            raw_response = await self._llm.analyze_image(
                image_base64=image_b64,
                prompt=f"{system_prompt}\n\nUSER: {user_message}",
                temperature=0.3,
                max_tokens=2048,
            )
        except Exception as exc:
            logger.error("novelty_detector_llm_error", error=str(exc))
            errors.append(
                AnalysisError(
                    code="E-LLM-NOVELTY",
                    message=f"LLM call failed during novelty detection: {exc}",
                    severity="error",
                )
            )
            return None, errors

        alert, parse_errors = self._parse_response(
            raw_response,
            trigger_reason,
            closest_known_types or [],
        )
        errors.extend(parse_errors)

        if alert is not None:
            confidence = (
                alert.proposed_new_type.confidence_in_novelty
                if alert.proposed_new_type
                else 0.0
            )
            logger.info(
                "novelty_detector_done",
                triggered=alert.triggered,
                alert_id=alert.alert_id,
                confidence_in_novelty=confidence,
                priority_review=confidence >= _CONFIDENCE_NOVELTY_PRIORITY_THRESHOLD,
            )

        return alert, errors

    # ------------------------------------------------------------------
    # Privati
    # ------------------------------------------------------------------

    def _parse_response(
        self,
        raw: str,
        trigger_reason: str,
        closest_known_types: list[Classification],
    ) -> tuple[NewTypeAlert | None, list[AnalysisError]]:
        """Parsa la risposta LLM e costruisce il NewTypeAlert."""
        errors: list[AnalysisError] = []
        cleaned = _strip_markdown_fences(raw)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.warning(
                "novelty_detector_json_error",
                error=str(exc),
                raw_preview=raw[:300],
            )
            errors.append(
                AnalysisError(
                    code="E-JSON-NOVELTY",
                    message=f"Failed to parse novelty detection response as JSON: {exc}",
                    severity="warning",
                )
            )
            return self._fallback_alert(trigger_reason, closest_known_types), errors

        try:
            novelty_assessment = data.get("novelty_assessment", {})
            is_truly_novel = bool(novelty_assessment.get("is_truly_novel", False))
            confidence_in_novelty = float(
                novelty_assessment.get("confidence_in_novelty", 0.0)
            )

            # triggered = True solo se il modello ritiene genuinamente nuovo
            triggered = is_truly_novel and confidence_in_novelty >= _CONFIDENCE_NOVELTY_PRIORITY_THRESHOLD

            # Costruisce la lista dei tipi più vicini dalla risposta LLM
            # oppure dai closest_known_types originali come fallback
            closest: list[ClosestKnownType] = []
            raw_proposed = data.get("proposed_new_type", {})

            # Se il LLM ha restituito closest_known_types nel JSON, usali
            raw_closest_llm = data.get("closest_known_types", [])
            for item in raw_closest_llm[:3]:
                if isinstance(item, dict):
                    try:
                        closest.append(
                            ClosestKnownType(
                                category_id=str(item.get("category_id", "")),
                                category_name=str(item.get("category_name", "")),
                                confidence=float(item.get("confidence", 0.0)),
                            )
                        )
                    except (KeyError, ValueError, TypeError):
                        pass

            # Complementa con le classificazioni originali se necessario
            if len(closest) < 3 and closest_known_types:
                existing_ids = {c.category_id for c in closest}
                for cls in closest_known_types:
                    if cls.category_id not in existing_ids and len(closest) < 3:
                        closest.append(
                            ClosestKnownType(
                                category_id=cls.category_id,
                                category_name=cls.category_name,
                                confidence=cls.confidence,
                            )
                        )

            proposed: Optional[ProposedNewType] = None
            if raw_proposed:
                try:
                    proposed = ProposedNewType(
                        working_name=str(raw_proposed.get("working_name", "Unnamed Format")),
                        description=str(raw_proposed.get("description", "")),
                        visual_elements=list(raw_proposed.get("visual_elements", [])),
                        suggested_macro_category=raw_proposed.get("suggested_macro_category"),
                        differentiation_from_closest=str(
                            raw_proposed.get("differentiation_from_closest", "")
                        ),
                        potential_use_cases=list(raw_proposed.get("use_cases", []))
                        or list(raw_proposed.get("potential_use_cases", [])),
                        confidence_in_novelty=float(
                            raw_proposed.get("confidence_in_novelty", confidence_in_novelty)
                        ),
                    )
                except (KeyError, ValueError, TypeError) as exc:
                    logger.warning(
                        "novelty_detector_proposed_parse_error",
                        error=str(exc),
                    )

            alert_id: Optional[str] = None
            if triggered:
                alert_id = self._generate_alert_id()

            alert = NewTypeAlert(
                triggered=triggered,
                trigger_reason=trigger_reason,
                closest_known_types=closest,
                proposed_new_type=proposed,
                alert_id=alert_id,
                timestamp=datetime.now(tz=timezone.utc),
                review_status="pending",
            )
            return alert, errors

        except (KeyError, ValueError, TypeError) as exc:
            logger.warning(
                "novelty_detector_parse_error",
                error=str(exc),
            )
            errors.append(
                AnalysisError(
                    code="E-PARSE-NOVELTY",
                    message=f"Failed to build NewTypeAlert from LLM response: {exc}",
                    severity="warning",
                )
            )
            return self._fallback_alert(trigger_reason, closest_known_types), errors

    def _fallback_alert(
        self,
        trigger_reason: str,
        closest_known_types: list[Classification],
    ) -> NewTypeAlert:
        """Alert minimale usato quando il parsing LLM fallisce."""
        closest = [
            ClosestKnownType(
                category_id=cls.category_id,
                category_name=cls.category_name,
                confidence=cls.confidence,
            )
            for cls in closest_known_types[:3]
        ]
        return NewTypeAlert(
            triggered=False,
            trigger_reason=trigger_reason,
            closest_known_types=closest,
            proposed_new_type=None,
            alert_id=None,
            timestamp=datetime.now(tz=timezone.utc),
            review_status="pending",
        )

    def _generate_alert_id(self) -> str:
        """Genera un alert_id univoco nel formato ALT-YYYYMMDD-NNN."""
        self._alert_counter += 1
        date_str = datetime.now(tz=timezone.utc).strftime("%Y%m%d")
        return f"ALT-{date_str}-{self._alert_counter:03d}"


def _build_closest_list(classifications: list[Classification]) -> list[dict]:
    """Converte le Classification nel formato atteso da build_novelty_prompt."""
    return [
        {
            "category_id": cls.category_id,
            "category_name": cls.category_name,
            "confidence": cls.confidence,
        }
        for cls in classifications[:3]
    ]


def _strip_markdown_fences(text: str) -> str:
    """Rimuove i fence ```json ... ``` se presenti nella risposta LLM."""
    stripped = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", stripped)
    if match:
        return match.group(1).strip()
    return stripped
