from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ImageSource(str, Enum):
    URL = "url"
    UPLOAD = "upload"


class FunnelStage(str, Enum):
    TOFU = "tofu"
    MOFU = "mofu"
    BOFU = "bofu"


class PlatformHint(str, Enum):
    META = "meta"
    TIKTOK = "tiktok"
    PINTEREST = "pinterest"
    YOUTUBE = "youtube"
    GOOGLE_DISPLAY = "google_display"


class AnalysisRequest(BaseModel):
    image_url: Optional[str] = None
    platform_hint: Optional[PlatformHint] = None
    vertical_hint: Optional[str] = None
    funnel_stage: Optional[FunnelStage] = None
    platform_target: Optional[PlatformHint] = None
    audience_hint: Optional[str] = None
    force_new_type_check: bool = False


class Classification(BaseModel):
    category_id: str
    category_name: str
    macro_category_id: int
    macro_category_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str = Field(min_length=20)


class QualityCriterionScore(BaseModel):
    criterion: str
    label: str
    score: int = Field(ge=1, le=10)
    rationale: str = Field(min_length=20)


class QualityEvaluation(BaseModel):
    category_id: str
    category_name: str
    overall_score: float = Field(ge=1.0, le=10.0)
    criteria: list[QualityCriterionScore]


class ClosestKnownType(BaseModel):
    category_id: str
    category_name: str
    confidence: float


class ProposedNewType(BaseModel):
    working_name: str
    description: str
    visual_elements: list[str]
    suggested_macro_category: Optional[str] = None
    differentiation_from_closest: str
    potential_use_cases: list[str]
    confidence_in_novelty: float = Field(ge=0.0, le=1.0)


class NewTypeAlert(BaseModel):
    triggered: bool
    trigger_reason: str
    closest_known_types: list[ClosestKnownType]
    proposed_new_type: Optional[ProposedNewType] = None
    alert_id: Optional[str] = None
    timestamp: datetime
    review_status: str = "pending"


class ProductContext(BaseModel):
    identified_product: str
    identified_brand: str
    identified_vertical: str
    identified_current_angle: str


class AngleRecommendation(BaseModel):
    angle_id: int
    angle_name: str
    creative_format_reference: str
    hook_example: str
    rationale: str
    suggested_format: str


class RecommendationsOutput(BaseModel):
    product_context: ProductContext
    angle_recommendations: list[AngleRecommendation]
    hook_variations: list[str]
    funnel_mapping: dict


class ProcessingMetadata(BaseModel):
    model_used: str
    processing_time_ms: int
    pipeline_steps_executed: list[str]


class AnalysisError(BaseModel):
    code: str
    message: str
    severity: str = "warning"


class AnalysisResponse(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    input: dict
    processing_metadata: ProcessingMetadata
    classifications: list[Classification]
    quality_evaluations: Optional[list[QualityEvaluation]] = None
    new_type_alert: Optional[NewTypeAlert] = None
    angle_recommendations: Optional[RecommendationsOutput] = None
    errors: list[AnalysisError] = []
    schema_version: str = "1.0"
