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

from src.db.models.prediction_job import PredictionJob
from src.services.prediction_job_service import PredictionJobService
from src.services.prediction_queue_client import EnqueuedPrediction
from src.services.prediction_service import PredictionResult


def _job(
    *,
    job_id: uuid.UUID | None = None,
    student_profile_id: uuid.UUID | None = None,
    status: str = "pending",
    batch_id: uuid.UUID | None = None,
    result: dict[str, Any] | None = None,
) -> PredictionJob:
    now = datetime.now(UTC)
    return PredictionJob(
        id=job_id or uuid.uuid4(),
        bullmq_job_id=None,
        batch_id=batch_id,
        student_profile_id=student_profile_id or uuid.uuid4(),
        feature_snapshot_id=None,
        prediction_record_id=None,
        status=status,
        attempts=0,
        max_attempts=3,
        last_error=None,
        result=result,
        metadata_json={},
        queued_at=now,
        started_at=None,
        completed_at=None,
        failed_at=None,
        created_at=now,
        updated_at=now,
    )


class FakeJobRepository:
    def __init__(self) -> None:
        self.jobs: dict[uuid.UUID, PredictionJob] = {}
        self.status_counts = {
            "pending": 1,
            "processing": 1,
            "completed": 2,
            "failed": 1,
            "retrying": 1,
        }

    async def create_job(self, **kwargs: Any) -> PredictionJob:
        job = _job(
            student_profile_id=kwargs["student_profile_id"],
            batch_id=kwargs.get("batch_id"),
        )
        job.feature_snapshot_id = kwargs.get("feature_snapshot_id")
        job.metadata_json = kwargs.get("metadata")
        self.jobs[job.id] = job
        return job

    async def set_bullmq_job_id(
        self,
        job_id: uuid.UUID,
        bullmq_job_id: str,
    ) -> PredictionJob | None:
        self.jobs[job_id].bullmq_job_id = bullmq_job_id
        return self.jobs[job_id]

    async def get_by_id(self, job_id: uuid.UUID) -> PredictionJob | None:
        return self.jobs.get(job_id)

    async def mark_processing(
        self,
        job_id: uuid.UUID,
        *,
        attempts: int,
    ) -> PredictionJob:
        job = self.jobs[job_id]
        job.status = "processing"
        job.attempts = attempts
        return job

    async def mark_completed(
        self,
        job_id: uuid.UUID,
        *,
        prediction_record_id: uuid.UUID,
        result: dict[str, Any],
        attempts: int,
    ) -> PredictionJob:
        job = self.jobs[job_id]
        job.status = "completed"
        job.prediction_record_id = prediction_record_id
        job.result = result
        job.attempts = attempts
        return job

    async def mark_retrying(
        self,
        job_id: uuid.UUID,
        *,
        attempts: int,
        error: str,
    ) -> PredictionJob:
        job = self.jobs[job_id]
        job.status = "retrying"
        job.attempts = attempts
        job.last_error = error
        return job

    async def mark_failed(
        self,
        job_id: uuid.UUID,
        *,
        attempts: int,
        error: str,
    ) -> PredictionJob:
        job = self.jobs[job_id]
        job.status = "failed"
        job.attempts = attempts
        job.last_error = error
        return job

    async def count_by_status(self) -> dict[str, int]:
        return self.status_counts

    async def recent_jobs(self) -> list[PredictionJob]:
        return list(self.jobs.values())


class FakeQueueClient:
    def __init__(self) -> None:
        self.enqueued: list[dict[str, Any]] = []

    async def enqueue_prediction(self, **kwargs: Any) -> EnqueuedPrediction:
        self.enqueued.append(kwargs)
        return EnqueuedPrediction(
            bullmq_job_id=f"bullmq-{kwargs['job_id']}",
            queue_name="prediction-processing",
        )


def _service(
    repo: FakeJobRepository,
    queue_client: FakeQueueClient | None = None,
) -> PredictionJobService:
    service = PredictionJobService(object(), queue_client=queue_client or FakeQueueClient())  # type: ignore[arg-type]
    service._jobs = repo  # type: ignore[assignment]
    return service


def test_queue_creation_persists_job_and_enqueues_bullmq_job() -> None:
    repo = FakeJobRepository()
    queue_client = FakeQueueClient()
    service = _service(repo, queue_client)
    profile_id = uuid.uuid4()

    job = asyncio.run(service.enqueue_prediction(student_profile_id=profile_id))

    assert job.student_profile_id == profile_id
    assert job.status == "pending"
    assert job.bullmq_job_id == f"bullmq-{job.id}"
    assert queue_client.enqueued[0]["job_id"] == job.id


