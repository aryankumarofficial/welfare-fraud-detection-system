from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.feature_snapshot import FeatureSnapshot
from src.db.models.student_profile import StudentProfile
from src.exceptions import (
    ProfileNotFoundError,
    SnapshotNotFoundError,
    SnapshotProfileMismatchError,
)
from src.repositories.feature_snapshot_repository import FeatureSnapshotRepository
from src.repositories.student_profile_repository import StudentProfileRepository
from src.schemas.feature_snapshot import InvalidFeatureSetError, validate_feature_snapshot


@dataclass(frozen=True)
class LoadedFeatures:
    profile: StudentProfile
    snapshot: FeatureSnapshot
    features: dict[str, Any]


class FeatureLoader:
    """Loads and validates the latest feature snapshot for a beneficiary profile."""

    def __init__(self, session: AsyncSession) -> None:
        self._profiles = StudentProfileRepository(session)
        self._snapshots = FeatureSnapshotRepository(session)

    async def load_latest_features(self, student_profile_id: UUID) -> LoadedFeatures:
        profile = await self._profiles.get_by_id(student_profile_id)
        if profile is None:
            raise ProfileNotFoundError(student_profile_id)

        snapshot = await self._snapshots.get_latest_by_profile_id(student_profile_id)
        if snapshot is None:
            raise SnapshotNotFoundError(student_profile_id)

        features = validate_feature_snapshot(
            snapshot.features,
            feature_schema_version=snapshot.feature_schema_version,
        )

        return LoadedFeatures(profile=profile, snapshot=snapshot, features=features)

    async def load_features_by_snapshot_id(
        self,
        *,
        student_profile_id: UUID,
        feature_snapshot_id: UUID,
    ) -> LoadedFeatures:
        profile = await self._profiles.get_by_id(student_profile_id)
        if profile is None:
            raise ProfileNotFoundError(student_profile_id)

        snapshot = await self._snapshots.get_by_id(feature_snapshot_id)
        if snapshot is None:
            raise SnapshotNotFoundError(student_profile_id)
        if snapshot.student_profile_id != student_profile_id:
            raise SnapshotProfileMismatchError(student_profile_id, feature_snapshot_id)

        features = validate_feature_snapshot(
            snapshot.features,
            feature_schema_version=snapshot.feature_schema_version,
        )

        return LoadedFeatures(profile=profile, snapshot=snapshot, features=features)
