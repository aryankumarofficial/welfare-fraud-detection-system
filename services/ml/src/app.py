import json
import time
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from pydantic import BaseModel, Field

from src.db.session import close_db, get_db_session, get_engine
from src.exceptions import (
    FeatureGenerationError,
    MissingSourceDataError,
    PredictionFailedError,
    ProfileNotFoundError,
    SnapshotGenerationError,
    SnapshotNotFoundError,
    SnapshotProfileMismatchError,
)
from src.observability import log_request, log_event, logger
from src.predict import predict_all
from src.schemas.feature_snapshot import InvalidFeatureSetError
from src.security import (
    SystemRole,
    TokenRequest,
    TokenResponse,
    get_auth_settings,
    get_current_user,
    require_admin,
    require_analyst,
    require_internal_service,
    require_operator,
    require_queue_access,
    validate_user_credentials,
    create_access_token,
)
from src.services.prediction_analytics import PredictionAnalyticsService
from src.services.alert_service import AlertService
from src.services.drift_monitoring_service import DriftMonitoringService
from src.services.model_evaluation_service import ModelEvaluationService
from src.services.prediction_job_service import (
    PredictionJobService,
    QueuePredictionRequest,
    _serialize_job,
)
from src.services.prediction_review_service import PredictionReviewService, _serialize_review
from src.services.prediction_service import PredictionService
from src.services.snapshot_generator import SnapshotGenerator
from src.services.model_registry_service import ModelRegistryService
from src.services.model_health_service import ModelHealthService
from src.test import run_test_predictions

app = FastAPI(
    title="Welfare Fraud Detection API",
    description="AI-powered welfare fraud detection service with prediction lifecycle, analytics, and model governance.",
    version="1.0.0",
)

app.middleware("http")(log_request)


@app.on_event("startup")
async def startup_event() -> None:
    settings = get_auth_settings()
    insecure_settings = []
    if settings.jwt_secret_key == "change-me":
        insecure_settings.append("JWT_SECRET_KEY")
    if settings.internal_api_key == "internal-change-me":
        insecure_settings.append("INTERNAL_API_KEY")
    if settings.queue_api_key == "queue-change-me":
        insecure_settings.append("QUEUE_API_KEY")
    if insecure_settings:
        logger.warning(json.dumps({"event": "insecure_default_settings", "settings": insecure_settings}))


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await close_db()


class UserData(BaseModel):
    income_in_rs: float
    land_owned_acres: float
    vehicles_owned: int
    electricity_consumption: float
    pending_loans: int
    business_ownership: int

    caste: str
    father_caste: str
    avg_caste_population_per: float
    officer_approvals_per_day: float

    weekly_spending: float
    monthly_spending: float
    transaction_count: int
    avg_transaction_value: float
    luxury_items_bought: int
    weekend_spending_ratio: float

    hospital_visits_per_year: int
    claim_frequency: int
    medical_claim_amount: float
    avg_claim_amount: float
    chronic_disease: int


class PredictProfileRequest(BaseModel):
    student_profile_id: UUID = Field(description="Beneficiary profile UUID")


class GenerateSnapshotRequest(BaseModel):
    student_profile_id: UUID = Field(description="Beneficiary profile UUID")


class QueuePredictionItem(BaseModel):
    student_profile_id: UUID
    feature_snapshot_id: UUID | None = None


class QueuePredictionBody(BaseModel):
    student_profile_id: UUID | None = None
    feature_snapshot_id: UUID | None = None
    predictions: list[QueuePredictionItem] | None = None


class JobAttemptBody(BaseModel):
    attempt: int = Field(default=1, ge=1, le=3)
    error: str | None = None


class RegisterModelBody(BaseModel):
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    description: str | None = None
    artifact_uri: str | None = None
    artifact_hash: str | None = None
    configuration: dict | None = None
    training_metadata: dict | None = None
    feature_schema_version: str | None = None
    parent_model_id: UUID | None = None


class PromoteModelBody(BaseModel):
    promoted_by: str | None = None


class RollbackModelBody(BaseModel):
    reason: str | None = None
    performed_by: str | None = None


class ArchiveModelBody(BaseModel):
    performed_by: str | None = None


class EvaluateModelBody(BaseModel):
    dataset_name: str = Field(min_length=1)
    dataset_version: str | None = None
    sample_size: int = Field(ge=1)
    precision: float = Field(ge=0, le=1)
    recall: float = Field(ge=0, le=1)
    f1_score: float = Field(ge=0, le=1)
    false_positive_rate: float = Field(ge=0, le=1)
    additional_metrics: dict | None = None
    evaluated_by: str | None = None