def test_batch_jobs_share_batch_id_and_enqueue_each_job() -> None:
    repo = FakeJobRepository()
    queue_client = FakeQueueClient()
    service = _service(repo, queue_client)

    result = asyncio.run(
        service.enqueue_batch(
            [
                type("Request", (), {"student_profile_id": uuid.uuid4(), "feature_snapshot_id": None})(),
                type("Request", (), {"student_profile_id": uuid.uuid4(), "feature_snapshot_id": None})(),
            ]
        )
    )

    assert len(result["jobs"]) == 2
    assert result["jobs"][0]["batch_id"] == result["batch_id"]
    assert result["jobs"][1]["batch_id"] == result["batch_id"]
    assert len(queue_client.enqueued) == 2


def test_worker_execution_marks_completed_and_stores_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.services import prediction_job_service as module

    repo = FakeJobRepository()
    job = _job()
    repo.jobs[job.id] = job
    service = _service(repo)
    prediction_id = uuid.uuid4()
    snapshot_id = uuid.uuid4()

    class FakePredictionService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def predict_for_snapshot(
            self,
            student_profile_id: uuid.UUID,
            *,
            job_id: uuid.UUID,
            inference_source: str,
        ) -> PredictionResult:
            assert job_id == job.id
            assert inference_source == "async"
            return PredictionResult(
                student_profile_id=student_profile_id,
                feature_snapshot_id=snapshot_id,
                prediction_id=prediction_id,
                model_version_id=None,
                risks={
                    "income_risk": 0.1,
                    "caste_risk": 0.2,
                    "transaction_risk": 0.3,
                    "medical_risk": 0.4,
                    "final_risk": 0.65,
                },
                risk_level="HIGH",
                prediction_duration_ms=9,
                explanation={"summary": "test"},
            )

    monkeypatch.setattr(module, "PredictionService", FakePredictionService)

    result = asyncio.run(service.execute_job(job.id, attempt=1))

    assert repo.jobs[job.id].status == "completed"
    assert repo.jobs[job.id].prediction_record_id == prediction_id
    assert result["risk_level"] == "HIGH"
    assert result["prediction_duration_ms"] == 9


def test_worker_failure_marks_failed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.services import prediction_job_service as module

    repo = FakeJobRepository()
    job = _job()
    repo.jobs[job.id] = job
    service = _service(repo)

    class FailingPredictionService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def predict_for_snapshot(self, *args: Any, **kwargs: Any) -> PredictionResult:
            raise RuntimeError("boom")

    monkeypatch.setattr(module, "PredictionService", FailingPredictionService)

    with pytest.raises(RuntimeError):
        asyncio.run(service.execute_job(job.id, attempt=3))

    assert repo.jobs[job.id].status == "failed"
    assert repo.jobs[job.id].attempts == 3
    assert repo.jobs[job.id].last_error == "boom"


def test_retry_status_records_attempt_and_error() -> None:
    repo = FakeJobRepository()
    job = _job()
    repo.jobs[job.id] = job
    service = _service(repo)

    updated = asyncio.run(service.mark_retrying(job.id, attempt=2, error="temporary"))

    assert updated.status == "retrying"
    assert updated.attempts == 2
    assert updated.last_error == "temporary"


def test_queue_analytics_includes_status_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.services import prediction_job_service as module

    repo = FakeJobRepository()
    repo.jobs[uuid.uuid4()] = _job(status="completed")
    service = _service(repo)

    class FakeAnalytics:
        def __init__(self, session: object) -> None:
            self.session = session

        async def get_operational_metrics(self) -> dict[str, Any]:
            return {"total_predictions": 2}

    monkeypatch.setattr(module, "PredictionAnalyticsService", FakeAnalytics)

    analytics = asyncio.run(service.get_queue_analytics())

    assert analytics["total_jobs"] == 6
    assert analytics["pending"] == 1
    assert analytics["processing"] == 1
    assert analytics["completed"] == 2
    assert analytics["failed"] == 1
    assert analytics["retrying"] == 1
    assert analytics["success_rate"] == 33.33


def test_queue_endpoints_return_job_status_and_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src import app as app_module

    job = _job(status="completed", result={"prediction_id": str(uuid.uuid4())})

    @asynccontextmanager
    async def fake_db_session() -> AsyncIterator[object]:
        yield object()

    class FakeJobService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def get_job(self, job_id: uuid.UUID) -> PredictionJob:
            assert job_id == job.id
            return job

    monkeypatch.setattr(app_module, "get_db_session", fake_db_session)
    monkeypatch.setattr(app_module, "PredictionJobService", FakeJobService)

    status_response = asyncio.run(app_module.get_prediction_job(job.id))
    result_response = asyncio.run(app_module.get_prediction_job_result(job.id))

    assert status_response["data"]["status"] == "completed"
    assert result_response == {"success": True, "data": job.result}
