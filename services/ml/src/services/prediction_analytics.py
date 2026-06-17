from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import Date

from src.db.models.audit_log import AuditLog
from src.db.models.feature_snapshot import FeatureSnapshot
from src.db.models.model_version import ModelVersion
from src.db.models.prediction_record import PredictionRecord
from src.db.models.student_profile import StudentProfile


class PredictionAnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_prediction_analytics(self) -> dict[str, Any]:
        summary = await self._fetch_prediction_summary()
        return {
            **summary,
            "predictions_by_model_version": await self._fetch_by_model_version(),
            "predictions_by_date": await self._fetch_by_date(),
        }

    async def get_operational_metrics(self) -> dict[str, Any]:
        summary = await self._fetch_prediction_summary()
        failed_predictions = await self._count_failed_predictions()
        latest_model_version = await self._fetch_latest_model_version()
        total = summary["total_predictions"]
        high_risk_percentage = (
            round((summary["high_risk_count"] / total) * 100, 2) if total else 0.0
        )

        return {
            "total_predictions": total,
            "failed_predictions": failed_predictions,
            "average_latency": summary["average_latency_ms"],
            "latest_model_version": latest_model_version,
            "high_risk_percentage": high_risk_percentage,
        }

    async def get_dashboard_summary(self) -> dict[str, int]:
        profile_count = await self._count(StudentProfile.id)
        snapshot_count = await self._count(FeatureSnapshot.id)
        prediction_count = await self._count(PredictionRecord.id)
        risk_counts = await self._fetch_risk_level_counts()

        return {
            "profiles": profile_count,
            "snapshots": snapshot_count,
            "predictions": prediction_count,
            "high_risk": risk_counts.get("HIGH", 0),
            "medium_risk": risk_counts.get("MEDIUM", 0),
            "low_risk": risk_counts.get("LOW", 0),
        }

    async def get_prediction_history(self, student_profile_id: UUID) -> dict[str, Any] | None:
        records_statement = (
            select(PredictionRecord, FeatureSnapshot, ModelVersion)
            .outerjoin(
                FeatureSnapshot,
                PredictionRecord.feature_snapshot_id == FeatureSnapshot.id,
            )
            .outerjoin(ModelVersion, PredictionRecord.model_version_id == ModelVersion.id)
            .where(PredictionRecord.student_profile_id == student_profile_id)
            .order_by(
                func.coalesce(
                    PredictionRecord.prediction_timestamp,
                    PredictionRecord.created_at,
                ).desc()
            )
        )
        records_result = await self._session.execute(records_statement)
        rows = records_result.all()
        if not rows:
            return None

        snapshot_statement = (
            select(FeatureSnapshot)
            .where(FeatureSnapshot.student_profile_id == student_profile_id)
            .order_by(FeatureSnapshot.created_at.desc())
        )
        snapshot_result = await self._session.execute(snapshot_statement)
        snapshots = [_serialize_snapshot(snapshot) for snapshot in snapshot_result.scalars().all()]
        history = [
            _serialize_prediction(record, snapshot=snapshot, model_version=model_version)
            for record, snapshot, model_version in rows
        ]

        return {
            "student_profile_id": str(student_profile_id),
            "latest_prediction": history[0],
            "prediction_history": history,
            "associated_snapshots": snapshots,
        }

    async def get_prediction_details(self, prediction_id: UUID) -> dict[str, Any] | None:
        statement = (
            select(PredictionRecord, FeatureSnapshot, ModelVersion)
            .outerjoin(
                FeatureSnapshot,
                PredictionRecord.feature_snapshot_id == FeatureSnapshot.id,
            )
            .outerjoin(ModelVersion, PredictionRecord.model_version_id == ModelVersion.id)
            .where(PredictionRecord.id == prediction_id)
            .limit(1)
        )
        result = await self._session.execute(statement)
        row = result.first()
        if row is None:
            return None

        record, snapshot, model_version = row
        return _serialize_prediction(record, snapshot=snapshot, model_version=model_version)

    async def _fetch_prediction_summary(self) -> dict[str, Any]:
        statement = select(
            func.count(PredictionRecord.id),
            func.avg(PredictionRecord.final_risk),
            func.sum(case((PredictionRecord.risk_level == "HIGH", 1), else_=0)),
            func.sum(case((PredictionRecord.risk_level == "LOW", 1), else_=0)),
            func.avg(PredictionRecord.prediction_duration_ms),
        )
        result = await self._session.execute(statement)
        total, avg_risk, high_count, low_count, avg_latency = result.one()
        return {
            "total_predictions": int(total or 0),
            "average_risk": float(avg_risk or 0.0),
            "high_risk_count": int(high_count or 0),
            "low_risk_count": int(low_count or 0),
            "average_latency_ms": float(avg_latency or 0.0),
        }

    async def _fetch_by_model_version(self) -> list[dict[str, Any]]:
        statement = (
            select(
                func.coalesce(PredictionRecord.model_name, "unknown"),
                func.coalesce(PredictionRecord.model_version, "unknown"),
                func.count(PredictionRecord.id),
            )
            .group_by(
                func.coalesce(PredictionRecord.model_name, "unknown"),
                func.coalesce(PredictionRecord.model_version, "unknown"),
            )
            .order_by(func.count(PredictionRecord.id).desc())
        )
        result = await self._session.execute(statement)
        return [
            {
                "model_name": model_name,
                "model_version": model_version,
                "count": int(count),
            }
            for model_name, model_version, count in result.all()
        ]

    async def _fetch_by_date(self) -> list[dict[str, Any]]:
        prediction_date = cast(
            func.coalesce(
                PredictionRecord.prediction_timestamp,
                PredictionRecord.created_at,
            ),
            Date,
        )
        statement = (
            select(prediction_date.label("prediction_date"), func.count(PredictionRecord.id))
            .group_by(prediction_date)
            .order_by(prediction_date)
        )
        result = await self._session.execute(statement)
        return [
            {
                "date": _serialize_date(prediction_date_value),
                "count": int(count),
            }
            for prediction_date_value, count in result.all()
        ]

    async def _fetch_risk_level_counts(self) -> dict[str, int]:
        statement = (
            select(PredictionRecord.risk_level, func.count(PredictionRecord.id))
            .group_by(PredictionRecord.risk_level)
        )
        result = await self._session.execute(statement)
        return {
            risk_level: int(count)
            for risk_level, count in result.all()
            if risk_level is not None
        }

    async def _count_failed_predictions(self) -> int:
        statement = select(func.count(AuditLog.id)).where(
            AuditLog.action == "prediction.failed"
        )
        result = await self._session.execute(statement)
        return int(result.scalar_one() or 0)

    async def _fetch_latest_model_version(self) -> dict[str, Any] | None:
        statement = (
            select(ModelVersion)
            .where(ModelVersion.is_active.is_(True))
            .order_by(
                ModelVersion.deployed_at.desc().nulls_last(),
                ModelVersion.created_at.desc(),
            )
            .limit(1)
        )
        result = await self._session.execute(statement)
        model_version = result.scalar_one_or_none()
        if model_version is None:
            return None
        return _serialize_model_version(model_version)

    async def _count(self, column: Any) -> int:
        statement = select(func.count(column))
        result = await self._session.execute(statement)
        return int(result.scalar_one() or 0)


