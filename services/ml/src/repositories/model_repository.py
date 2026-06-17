from sqlalchemy import select

from src.db.models.model_version import ModelVersion
from src.db.repositories.base import AsyncRepository


class ModelRepository(AsyncRepository[ModelVersion]):
    model = ModelVersion

    async def get_active(self) -> ModelVersion | None:
        statement = (
            select(ModelVersion)
            .where(ModelVersion.is_active.is_(True))
            .order_by(
                ModelVersion.deployed_at.desc().nulls_last(),
                ModelVersion.created_at.desc(),
            )
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
