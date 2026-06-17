from uuid import UUID
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select

from src.db.models.feature_snapshot import FeatureSnapshot
from src.db.repositories.base import AsyncRepository


class FeatureSnapshotRepository(AsyncRepository[FeatureSnapshot]):
    model = FeatureSnapshot

    async def get_latest_by_profile_id(
        self,
        student_profile_id: UUID,
    ) -> FeatureSnapshot | None:
        statement = (
            select(FeatureSnapshot)
            .where(FeatureSnapshot.student_profile_id == student_profile_id)
            .order_by(FeatureSnapshot.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_by_profile_id(
        self,
        student_profile_id: UUID,
        *,
        limit: int = 100,
    ) -> list[FeatureSnapshot]:
        statement = (
            select(FeatureSnapshot)
            .where(FeatureSnapshot.student_profile_id == student_profile_id)
            .order_by(FeatureSnapshot.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_snapshot(
        self,
        *,
        student_profile_id: UUID,
        features: dict[str, Any],
        feature_schema_version: str,
        checksum: str,
        source: str = "profile_snapshot",
    ) -> FeatureSnapshot:
        snapshot = FeatureSnapshot(
            id=uuid.uuid4(),
            student_profile_id=student_profile_id,
            source=source,
            features=features,
            feature_schema_version=feature_schema_version,
            checksum=checksum,
            created_at=datetime.now(UTC),
        )
        return await self.add(snapshot)
