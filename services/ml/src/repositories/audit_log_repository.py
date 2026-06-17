import uuid
from datetime import UTC, datetime
from typing import Any

from src.db.models.audit_log import AuditLog
from src.db.repositories.base import AsyncRepository


class AuditLogRepository(AsyncRepository[AuditLog]):
    model = AuditLog

    async def create_audit_log(
        self,
        *,
        action: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        actor_user_id: uuid.UUID | None = None,
    ) -> AuditLog:
        log = AuditLog(
            id=uuid.uuid4(),
            actor_user_id=actor_user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_json=metadata,
            created_at=datetime.now(UTC),
        )
        return await self.add(log)
