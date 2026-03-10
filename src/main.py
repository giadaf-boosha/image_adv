from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator

import structlog
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from src.config import Settings
from src.llm.base import LLMClientError, LLMRateLimitError, LLMServerError, LLMTimeoutError
from src.llm.gemini_client import GeminiClient
from src.llm.openai_client import OpenAIClient
from src.models.schemas import (
    AnalysisError,
    AnalysisRequest,
    AnalysisResponse,
    FunnelStage,
    PlatformHint,
    ProcessingMetadata,
)
from src.models.taxonomy import TaxonomyManager
from src.pipeline.classifier import AdClassifier
from src.pipeline.novelty_detector import NoveltyDetector
from src.pipeline.preprocessor import ImagePreprocessor
from src.pipeline.quality_evaluator import QualityEvaluator
from src.pipeline.recommender import AngleHookRecommender

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Costanti pipeline
# ---------------------------------------------------------------------------

# Classificazioni con confidence >= questa soglia attivano RF-02
_QUALITY_EVAL_THRESHOLD = 0.45


# ---------------------------------------------------------------------------
# Lifespan: startup / shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Inizializza le risorse condivise all'avvio dell'applicazione."""
    settings = Settings()
    app.state.settings = settings

    # Tassonomia
    taxonomy_manager = TaxonomyManager()
    try:
        taxonomy_manager.load_taxonomy(settings.taxonomy_path)
        taxonomy_manager.load_quality_criteria(settings.quality_criteria_path)
        logger.info("taxonomy_loaded", path=settings.taxonomy_path)
    except FileNotFoundError as exc:
        logger.warning(
            "taxonomy_file_not_found",
            error=str(exc),
            note="Pipeline sarà operativa ma senza tassonomia completa",
        )

    app.state.taxonomy_manager = taxonomy_manager

    # Client LLM primario (Gemini)
    primary_client: GeminiClient | None = None
    try:
        primary_client = GeminiClient(
            api_key=settings.google_api_key,
            request_timeout_seconds=settings.llm_timeout_seconds,
        )
        logger.info("primary_llm_initialized", model=primary_client._model_name)
    except LLMClientError as exc:
        logger.warning(
            "primary_llm_init_failed",
            error=str(exc),
            note="Le richieste useranno direttamente il fallback OpenAI",
        )

    app.state.primary_client = primary_client

    # Client LLM fallback (OpenAI)
    fallback_client: OpenAIClient | None = None
    try:
        fallback_client = OpenAIClient(
            api_key=settings.openai_api_key,
            model_name=settings.fallback_model,
            request_timeout_seconds=settings.llm_timeout_seconds,
        )
        logger.info("fallback_llm_initialized", model=settings.fallback_model)
    except LLMClientError as exc:
        logger.warning(
            "fallback_llm_init_failed",
            error=str(exc),
            note="Nessun fallback disponibile — errori primario saranno bloccanti",
        )

    app.state.fallback_client = fallback_client

    logger.info("application_startup_complete", version=settings.app_version)
    yield

    logger.info("application_shutdown")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Image ADV Analyzer",
    description="Agente AI per l'analisi e classificazione di immagini pubblicitarie",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Helper: selezione client LLM
# ---------------------------------------------------------------------------

def _get_active_llm(app_state):
    """Restituisce il client LLM attivo (primario se disponibile, altrimenti fallback)."""
    if app_state.primary_client is not None:
        return app_state.primary_client
    if app_state.fallback_client is not None:
        return app_state.fallback_client
    return None


def _active_model_name(app_state) -> str:
    client = _get_active_llm(app_state)
    if client is not None:
        return client._model_name
    return "unavailable"


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------

