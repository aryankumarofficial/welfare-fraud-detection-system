from uuid import UUID

from sqlalchemy import select

from src.db.models.source_records import (
    StudentFinancialRecord,
    StudentMedicalSummary,
    StudentSocialRecord,
    StudentTransactionSummary,
)
from src.db.repositories.base import AsyncRepository


class StudentFinancialRecordRepository(AsyncRepository[StudentFinancialRecord]):
    model = StudentFinancialRecord

    async def get_latest_by_profile_id(
        self,
        student_profile_id: UUID,
    ) -> StudentFinancialRecord | None:
        statement = (
            select(StudentFinancialRecord)
            .where(StudentFinancialRecord.student_profile_id == student_profile_id)
            .order_by(StudentFinancialRecord.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()


class StudentSocialRecordRepository(AsyncRepository[StudentSocialRecord]):
    model = StudentSocialRecord

    async def get_latest_by_profile_id(
        self,
        student_profile_id: UUID,
    ) -> StudentSocialRecord | None:
        statement = (
            select(StudentSocialRecord)
            .where(StudentSocialRecord.student_profile_id == student_profile_id)
            .order_by(StudentSocialRecord.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()


class StudentTransactionSummaryRepository(
    AsyncRepository[StudentTransactionSummary]
):
    model = StudentTransactionSummary

    async def get_latest_by_profile_id(
        self,
        student_profile_id: UUID,
    ) -> StudentTransactionSummary | None:
        statement = (
            select(StudentTransactionSummary)
            .where(StudentTransactionSummary.student_profile_id == student_profile_id)
            .order_by(StudentTransactionSummary.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()


class StudentMedicalSummaryRepository(AsyncRepository[StudentMedicalSummary]):
    model = StudentMedicalSummary

    async def get_latest_by_profile_id(
        self,
        student_profile_id: UUID,
    ) -> StudentMedicalSummary | None:
        statement = (
            select(StudentMedicalSummary)
            .where(StudentMedicalSummary.student_profile_id == student_profile_id)
            .order_by(StudentMedicalSummary.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
