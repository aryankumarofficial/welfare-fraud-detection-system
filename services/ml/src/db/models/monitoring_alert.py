import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base

MONITORING_ALERT_TYPES = (
    "MODEL_DRIFT",
    "HIGH_FAILURE_RATE",
    "QUEUE_BACKLOG",
    "HIGH_FALSE_POSITIVE_RATE",
)

MONITORING_ALERT_SEVERITIES = ("info", "warning", "critical")


class MonitoringAlert(Base):
    __tablename__ = "monitoring_alerts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    alert_type: Mapped[str] = mapped_column(
        Enum(*MONITORING_ALERT_TYPES, name="monitoring_alert_type", native_enum=True),
        nullable=False,
    )
    severity: Mapped[str] = mapped_column(
        Enum(
            *MONITORING_ALERT_SEVERITIES,
            name="monitoring_alert_severity",
            native_enum=True,
        ),
        nullable=False,
        default="warning",
    )
    message: Mapped[str] = mapped_column(String, nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
