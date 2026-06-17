from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.monitoring_alert import MonitoringAlert
from src.repositories.drift_snapshot_repository import DriftSnapshotRepository
from src.repositories.monitoring_alert_repository import MonitoringAlertRepository
from src.services.model_evaluation_service import ModelEvaluationService
from src.services.prediction_job_service import PredictionJobService
from src.services.prediction_analytics import PredictionAnalyticsService


class AlertService:
    def __init__(self, session: AsyncSession) -> None:
        self._alerts = MonitoringAlertRepository(session)
        self._drift_snapshots = DriftSnapshotRepository(session)
        self._analytics = PredictionAnalyticsService(session)
        self._evaluation = ModelEvaluationService(session)
        self._queue = PredictionJobService(session)

    async def get_alerts(self) -> dict[str, Any]:
        generated = await self.generate_alerts()
        recent = await self._alerts.recent_alerts()
        return {
            "generated": [_serialize_alert(alert) for alert in generated],
            "recent_alerts": [_serialize_alert(alert) for alert in recent],
        }

    async def generate_alerts(self) -> list[MonitoringAlert]:
        alerts: list[MonitoringAlert] = []
        recent_drift = await self._drift_snapshots.recent_snapshots(limit=1)
        if recent_drift and recent_drift[0].drift_score >= 50:
            alerts.append(
                await self._alerts.create_alert(
                    alert_type="MODEL_DRIFT",
                    severity="critical" if recent_drift[0].drift_score >= 100 else "warning",
                    message="Model input or output drift exceeded monitoring threshold.",
                    metadata={
                        "drift_snapshot_id": str(recent_drift[0].id),
                        "drift_score": recent_drift[0].drift_score,
                    },
                )
            )

        operational = await self._analytics.get_operational_metrics()
        total_predictions = operational.get("total_predictions", 0) or 0
        failed_predictions = operational.get("failed_predictions", 0) or 0
        failure_rate = (
            failed_predictions / total_predictions if total_predictions else 0.0
        )
        if failure_rate >= 0.1 and total_predictions >= 10:
            alerts.append(
                await self._alerts.create_alert(
                    alert_type="HIGH_FAILURE_RATE",
                    severity="critical" if failure_rate >= 0.25 else "warning",
                    message="Prediction failure rate exceeded monitoring threshold.",
                    metadata={"failure_rate": round(failure_rate, 4), **operational},
                )
            )

        queue_analytics = await self._queue.get_queue_analytics()
        backlog = (
            queue_analytics.get("pending", 0)
            + queue_analytics.get("processing", 0)
            + queue_analytics.get("retrying", 0)
        )
        if backlog >= 50:
            alerts.append(
                await self._alerts.create_alert(
                    alert_type="QUEUE_BACKLOG",
                    severity="warning",
                    message="Prediction queue backlog exceeded monitoring threshold.",
                    metadata={"backlog": backlog, **queue_analytics},
                )
            )

        performance = await self._evaluation.get_model_performance()
        reviewed = performance.get("reviewed_predictions", 0) or 0
        false_positives = performance.get("false_positives", 0) or 0
        false_positive_rate = false_positives / reviewed if reviewed else 0.0
        if false_positive_rate >= 0.3 and reviewed >= 10:
            alerts.append(
                await self._alerts.create_alert(
                    alert_type="HIGH_FALSE_POSITIVE_RATE",
                    severity="warning",
                    message="False positive review rate exceeded monitoring threshold.",
                    metadata={
                        "false_positive_rate": round(false_positive_rate, 4),
                        **performance,
                    },
                )
            )

        return alerts


def _serialize_alert(alert: MonitoringAlert) -> dict[str, Any]:
    return {
        "alert_id": str(alert.id),
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "message": alert.message,
        "metadata": alert.metadata_json,
        "created_at": alert.created_at.isoformat(),
    }
