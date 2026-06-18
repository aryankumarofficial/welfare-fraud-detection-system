import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update

from src.db.models.model_version import ModelVersion
from src.db.repositories.base import AsyncRepository


MODEL_STATUSES = ("DRAFT", "VALIDATED", "STAGING", "PRODUCTION", "ARCHIVED", "ROLLED_BACK")
MODEL_ROLES = ("champion", "challenger", "none")


class ModelRepository(AsyncRepository[ModelVersion]):
    model = ModelVersion

    async def get_active(self) -> ModelVersion | None:
        """Backward-compatible: returns the active model (is_active=True)."""
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

    async def get_champion(self) -> ModelVersion | None:
        """Get the current champion model (role='champion', status='PRODUCTION')."""
        statement = (
            select(ModelVersion)
            .where(
                ModelVersion.role == "champion",
                ModelVersion.status == "PRODUCTION",
            )
            .limit(1)
        )
        result = await self.session.execute(statement)
        champion = result.scalar_one_or_none()
        if champion is not None:
            return champion
        # Fallback to legacy is_active for backward compatibility
        return await self.get_active()

    async def list_by_status(self, status: str) -> list[ModelVersion]:
        statement = (
            select(ModelVersion)
            .where(ModelVersion.status == status)
            .order_by(ModelVersion.created_at.desc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_by_role(self, role: str) -> list[ModelVersion]:
        statement = (
            select(ModelVersion)
            .where(ModelVersion.role == role)
            .order_by(ModelVersion.created_at.desc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_filtered(
        self,
        *,
        status: str | None = None,
        role: str | None = None,
        limit: int = 100,
    ) -> list[ModelVersion]:
        statement = select(ModelVersion)
        if status is not None:
            statement = statement.where(ModelVersion.status == status)
        if role is not None:
            statement = statement.where(ModelVersion.role == role)
        statement = statement.order_by(ModelVersion.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_model(
        self,
        *,
        name: str,
        version: str,
        description: str | None = None,
        artifact_uri: str | None = None,
        artifact_hash: str | None = None,
        configuration: dict | None = None,
        training_metadata: dict | None = None,
        feature_schema_version: str | None = None,
        parent_model_id: uuid.UUID | None = None,
    ) -> ModelVersion:
        now = datetime.now(UTC)
        model = ModelVersion(
            id=uuid.uuid4(),
            name=name,
            version=version,
            description=description,
            artifact_uri=artifact_uri,
            artifact_hash=artifact_hash,
            configuration=configuration,
            training_metadata=training_metadata,
            feature_schema_version=feature_schema_version,
            parent_model_id=parent_model_id,
            is_active=False,
            status="DRAFT",
            role="none",
            created_at=now,
        )
        return await self.add(model)

    async def update_status(
        self,
        model_id: uuid.UUID,
        status: str,
    ) -> ModelVersion | None:
        model = await self.get_by_id(model_id)
        if model is None:
            return None
        model.status = status
        await self.session.flush()
        return model

    async def update_role(
        self,
        model_id: uuid.UUID,
        role: str,
    ) -> ModelVersion | None:
        model = await self.get_by_id(model_id)
        if model is None:
            return None
        model.role = role
        await self.session.flush()
        return model

    async def promote_to_champion(
        self,
        model_id: uuid.UUID,
        *,
        promoted_by: str | None = None,
    ) -> tuple[ModelVersion | None, ModelVersion | None]:
        """
        Promote a model to champion.
        Returns (promoted_model, demoted_model).
        Demotes existing champion to STAGING with role='none'.
        """
        model = await self.get_by_id(model_id)
        if model is None:
            return None, None

        # Demote current champion
        demoted = None
        current_champion = await self._get_current_champion()
        if current_champion is not None and current_champion.id != model_id:
            current_champion.status = "STAGING"
            current_champion.role = "none"
            current_champion.is_active = False
            demoted = current_champion

        # Promote the target model
        now = datetime.now(UTC)
        model.status = "PRODUCTION"
        model.role = "champion"
        model.is_active = True
        model.deployed_at = now
        model.promoted_at = now
        model.promoted_by = promoted_by

        await self.session.flush()
        return model, demoted

    async def rollback_champion(
        self,
        model_id: uuid.UUID,
        *,
        previous_champion_id: uuid.UUID | None = None,
    ) -> tuple[ModelVersion | None, ModelVersion | None]:
        """
        Rollback a champion model.
        Returns (rolled_back_model, restored_model).
        """
        model = await self.get_by_id(model_id)
        if model is None:
            return None, None

        # Mark current champion as rolled back
        now = datetime.now(UTC)
        model.status = "ROLLED_BACK"
        model.role = "none"
        model.is_active = False
        model.rolled_back_at = now

        # Restore previous champion if available
        restored = None
        if previous_champion_id is not None:
            previous = await self.get_by_id(previous_champion_id)
            if previous is not None:
                previous.status = "PRODUCTION"
                previous.role = "champion"
                previous.is_active = True
                previous.deployed_at = now
                restored = previous

        await self.session.flush()
        return model, restored

    async def _get_current_champion(self) -> ModelVersion | None:
        statement = (
            select(ModelVersion)
            .where(ModelVersion.role == "champion")
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
