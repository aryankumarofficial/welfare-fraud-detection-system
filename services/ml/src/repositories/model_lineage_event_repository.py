import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, select

from src.db.models.model_lineage_event import ModelLineageEvent
from src.db.repositories.base import AsyncRepository


class ModelLineageEventRepository(AsyncRepository[ModelLineageEvent]):
    model = ModelLineageEvent

    async def create_event(
        self,
        *,
        model_version_id: uuid.UUID,
        event_type: str,
        from_status: str | None = None,
        to_status: str | None = None,
        from_role: str | None = None,
        to_role: str | None = None,
        metadata: dict[str, Any] | None = None,
        performed_by: str | None = None,
    ) -> ModelLineageEvent:
        event = ModelLineageEvent(
            id=uuid.uuid4(),
            model_version_id=model_version_id,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            from_role=from_role,
            to_role=to_role,
            metadata_json=metadata,
            performed_by=performed_by,
            created_at=datetime.now(UTC),
        )
        return await self.add(event)

    async def list_by_model_version_id(
        self,
        model_version_id: uuid.UUID,
        *,
        limit: int = 100,
    ) -> list[ModelLineageEvent]:
        statement = (
            select(ModelLineageEvent)
            .where(ModelLineageEvent.model_version_id == model_version_id)
            .order_by(desc(ModelLineageEvent.created_at))
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_previous_champion_model_id(
        self,
        current_champion_id: uuid.UUID,
    ) -> uuid.UUID | None:
        """Find the model that was champion before the current one by looking at demotion events."""
        statement = (
            select(ModelLineageEvent.model_version_id)
            .where(
                ModelLineageEvent.event_type == "demoted",
                ModelLineageEvent.from_role == "champion",
                ModelLineageEvent.to_role == "none",
            )
            .order_by(desc(ModelLineageEvent.created_at))
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
