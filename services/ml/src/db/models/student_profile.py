import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    income_in_rs: Mapped[float | None] = mapped_column(Float, nullable=True)
    land_owned_acres: Mapped[float | None] = mapped_column(Float, nullable=True)
    vehicles_owned: Mapped[int | None] = mapped_column(Integer, nullable=True)
    electricity_consumption: Mapped[float | None] = mapped_column(Float, nullable=True)
    pending_loans: Mapped[int | None] = mapped_column(Integer, nullable=True)
    business_ownership: Mapped[int | None] = mapped_column(Integer, nullable=True)

    caste: Mapped[str | None] = mapped_column(String, nullable=True)
    father_caste: Mapped[str | None] = mapped_column(String, nullable=True)
    avg_caste_population_per: Mapped[float | None] = mapped_column(Float, nullable=True)
    officer_approvals_per_day: Mapped[float | None] = mapped_column(Float, nullable=True)

    weekly_spending: Mapped[float | None] = mapped_column(Float, nullable=True)
    monthly_spending: Mapped[float | None] = mapped_column(Float, nullable=True)
    transaction_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_transaction_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    luxury_items_bought: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weekend_spending_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)

    hospital_visits_per_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    claim_frequency: Mapped[int | None] = mapped_column(Integer, nullable=True)
    medical_claim_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_claim_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    chronic_disease: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
