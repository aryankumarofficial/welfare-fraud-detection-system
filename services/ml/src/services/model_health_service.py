from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.drift_snapshot import DriftSnapshot
from src.db.models.model_version import ModelVersion
from src.db.models.monitoring_alert import MonitoringAlert
from src.db.models.prediction_record import PredictionRecord
from src.db.models.prediction_review import PredictionReview
from src.repositories.model_evaluation_run_repository import ModelEvaluationRunRepository
from src.repositories.model_repository import ModelRepository


class ModelHealthService:
    """
    Aggregates model health analytics from predictions, drift, reviews,
    evaluations, and alerts for the current champion model.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._models = ModelRepository(session)
        self._evaluations = ModelEvaluationRunRepository(session)

    async def get_model_health(self) -> dict[str, Any]:
        champion = await self._models.get_champion()

        champion_info = None
        latest_evaluation = None
        champion_prediction_stats = None
        champion_uptime_hours = None

        if champion is not None:
            champion_info = {
                "model_version_id": str(champion.id),
                "name": champion.name,
                "version": champion.version,
                "status": champion.status,
                "role": champion.role,
                "deployed_at": champion.deployed_at.isoformat() if champion.deployed_at else None,
                "promoted_at": champion.promoted_at.isoformat() if champion.promoted_at else None,
            }

            # Latest evaluation
            eval_run = await self._evaluations.get_latest_by_model_version_id(champion.id)
            if eval_run is not None:
                latest_evaluation = {
                    "precision": eval_run.precision,
                    "recall": eval_run.recall,
                    "f1_score": eval_run.f1_score,
                    "false_positive_rate": eval_run.false_positive_rate,
                    "dataset_name": eval_run.dataset_name,
                    "sample_size": eval_run.sample_size,
                    "evaluated_at": eval_run.evaluated_at.isoformat(),
                }

            # Prediction stats for champion
            champion_prediction_stats = await self._champion_prediction_stats(champion.id)

            # Uptime
            if champion.deployed_at:
                delta = datetime.now(UTC) - champion.deployed_at
                champion_uptime_hours = round(delta.total_seconds() / 3600, 2)

        # Global stats
        drift_summary = await self._latest_drift_score()
        false_positive_rate = await self._false_positive_rate()
        alert_summary = await self._alert_summary()
        total_models = await self._total_model_count()

        return {
            "champion": champion_info,
            "latest_evaluation": latest_evaluation,
            "champion_predictions": champion_prediction_stats,
            "champion_uptime_hours": champion_uptime_hours,
            "latest_drift_score": drift_summary,
            "false_positive_rate": false_positive_rate,
            "alert_summary": alert_summary,
            "total_registered_models": total_models,
        }

    async def _champion_prediction_stats(
        self,
        model_version_id: Any,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        last_24h = now - timedelta(hours=24)

        statement = select(
            func.count(PredictionRecord.id),
            func.avg(PredictionRecord.prediction_duration_ms),
            func.avg(PredictionRecord.final_risk),
        ).where(
            PredictionRecord.model_version_id == model_version_id,
            func.coalesce(
                PredictionRecord.prediction_timestamp,
                PredictionRecord.created_at,
            ) >= last_24h,
        )
        result = await self._session.execute(statement)
        count, avg_latency, avg_risk = result.one()

        total_statement = select(func.count(PredictionRecord.id)).where(
            PredictionRecord.model_version_id == model_version_id,
        )
        total_result = await self._session.execute(total_statement)
        total_count = total_result.scalar_one()

        return {
            "total_predictions": int(total_count or 0),
            "predictions_last_24h": int(count or 0),
            "average_latency_ms": round(float(avg_latency or 0), 2),
            "average_risk_last_24h": round(float(avg_risk or 0), 6),
        }

    async def _latest_drift_score(self) -> float | None:
        statement = (
            select(DriftSnapshot.drift_score)
            .order_by(DriftSnapshot.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(statement)
        score = result.scalar_one_or_none()
        return float(score) if score is not None else None

    async def _false_positive_rate(self) -> float | None:
        statement = select(
            PredictionReview.decision,
            func.count(PredictionReview.id),
        ).group_by(PredictionReview.decision)
        result = await self._session.execute(statement)
        counts = {decision: int(c) for decision, c in result.all()}

        total_decisive = counts.get("confirmed_fraud", 0) + counts.get("false_positive", 0)
        if total_decisive == 0:
            return None
        return round(counts.get("false_positive", 0) / total_decisive, 4)

    async def _alert_summary(self) -> dict[str, int]:
        now = datetime.now(UTC)
        last_7d = now - timedelta(days=7)
        statement = (
            select(
                MonitoringAlert.alert_type,
                func.count(MonitoringAlert.id),
            )
            .where(MonitoringAlert.created_at >= last_7d)
            .group_by(MonitoringAlert.alert_type)
        )
        result = await self._session.execute(statement)
        return {alert_type: int(c) for alert_type, c in result.all()}

    async def _total_model_count(self) -> int:
        statement = select(func.count(ModelVersion.id))
        result = await self._session.execute(statement)
        return int(result.scalar_one() or 0)
