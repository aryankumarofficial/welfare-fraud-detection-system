import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base

FEATURE_SOURCES = ("api_payload", "csv_ingest", "profile_snapshot")


class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(
        Enum(*FEATURE_SOURCES, name="feature_source", native_enum=True),
        nullable=False,
        default="api_payload",
    )
    features: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    feature_schema_version: Mapped[str] = mapped_column(
        String, nullable=False, default="v1"
    )
    checksum: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
