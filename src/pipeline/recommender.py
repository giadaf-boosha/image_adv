from __future__ import annotations

import json
import re
from typing import Optional

import structlog

from src.llm.base import BaseLLMClient
from src.models.schemas import (
    AnalysisError,
    AngleRecommendation,
    Classification,
    FunnelStage,
    PlatformHint,
    ProductContext,
    RecommendationsOutput,
)
from src.models.taxonomy import TaxonomyManager
from src.config import Settings
from src.prompts.recommendation import build_recommendation_prompt

logger = structlog.get_logger(__name__)


class AngleHookRecommender:
    """RF-04: Genera angoli alternativi e hook creativi per l'immagine analizzata."""

    def __init__(
        self,
        llm_client: BaseLLMClient,
        taxonomy_manager: TaxonomyManager,
        settings: Settings,
    ) -> None:
        self._llm = llm_client
        self._taxonomy = taxonomy_manager
        self._settings = settings

    async def recommend(
        self,
        image_b64: str,
        classifications: list[Classification],
        funnel_stage: Optional[FunnelStage] = None,
        platform: Optional[PlatformHint] = None,
        audience_hint: Optional[str] = None,
    ) -> tuple[RecommendationsOutput | None, list[AnalysisError]]:
        """Genera raccomandazioni di angoli e hook.

        Usa temperature=0.7 per massimizzare la creatività delle raccomandazioni.

        Args:
            image_b64: Immagine in base64.
            classifications: Classificazioni identificate da RF-01.
            funnel_stage: Stage del funnel (tofu/mofu/bofu). Se None, copre tutti e tre.
            platform: Piattaforma target per calibrare il tone of voice.
            audience_hint: Descrizione del pubblico target.

        Returns:
            Tuple (recommendations, errors) dove:
              - recommendations: RecommendationsOutput con 3-5 angoli e 5 hook variations,
                                 o None se il LLM fallisce in modo irrecuperabile.
              - errors: lista di AnalysisError non bloccanti.
        """
        errors: list[AnalysisError] = []

        classifications_as_dicts = _classifications_to_dicts(classifications)
        taxonomy_summary = self._taxonomy.build_taxonomy_for_prompt()
        funnel_value = funnel_stage.value if funnel_stage else None
        platform_value = platform.value if platform else None

        system_prompt = build_recommendation_prompt(
            classifications=classifications_as_dicts,
            taxonomy_summary=taxonomy_summary,
            funnel_stage=funnel_value,
            platform_target=platform_value,
            audience_hint=audience_hint,
        )

        logger.info(
            "recommender_start",
            classifications_count=len(classifications),
            funnel_stage=funnel_value,
            platform=platform_value,
        )

        try:
            raw_response = await self._llm.analyze_image(
                image_base64=image_b64,
                prompt=system_prompt,
                temperature=0.7,
                max_tokens=3072,
            )
        except Exception as exc:
            logger.error("recommender_llm_error", error=str(exc))
            errors.append(
                AnalysisError(
                    code="E-LLM-RECOMMEND",
                    message=f"LLM call failed during recommendation: {exc}",
                    severity="error",
                )
            )
            return None, errors

        result, parse_errors = self._parse_response(raw_response, classifications)
        errors.extend(parse_errors)

        if result is not None:
            self._verify_no_format_overlap(result, classifications, errors)
            logger.info(
                "recommender_done",
                angles_count=len(result.angle_recommendations),
                hooks_count=len(result.hook_variations),
                errors_count=len(errors),
            )

        return result, errors

    # ------------------------------------------------------------------
    # Privati
    # ------------------------------------------------------------------

    def _parse_response(
        self,
        raw: str,
        classifications: list[Classification],
    ) -> tuple[RecommendationsOutput | None, list[AnalysisError]]:
        """Parsa la risposta LLM e costruisce il RecommendationsOutput."""
        errors: list[AnalysisError] = []
        cleaned = _strip_markdown_fences(raw)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.warning(
                "recommender_json_error",
                error=str(exc),
                raw_preview=raw[:300],
            )
            errors.append(
                AnalysisError(
                    code="E-JSON-RECOMMEND",
                    message=f"Failed to parse recommendation response as JSON: {exc}",
                    severity="warning",
                )
            )
            return None, errors

        try:
            pc_data = data.get("product_context", {})
            product_context = ProductContext(
                identified_product=str(pc_data.get("identified_product", "Unknown")),
                identified_brand=str(pc_data.get("identified_brand", "Unknown")),
                identified_vertical=str(pc_data.get("identified_vertical", "Unknown")),
                identified_current_angle=str(
                    pc_data.get("identified_current_angle", "Unknown")
                ),
            )

            angles: list[AngleRecommendation] = []
            for item in data.get("angle_recommendations", [])[:5]:
                try:
                    angles.append(
                        AngleRecommendation(
                            angle_id=int(item.get("angle_id", len(angles) + 1)),
                            angle_name=str(item.get("angle_name", "")),
                            creative_format_reference=str(
                                item.get("creative_format_reference", "")
                            ),
                            hook_example=str(item.get("hook_example", "")),
                            rationale=str(item.get("rationale", "")),
                            suggested_format=str(item.get("suggested_format", "")),
                        )
                    )
                except (KeyError, ValueError, TypeError) as exc:
                    logger.warning(
                        "recommender_skip_invalid_angle",
                        error=str(exc),
                        item=item,
                    )

            hook_variations: list[str] = [
                str(h) for h in data.get("hook_variations", [])[:5] if h
            ]

            funnel_mapping: dict = data.get(
                "funnel_mapping",
                {
                    "tofu": "Brand awareness content",
                    "mofu": "Product education content",
                    "bofu": "Conversion-focused content",
                },
            )

            return (
                RecommendationsOutput(
                    product_context=product_context,
                    angle_recommendations=angles,
                    hook_variations=hook_variations,
                    funnel_mapping=funnel_mapping,
                ),
                errors,
            )

        except (KeyError, ValueError, TypeError) as exc:
            logger.warning("recommender_parse_error", error=str(exc))
            errors.append(
                AnalysisError(
                    code="E-PARSE-RECOMMEND",
                    message=f"Failed to build RecommendationsOutput: {exc}",
                    severity="warning",
                )
            )
            return None, errors

    def _verify_no_format_overlap(
        self,
        result: RecommendationsOutput,
        classifications: list[Classification],
        errors: list[AnalysisError],
    ) -> None:
        """Verifica che gli angoli suggeriti non coincidano con i formati già classificati.

        Confronta il creative_format_reference di ogni angolo raccomandato con
        gli category_id delle classificazioni esistenti. Se c'è sovrapposizione,
        aggiunge un warning non bloccante nell'errors list.
        """
        classified_ids = {cls.category_id for cls in classifications}
        classified_names_lower = {cls.category_name.lower() for cls in classifications}

        for angle in result.angle_recommendations:
            ref = angle.creative_format_reference.lower()
            # Controlla se il riferimento al formato contiene un ID già classificato
            format_overlap = any(cid in ref for cid in classified_ids)
            # Controlla anche per nome (es. "Before / After" già classificato)
            name_overlap = any(name in ref for name in classified_names_lower)

            if format_overlap or name_overlap:
                logger.warning(
                    "recommender_format_overlap",
                    angle_name=angle.angle_name,
                    creative_format_reference=angle.creative_format_reference,
                )
                errors.append(
                    AnalysisError(
                        code="W-FORMAT-OVERLAP",
                        message=(
                            f"Angle '{angle.angle_name}' references format "
                            f"'{angle.creative_format_reference}' which overlaps "
                            f"with an already-classified format. Consider replacing "
                            f"with a genuinely different creative approach."
                        ),
                        severity="warning",
                    )
                )


def _classifications_to_dicts(classifications: list[Classification]) -> list[dict]:
    """Converte le Classification nel formato atteso da build_recommendation_prompt."""
    return [
        {
            "category_id": cls.category_id,
            "category_name": cls.category_name,
            "macro_category_name": cls.macro_category_name,
            "confidence": cls.confidence,
        }
        for cls in classifications
    ]


def _strip_markdown_fences(text: str) -> str:
    """Rimuove i fence ```json ... ``` se presenti nella risposta LLM."""
    stripped = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", stripped)
    if match:
        return match.group(1).strip()
    return stripped
