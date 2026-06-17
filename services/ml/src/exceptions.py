from uuid import UUID


class ProfileNotFoundError(Exception):
    def __init__(self, student_profile_id: UUID) -> None:
        self.student_profile_id = student_profile_id
        super().__init__(f"Student profile not found: {student_profile_id}")


class SnapshotNotFoundError(Exception):
    def __init__(self, student_profile_id: UUID) -> None:
        self.student_profile_id = student_profile_id
        super().__init__(f"No feature snapshot found for profile: {student_profile_id}")


class PredictionFailedError(Exception):
    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        self.cause = cause
        super().__init__(message)
