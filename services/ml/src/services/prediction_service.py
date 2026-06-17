from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import PredictionFailedError
from src.predict import predict_all
from src.repositories.model_repository import ModelRepository
from src.repositories.prediction_repository import PredictionRepository
from src.services.feature_loader import FeatureLoader, LoadedFeatures


@dataclass(frozen=True)
class PredictionResult:
    student_profile_id: UUID
    feature_snapshot_id: UUID
    prediction_id: UUID
    model_version_id: UUID | None
    risks: dict[str, float]


class PredictionService:
    """
    Orchestrates DB-backed inference: load snapshot → validate → predict → persist.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._feature_loader = FeatureLoader(session)
        self._predictions = PredictionRepository(session)
        self._models = ModelRepository(session)

    async def predict_for_snapshot(self, student_profile_id: UUID) -> PredictionResult:
        loaded = await self._feature_loader.load_latest_features(student_profile_id)
        return await self._predict_loaded_features(loaded)

    async def predict_for_feature_snapshot(
        self,
        *,
        student_profile_id: UUID,
        feature_snapshot_id: UUID,
    ) -> PredictionResult:
        loaded = await self._feature_loader.load_features_by_snapshot_id(
            student_profile_id=student_profile_id,
            feature_snapshot_id=feature_snapshot_id,
        )
        return await self._predict_loaded_features(loaded)

    async def _predict_loaded_features(self, loaded: LoadedFeatures) -> PredictionResult:
        risks = await self._run_inference(loaded.features)
        model_version = await self._models.get_active()
        model_version_id = model_version.id if model_version is not None else None

        record = await self._predictions.create_prediction(
            student_profile_id=loaded.profile.id,
            feature_snapshot_id=loaded.snapshot.id,
            model_version_id=model_version_id,
            income_risk=risks["income_risk"],
            caste_risk=risks["caste_risk"],
            transaction_risk=risks["transaction_risk"],
            medical_risk=risks["medical_risk"],
            final_risk=risks["final_risk"],
            inference_source="sync",
        )

        return PredictionResult(
            student_profile_id=loaded.profile.id,
            feature_snapshot_id=loaded.snapshot.id,
            prediction_id=record.id,
            model_version_id=model_version_id,
            risks=risks,
        )

    async def _run_inference(self, features: dict[str, Any]) -> dict[str, float]:
        try:
            return predict_all(features)
        except Exception as exc:
            raise PredictionFailedError(
                "Model inference failed.",
                cause=exc,
            ) from exc