def _serialize_prediction(
    record: PredictionRecord,
    *,
    snapshot: FeatureSnapshot | None,
    model_version: ModelVersion | None,
) -> dict[str, Any]:
    return {
        "prediction_id": str(record.id),
        "student_profile_id": str(record.student_profile_id),
        "feature_snapshot_id": (
            str(record.feature_snapshot_id) if record.feature_snapshot_id else None
        ),
        "model_version_id": (
            str(record.model_version_id) if record.model_version_id else None
        ),
        "prediction_timestamp": _serialize_datetime(
            record.prediction_timestamp or record.created_at
        ),
        "model_name": record.model_name
        or (model_version.name if model_version is not None else None),
        "model_version": record.model_version
        or (model_version.version if model_version is not None else None),
        "snapshot_checksum": record.snapshot_checksum
        or (snapshot.checksum if snapshot is not None else None),
        "prediction_duration_ms": record.prediction_duration_ms,
        "income_risk": record.income_risk,
        "caste_risk": record.caste_risk,
        "transaction_risk": record.transaction_risk,
        "medical_risk": record.medical_risk,
        "final_risk": record.final_risk,
        "risk_level": record.risk_level,
        "inference_source": record.inference_source,
        "created_at": _serialize_datetime(record.created_at),
        "snapshot": _serialize_snapshot(snapshot) if snapshot is not None else None,
        "model_version_metadata": (
            _serialize_model_version(model_version) if model_version is not None else None
        ),
    }


def _serialize_snapshot(snapshot: FeatureSnapshot) -> dict[str, Any]:
    return {
        "feature_snapshot_id": str(snapshot.id),
        "student_profile_id": str(snapshot.student_profile_id),
        "source": snapshot.source,
        "feature_schema_version": snapshot.feature_schema_version,
        "checksum": snapshot.checksum,
        "features": snapshot.features,
        "created_at": _serialize_datetime(snapshot.created_at),
    }


def _serialize_model_version(model_version: ModelVersion) -> dict[str, Any]:
    return {
        "model_version_id": str(model_version.id),
        "name": model_version.name,
        "version": model_version.version,
        "description": model_version.description,
        "artifact_uri": model_version.artifact_uri,
        "configuration": model_version.configuration,
        "is_active": model_version.is_active,
        "deployed_at": _serialize_datetime(model_version.deployed_at),
        "created_at": _serialize_datetime(model_version.created_at),
    }


def _serialize_datetime(value: Any) -> str | None:
    return value.isoformat() if value is not None else None


def _serialize_date(value: Any) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)