class PredictionReviewBody(BaseModel):
    reviewer: str = Field(min_length=1)
    decision: str = Field(default="pending")
    notes: str | None = None


@app.get("/")
def home():
    return {"message": "Welfare Fraud Detection API is running"}


@app.post("/auth/token", response_model=TokenResponse)
def create_token(body: TokenRequest):
    role = validate_user_credentials(body.username, body.password)
    if role is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token, expires_at = create_access_token(body.username, role)
    return {
        "access_token": token,
        "expires_in": max(0, expires_at - int(time.time())),
        "role": role,
    }


@app.get("/health")
async def health():
    engine = get_engine()
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "error": "database_unavailable", "detail": str(exc)},
        )

    return {
        "status": "ok",
        "database": "ok",
        "models_loaded": True,
        "service": "ready",
    }


@app.get("/ready")
async def ready():
    engine = get_engine()
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unready"})
    return {"status": "ready"}


@app.post("/predict", dependencies=[Depends(require_operator)])
def predict(data: UserData):
    result = predict_all(data.model_dump())

    return {"success": True, "data": result}


@app.post("/predict/profile", dependencies=[Depends(require_operator)])
async def predict_profile(body: PredictProfileRequest):
    async with get_db_session() as session:
        service = PredictionService(session)

        try:
            result = await service.predict_for_snapshot(body.student_profile_id)
        except ProfileNotFoundError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PROFILE_NOT_FOUND"},
            )
        except SnapshotNotFoundError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "SNAPSHOT_NOT_FOUND"},
            )
        except InvalidFeatureSetError:
            return JSONResponse(
                status_code=422,
                content={"success": False, "error": "INVALID_FEATURE_SET"},
            )
        except PredictionFailedError:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "PREDICTION_FAILED"},
            )

        return {
            "success": True,
            "data": {
                "prediction_id": str(result.prediction_id),
                "student_profile_id": str(result.student_profile_id),
                "feature_snapshot_id": str(result.feature_snapshot_id),
                "model_version_id": (
                    str(result.model_version_id) if result.model_version_id else None
                ),
                "risk_level": result.risk_level,
                "prediction_duration_ms": result.prediction_duration_ms,
                "explanation": result.explanation,
                **result.risks,
            },
        }


@app.post("/snapshot/generate", dependencies=[Depends(require_operator)])
async def generate_snapshot(body: GenerateSnapshotRequest):
    async with get_db_session() as session:
        generator = SnapshotGenerator(session)

        try:
            result = await generator.generate_for_profile(body.student_profile_id)
        except ProfileNotFoundError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PROFILE_NOT_FOUND"},
            )
        except MissingSourceDataError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": "MISSING_SOURCE_DATA",
                    "missing_sources": exc.missing_sources,
                },
            )
        except FeatureGenerationError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": "FEATURE_GENERATION_FAILED",
                    "details": exc.details,
                },
            )
        except SnapshotGenerationError:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "SNAPSHOT_GENERATION_FAILED"},
            )

        return {
            "success": True,
            "data": {
                "feature_snapshot_id": str(result.snapshot.id),
                "student_profile_id": str(result.snapshot.student_profile_id),
                "feature_schema_version": result.snapshot.feature_schema_version,
                "source": result.snapshot.source,
                "checksum": result.snapshot.checksum,
                "features": result.features,
            },
        }


@app.post("/predict/generate", dependencies=[Depends(require_operator)])
async def predict_generated_snapshot(body: PredictProfileRequest):
    async with get_db_session() as session:
        generator = SnapshotGenerator(session)
        prediction_service = PredictionService(session)

        try:
            generated = await generator.generate_for_profile(body.student_profile_id)
            result = await prediction_service.predict_for_feature_snapshot(
                student_profile_id=body.student_profile_id,
                feature_snapshot_id=generated.snapshot.id,
            )
        except ProfileNotFoundError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PROFILE_NOT_FOUND"},
            )
        except MissingSourceDataError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": "MISSING_SOURCE_DATA",
                    "missing_sources": exc.missing_sources,
                },
            )
        except FeatureGenerationError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": "FEATURE_GENERATION_FAILED",
                    "details": exc.details,
                },
            )
        except SnapshotGenerationError:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "SNAPSHOT_GENERATION_FAILED"},
            )
        except InvalidFeatureSetError:
            return JSONResponse(
                status_code=422,
                content={"success": False, "error": "INVALID_FEATURE_SET"},
            )
        except (SnapshotNotFoundError, SnapshotProfileMismatchError):
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "SNAPSHOT_NOT_FOUND"},
            )
        except PredictionFailedError:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "PREDICTION_FAILED"},
            )

        return {
            "success": True,
            "data": {
                "prediction_id": str(result.prediction_id),
                "student_profile_id": str(result.student_profile_id),
                "feature_snapshot_id": str(generated.snapshot.id),
                "model_version_id": (
                    str(result.model_version_id) if result.model_version_id else None
                ),
                "risk_level": result.risk_level,
                "prediction_duration_ms": result.prediction_duration_ms,
                "explanation": result.explanation,
                **result.risks,
            },
        }


