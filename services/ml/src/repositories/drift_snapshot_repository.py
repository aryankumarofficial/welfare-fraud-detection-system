import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, select

from src.db.models.drift_snapshot import DriftSnapshot
from src.db.repositories.base import AsyncRepository


class DriftSnapshotRepository(AsyncRepository[DriftSnapshot]):
    model = DriftSnapshot

    async def create_snapshot(
        self,
        *,
        window: str,
        feature_distribution_changes: dict[str, Any],
        risk_distribution_changes: dict[str, Any],
        prediction_volume_changes: dict[str, Any],
        drift_score: float,
    ) -> DriftSnapshot:
        snapshot = DriftSnapshot(
            id=uuid.uuid4(),
            window=window,
            feature_distribution_changes=feature_distribution_changes,
            risk_distribution_changes=risk_distribution_changes,
            prediction_volume_changes=prediction_volume_changes,
            drift_score=drift_score,
            created_at=datetime.now(UTC),
        )
        return await self.add(snapshot)

    async def recent_snapshots(self, *, limit: int = 20) -> list[DriftSnapshot]:
        statement = select(DriftSnapshot).order_by(desc(DriftSnapshot.created_at)).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())
