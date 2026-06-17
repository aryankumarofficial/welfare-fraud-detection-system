import asyncio
import os
import sys
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

ML_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ML_ROOT))
os.chdir(ML_ROOT)

from src.services.prediction_analytics import PredictionAnalyticsService
from src.services.risk_classifier import RiskClassifier


def test_risk_classifier_boundaries() -> None:
    classifier = RiskClassifier()

    assert classifier.classify(0.0).level == "LOW"
    assert classifier.classify(0.30).level == "LOW"
    assert classifier.classify(0.31).level == "MEDIUM"
    assert classifier.classify(0.60).level == "MEDIUM"
    assert classifier.classify(0.61).level == "HIGH"
    assert classifier.classify(1.0).level == "HIGH"


def test_operational_metrics_calculates_high_risk_percentage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = PredictionAnalyticsService(object())  # type: ignore[arg-type]

    async def fake_summary() -> dict[str, Any]:
        return {
            "total_predictions": 4,
            "average_risk": 0.55,
            "high_risk_count": 1,
            "low_risk_count": 2,
            "average_latency_ms": 18.5,
        }

    async def fake_failed_predictions() -> int:
        return 3

    async def fake_latest_model_version() -> dict[str, Any]:
        return {"name": "isolation_forest", "version": "v1"}

    monkeypatch.setattr(service, "_fetch_prediction_summary", fake_summary)
    monkeypatch.setattr(service, "_count_failed_predictions", fake_failed_predictions)
    monkeypatch.setattr(service, "_fetch_latest_model_version", fake_latest_model_version)

    metrics = asyncio.run(service.get_operational_metrics())

    assert metrics == {
        "total_predictions": 4,
        "failed_predictions": 3,
        "average_latency": 18.5,
        "latest_model_version": {"name": "isolation_forest", "version": "v1"},
        "high_risk_percentage": 25.0,
    }


def test_dashboard_summary_uses_risk_level_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = PredictionAnalyticsService(object())  # type: ignore[arg-type]
    counts = iter([7, 5, 9])

    async def fake_count(column: object) -> int:
        return next(counts)

    async def fake_risk_counts() -> dict[str, int]:
        return {"HIGH": 2, "MEDIUM": 3, "LOW": 4}

    monkeypatch.setattr(service, "_count", fake_count)
    monkeypatch.setattr(service, "_fetch_risk_level_counts", fake_risk_counts)

    summary = asyncio.run(service.get_dashboard_summary())

    assert summary == {
        "profiles": 7,
        "snapshots": 5,
        "predictions": 9,
        "high_risk": 2,
        "medium_risk": 3,
        "low_risk": 4,
    }


def test_prediction_history_endpoint_returns_latest_history_and_snapshots(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src import app as app_module

    profile_id = uuid.uuid4()
    payload = {
        "student_profile_id": str(profile_id),
        "latest_prediction": {"prediction_id": str(uuid.uuid4())},
        "prediction_history": [{"prediction_id": str(uuid.uuid4())}],
        "associated_snapshots": [{"feature_snapshot_id": str(uuid.uuid4())}],
    }

    @asynccontextmanager
    async def fake_db_session() -> AsyncIterator[object]:
        yield object()

    class FakeAnalyticsService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def get_prediction_history(self, student_profile_id: uuid.UUID) -> dict[str, Any]:
            assert student_profile_id == profile_id
            return payload

        async def get_prediction_details(self, prediction_id: uuid.UUID) -> None:
            return None

    monkeypatch.setattr(app_module, "get_db_session", fake_db_session)
    monkeypatch.setattr(app_module, "PredictionAnalyticsService", FakeAnalyticsService)

    response = asyncio.run(app_module.get_predictions_by_student_profile(profile_id))

    assert response == {"success": True, "data": payload}


def test_predictions_endpoint_falls_back_to_prediction_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src import app as app_module

    prediction_id = uuid.uuid4()
    payload = {"prediction_id": str(prediction_id), "final_risk": 0.8, "risk_level": "HIGH"}

    @asynccontextmanager
    async def fake_db_session() -> AsyncIterator[object]:
        yield object()

    class FakeAnalyticsService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def get_prediction_history(self, student_profile_id: uuid.UUID) -> None:
            return None

        async def get_prediction_details(self, requested_prediction_id: uuid.UUID) -> dict[str, Any]:
            assert requested_prediction_id == prediction_id
            return payload

    monkeypatch.setattr(app_module, "get_db_session", fake_db_session)
    monkeypatch.setattr(app_module, "PredictionAnalyticsService", FakeAnalyticsService)

    response = asyncio.run(app_module.get_predictions_by_student_profile(prediction_id))

    assert response == {"success": True, "data": payload}


def test_metrics_and_dashboard_endpoints_return_json_payloads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src import app as app_module

    metrics = {
        "total_predictions": 10,
        "failed_predictions": 1,
        "average_latency": 8.5,
        "latest_model_version": {"name": "isolation_forest", "version": "v1"},
        "high_risk_percentage": 40.0,
    }
    dashboard = {
        "profiles": 3,
        "snapshots": 4,
        "predictions": 10,
        "high_risk": 4,
        "medium_risk": 5,
        "low_risk": 1,
    }

    @asynccontextmanager
    async def fake_db_session() -> AsyncIterator[object]:
        yield object()

    class FakeAnalyticsService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def get_operational_metrics(self) -> dict[str, Any]:
            return metrics

        async def get_dashboard_summary(self) -> dict[str, int | float | dict[str, str]]:
            return dashboard

    monkeypatch.setattr(app_module, "get_db_session", fake_db_session)
    monkeypatch.setattr(app_module, "PredictionAnalyticsService", FakeAnalyticsService)

    assert asyncio.run(app_module.get_prediction_metrics()) == metrics
    assert asyncio.run(app_module.get_dashboard_summary()) == dashboard
