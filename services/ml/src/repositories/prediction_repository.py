import uuid
from datetime import UTC, datetime

from sqlalchemy import desc, func, select

from src.db.models.prediction_record import PredictionRecord
from src.db.repositories.base import AsyncRepository


class PredictionRepository(AsyncRepository[PredictionRecord]):
    model = PredictionRecord

    async def create_prediction(
        self,
        *,
        student_profile_id: uuid.UUID,
        feature_snapshot_id: uuid.UUID,
        model_version_id: uuid.UUID | None,
        income_risk: float,
        caste_risk: float,
        transaction_risk: float,
        medical_risk: float,
        final_risk: float,
        risk_level: str,
        prediction_timestamp: datetime,
        job_id: uuid.UUID | None = None,
        model_name: str | None = None,
        model_version: str | None = None,
        snapshot_checksum: str | None = None,
        prediction_duration_ms: int | None = None,
        inference_source: str = "sync",
        requested_by_user_id: uuid.UUID | None = None,
    ) -> PredictionRecord:
        record = PredictionRecord(
            id=uuid.uuid4(),
            student_profile_id=student_profile_id,
            feature_snapshot_id=feature_snapshot_id,
            model_version_id=model_version_id,
            job_id=job_id,
            prediction_timestamp=prediction_timestamp,
            model_name=model_name,
            model_version=model_version,
            snapshot_checksum=snapshot_checksum,
            prediction_duration_ms=prediction_duration_ms,
            income_risk=income_risk,
            caste_risk=caste_risk,
            transaction_risk=transaction_risk,
            medical_risk=medical_risk,
            final_risk=final_risk,
            risk_level=risk_level,
            inference_source=inference_source,
            requested_by_user_id=requested_by_user_id,
            created_at=datetime.now(UTC),
        )
        return await self.add(record)

    async def list_by_student_profile_id(
        self,
        student_profile_id: uuid.UUID,
        *,
        limit: int = 100,
    ) -> list[PredictionRecord]:
        statement = (
            select(PredictionRecord)
            .where(PredictionRecord.student_profile_id == student_profile_id)
            .order_by(
                desc(func.coalesce(PredictionRecord.prediction_timestamp, PredictionRecord.created_at))
            )
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_latest_by_student_profile_id(
        self,
        student_profile_id: uuid.UUID,
    ) -> PredictionRecord | None:
        records = await self.list_by_student_profile_id(student_profile_id, limit=1)
        return records[0] if records else None
