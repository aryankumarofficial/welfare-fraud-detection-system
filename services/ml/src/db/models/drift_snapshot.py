import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class DriftSnapshot(Base):
    __tablename__ = "drift_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    window: Mapped[str] = mapped_column(String, nullable=False)
    feature_distribution_changes: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    risk_distribution_changes: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    prediction_volume_changes: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    drift_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
