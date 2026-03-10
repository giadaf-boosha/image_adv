from __future__ import annotations

import json
import re
from typing import Any

import structlog

from src.llm.base import BaseLLMClient
from src.models.schemas import (
    AnalysisError,
    Classification,
    QualityCriterionScore,
    QualityEvaluation,
)
from src.models.taxonomy import TaxonomyManager
from src.config import Settings
from src.prompts.quality import build_quality_prompt

logger = structlog.get_logger(__name__)

# Identifiers dei criteri universali nel formato restituito dal LLM
_UNIVERSAL_CRITERION_IDS = {"U1", "U2", "U3", "U4", "U5", "U6"}


class QualityEvaluator:
    """RF-02: Valuta la qualità visiva per ogni classificazione identificata."""

    def __init__(
        self,
        llm_client: BaseLLMClient,
        taxonomy_manager: TaxonomyManager,
        settings: Settings,
    ) -> None:
        self._llm = llm_client
        self._taxonomy = taxonomy_manager
        self._settings = settings

    async def evaluate(
        self,
        image_b64: str,
        classifications: list[Classification],
    ) -> tuple[list[QualityEvaluation], list[AnalysisError]]:
        """Valuta la qualità per ogni classificazione.

        Un errore su una singola classificazione non blocca le altre:
        l'errore viene registrato e la classificazione viene saltata.

        Args:
            image_b64: Immagine in base64.
            classifications: Classificazioni da RF-01 con confidence >= 0.45.

        Returns:
            Tuple (evaluations, errors) dove:
              - evaluations: lista di QualityEvaluation, una per classificazione
                valutata con successo.
              - errors: lista di AnalysisError non bloccanti per classificazioni
                che non è stato possibile valutare.
        """
        evaluations: list[QualityEvaluation] = []
        all_errors: list[AnalysisError] = []

        for cls in classifications:
            try:
                evaluation, step_errors = await self._evaluate_single(image_b64, cls)
                all_errors.extend(step_errors)
                if evaluation is not None:
                    evaluations.append(evaluation)
            except Exception as exc:
                logger.warning(
                    "quality_evaluator_step_failed",
                    category_id=cls.category_id,
                    category_name=cls.category_name,
                    error=str(exc),
                )
                all_errors.append(
                    AnalysisError(
                        code="E-QUALITY-STEP",
                        message=(
                            f"Quality evaluation failed for format {cls.category_id} "
                            f"({cls.category_name}): {exc}"
                        ),
                        severity="warning",
                    )
                )

        logger.info(
            "quality_evaluator_done",
            classifications_count=len(classifications),
            evaluations_count=len(evaluations),
            errors_count=len(all_errors),
        )
        return evaluations, all_errors

    # ------------------------------------------------------------------
    # Privati
    # ------------------------------------------------------------------

    async def _evaluate_single(
        self,
        image_b64: str,
        cls: Classification,
    ) -> tuple[QualityEvaluation | None, list[AnalysisError]]:
        """Esegue la valutazione per una singola classificazione."""
        errors: list[AnalysisError] = []

        try:
            # get_criteria_for_format ritorna list[{"criterion": str, "weight": float}]
            criteria = self._taxonomy.get_criteria_for_format(cls.category_id)
        except (KeyError, RuntimeError) as exc:
            logger.warning(
                "quality_evaluator_no_criteria",
                category_id=cls.category_id,
                error=str(exc),
            )
            errors.append(
                AnalysisError(
                    code="E-NO-CRITERIA",
                    message=f"No quality criteria found for format {cls.category_id}: {exc}",
                    severity="warning",
                )
            )
            return None, errors

        system_prompt = build_quality_prompt(
            category_id=cls.category_id,
            category_name=cls.category_name,
            criteria_list=criteria,
        )

        try:
            raw_response = await self._llm.analyze_image(
                image_base64=image_b64,
                prompt=system_prompt,
                temperature=0.2,
                max_tokens=4096,
            )
        except Exception as exc:
            logger.error(
                "quality_evaluator_llm_error",
                category_id=cls.category_id,
                error=str(exc),
            )
            errors.append(
                AnalysisError(
                    code="E-LLM-QUALITY",
                    message=f"LLM call failed for quality evaluation of {cls.category_id}: {exc}",
                    severity="warning",
                )
            )
            return None, errors

        evaluation, parse_errors = self._parse_response(raw_response, cls, criteria)
        errors.extend(parse_errors)
        return evaluation, errors

    def _parse_response(
        self,
        raw: str,
        cls: Classification,
        criteria_spec: list[dict[str, Any]],
    ) -> tuple[QualityEvaluation | None, list[AnalysisError]]:
        """Parsa la risposta LLM e costruisce il QualityEvaluation.

        Gestisce due possibili strutture JSON:
        1. Schema del prompt builder: {"universal_criteria": [...], "category_criteria": [...]}
        2. Schema flat alternativo: {"criteria": [...]} (compatibilità con vecchio codice)

        Se il LLM non restituisce un overall_score valido, lo calcola come
        media pesata: (avg_universali * 0.35) + (avg_pesata_categoria * 0.65).
        """
        errors: list[AnalysisError] = []
        cleaned = _strip_markdown_fences(raw)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.warning(
                "quality_evaluator_json_error",
                category_id=cls.category_id,
                error=str(exc),
                raw_preview=raw[:300],
            )
            errors.append(
                AnalysisError(
                    code="E-JSON-QUALITY",
                    message=f"Failed to parse quality response for {cls.category_id}: {exc}",
                    severity="warning",
                )
            )
            return None, errors

        try:
            # Raccoglie tutti i criteri dalla risposta: universali + di categoria
            all_raw_items: list[dict] = []
            if "universal_criteria" in data or "category_criteria" in data:
                all_raw_items.extend(data.get("universal_criteria", []))
                all_raw_items.extend(data.get("category_criteria", []))
            else:
                # Fallback: schema flat con "criteria"
                all_raw_items.extend(data.get("criteria", []))

            parsed_criteria: list[QualityCriterionScore] = []
            for item in all_raw_items:
                try:
                    score_raw = int(item.get("score", 5))
                    score_clamped = max(1, min(10, score_raw))
                    label = str(item.get("label", _score_to_label(score_clamped)))
                    parsed_criteria.append(
                        QualityCriterionScore(
                            criterion=str(item.get("criterion", "")),
                            label=label,
                            score=score_clamped,
                            rationale=str(item.get("rationale", "")),
                        )
                    )
                except (KeyError, ValueError, TypeError) as exc:
                    logger.warning(
                        "quality_evaluator_skip_criterion",
                        category_id=cls.category_id,
                        error=str(exc),
                        item=item,
                    )

            # Usa overall_score dal LLM se valido; altrimenti calcola
            overall_score_raw = data.get("overall_score")
            if overall_score_raw is not None:
                overall_score = float(overall_score_raw)
                overall_score = max(1.0, min(10.0, overall_score))
            else:
                overall_score = _compute_weighted_score(parsed_criteria, criteria_spec)

            return (
                QualityEvaluation(
                    category_id=str(data.get("category_id", cls.category_id)),
                    category_name=str(data.get("category_name", cls.category_name)),
                    overall_score=round(overall_score, 1),
                    criteria=parsed_criteria,
                ),
                errors,
            )

        except (KeyError, ValueError, TypeError) as exc:
            logger.warning(
                "quality_evaluator_parse_error",
                category_id=cls.category_id,
                error=str(exc),
            )
            errors.append(
                AnalysisError(
                    code="E-PARSE-QUALITY",
                    message=f"Failed to build QualityEvaluation for {cls.category_id}: {exc}",
                    severity="warning",
                )
            )
            return None, errors


