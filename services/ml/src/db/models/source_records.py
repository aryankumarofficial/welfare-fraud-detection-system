import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class StudentFinancialRecord(Base):
    __tablename__ = "student_financial_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    income_in_rs: Mapped[float] = mapped_column(Float, nullable=False)
    land_owned_acres: Mapped[float] = mapped_column(Float, nullable=False)
    vehicles_owned: Mapped[int] = mapped_column(Integer, nullable=False)
    electricity_consumption: Mapped[float] = mapped_column(Float, nullable=False)
    pending_loans: Mapped[int] = mapped_column(Integer, nullable=False)
    business_ownership: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class StudentSocialRecord(Base):
    __tablename__ = "student_social_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    caste: Mapped[str] = mapped_column(String, nullable=False)
    father_caste: Mapped[str] = mapped_column(String, nullable=False)
    avg_caste_population_per: Mapped[float] = mapped_column(Float, nullable=False)
    officer_approvals_per_day: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class StudentTransactionSummary(Base):
    __tablename__ = "student_transaction_summaries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    weekly_spending: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_spending: Mapped[float] = mapped_column(Float, nullable=False)
    transaction_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_transaction_value: Mapped[float] = mapped_column(Float, nullable=False)
    luxury_items_bought: Mapped[int] = mapped_column(Integer, nullable=False)
    weekend_spending_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class StudentMedicalSummary(Base):
    __tablename__ = "student_medical_summaries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    hospital_visits_per_year: Mapped[int] = mapped_column(Integer, nullable=False)
    claim_frequency: Mapped[int] = mapped_column(Integer, nullable=False)
    medical_claim_amount: Mapped[float] = mapped_column(Float, nullable=False)
    avg_claim_amount: Mapped[float] = mapped_column(Float, nullable=False)
    chronic_disease: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