@app.get("/test", dependencies=[Depends(require_admin)])
def test():
    pridictions = run_test_predictions()

    return {"success": True, "result": pridictions}


@app.post("/predictions/queue", dependencies=[Depends(require_operator)])
async def queue_prediction(body: QueuePredictionBody):
    async with get_db_session() as session:
        service = PredictionJobService(session)

        if body.predictions:
            result = await service.enqueue_batch(
                [
                    QueuePredictionRequest(
                        student_profile_id=item.student_profile_id,
                        feature_snapshot_id=item.feature_snapshot_id,
                    )
                    for item in body.predictions
                ]
            )
            return {"success": True, "data": result}

        if body.student_profile_id is None:
            return JSONResponse(
                status_code=422,
                content={"success": False, "error": "STUDENT_PROFILE_ID_REQUIRED"},
            )

        job = await service.enqueue_prediction(
            student_profile_id=body.student_profile_id,
            feature_snapshot_id=body.feature_snapshot_id,
        )
        return {"success": True, "data": _serialize_job(job)}


@app.get("/predictions/reviews", dependencies=[Depends(require_analyst)])
async def get_prediction_reviews(decision: str | None = None, limit: int = 100):
    async with get_db_session() as session:
        service = PredictionReviewService(session)
        return {"success": True, "data": await service.list_reviews(decision=decision, limit=limit)}


@app.get("/predictions/{student_profile_id}", dependencies=[Depends(require_operator)])
async def get_predictions_by_student_profile(student_profile_id: UUID):
    async with get_db_session() as session:
        service = PredictionAnalyticsService(session)
        history = await service.get_prediction_history(student_profile_id)

        if history is not None:
            return {"success": True, "data": history}

        details = await service.get_prediction_details(student_profile_id)
        if details is not None:
            return {"success": True, "data": details}

        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "PREDICTION_NOT_FOUND"},
        )


@app.get("/predictions/detail/{prediction_id}", dependencies=[Depends(require_operator)])
async def get_prediction_by_id(prediction_id: UUID):
    async with get_db_session() as session:
        service = PredictionAnalyticsService(session)
        result = await service.get_prediction_details(prediction_id)

        if result is None:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PREDICTION_NOT_FOUND"},
            )

        return {"success": True, "data": result}


@app.get("/metrics/predictions", dependencies=[Depends(require_analyst)])
async def get_prediction_metrics():
    async with get_db_session() as session:
        service = PredictionAnalyticsService(session)
        return await service.get_operational_metrics()


@app.get("/analytics/predictions", dependencies=[Depends(require_analyst)])
async def get_prediction_analytics():
    async with get_db_session() as session:
        service = PredictionAnalyticsService(session)
        return await service.get_prediction_analytics()


@app.post("/predictions/{prediction_id}/review", dependencies=[Depends(require_analyst)])
async def create_prediction_review(prediction_id: UUID, body: PredictionReviewBody):
    async with get_db_session() as session:
        service = PredictionReviewService(session)
        try:
            review = await service.create_review(
                prediction_id=prediction_id,
                reviewer=body.reviewer,
                decision=body.decision,
                notes=body.notes,
            )
        except LookupError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PREDICTION_NOT_FOUND"},
            )
        except ValueError:
            return JSONResponse(
                status_code=422,
                content={"success": False, "error": "INVALID_REVIEW_DECISION"},
            )
        return {"success": True, "data": _serialize_review(review)}


@app.get("/predictions/jobs/{job_id}", dependencies=[Depends(require_operator)])
async def get_prediction_job(job_id: UUID):
    async with get_db_session() as session:
        service = PredictionJobService(session)
        job = await service.get_job(job_id)
        if job is None:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PREDICTION_JOB_NOT_FOUND"},
            )
        return {"success": True, "data": _serialize_job(job)}


