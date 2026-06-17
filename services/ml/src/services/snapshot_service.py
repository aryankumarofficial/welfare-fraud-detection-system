import hashlib
import json
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.feature_snapshot import FeatureSnapshot
from src.exceptions import SnapshotGenerationError
from src.repositories.feature_snapshot_repository import FeatureSnapshotRepository
from src.schemas.feature_snapshot import FEATURE_SCHEMA_VERSION_V1
from src.services.audit_service import PredictionAuditService


class SnapshotService:
    """Persists validated feature snapshots and derives stable checksums."""

    def __init__(self, session: AsyncSession) -> None:
        self._snapshots = FeatureSnapshotRepository(session)
        self._audit = PredictionAuditService(session)

    async def create_snapshot(
        self,
        *,
        student_profile_id: UUID,
        features: dict[str, Any],
        source: str = "profile_snapshot",
    ) -> FeatureSnapshot:
        checksum = self._build_checksum(features)

        try:
            snapshot = await self._snapshots.create_snapshot(
                student_profile_id=student_profile_id,
                features=features,
                feature_schema_version=FEATURE_SCHEMA_VERSION_V1,
                checksum=checksum,
                source=source,
            )
            await self._audit.snapshot_generated(
                snapshot_id=snapshot.id,
                student_profile_id=student_profile_id,
                checksum=snapshot.checksum,
                feature_schema_version=snapshot.feature_schema_version,
            )
            return snapshot
        except Exception as exc:
            raise SnapshotGenerationError(
                "Failed to persist generated feature snapshot.",
                cause=exc,
            ) from exc

    def _build_checksum(self, features: dict[str, Any]) -> str:
        serialized = json.dumps(
            features,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
