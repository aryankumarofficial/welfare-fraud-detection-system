from uuid import UUID

from src.db.models.student_profile import StudentProfile
from src.db.repositories.base import AsyncRepository


class StudentProfileRepository(AsyncRepository[StudentProfile]):
    model = StudentProfile

    async def get_by_id(self, profile_id: UUID) -> StudentProfile | None:
        return await super().get_by_id(profile_id)
