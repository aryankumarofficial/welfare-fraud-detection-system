import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen
from uuid import UUID


@dataclass(frozen=True)
class EnqueuedPrediction:
    bullmq_job_id: str | None
    queue_name: str


class PredictionQueueClient:
    """HTTP bridge to the BullMQ enqueue service.

    The ML API owns durable prediction_jobs rows. A separate Node/BullMQ process owns
    Redis-backed scheduling and calls back into the ML API to execute each job.
    """

    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = (base_url or os.getenv("PREDICTION_QUEUE_API_URL") or "").rstrip("/")

    @property
    def enabled(self) -> bool:
        return bool(self._base_url)

    async def enqueue_prediction(
        self,
        *,
        job_id: UUID,
        student_profile_id: UUID,
        feature_snapshot_id: UUID | None,
        batch_id: UUID | None,
    ) -> EnqueuedPrediction:
        if not self.enabled:
            return EnqueuedPrediction(bullmq_job_id=None, queue_name="prediction-processing")

        payload = {
            "job_id": str(job_id),
            "student_profile_id": str(student_profile_id),
            "feature_snapshot_id": str(feature_snapshot_id) if feature_snapshot_id else None,
            "batch_id": str(batch_id) if batch_id else None,
        }
        response = await asyncio.to_thread(self._post_json, "/predictions/enqueue", payload)
        return EnqueuedPrediction(
            bullmq_job_id=response.get("bullmq_job_id"),
            queue_name=response.get("queue_name", "prediction-processing"),
        )

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(
            f"{self._base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except URLError as exc:
            raise RuntimeError("Failed to enqueue prediction job in BullMQ.") from exc
