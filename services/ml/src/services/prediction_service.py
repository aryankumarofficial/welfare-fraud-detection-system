from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import PredictionFailedError
from src.predict import predict_all
from src.repositories.model_repository import ModelRepository
from src.repositories.prediction_repository import PredictionRepository
from src.services.audit_service import PredictionAuditService
from src.services.feature_loader import FeatureLoader, LoadedFeatures
from src.services.risk_classifier import RiskClassifier


@dataclass(frozen=True)
class PredictionResult:
    student_profile_id: UUID
    feature_snapshot_id: UUID
    prediction_id: UUID
    model_version_id: UUID | None
    risks: dict[str, float]
    risk_level: str
    prediction_duration_ms: int


class PredictionService:
    """
    Orchestrates DB-backed inference: load snapshot → validate → predict → persist.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._feature_loader = FeatureLoader(session)
        self._predictions = PredictionRepository(session)
        self._models = ModelRepository(session)
        self._audit = PredictionAuditService(session)
        self._classifier = RiskClassifier()

    async def predict_for_snapshot(
        self,
        student_profile_id: UUID,
        *,
        job_id: UUID | None = None,
        inference_source: str = "sync",
    ) -> PredictionResult:
        loaded = await self._feature_loader.load_latest_features(student_profile_id)
        return await self._predict_loaded_features(
            loaded,
            job_id=job_id,
            inference_source=inference_source,
        )

    async def predict_for_feature_snapshot(
        self,
        *,
        student_profile_id: UUID,
        feature_snapshot_id: UUID,
        job_id: UUID | None = None,
        inference_source: str = "sync",
    ) -> PredictionResult:
        loaded = await self._feature_loader.load_features_by_snapshot_id(
            student_profile_id=student_profile_id,
            feature_snapshot_id=feature_snapshot_id,
        )
        return await self._predict_loaded_features(
            loaded,
            job_id=job_id,
            inference_source=inference_source,
        )

    async def _predict_loaded_features(
        self,
        loaded: LoadedFeatures,
        *,
        job_id: UUID | None,
        inference_source: str,
    ) -> PredictionResult:
        prediction_timestamp = datetime.now(UTC)
        started_at = perf_counter()
        try:
            risks = await self._run_inference(loaded.features)
        except PredictionFailedError as exc:
            await self._audit.prediction_failed(
                student_profile_id=loaded.profile.id,
                feature_snapshot_id=loaded.snapshot.id,
                error=str(exc),
            )
            raise
        prediction_duration_ms = int((perf_counter() - started_at) * 1000)

        model_version = await self._models.get_active()
        model_version_id = model_version.id if model_version is not None else None
        classification = self._classifier.classify(risks["final_risk"])

        record = await self._predictions.create_prediction(
            student_profile_id=loaded.profile.id,
            feature_snapshot_id=loaded.snapshot.id,
            model_version_id=model_version_id,
            job_id=job_id,
            prediction_timestamp=prediction_timestamp,
            model_name=model_version.name if model_version is not None else None,
            model_version=model_version.version if model_version is not None else None,
            snapshot_checksum=loaded.snapshot.checksum,
            prediction_duration_ms=prediction_duration_ms,
            income_risk=risks["income_risk"],
            caste_risk=risks["caste_risk"],
            transaction_risk=risks["transaction_risk"],
            medical_risk=risks["medical_risk"],
            final_risk=risks["final_risk"],
            risk_level=classification.level,
            inference_source=inference_source,
        )
        await self._audit.prediction_executed(
            prediction_id=record.id,
            student_profile_id=loaded.profile.id,
            feature_snapshot_id=loaded.snapshot.id,
            metadata={
                "model_version_id": str(model_version_id) if model_version_id else None,
                "model_name": record.model_name,
                "model_version": record.model_version,
                "snapshot_checksum": record.snapshot_checksum,
                "prediction_duration_ms": prediction_duration_ms,
                "risk_level": classification.level,
                "final_risk": risks["final_risk"],
            },
        )

        return PredictionResult(
            student_profile_id=loaded.profile.id,
            feature_snapshot_id=loaded.snapshot.id,
            prediction_id=record.id,
            model_version_id=model_version_id,
            risks=risks,
            risk_level=classification.level,
            prediction_duration_ms=prediction_duration_ms,
        )

    async def _run_inference(self, features: dict[str, Any]) -> dict[str, float]:
        try:
            return predict_all(features)
        except Exception as exc:
            raise PredictionFailedError(
                "Model inference failed.",
                cause=exc,
            ) from exc
