from uuid import UUID


class ProfileNotFoundError(Exception):
    def __init__(self, student_profile_id: UUID) -> None:
        self.student_profile_id = student_profile_id
        super().__init__(f"Student profile not found: {student_profile_id}")


class SnapshotNotFoundError(Exception):
    def __init__(self, student_profile_id: UUID) -> None:
        self.student_profile_id = student_profile_id
        super().__init__(f"No feature snapshot found for profile: {student_profile_id}")


class SnapshotProfileMismatchError(Exception):
    def __init__(self, student_profile_id: UUID, feature_snapshot_id: UUID) -> None:
        self.student_profile_id = student_profile_id
        self.feature_snapshot_id = feature_snapshot_id
        super().__init__(
            "Feature snapshot does not belong to profile: "
            f"{feature_snapshot_id} -> {student_profile_id}"
        )


class PredictionFailedError(Exception):
    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        self.cause = cause
        super().__init__(message)


class MissingSourceDataError(Exception):
    def __init__(self, student_profile_id: UUID, missing_sources: list[str]) -> None:
        self.student_profile_id = student_profile_id
        self.missing_sources = missing_sources
        source_list = ", ".join(missing_sources)
        super().__init__(
            f"Missing source data for profile {student_profile_id}: {source_list}"
        )


class FeatureGenerationError(Exception):
    def __init__(
        self,
        message: str,
        *,
        details: list[dict[str, object]] | None = None,
        cause: Exception | None = None,
    ) -> None:
        self.details = details or []
        self.cause = cause
        super().__init__(message)


class SnapshotGenerationError(Exception):
    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        self.cause = cause
        super().__init__(message)
