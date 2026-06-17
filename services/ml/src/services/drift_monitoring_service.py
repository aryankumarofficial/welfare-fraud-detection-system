from datetime import UTC, datetime, timedelta
from statistics import mean
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.drift_snapshot import DriftSnapshot
from src.db.models.feature_snapshot import FeatureSnapshot
from src.db.models.prediction_record import PredictionRecord
from src.repositories.drift_snapshot_repository import DriftSnapshotRepository


class DriftMonitoringService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._snapshots = DriftSnapshotRepository(session)

    async def get_drift_report(self, *, days: int = 7) -> dict[str, Any]:
        current_start = datetime.now(UTC) - timedelta(days=days)
        baseline_start = current_start - timedelta(days=days)

        current_features = await self._feature_rows(start=current_start)
        baseline_features = await self._feature_rows(start=baseline_start, end=current_start)
        current_predictions = await self._prediction_rows(start=current_start)
        baseline_predictions = await self._prediction_rows(
            start=baseline_start,
            end=current_start,
        )

        feature_changes = self._feature_distribution_changes(
            baseline=baseline_features,
            current=current_features,
        )
        risk_changes = self._risk_distribution_changes(
            baseline=baseline_predictions,
            current=current_predictions,
        )
        volume_changes = {
            "baseline_count": len(baseline_predictions),
            "current_count": len(current_predictions),
            "change_percentage": _percentage_change(
                len(baseline_predictions),
                len(current_predictions),
            ),
        }
        drift_score = self._drift_score(
            feature_changes=feature_changes,
            risk_changes=risk_changes,
            volume_changes=volume_changes,
        )
        snapshot = await self._snapshots.create_snapshot(
            window=f"{days}d",
            feature_distribution_changes=feature_changes,
            risk_distribution_changes=risk_changes,
            prediction_volume_changes=volume_changes,
            drift_score=drift_score,
        )
        return {
            "latest_snapshot": _serialize_drift_snapshot(snapshot),
            "recent_snapshots": [
                _serialize_drift_snapshot(item)
                for item in await self._snapshots.recent_snapshots()
            ],
        }

    async def _feature_rows(
        self,
        *,
        start: datetime,
        end: datetime | None = None,
    ) -> list[dict[str, Any]]:
        statement = select(FeatureSnapshot.features).where(FeatureSnapshot.created_at >= start)
        if end is not None:
            statement = statement.where(FeatureSnapshot.created_at < end)
        result = await self._session.execute(statement)
        return [row for row in result.scalars().all()]

    async def _prediction_rows(
        self,
        *,
        start: datetime,
        end: datetime | None = None,
    ) -> list[tuple[float, str | None]]:
        prediction_time = func.coalesce(
            PredictionRecord.prediction_timestamp,
            PredictionRecord.created_at,
        )
        statement = select(PredictionRecord.final_risk, PredictionRecord.risk_level).where(
            prediction_time >= start
        )
        if end is not None:
            statement = statement.where(prediction_time < end)
        result = await self._session.execute(statement)
        return [(float(risk), level) for risk, level in result.all()]

    def _feature_distribution_changes(
        self,
        *,
        baseline: list[dict[str, Any]],
        current: list[dict[str, Any]],
    ) -> dict[str, Any]:
        keys = sorted({key for row in baseline + current for key in row.keys()})
        changes: dict[str, Any] = {}
        for key in keys:
            baseline_values = _numeric_values(row.get(key) for row in baseline)
            current_values = _numeric_values(row.get(key) for row in current)
            if not baseline_values and not current_values:
                continue
            baseline_mean = mean(baseline_values) if baseline_values else 0.0
            current_mean = mean(current_values) if current_values else 0.0
            changes[key] = {
                "baseline_mean": round(baseline_mean, 6),
                "current_mean": round(current_mean, 6),
                "change_percentage": _percentage_change(baseline_mean, current_mean),
            }
        return changes

    def _risk_distribution_changes(
        self,
        *,
        baseline: list[tuple[float, str | None]],
        current: list[tuple[float, str | None]],
    ) -> dict[str, Any]:
        baseline_risks = [risk for risk, _ in baseline]
        current_risks = [risk for risk, _ in current]
        return {
            "baseline_average_risk": round(mean(baseline_risks), 6)
            if baseline_risks
            else 0.0,
            "current_average_risk": round(mean(current_risks), 6)
            if current_risks
            else 0.0,
            "average_risk_change_percentage": _percentage_change(
                mean(baseline_risks) if baseline_risks else 0.0,
                mean(current_risks) if current_risks else 0.0,
            ),
            "baseline_risk_levels": _risk_level_counts(baseline),
            "current_risk_levels": _risk_level_counts(current),
        }

    def _drift_score(
        self,
        *,
        feature_changes: dict[str, Any],
        risk_changes: dict[str, Any],
        volume_changes: dict[str, Any],
    ) -> float:
        feature_component = max(
            [abs(item["change_percentage"]) for item in feature_changes.values()] or [0.0]
        )
        risk_component = abs(risk_changes["average_risk_change_percentage"])
        volume_component = abs(volume_changes["change_percentage"])
        return round(max(feature_component, risk_component, volume_component), 4)


def _numeric_values(values: Any) -> list[float]:
    numeric: list[float] = []
    for value in values:
        if isinstance(value, bool):
            numeric.append(float(int(value)))
        elif isinstance(value, (int, float)):
            numeric.append(float(value))
    return numeric


def _risk_level_counts(rows: list[tuple[float, str | None]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for _, level in rows:
        if level is None:
            continue
        counts[level] = counts.get(level, 0) + 1
    return counts


def _percentage_change(baseline: float, current: float) -> float:
    if baseline == 0:
        return 100.0 if current else 0.0
    return round(((current - baseline) / abs(baseline)) * 100, 4)


def _serialize_drift_snapshot(snapshot: DriftSnapshot) -> dict[str, Any]:
    return {
        "drift_snapshot_id": str(snapshot.id),
        "window": snapshot.window,
        "feature_distribution_changes": snapshot.feature_distribution_changes,
        "risk_distribution_changes": snapshot.risk_distribution_changes,
        "prediction_volume_changes": snapshot.prediction_volume_changes,
        "drift_score": snapshot.drift_score,
        "created_at": snapshot.created_at.isoformat(),
    }
