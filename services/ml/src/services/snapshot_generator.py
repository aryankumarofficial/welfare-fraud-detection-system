from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.feature_snapshot import FeatureSnapshot
from src.exceptions import (
    FeatureGenerationError,
    MissingSourceDataError,
    ProfileNotFoundError,
)
from src.repositories.source_record_repositories import (
    StudentFinancialRecordRepository,
    StudentMedicalSummaryRepository,
    StudentSocialRecordRepository,
    StudentTransactionSummaryRepository,
)
from src.repositories.student_profile_repository import StudentProfileRepository
from src.schemas.feature_snapshot import (
    FEATURE_SCHEMA_VERSION_V1,
    InvalidFeatureSetError,
    validate_feature_snapshot,
)
from src.services.feature_builder import FeatureBuilder, FeatureSourceRecords
from src.services.snapshot_service import SnapshotService


@dataclass(frozen=True)
class GeneratedSnapshot:
    snapshot: FeatureSnapshot
    features: dict[str, Any]


class SnapshotGenerator:
    """Orchestrates source-data loading, feature generation, validation, and storage."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        feature_builder: FeatureBuilder | None = None,
    ) -> None:
        self._profiles = StudentProfileRepository(session)
        self._financial_records = StudentFinancialRecordRepository(session)
        self._social_records = StudentSocialRecordRepository(session)
        self._transaction_summaries = StudentTransactionSummaryRepository(session)
        self._medical_summaries = StudentMedicalSummaryRepository(session)
        self._feature_builder = feature_builder or FeatureBuilder()
        self._snapshot_service = SnapshotService(session)

    async def generate_for_profile(
        self,
        student_profile_id: UUID,
    ) -> GeneratedSnapshot:
        profile = await self._profiles.get_by_id(student_profile_id)
        if profile is None:
            raise ProfileNotFoundError(student_profile_id)

        source_records = FeatureSourceRecords(
            profile=profile,
            financial=await self._financial_records.get_latest_by_profile_id(
                student_profile_id
            ),
            social=await self._social_records.get_latest_by_profile_id(
                student_profile_id
            ),
            transaction=await self._transaction_summaries.get_latest_by_profile_id(
                student_profile_id
            ),
            medical=await self._medical_summaries.get_latest_by_profile_id(
                student_profile_id
            ),
        )

        try:
            features = self._feature_builder.build(source_records)
            validated_features = validate_feature_snapshot(
                features,
                feature_schema_version=FEATURE_SCHEMA_VERSION_V1,
            )
        except InvalidFeatureSetError as exc:
            raise FeatureGenerationError(
                "Generated feature set failed schema validation.",
                details=exc.details,
                cause=exc,
            ) from exc
        except MissingSourceDataError:
            raise
        except Exception as exc:
            raise FeatureGenerationError(
                "Failed to build feature set from source records.",
                cause=exc,
            ) from exc

        snapshot = await self._snapshot_service.create_snapshot(
            student_profile_id=student_profile_id,
            features=validated_features,
        )

        return GeneratedSnapshot(snapshot=snapshot, features=validated_features)
