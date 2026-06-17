from uuid import UUID

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.db.session import get_db_session
from src.exceptions import (
    FeatureGenerationError,
    MissingSourceDataError,
    PredictionFailedError,
    ProfileNotFoundError,
    SnapshotGenerationError,
    SnapshotNotFoundError,
    SnapshotProfileMismatchError,
)
from src.predict import predict_all
from src.schemas.feature_snapshot import InvalidFeatureSetError
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
from src.test import run_test_predictions

app = FastAPI()


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


class PredictionReviewBody(BaseModel):
    reviewer: str = Field(min_length=1)
    decision: str = Field(default="pending")
    notes: str | None = None


@app.get("/")
def home():
    return {"message": "Welfare Fraud Detection API is running"}


@app.post("/predict")
def predict(data: UserData):
    result = predict_all(data.model_dump())

    return {"success": True, "data": result}


@app.post("/predict/profile")
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


@app.post("/snapshot/generate")
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


@app.post("/predict/generate")
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


@app.get("/test")
def test():
    pridictions = run_test_predictions()

    return {"success": True, "result": pridictions}


@app.post("/predictions/queue")
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


@app.get("/predictions/reviews")
async def get_prediction_reviews(decision: str | None = None, limit: int = 100):
    async with get_db_session() as session:
        service = PredictionReviewService(session)
        return {"success": True, "data": await service.list_reviews(decision=decision, limit=limit)}


@app.get("/predictions/{student_profile_id}")
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


@app.get("/predictions/detail/{prediction_id}")
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


@app.get("/metrics/predictions")
async def get_prediction_metrics():
    async with get_db_session() as session:
        service = PredictionAnalyticsService(session)
        return await service.get_operational_metrics()


@app.get("/analytics/predictions")
async def get_prediction_analytics():
    async with get_db_session() as session:
        service = PredictionAnalyticsService(session)
        return await service.get_prediction_analytics()


@app.post("/predictions/{prediction_id}/review")
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


@app.get("/predictions/jobs/{job_id}")
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


@app.get("/predictions/jobs/{job_id}/result")
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


@app.get("/analytics/queue")
async def get_queue_analytics():
    async with get_db_session() as session:
        service = PredictionJobService(session)
        return await service.get_queue_analytics()


@app.get("/analytics/model-performance")
async def get_model_performance():
    async with get_db_session() as session:
        service = ModelEvaluationService(session)
        return await service.get_model_performance()


@app.get("/analytics/drift")
async def get_drift_analytics(days: int = 7):
    async with get_db_session() as session:
        service = DriftMonitoringService(session)
        return await service.get_drift_report(days=days)


@app.get("/analytics/alerts")
async def get_alerts():
    async with get_db_session() as session:
        service = AlertService(session)
        return await service.get_alerts()


@app.post("/internal/predictions/jobs/{job_id}/execute")
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


@app.post("/internal/predictions/jobs/{job_id}/retrying")
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


@app.post("/internal/predictions/jobs/{job_id}/failed")
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


@app.get("/dashboard/summary")
async def get_dashboard_summary():
    async with get_db_session() as session:
        service = PredictionAnalyticsService(session)
        return await service.get_dashboard_summary()
