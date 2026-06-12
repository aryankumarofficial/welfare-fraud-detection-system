import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base

INFERENCE_SOURCES = ("sync_api", "batch_worker", "scheduled_job")


class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    feature_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("feature_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )
    model_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("model_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    income_risk: Mapped[float] = mapped_column(Float, nullable=False)
    caste_risk: Mapped[float] = mapped_column(Float, nullable=False)
    transaction_risk: Mapped[float] = mapped_column(Float, nullable=False)
    medical_risk: Mapped[float] = mapped_column(Float, nullable=False)
    final_risk: Mapped[float] = mapped_column(Float, nullable=False)
    inference_source: Mapped[str] = mapped_column(
        Enum(*INFERENCE_SOURCES, name="inference_source", native_enum=True),
        nullable=False,
        default="sync_api",
    )
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