def _score_to_label(score: int) -> str:
    """Mappa lo score numerico all'etichetta qualitativa."""
    if score <= 3:
        return "Critical"
    if score <= 6:
        return "Average"
    if score <= 9:
        return "Good"
    return "Excellent"


def _compute_weighted_score(
    parsed_criteria: list[QualityCriterionScore],
    criteria_spec: list[dict[str, Any]],
) -> float:
    """Calcola la media pesata dei criteri parsati.

    Formula (da 02_criteri_qualita_per_tipologia.md):
      Score = (avg_universali × 0.35) + (weighted_avg_categoria × 0.65)

    Se non è possibile distinguere i criteri universali da quelli di categoria
    (perché tutti o nessuno ha ID U1-U6), usa la media semplice come fallback.

    criteria_spec ha formato: [{"criterion": str, "weight": float}]
    — questo è il formato di TaxonomyManager.get_criteria_for_format().
    """
    if not parsed_criteria:
        return 5.0

    # Costruisce mappa criterion_name -> weight dai criteri di spec
    weight_map: dict[str, float] = {
        c.get("criterion", ""): float(c.get("weight", 1.0))
        for c in criteria_spec
    }

    universal_scores: list[float] = []
    category_scores: list[float] = []
    category_weights: list[float] = []

    for pc in parsed_criteria:
        if pc.criterion in _UNIVERSAL_CRITERION_IDS:
            universal_scores.append(float(pc.score))
        else:
            w = weight_map.get(pc.criterion, 1.0)
            category_scores.append(float(pc.score) * w)
            category_weights.append(w)

    avg_universal = (
        sum(universal_scores) / len(universal_scores) if universal_scores else None
    )
    avg_category = (
        sum(category_scores) / sum(category_weights)
        if category_scores and sum(category_weights) > 0
        else None
    )

    if avg_universal is not None and avg_category is not None:
        return avg_universal * 0.35 + avg_category * 0.65
    if avg_universal is not None:
        return avg_universal
    if avg_category is not None:
        return avg_category

    # Fallback: media semplice su tutti i criteri parsati
    return sum(float(pc.score) for pc in parsed_criteria) / len(parsed_criteria)


def _strip_markdown_fences(text: str) -> str:
    """Rimuove i fence ```json ... ``` se presenti nella risposta LLM."""
    stripped = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", stripped)
    if match:
        return match.group(1).strip()
    return stripped
