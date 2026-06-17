from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.audit_log_repository import AuditLogRepository


class PredictionAuditService:
    def __init__(self, session: AsyncSession) -> None:
        self._logs = AuditLogRepository(session)

    async def snapshot_generated(
        self,
        *,
        snapshot_id: UUID,
        student_profile_id: UUID,
        checksum: str | None,
        feature_schema_version: str,
    ) -> None:
        await self._logs.create_audit_log(
            action="snapshot.generated",
            resource_type="feature_snapshot",
            resource_id=str(snapshot_id),
            metadata={
                "student_profile_id": str(student_profile_id),
                "checksum": checksum,
                "feature_schema_version": feature_schema_version,
            },
        )

    async def prediction_executed(
        self,
        *,
        prediction_id: UUID,
        student_profile_id: UUID,
        feature_snapshot_id: UUID,
        metadata: dict[str, Any],
    ) -> None:
        await self._logs.create_audit_log(
            action="prediction.executed",
            resource_type="prediction_record",
            resource_id=str(prediction_id),
            metadata={
                "student_profile_id": str(student_profile_id),
                "feature_snapshot_id": str(feature_snapshot_id),
                **metadata,
            },
        )

    async def prediction_failed(
        self,
        *,
        student_profile_id: UUID,
        feature_snapshot_id: UUID | None,
        error: str,
    ) -> None:
        await self._logs.create_audit_log(
            action="prediction.failed",
            resource_type="prediction_record",
            metadata={
                "student_profile_id": str(student_profile_id),
                "feature_snapshot_id": (
                    str(feature_snapshot_id) if feature_snapshot_id else None
                ),
                "error": error,
            },
        )