@app.get("/predictions/jobs/{job_id}/result", dependencies=[Depends(require_operator)])
async def get_prediction_job_result(job_id: UUID):
    async with get_db_session() as session:
        service = PredictionJobService(session)
        job = await service.get_job(job_id)
        if job is None:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PREDICTION_JOB_NOT_FOUND"},
            )
        if job.status != "completed":
            return JSONResponse(
                status_code=409,
                content={
                    "success": False,
                    "error": "PREDICTION_JOB_NOT_COMPLETED",
                    "status": job.status,
                },
            )
        return {"success": True, "data": job.result}


@app.get("/analytics/queue", dependencies=[Depends(require_analyst)])
async def get_queue_analytics():
    async with get_db_session() as session:
        service = PredictionJobService(session)
        return await service.get_queue_analytics()


@app.get("/analytics/model-performance", dependencies=[Depends(require_analyst)])
async def get_model_performance():
    async with get_db_session() as session:
        service = ModelEvaluationService(session)
        return await service.get_model_performance()


@app.get("/analytics/drift", dependencies=[Depends(require_analyst)])
async def get_drift_analytics(days: int = 7):
    async with get_db_session() as session:
        service = DriftMonitoringService(session)
        return await service.get_drift_report(days=days)


@app.get("/analytics/alerts", dependencies=[Depends(require_analyst)])
async def get_alerts():
    async with get_db_session() as session:
        service = AlertService(session)
        return await service.get_alerts()


@app.post(
    "/internal/predictions/jobs/{job_id}/execute",
    dependencies=[Depends(require_internal_service)],
    include_in_schema=False,
)
async def execute_prediction_job(job_id: UUID, body: JobAttemptBody):
    async with get_db_session() as session:
        service = PredictionJobService(session)
        try:
            result = await service.execute_job(job_id, attempt=body.attempt)
        except LookupError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PREDICTION_JOB_NOT_FOUND"},
            )
        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "PREDICTION_JOB_FAILED", "detail": str(exc)},
            )
        return {"success": True, "data": result}


@app.post(
    "/internal/predictions/jobs/{job_id}/retrying",
    dependencies=[Depends(require_internal_service)],
    include_in_schema=False,
)
async def mark_prediction_job_retrying(job_id: UUID, body: JobAttemptBody):
    async with get_db_session() as session:
        service = PredictionJobService(session)
        try:
            job = await service.mark_retrying(
                job_id,
                attempt=body.attempt,
                error=body.error or "Prediction job will be retried.",
            )
        except LookupError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PREDICTION_JOB_NOT_FOUND"},
            )
        return {"success": True, "data": _serialize_job(job)}


@app.post(
    "/internal/predictions/jobs/{job_id}/failed",
    dependencies=[Depends(require_internal_service)],
    include_in_schema=False,
)
async def mark_prediction_job_failed(job_id: UUID, body: JobAttemptBody):
    async with get_db_session() as session:
        service = PredictionJobService(session)
        try:
            job = await service.mark_failed(
                job_id,
                attempt=body.attempt,
                error=body.error or "Prediction job failed.",
            )
        except LookupError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PREDICTION_JOB_NOT_FOUND"},
            )
        return {"success": True, "data": _serialize_job(job)}


@app.get("/dashboard/summary", dependencies=[Depends(require_analyst)])
async def get_dashboard_summary():
    async with get_db_session() as session:
        service = PredictionAnalyticsService(session)
        return await service.get_dashboard_summary()


@app.get("/admin/import/status", dependencies=[Depends(require_analyst)])
async def get_import_status():
    async with get_db_session() as session:
        statements = {
            "profiles": "SELECT COUNT(*) FROM student_profiles",
            "financial_records": "SELECT COUNT(*) FROM student_financial_records",
            "social_records": "SELECT COUNT(*) FROM student_social_records",
            "transaction_records": "SELECT COUNT(*) FROM student_transaction_summaries",
            "medical_records": "SELECT COUNT(*) FROM student_medical_summaries",
            "imported_at": "SELECT MAX(created_at) FROM student_profiles",
        }

        counts: dict[str, int | str | None] = {}
        for key, statement in statements.items():
            result = await session.execute(text(statement))
            value = result.scalar_one()
            counts[key] = value

        imported_at = counts.pop("imported_at")
        imported_at_iso = imported_at.isoformat() if imported_at is not None else None

        return {
            "success": True,
            "data": {
                **counts,
                "imported_at": imported_at_iso,
                "status": "completed",
            },
        }


