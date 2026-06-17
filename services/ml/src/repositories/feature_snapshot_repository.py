from uuid import UUID

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