async def _run_pipeline(
    app_state,
    image_url: Optional[str],
    image_bytes: Optional[bytes],
    request_params: AnalysisRequest,
) -> AnalysisResponse:
    """Esegue la pipeline completa RF-01 -> RF-02 -> RF-03 -> RF-04.

    I return type dei moduli pipeline:
      - preprocessor.validate_and_prepare_from_parts() -> tuple[str, list[AnalysisError]]
      - classifier.classify() -> tuple[list[Classification], list[AnalysisError]]
      - evaluator.evaluate() -> tuple[list[QualityEvaluation], list[AnalysisError]]
      - novelty_detector.detect() -> tuple[NewTypeAlert | None, list[AnalysisError]]
      - recommender.recommend() -> tuple[RecommendationsOutput | None, list[AnalysisError]]

    Raises:
        HTTPException: per errori bloccanti (immagine illeggibile, URL irraggiungibile).
    """
    pipeline_start = time.monotonic()
    steps_executed: list[str] = []
    errors: list[AnalysisError] = []
    model_used: str = _active_model_name(app_state)

    settings: Settings = app_state.settings
    taxonomy_manager: TaxonomyManager = app_state.taxonomy_manager

    # -----------------------------------------------------------------------
    # PREPROCESSING
    # validate_and_prepare_from_parts() -> tuple[str, list[AnalysisError]]
    # -----------------------------------------------------------------------
    step_start = time.monotonic()
    preprocessor = ImagePreprocessor()
    try:
        image_b64, preprocessing_warnings = await preprocessor.validate_and_prepare_from_parts(
            image_url=image_url,
            image_bytes=image_bytes,
        )
        errors.extend(preprocessing_warnings)
    except ValueError as exc:
        error_msg = str(exc)
        if "image_url_unreachable" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "E-105", "message": error_msg},
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "E-101", "message": error_msg},
        )

    steps_executed.append("preprocessing")
    logger.info(
        "pipeline_step_done",
        step="preprocessing",
        elapsed_ms=int((time.monotonic() - step_start) * 1000),
    )

    # -----------------------------------------------------------------------
    # RF-01 — Classificazione
    # classify() -> tuple[list[Classification], list[AnalysisError]]
    # -----------------------------------------------------------------------
    step_start = time.monotonic()

    active_client = _get_active_llm(app_state)
    if active_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nessun client LLM disponibile.",
        )

    platform_hint_value = (
        request_params.platform_hint.value if request_params.platform_hint else None
    )

    classifications = []
    classification_model_used = model_used

    # Tenta prima con il client primario; in caso di errore recuperabile usa il fallback
    for attempt_client, is_fallback in [
        (active_client, False),
        (app_state.fallback_client, True),
    ]:
        if attempt_client is None:
            continue

        classifier = AdClassifier(
            llm_client=attempt_client,
            taxonomy_manager=taxonomy_manager,
            settings=settings,
        )
        try:
            cls_result, cls_errors = await classifier.classify(
                image_b64=image_b64,
                platform_hint=platform_hint_value,
                vertical_hint=request_params.vertical_hint,
            )
            errors.extend(cls_errors)
            classifications = cls_result
            classification_model_used = attempt_client._model_name

            if is_fallback:
                errors.append(
                    AnalysisError(
                        code="W-001",
                        message="Classificazione eseguita con modello fallback OpenAI",
                        severity="warning",
                    )
                )
            break  # successo — non tentare ulteriori fallback

        except (LLMServerError, LLMTimeoutError, LLMRateLimitError) as exc:
            if not is_fallback:
                logger.warning("rf01_primary_failed", error=str(exc))
                # Continua il loop per tentare il fallback
            else:
                logger.error("rf01_fallback_also_failed", error=str(exc))
                errors.append(
                    AnalysisError(
                        code="E-201",
                        message=f"Classificazione fallita su entrambi i modelli: {exc}",
                        severity="error",
                    )
                )

    model_used = classification_model_used
    steps_executed.append("classification_rf01")
    logger.info(
        "pipeline_step_done",
        step="classification_rf01",
        classifications_count=len(classifications),
        model=model_used,
        elapsed_ms=int((time.monotonic() - step_start) * 1000),
    )

    # Determina il client da usare nei passi successivi coerentemente con RF-01
    if active_client is not None and classification_model_used == active_client._model_name:
        pipeline_llm_client = active_client
    elif app_state.fallback_client is not None:
        pipeline_llm_client = app_state.fallback_client
    else:
        pipeline_llm_client = active_client

    # -----------------------------------------------------------------------
    # RF-02 — Valutazione Qualità (solo se ci sono classificazioni sopra soglia)
    # evaluate() -> tuple[list[QualityEvaluation], list[AnalysisError]]
    # -----------------------------------------------------------------------
    quality_evaluations = None
    qualified_classifications = [
        c for c in classifications if c.confidence >= _QUALITY_EVAL_THRESHOLD
    ]

    if qualified_classifications:
        step_start = time.monotonic()
        evaluator = QualityEvaluator(
            llm_client=pipeline_llm_client,
            taxonomy_manager=taxonomy_manager,
            settings=settings,
        )
        try:
            eval_result, eval_errors = await evaluator.evaluate(
                image_b64=image_b64,
                classifications=qualified_classifications,
            )
            errors.extend(eval_errors)
            quality_evaluations = eval_result if eval_result else None
        except Exception as exc:
            logger.warning("rf02_failed", error=str(exc))
            errors.append(
                AnalysisError(
                    code="W-002",
                    message=f"Valutazione qualità non completata: {exc}",
                    severity="warning",
                )
            )

        steps_executed.append("quality_evaluation_rf02")
        logger.info(
            "pipeline_step_done",
            step="quality_evaluation_rf02",
            evaluations_count=len(quality_evaluations or []),
            elapsed_ms=int((time.monotonic() - step_start) * 1000),
        )

    # -----------------------------------------------------------------------
    # RF-03 — Novelty Detection
    # Trigger: nessuna classificazione >= soglia OPPURE force_new_type_check
    # detect() -> tuple[NewTypeAlert | None, list[AnalysisError]]
    # -----------------------------------------------------------------------
    new_type_alert = None
    should_run_novelty = (
        len(qualified_classifications) == 0
        or request_params.force_new_type_check
    )

    if should_run_novelty:
        step_start = time.monotonic()
        trigger_reason = (
            "force_new_type_check"
            if request_params.force_new_type_check and qualified_classifications
            else "no_classification_above_threshold"
        )

        novelty_detector = NoveltyDetector(
            llm_client=pipeline_llm_client,
            settings=settings,
        )
        try:
            alert_result, alert_errors = await novelty_detector.detect(
                image_b64=image_b64,
                closest_known_types=classifications,
                trigger_reason=trigger_reason,
            )
            errors.extend(alert_errors)
            new_type_alert = alert_result
        except Exception as exc:
            logger.warning("rf03_failed", error=str(exc))
            errors.append(
                AnalysisError(
                    code="W-003",
                    message=f"Rilevamento nuova tipologia non completato: {exc}",
                    severity="warning",
                )
            )

        steps_executed.append("novelty_detection_rf03")
        logger.info(
            "pipeline_step_done",
            step="novelty_detection_rf03",
            triggered=new_type_alert.triggered if new_type_alert else None,
            elapsed_ms=int((time.monotonic() - step_start) * 1000),
        )

    # -----------------------------------------------------------------------
    # RF-04 — Raccomandazioni Angoli e Hook
    # recommend() -> tuple[RecommendationsOutput | None, list[AnalysisError]]
    # -----------------------------------------------------------------------
    step_start = time.monotonic()
    recommender = AngleHookRecommender(
        llm_client=pipeline_llm_client,
        taxonomy_manager=taxonomy_manager,
        settings=settings,
    )

    angle_recommendations = None
    try:
        rec_result, rec_errors = await recommender.recommend(
            image_b64=image_b64,
            classifications=classifications,
            funnel_stage=request_params.funnel_stage,
            platform=request_params.platform_target or request_params.platform_hint,
            audience_hint=request_params.audience_hint,
        )
        errors.extend(rec_errors)
        angle_recommendations = rec_result
    except Exception as exc:
        logger.warning("rf04_failed", error=str(exc))
        errors.append(
            AnalysisError(
                code="W-004",
                message=f"Raccomandazioni angoli non generate: {exc}",
                severity="warning",
            )
        )

    steps_executed.append("angle_recommendations_rf04")
    logger.info(
        "pipeline_step_done",
        step="angle_recommendations_rf04",
        angles_count=(
            len(angle_recommendations.angle_recommendations)
            if angle_recommendations
            else 0
        ),
        elapsed_ms=int((time.monotonic() - step_start) * 1000),
    )

    # -----------------------------------------------------------------------
    # Assembla la risposta finale
    # -----------------------------------------------------------------------
    total_ms = int((time.monotonic() - pipeline_start) * 1000)
    image_source = "url" if image_url else "upload"

    response = AnalysisResponse(
        input={
            "image_source": image_source,
            "image_url": image_url,
            "platform_hint": platform_hint_value,
            "vertical_hint": request_params.vertical_hint,
            "funnel_stage": (
                request_params.funnel_stage.value if request_params.funnel_stage else None
            ),
            "audience_hint": request_params.audience_hint,
            "force_new_type_check": request_params.force_new_type_check,
        },
        processing_metadata=ProcessingMetadata(
            model_used=model_used,
            processing_time_ms=total_ms,
            pipeline_steps_executed=steps_executed,
        ),
        classifications=classifications,
        quality_evaluations=quality_evaluations,
        new_type_alert=new_type_alert,
        angle_recommendations=angle_recommendations,
        errors=errors,
    )

    logger.info(
        "pipeline_complete",
        analysis_id=response.analysis_id,
        total_ms=total_ms,
        steps=steps_executed,
        classifications_count=len(classifications),
        has_quality_evaluations=quality_evaluations is not None,
        has_novelty_alert=new_type_alert is not None and new_type_alert.triggered,
        has_recommendations=angle_recommendations is not None,
    )

    return response


