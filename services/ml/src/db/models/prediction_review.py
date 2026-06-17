import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base

PREDICTION_REVIEW_DECISIONS = (
    "pending",
    "confirmed_fraud",
    "false_positive",
    "under_investigation",
)


class PredictionReview(Base):
    __tablename__ = "prediction_reviews"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    prediction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("prediction_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    reviewer: Mapped[str] = mapped_column(String, nullable=False)
    decision: Mapped[str] = mapped_column(
        Enum(
            *PREDICTION_REVIEW_DECISIONS,
            name="prediction_review_decision",
            native_enum=True,
        ),
        nullable=False,
        default="pending",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