# ── Model Registry & Lifecycle Endpoints ─────────────────────────────


@app.get("/models", dependencies=[Depends(require_analyst)])
async def list_models(status: str | None = None, role: str | None = None, limit: int = 100):
    async with get_db_session() as session:
        service = ModelRegistryService(session)
        models = await service.list_models(status=status, role=role, limit=limit)
        return {"success": True, "data": models}


@app.get("/models/compare", dependencies=[Depends(require_analyst)])
async def compare_models(ids: str):
    model_ids = [UUID(mid.strip()) for mid in ids.split(",") if mid.strip()]
    if len(model_ids) < 2:
        return JSONResponse(
            status_code=422,
            content={"success": False, "error": "At least two model IDs required for comparison."},
        )
    async with get_db_session() as session:
        service = ModelRegistryService(session)
        comparison = await service.compare_models(model_ids)
        return {"success": True, "data": comparison}


@app.get("/models/{model_id}", dependencies=[Depends(require_analyst)])
async def get_model(model_id: UUID):
    async with get_db_session() as session:
        service = ModelRegistryService(session)
        model = await service.get_model(model_id)
        if model is None:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "MODEL_NOT_FOUND"},
            )
        return {"success": True, "data": model}


@app.post("/models", dependencies=[Depends(require_admin)])
async def register_model(body: RegisterModelBody):
    async with get_db_session() as session:
        service = ModelRegistryService(session)
        model = await service.register_model(
            name=body.name,
            version=body.version,
            description=body.description,
            artifact_uri=body.artifact_uri,
            artifact_hash=body.artifact_hash,
            configuration=body.configuration,
            training_metadata=body.training_metadata,
            feature_schema_version=body.feature_schema_version,
            parent_model_id=body.parent_model_id,
        )
        return {"success": True, "data": model}


@app.post("/models/{model_id}/promote", dependencies=[Depends(require_admin)])
async def promote_model(model_id: UUID, body: PromoteModelBody | None = None):
    async with get_db_session() as session:
        service = ModelRegistryService(session)
        try:
            result = await service.promote_model(
                model_id,
                promoted_by=body.promoted_by if body else None,
            )
        except LookupError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "MODEL_NOT_FOUND"},
            )
        except ValueError as exc:
            return JSONResponse(
                status_code=422,
                content={"success": False, "error": str(exc)},
            )
        return {"success": True, "data": result}


@app.post("/models/{model_id}/rollback", dependencies=[Depends(require_admin)])
async def rollback_model(model_id: UUID, body: RollbackModelBody | None = None):
    async with get_db_session() as session:
        service = ModelRegistryService(session)
        try:
            result = await service.rollback_model(
                model_id,
                reason=body.reason if body else None,
                performed_by=body.performed_by if body else None,
            )
        except LookupError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "MODEL_NOT_FOUND"},
            )
        except ValueError as exc:
            return JSONResponse(
                status_code=422,
                content={"success": False, "error": str(exc)},
            )
        return {"success": True, "data": result}


@app.post("/models/{model_id}/evaluate", dependencies=[Depends(require_analyst)])
async def evaluate_model(model_id: UUID, body: EvaluateModelBody):
    async with get_db_session() as session:
        service = ModelRegistryService(session)
        try:
            result = await service.create_evaluation_run(
                model_id,
                dataset_name=body.dataset_name,
                dataset_version=body.dataset_version,
                sample_size=body.sample_size,
                precision=body.precision,
                recall=body.recall,
                f1_score=body.f1_score,
                false_positive_rate=body.false_positive_rate,
                additional_metrics=body.additional_metrics,
                evaluated_by=body.evaluated_by,
            )
        except LookupError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "MODEL_NOT_FOUND"},
            )
        return {"success": True, "data": result}


@app.post("/models/{model_id}/archive", dependencies=[Depends(require_admin)])
async def archive_model(model_id: UUID, body: ArchiveModelBody | None = None):
    async with get_db_session() as session:
        service = ModelRegistryService(session)
        try:
            result = await service.archive_model(
                model_id,
                performed_by=body.performed_by if body else None,
            )
        except LookupError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "MODEL_NOT_FOUND"},
            )
        except ValueError as exc:
            return JSONResponse(
                status_code=422,
                content={"success": False, "error": str(exc)},
            )
        return {"success": True, "data": result}


@app.get("/analytics/model-health", dependencies=[Depends(require_analyst)])
async def get_model_health():
    async with get_db_session() as session:
        service = ModelHealthService(session)
        return await service.get_model_health()
