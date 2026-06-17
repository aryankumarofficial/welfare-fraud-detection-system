import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, func, select

from src.db.models.prediction_job import PredictionJob
from src.db.repositories.base import AsyncRepository


class PredictionJobRepository(AsyncRepository[PredictionJob]):
    model = PredictionJob

    async def create_job(
        self,
        *,
        student_profile_id: uuid.UUID,
        feature_snapshot_id: uuid.UUID | None = None,
        batch_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
        max_attempts: int = 3,
    ) -> PredictionJob:
        now = datetime.now(UTC)
        job = PredictionJob(
            id=uuid.uuid4(),
            student_profile_id=student_profile_id,
            feature_snapshot_id=feature_snapshot_id,
            batch_id=batch_id,
            status="pending",
            attempts=0,
            max_attempts=max_attempts,
            metadata_json=metadata,
            queued_at=now,
            created_at=now,
            updated_at=now,
        )
        return await self.add(job)

    async def set_bullmq_job_id(
        self,
        job_id: uuid.UUID,
        bullmq_job_id: str,
    ) -> PredictionJob | None:
        job = await self.get_by_id(job_id)
        if job is None:
            return None
        job.bullmq_job_id = bullmq_job_id
        job.updated_at = datetime.now(UTC)
        await self.session.flush()
        return job

    async def mark_processing(
        self,
        job_id: uuid.UUID,
        *,
        attempts: int,
    ) -> PredictionJob | None:
        job = await self.get_by_id(job_id)
        if job is None:
            return None
        now = datetime.now(UTC)
        job.status = "processing"
        job.attempts = attempts
        job.started_at = job.started_at or now
        job.updated_at = now
        await self.session.flush()
        return job

    async def mark_retrying(
        self,
        job_id: uuid.UUID,
        *,
        attempts: int,
        error: str,
    ) -> PredictionJob | None:
        job = await self.get_by_id(job_id)
        if job is None:
            return None
        job.status = "retrying"
        job.attempts = attempts
        job.last_error = error
        job.failed_at = None
        job.updated_at = datetime.now(UTC)
        await self.session.flush()
        return job

    async def mark_completed(
        self,
        job_id: uuid.UUID,
        *,
        prediction_record_id: uuid.UUID,
        result: dict[str, Any],
        attempts: int,
    ) -> PredictionJob | None:
        job = await self.get_by_id(job_id)
        if job is None:
            return None
        now = datetime.now(UTC)
        job.status = "completed"
        job.prediction_record_id = prediction_record_id
        job.result = result
        job.attempts = attempts
        job.completed_at = now
        job.failed_at = None
        job.last_error = None
        job.updated_at = now
        await self.session.flush()
        return job

    async def mark_failed(
        self,
        job_id: uuid.UUID,
        *,
        attempts: int,
        error: str,
    ) -> PredictionJob | None:
        job = await self.get_by_id(job_id)
        if job is None:
            return None
        now = datetime.now(UTC)
        job.status = "failed"
        job.attempts = attempts
        job.last_error = error
        job.failed_at = now
        job.updated_at = now
        await self.session.flush()
        return job

    async def list_by_batch_id(self, batch_id: uuid.UUID) -> list[PredictionJob]:
        statement = (
            select(PredictionJob)
            .where(PredictionJob.batch_id == batch_id)
            .order_by(PredictionJob.created_at)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count_by_status(self) -> dict[str, int]:
        statement = select(PredictionJob.status, func.count(PredictionJob.id)).group_by(
            PredictionJob.status
        )
        result = await self.session.execute(statement)
        return {status: int(count) for status, count in result.all()}

    async def recent_jobs(self, *, limit: int = 20) -> list[PredictionJob]:
        statement = select(PredictionJob).order_by(desc(PredictionJob.created_at)).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())
