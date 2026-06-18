import json
import logging
import time
import uuid
from typing import Any

from fastapi import Request

logger = logging.getLogger("welfare_fraud_ml")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


def redact_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    redacted = {}
    for key, value in payload.items():
        if key.lower() in {"income_in_rs", "caste", "father_caste", "student_profile_id", "external_id"}:
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted


async def log_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start = time.time()
    request.state.request_id = request_id
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)
    payload = {
        "event": "http_request",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
        "client_host": request.client.host if request.client else None,
    }
    logger.info(json.dumps(payload, default=str))
    response.headers["X-Request-ID"] = request_id
    return response


def log_event(event: str, **metadata: Any) -> None:
    payload = {"event": event, **metadata}
    logger.info(json.dumps(payload, default=str))
