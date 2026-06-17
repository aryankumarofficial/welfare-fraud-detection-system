import asyncio
import os
import sys
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

ML_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ML_ROOT))
os.chdir(ML_ROOT)

from src.db.models.monitoring_alert import MonitoringAlert
from src.db.models.prediction_record import PredictionRecord
from src.db.models.prediction_review import PredictionReview
from src.services.drift_monitoring_service import DriftMonitoringService
from src.services.explainability_service import ExplainabilityService
from src.services.model_evaluation_service import ModelEvaluationService
from src.services.prediction_review_service import PredictionReviewService


def test_explainability_metadata_includes_top_features_and_summary() -> None:
    service = ExplainabilityService()

    explanation = service.generate(
        features={
            "income_in_rs": 10_000,
            "monthly_spending": 50_000,
            "transaction_count": 80,
            "medical_claim_amount": 25_000,
        },
        risks={
            "income_risk": 0.8,
            "caste_risk": 0.1,
            "transaction_risk": 0.6,
            "medical_risk": 0.3,
            "final_risk": 0.72,
        },
        risk_level="HIGH",
    )

    assert explanation["method"] == "risk-component-attribution-v1"
    assert explanation["top_contributing_features"]
    assert "Prediction classified as HIGH" in explanation["summary"]
    assert "income_in_rs" in explanation["feature_values"]


def test_model_evaluation_metrics_calculate_precision_and_agreement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ModelEvaluationService(object())  # type: ignore[arg-type]

    async def fake_decision_counts() -> dict[str, int]:
        return {
            "confirmed_fraud": 6,
            "false_positive": 2,
            "pending": 1,
            "under_investigation": 1,
        }

    monkeypatch.setattr(service, "_decision_counts", fake_decision_counts)

    metrics = asyncio.run(service.get_model_performance())

    assert metrics["reviewed_predictions"] == 10
    assert metrics["confirmed_fraud_count"] == 6
    assert metrics["false_positives"] == 2
    assert metrics["precision"] == 0.75
    assert metrics["review_agreement_rate"] == 0.6


def test_drift_monitoring_tracks_feature_risk_and_volume_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = DriftMonitoringService(object())  # type: ignore[arg-type]
    snapshot_id = uuid.uuid4()

    class FakeDriftRepository:
        async def create_snapshot(self, **kwargs: Any) -> Any:
            return type(
                "Snapshot",
                (),
                {
                    "id": snapshot_id,
                    "created_at": datetime.now(UTC),
                    **kwargs,
                },
            )()

        async def recent_snapshots(self, *, limit: int = 20) -> list[Any]:
            return []

    async def fake_feature_rows(*, start: datetime, end: datetime | None = None) -> list[dict[str, Any]]:
        if end is None:
            return [{"income_in_rs": 200.0}, {"income_in_rs": 300.0}]
        return [{"income_in_rs": 100.0}, {"income_in_rs": 100.0}]

    async def fake_prediction_rows(
        *,
        start: datetime,
        end: datetime | None = None,
    ) -> list[tuple[float, str | None]]:
        if end is None:
            return [(0.8, "HIGH"), (0.6, "MEDIUM")]
        return [(0.2, "LOW")]

    monkeypatch.setattr(service, "_snapshots", FakeDriftRepository())
    monkeypatch.setattr(service, "_feature_rows", fake_feature_rows)
    monkeypatch.setattr(service, "_prediction_rows", fake_prediction_rows)

    report = asyncio.run(service.get_drift_report(days=7))

    latest = report["latest_snapshot"]
    assert latest["window"] == "7d"
    assert latest["feature_distribution_changes"]["income_in_rs"]["change_percentage"] == 150.0
    assert latest["risk_distribution_changes"]["current_risk_levels"] == {
        "HIGH": 1,
        "MEDIUM": 1,
    }
    assert latest["prediction_volume_changes"]["change_percentage"] == 100.0
    assert latest["drift_score"] == 250.0


def test_prediction_review_service_creates_review_and_audit_log() -> None:
    prediction_id = uuid.uuid4()
    review_id = uuid.uuid4()
    created_logs: list[dict[str, Any]] = []

    class FakePredictionRepository:
        async def get_by_id(self, requested_id: uuid.UUID) -> PredictionRecord:
            assert requested_id == prediction_id
            return object()  # type: ignore[return-value]

    class FakeReviewRepository:
        async def create_review(self, **kwargs: Any) -> PredictionReview:
            return PredictionReview(
                id=review_id,
                prediction_id=kwargs["prediction_id"],
                reviewer=kwargs["reviewer"],
                decision=kwargs["decision"],
                notes=kwargs["notes"],
                created_at=datetime.now(UTC),
            )

    class FakeAuditRepository:
        async def create_audit_log(self, **kwargs: Any) -> None:
            created_logs.append(kwargs)

    service = PredictionReviewService(object())  # type: ignore[arg-type]
    service._predictions = FakePredictionRepository()  # type: ignore[assignment]
    service._reviews = FakeReviewRepository()  # type: ignore[assignment]
    service._audit = FakeAuditRepository()  # type: ignore[assignment]

    review = asyncio.run(
        service.create_review(
            prediction_id=prediction_id,
            reviewer="analyst@example.com",
            decision="confirmed_fraud",
            notes="Matched field evidence.",
        )
    )

    assert review.id == review_id
    assert review.decision == "confirmed_fraud"
    assert created_logs[0]["action"] == "prediction.reviewed"


