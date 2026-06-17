import uuid
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.prediction_job import PredictionJob
from src.exceptions import (
    PredictionFailedError,
    ProfileNotFoundError,
    SnapshotNotFoundError,
    SnapshotProfileMismatchError,
)
from src.repositories.prediction_job_repository import PredictionJobRepository
from src.schemas.feature_snapshot import InvalidFeatureSetError
from src.services.prediction_analytics import PredictionAnalyticsService
from src.services.prediction_queue_client import PredictionQueueClient
from src.services.prediction_service import PredictionService


@dataclass(frozen=True)
class QueuePredictionRequest:
    student_profile_id: UUID
    feature_snapshot_id: UUID | None = None


class PredictionJobService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        queue_client: PredictionQueueClient | None = None,
    ) -> None:
        self._session = session
        self._jobs = PredictionJobRepository(session)
        self._queue = queue_client or PredictionQueueClient()

    async def enqueue_prediction(
        self,
        *,
        student_profile_id: UUID,
        feature_snapshot_id: UUID | None = None,
    ) -> PredictionJob:
        job = await self._jobs.create_job(
            student_profile_id=student_profile_id,
            feature_snapshot_id=feature_snapshot_id,
            metadata={"queue": "prediction-processing", "mode": "single"},
        )
        enqueued = await self._queue.enqueue_prediction(
            job_id=job.id,
            student_profile_id=student_profile_id,
            feature_snapshot_id=feature_snapshot_id,
            batch_id=None,
        )
        if enqueued.bullmq_job_id is not None:
            await self._jobs.set_bullmq_job_id(job.id, enqueued.bullmq_job_id)
        return job

    async def enqueue_batch(
        self,
        requests: list[QueuePredictionRequest],
    ) -> dict[str, Any]:
        batch_id = uuid.uuid4()
        jobs: list[PredictionJob] = []
        for request in requests:
            job = await self._jobs.create_job(
                student_profile_id=request.student_profile_id,
                feature_snapshot_id=request.feature_snapshot_id,
                batch_id=batch_id,
                metadata={"queue": "prediction-processing", "mode": "batch"},
            )
            enqueued = await self._queue.enqueue_prediction(
                job_id=job.id,
                student_profile_id=request.student_profile_id,
                feature_snapshot_id=request.feature_snapshot_id,
                batch_id=batch_id,
            )
            if enqueued.bullmq_job_id is not None:
                await self._jobs.set_bullmq_job_id(job.id, enqueued.bullmq_job_id)
            jobs.append(job)

        return {
            "batch_id": str(batch_id),
            "jobs": [_serialize_job(job) for job in jobs],
        }

    async def execute_job(self, job_id: UUID, *, attempt: int) -> dict[str, Any]:
        job = await self._jobs.get_by_id(job_id)
        if job is None:
            raise LookupError("Prediction job not found.")

        await self._jobs.mark_processing(job_id, attempts=attempt)
        prediction_service = PredictionService(self._session)

        try:
            if job.feature_snapshot_id is not None:
                result = await prediction_service.predict_for_feature_snapshot(
                    student_profile_id=job.student_profile_id,
                    feature_snapshot_id=job.feature_snapshot_id,
                    job_id=job.id,
                    inference_source="async",
                )
            else:
                result = await prediction_service.predict_for_snapshot(
                    job.student_profile_id,
                    job_id=job.id,
                    inference_source="async",
                )
        except (
            ProfileNotFoundError,
            SnapshotNotFoundError,
            SnapshotProfileMismatchError,
            InvalidFeatureSetError,
            PredictionFailedError,
        ) as exc:
            await self._jobs.mark_failed(job_id, attempts=attempt, error=str(exc))
            raise
        except Exception as exc:
            await self._jobs.mark_failed(job_id, attempts=attempt, error=str(exc))
            raise

        payload = {
            "prediction_id": str(result.prediction_id),
            "student_profile_id": str(result.student_profile_id),
            "feature_snapshot_id": str(result.feature_snapshot_id),
            "model_version_id": str(result.model_version_id) if result.model_version_id else None,
            "risk_level": result.risk_level,
            "prediction_duration_ms": result.prediction_duration_ms,
            **result.risks,
        }
        await self._jobs.mark_completed(
            job_id,
            prediction_record_id=result.prediction_id,
            result=payload,
            attempts=attempt,
        )
        return payload

    async def mark_retrying(self, job_id: UUID, *, attempt: int, error: str) -> PredictionJob:
        job = await self._jobs.mark_retrying(job_id, attempts=attempt, error=error)
        if job is None:
            raise LookupError("Prediction job not found.")
        return job

    async def mark_failed(self, job_id: UUID, *, attempt: int, error: str) -> PredictionJob:
        job = await self._jobs.mark_failed(job_id, attempts=attempt, error=error)
        if job is None:
            raise LookupError("Prediction job not found.")
        return job

    async def get_job(self, job_id: UUID) -> PredictionJob | None:
        return await self._jobs.get_by_id(job_id)

    async def get_result(self, job_id: UUID) -> dict[str, Any] | None:
        job = await self._jobs.get_by_id(job_id)
        if job is None or job.status != "completed":
            return None
        return job.result

    async def get_queue_analytics(self) -> dict[str, Any]:
        status_counts = await self._jobs.count_by_status()
        recent_jobs = await self._jobs.recent_jobs()
        total_jobs = sum(status_counts.values())
        completed = status_counts.get("completed", 0)
        failed = status_counts.get("failed", 0)
        success_rate = round((completed / total_jobs) * 100, 2) if total_jobs else 0.0
        failure_rate = round((failed / total_jobs) * 100, 2) if total_jobs else 0.0

        prediction_metrics = await PredictionAnalyticsService(
            self._session
        ).get_operational_metrics()
        return {
            "total_jobs": total_jobs,
            "pending": status_counts.get("pending", 0),
            "processing": status_counts.get("processing", 0),
            "completed": completed,
            "failed": failed,
            "retrying": status_counts.get("retrying", 0),
            "success_rate": success_rate,
            "failure_rate": failure_rate,
            "prediction_metrics": prediction_metrics,
            "recent_jobs": [_serialize_job(job) for job in recent_jobs],
        }


def _serialize_job(job: PredictionJob) -> dict[str, Any]:
    return {
        "job_id": str(job.id),
        "bullmq_job_id": job.bullmq_job_id,
        "batch_id": str(job.batch_id) if job.batch_id else None,
        "student_profile_id": str(job.student_profile_id),
        "feature_snapshot_id": str(job.feature_snapshot_id) if job.feature_snapshot_id else None,
        "prediction_record_id": (
            str(job.prediction_record_id) if job.prediction_record_id else None
        ),
        "status": job.status,
        "attempts": job.attempts,
        "max_attempts": job.max_attempts,
        "last_error": job.last_error,
        "result": job.result,
        "metadata": job.metadata_json,
        "queued_at": _dt(job.queued_at),
        "started_at": _dt(job.started_at),
        "completed_at": _dt(job.completed_at),
        "failed_at": _dt(job.failed_at),
        "created_at": _dt(job.created_at),
        "updated_at": _dt(job.updated_at),
    }


def _dt(value: Any) -> str | None:
    return value.isoformat() if value is not None else None
