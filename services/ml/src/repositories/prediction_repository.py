import uuid
from datetime import UTC, datetime

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
        inference_source: str = "sync",
        requested_by_user_id: uuid.UUID | None = None,
    ) -> PredictionRecord:
        record = PredictionRecord(
            id=uuid.uuid4(),
            student_profile_id=student_profile_id,
            feature_snapshot_id=feature_snapshot_id,
            model_version_id=model_version_id,
            income_risk=income_risk,
            caste_risk=caste_risk,
            transaction_risk=transaction_risk,
            medical_risk=medical_risk,
            final_risk=final_risk,
            inference_source=inference_source,
            requested_by_user_id=requested_by_user_id,
            created_at=datetime.now(UTC),
        )
        return await self.add(record)