def test_alert_service_generates_monitoring_alerts(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.services.alert_service import AlertService

    drift_id = uuid.uuid4()
    created: list[MonitoringAlert] = []

    class FakeAlertRepository:
        async def create_alert(self, **kwargs: Any) -> MonitoringAlert:
            alert = MonitoringAlert(
                id=uuid.uuid4(),
                alert_type=kwargs["alert_type"],
                severity=kwargs["severity"],
                message=kwargs["message"],
                metadata_json=kwargs["metadata"],
                created_at=datetime.now(UTC),
            )
            created.append(alert)
            return alert

        async def recent_alerts(self, *, limit: int = 50) -> list[MonitoringAlert]:
            return created

    class FakeDriftRepository:
        async def recent_snapshots(self, *, limit: int = 20) -> list[Any]:
            return [
                type(
                    "Drift",
                    (),
                    {"id": drift_id, "drift_score": 75.0},
                )()
            ]

    class FakeAnalytics:
        async def get_operational_metrics(self) -> dict[str, Any]:
            return {"total_predictions": 20, "failed_predictions": 3}

    class FakeEvaluation:
        async def get_model_performance(self) -> dict[str, Any]:
            return {"reviewed_predictions": 10, "false_positives": 4}

    class FakeQueue:
        async def get_queue_analytics(self) -> dict[str, Any]:
            return {"pending": 51, "processing": 0, "retrying": 0}

    service = AlertService(object())  # type: ignore[arg-type]
    service._alerts = FakeAlertRepository()  # type: ignore[assignment]
    service._drift_snapshots = FakeDriftRepository()  # type: ignore[assignment]
    service._analytics = FakeAnalytics()  # type: ignore[assignment]
    service._evaluation = FakeEvaluation()  # type: ignore[assignment]
    service._queue = FakeQueue()  # type: ignore[assignment]

    alerts = asyncio.run(service.generate_alerts())

    assert {alert.alert_type for alert in alerts} == {
        "MODEL_DRIFT",
        "HIGH_FAILURE_RATE",
        "QUEUE_BACKLOG",
        "HIGH_FALSE_POSITIVE_RATE",
    }


def test_monitoring_endpoints_return_payloads(monkeypatch: pytest.MonkeyPatch) -> None:
    from src import app as app_module

    prediction_id = uuid.uuid4()
    review = PredictionReview(
        id=uuid.uuid4(),
        prediction_id=prediction_id,
        reviewer="analyst",
        decision="pending",
        notes=None,
        created_at=datetime.now(UTC),
    )

    @asynccontextmanager
    async def fake_db_session() -> AsyncIterator[object]:
        yield object()

    class FakeReviewService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def create_review(self, **kwargs: Any) -> PredictionReview:
            assert kwargs["prediction_id"] == prediction_id
            return review

        async def list_reviews(self, **kwargs: Any) -> list[dict[str, Any]]:
            return [{"review_id": str(review.id)}]

    class FakeEvaluationService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def get_model_performance(self) -> dict[str, Any]:
            return {"reviewed_predictions": 1}

    class FakeDriftService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def get_drift_report(self, *, days: int = 7) -> dict[str, Any]:
            return {"latest_snapshot": {"window": f"{days}d"}}

    class FakeAlertService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def get_alerts(self) -> dict[str, Any]:
            return {"recent_alerts": []}

    monkeypatch.setattr(app_module, "get_db_session", fake_db_session)
    monkeypatch.setattr(app_module, "PredictionReviewService", FakeReviewService)
    monkeypatch.setattr(app_module, "ModelEvaluationService", FakeEvaluationService)
    monkeypatch.setattr(app_module, "DriftMonitoringService", FakeDriftService)
    monkeypatch.setattr(app_module, "AlertService", FakeAlertService)

    body = app_module.PredictionReviewBody(
        reviewer="analyst",
        decision="pending",
        notes=None,
    )

    assert asyncio.run(app_module.create_prediction_review(prediction_id, body))["success"] is True
    assert asyncio.run(app_module.get_prediction_reviews())["data"] == [
        {"review_id": str(review.id)}
    ]
    assert asyncio.run(app_module.get_model_performance()) == {"reviewed_predictions": 1}
    assert asyncio.run(app_module.get_drift_analytics(days=14)) == {
        "latest_snapshot": {"window": "14d"}
    }
    assert asyncio.run(app_module.get_alerts()) == {"recent_alerts": []}