# ---------------------------------------------------------------------------
# Endpoint: POST /analyze (multipart/form-data)
# ---------------------------------------------------------------------------

@app.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analizza un'immagine pubblicitaria",
    description=(
        "Esegue la pipeline completa: classificazione formato creativo (RF-01), "
        "valutazione qualitativa (RF-02), rilevamento nuova tipologia (RF-03), "
        "raccomandazioni angoli e hook (RF-04)."
    ),
)
async def analyze(
    image_url: Optional[str] = Form(default=None),
    platform_hint: Optional[PlatformHint] = Form(default=None),
    vertical_hint: Optional[str] = Form(default=None),
    funnel_stage: Optional[FunnelStage] = Form(default=None),
    platform_target: Optional[PlatformHint] = Form(default=None),
    audience_hint: Optional[str] = Form(default=None),
    force_new_type_check: bool = Form(default=False),
    file: Optional[UploadFile] = File(default=None),
) -> AnalysisResponse:
    """Analizza un'immagine pubblicitaria con la pipeline AI completa.

    Accetta form multipart con `image_url` (URL stringa) oppure `file` (upload binario).
    La pipeline è resiliente: un errore in RF-02 non blocca RF-04.
    Il fallback da Gemini a OpenAI avviene in modo trasparente.
    """
    if image_url is None and file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deve essere fornito image_url oppure file",
        )

    image_bytes: Optional[bytes] = None
    if file is not None:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Il file caricato è vuoto",
            )

    request_params = AnalysisRequest(
        image_url=image_url,
        platform_hint=platform_hint,
        vertical_hint=vertical_hint,
        funnel_stage=funnel_stage,
        platform_target=platform_target,
        audience_hint=audience_hint,
        force_new_type_check=force_new_type_check,
    )

    return await _run_pipeline(
        app_state=app.state,
        image_url=image_url,
        image_bytes=image_bytes,
        request_params=request_params,
    )


