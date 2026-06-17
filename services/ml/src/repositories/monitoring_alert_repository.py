import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, select

from src.db.models.monitoring_alert import MonitoringAlert
from src.db.repositories.base import AsyncRepository


class MonitoringAlertRepository(AsyncRepository[MonitoringAlert]):
    model = MonitoringAlert

    async def create_alert(
        self,
        *,
        alert_type: str,
        severity: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> MonitoringAlert:
        alert = MonitoringAlert(
            id=uuid.uuid4(),
            alert_type=alert_type,
            severity=severity,
            message=message,
            metadata_json=metadata,
            created_at=datetime.now(UTC),
        )
        return await self.add(alert)

    async def recent_alerts(self, *, limit: int = 50) -> list[MonitoringAlert]:
        statement = select(MonitoringAlert).order_by(desc(MonitoringAlert.created_at)).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())