@app.post(
    "/analyze/json",
    response_model=AnalysisResponse,
    summary="Analizza un'immagine via JSON body",
    description="Variante JSON dell'endpoint /analyze, accetta AnalysisRequest nel body.",
)
async def analyze_json(request: AnalysisRequest) -> AnalysisResponse:
    """Variante JSON di /analyze per client che preferiscono application/json."""
    if request.image_url is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image_url è obbligatorio quando si usa l'endpoint JSON",
        )

    return await _run_pipeline(
        app_state=app.state,
        image_url=request.image_url,
        image_bytes=None,
        request_params=request,
    )


# ---------------------------------------------------------------------------
# Endpoint: GET /health
# ---------------------------------------------------------------------------

@app.get(
    "/health",
    summary="Health check",
    description="Verifica lo stato dell'applicazione e dei client LLM.",
)
async def health() -> dict:
    """Restituisce lo stato operativo dell'applicazione."""
    settings: Settings = app.state.settings
    primary = app.state.primary_client
    fallback = app.state.fallback_client

    primary_status = "not_configured"
    if primary is not None:
        primary_ok = await primary.health_check()
        primary_status = "ok" if primary_ok else "degraded"

    fallback_status = "not_configured"
    if fallback is not None:
        fallback_ok = await fallback.health_check()
        fallback_status = "ok" if fallback_ok else "degraded"

    overall = "ok"
    if primary_status not in ("ok",) and fallback_status not in ("ok",):
        overall = "degraded"

    return {
        "status": overall,
        "version": settings.app_version,
        "primary_model": primary._model_name if primary else None,
        "primary_llm_status": primary_status,
        "fallback_model": fallback._model_name if fallback else None,
        "fallback_llm_status": fallback_status,
    }


# ---------------------------------------------------------------------------
# Endpoint: GET /taxonomy
# ---------------------------------------------------------------------------

@app.get(
    "/taxonomy",
    summary="Tassonomia completa",
    description="Restituisce la tassonomia dei 128 formati creativi in formato JSON.",
)
async def get_taxonomy() -> JSONResponse:
    """Restituisce la tassonomia completa dei formati creativi."""
    taxonomy_manager: TaxonomyManager = app.state.taxonomy_manager

    if not taxonomy_manager._taxonomy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Tassonomia non caricata. Verificare la configurazione del server.",
        )

    return JSONResponse(content=taxonomy_manager._taxonomy)
