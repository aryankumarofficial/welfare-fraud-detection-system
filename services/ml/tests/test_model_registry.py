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

from src.db.models.model_evaluation_run import ModelEvaluationRun
from src.db.models.model_lineage_event import ModelLineageEvent
from src.db.models.model_version import ModelVersion


# ── Helpers ──────────────────────────────────────────────────────────────


def _now() -> datetime:
    return datetime.now(UTC)


def _model_version(
    *,
    model_id: uuid.UUID | None = None,
    name: str = "isolation_forest",
    version: str = "v1",
    status: str = "DRAFT",
    role: str = "none",
    is_active: bool = False,
    deployed_at: datetime | None = None,
    promoted_at: datetime | None = None,
    promoted_by: str | None = None,
) -> ModelVersion:
    return ModelVersion(
        id=model_id or uuid.uuid4(),
        name=name,
        version=version,
        description=None,
        artifact_uri=None,
        artifact_hash=None,
        configuration=None,
        training_metadata=None,
        feature_schema_version=None,
        parent_model_id=None,
        is_active=is_active,
        status=status,
        role=role,
        deployed_at=deployed_at,
        promoted_at=promoted_at,
        promoted_by=promoted_by,
        rolled_back_at=None,
        created_at=_now(),
    )


def _eval_run(
    *,
    model_version_id: uuid.UUID,
    precision: float = 0.92,
    recall: float = 0.88,
    f1_score: float = 0.90,
    false_positive_rate: float = 0.08,
) -> ModelEvaluationRun:
    return ModelEvaluationRun(
        id=uuid.uuid4(),
        model_version_id=model_version_id,
        dataset_name="welfare_test_set",
        dataset_version="v1",
        sample_size=1000,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        false_positive_rate=false_positive_rate,
        additional_metrics=None,
        evaluated_by="test_user",
        evaluated_at=_now(),
        created_at=_now(),
    )


# ── Fake Repositories ───────────────────────────────────────────────────


class FakeModelRepository:
    def __init__(self) -> None:
        self.models: dict[uuid.UUID, ModelVersion] = {}

    async def get_by_id(self, model_id: uuid.UUID) -> ModelVersion | None:
        return self.models.get(model_id)

    async def get_active(self) -> ModelVersion | None:
        for m in self.models.values():
            if m.is_active:
                return m
        return None

    async def get_champion(self) -> ModelVersion | None:
        for m in self.models.values():
            if m.role == "champion" and m.status == "PRODUCTION":
                return m
        return await self.get_active()

    async def list_filtered(
        self,
        *,
        status: str | None = None,
        role: str | None = None,
        limit: int = 100,
    ) -> list[ModelVersion]:
        result = list(self.models.values())
        if status:
            result = [m for m in result if m.status == status]
        if role:
            result = [m for m in result if m.role == role]
        return result[:limit]

    async def create_model(self, **kwargs: Any) -> ModelVersion:
        model = ModelVersion(
            id=uuid.uuid4(),
            name=kwargs["name"],
            version=kwargs["version"],
            description=kwargs.get("description"),
            artifact_uri=kwargs.get("artifact_uri"),
            artifact_hash=kwargs.get("artifact_hash"),
            configuration=kwargs.get("configuration"),
            training_metadata=kwargs.get("training_metadata"),
            feature_schema_version=kwargs.get("feature_schema_version"),
            parent_model_id=kwargs.get("parent_model_id"),
            is_active=False,
            status="DRAFT",
            role="none",
            deployed_at=None,
            promoted_at=None,
            promoted_by=None,
            rolled_back_at=None,
            created_at=_now(),
        )
        self.models[model.id] = model
        return model

    async def update_status(self, model_id: uuid.UUID, status: str) -> ModelVersion | None:
        model = self.models.get(model_id)
        if model:
            model.status = status
        return model

    async def update_role(self, model_id: uuid.UUID, role: str) -> ModelVersion | None:
        model = self.models.get(model_id)
        if model:
            model.role = role
        return model

    async def promote_to_champion(
        self,
        model_id: uuid.UUID,
        *,
        promoted_by: str | None = None,
    ) -> tuple[ModelVersion | None, ModelVersion | None]:
        model = self.models.get(model_id)
        if model is None:
            return None, None

        demoted = None
        for m in self.models.values():
            if m.role == "champion" and m.id != model_id:
                m.status = "STAGING"
                m.role = "none"
                m.is_active = False
                demoted = m

        now = _now()
        model.status = "PRODUCTION"
        model.role = "champion"
        model.is_active = True
        model.deployed_at = now
        model.promoted_at = now
        model.promoted_by = promoted_by
        return model, demoted

    async def rollback_champion(
        self,
        model_id: uuid.UUID,
        *,
        previous_champion_id: uuid.UUID | None = None,
    ) -> tuple[ModelVersion | None, ModelVersion | None]:
        model = self.models.get(model_id)
        if model is None:
            return None, None
        model.status = "ROLLED_BACK"
        model.role = "none"
        model.is_active = False
        model.rolled_back_at = _now()

        restored = None
        if previous_champion_id and previous_champion_id in self.models:
            restored = self.models[previous_champion_id]
            restored.status = "PRODUCTION"
            restored.role = "champion"
            restored.is_active = True
        return model, restored


class FakeEvaluationRunRepository:
    def __init__(self) -> None:
        self.runs: list[ModelEvaluationRun] = []

    async def create_run(self, **kwargs: Any) -> ModelEvaluationRun:
        run = ModelEvaluationRun(
            id=uuid.uuid4(),
            model_version_id=kwargs["model_version_id"],
            dataset_name=kwargs["dataset_name"],
            dataset_version=kwargs.get("dataset_version"),
            sample_size=kwargs["sample_size"],
            precision=kwargs["precision"],
            recall=kwargs["recall"],
            f1_score=kwargs["f1_score"],
            false_positive_rate=kwargs["false_positive_rate"],
            additional_metrics=kwargs.get("additional_metrics"),
            evaluated_by=kwargs.get("evaluated_by"),
            evaluated_at=_now(),
            created_at=_now(),
        )
        self.runs.append(run)
        return run

    async def list_by_model_version_id(
        self,
        model_version_id: uuid.UUID,
        *,
        limit: int = 50,
    ) -> list[ModelEvaluationRun]:
        return [r for r in self.runs if r.model_version_id == model_version_id][:limit]

    async def get_latest_by_model_version_id(
        self,
        model_version_id: uuid.UUID,
    ) -> ModelEvaluationRun | None:
        runs = [r for r in self.runs if r.model_version_id == model_version_id]
        return runs[-1] if runs else None


class FakeLineageEventRepository:
    def __init__(self) -> None:
        self.events: list[ModelLineageEvent] = []

    async def create_event(self, **kwargs: Any) -> ModelLineageEvent:
        event = ModelLineageEvent(
            id=uuid.uuid4(),
            model_version_id=kwargs["model_version_id"],
            event_type=kwargs["event_type"],
            from_status=kwargs.get("from_status"),
            to_status=kwargs.get("to_status"),
            from_role=kwargs.get("from_role"),
            to_role=kwargs.get("to_role"),
            metadata_json=kwargs.get("metadata"),
            performed_by=kwargs.get("performed_by"),
            created_at=_now(),
        )
        self.events.append(event)
        return event

    async def list_by_model_version_id(
        self,
        model_version_id: uuid.UUID,
        *,
        limit: int = 100,
    ) -> list[ModelLineageEvent]:
        return [e for e in self.events if e.model_version_id == model_version_id][:limit]

    async def get_previous_champion_model_id(
        self,
        current_champion_id: uuid.UUID,
    ) -> uuid.UUID | None:
        for event in reversed(self.events):
            if event.event_type == "demoted" and event.from_role == "champion":
                return event.model_version_id
        return None


class FakeAuditLogRepository:
    def __init__(self) -> None:
        self.logs: list[dict[str, Any]] = []

    async def create_audit_log(self, **kwargs: Any) -> None:
        self.logs.append(kwargs)


# ── Service Factory ──────────────────────────────────────────────────────


def _registry_service() -> tuple:
    from src.services.model_registry_service import ModelRegistryService

    service = ModelRegistryService(object())  # type: ignore[arg-type]
    models = FakeModelRepository()
    evals = FakeEvaluationRunRepository()
    lineage = FakeLineageEventRepository()
    audit = FakeAuditLogRepository()
    service._models = models  # type: ignore[assignment]
    service._evaluations = evals  # type: ignore[assignment]
    service._lineage = lineage  # type: ignore[assignment]
    service._audit = audit  # type: ignore[assignment]
    return service, models, evals, lineage, audit


# ── Tests ────────────────────────────────────────────────────────────────


def test_register_model_creates_draft_with_lineage() -> None:
    service, models, evals, lineage, audit = _registry_service()

    result = asyncio.run(
        service.register_model(
            name="isolation_forest",
            version="v2",
            description="New model",
        )
    )

    assert result["status"] == "DRAFT"
    assert result["role"] == "none"
    assert result["name"] == "isolation_forest"
    assert result["version"] == "v2"

    assert len(lineage.events) == 1
    assert lineage.events[0].event_type == "created"
    assert lineage.events[0].to_status == "DRAFT"

    assert len(audit.logs) == 1
    assert audit.logs[0]["action"] == "model.registered"


def test_evaluation_run_auto_transitions_draft_to_validated() -> None:
    service, models, evals, lineage, audit = _registry_service()

    model = asyncio.run(service.register_model(name="if", version="v1"))
    model_id = uuid.UUID(model["model_version_id"])

    eval_result = asyncio.run(
        service.create_evaluation_run(
            model_id,
            dataset_name="test_set",
            sample_size=500,
            precision=0.90,
            recall=0.85,
            f1_score=0.87,
            false_positive_rate=0.10,
        )
    )

    assert eval_result["precision"] == 0.90
    assert eval_result["f1_score"] == 0.87

    # Model should be auto-transitioned to VALIDATED
    model_obj = models.models[model_id]
    assert model_obj.status == "VALIDATED"

    # Lineage events: created, validated, evaluated
    event_types = [e.event_type for e in lineage.events]
    assert "created" in event_types
    assert "validated" in event_types
    assert "evaluated" in event_types


def test_promote_model_transitions_to_champion() -> None:
    service, models, evals, lineage, audit = _registry_service()

    model = asyncio.run(service.register_model(name="if", version="v1"))
    model_id = uuid.UUID(model["model_version_id"])
    models.models[model_id].status = "VALIDATED"

    result = asyncio.run(service.promote_model(model_id, promoted_by="admin"))

    assert result["status"] == "PRODUCTION"
    assert result["role"] == "champion"
    assert result["is_active"] is True

    promoted_events = [e for e in lineage.events if e.event_type == "promoted"]
    assert len(promoted_events) == 1
    assert promoted_events[0].from_status == "VALIDATED"
    assert promoted_events[0].to_status == "PRODUCTION"


def test_promote_demotes_existing_champion() -> None:
    service, models, evals, lineage, audit = _registry_service()

    # Register and promote first model
    m1 = asyncio.run(service.register_model(name="if", version="v1"))
    m1_id = uuid.UUID(m1["model_version_id"])
    models.models[m1_id].status = "VALIDATED"
    asyncio.run(service.promote_model(m1_id, promoted_by="admin"))

    # Register and promote second model
    m2 = asyncio.run(service.register_model(name="if", version="v2"))
    m2_id = uuid.UUID(m2["model_version_id"])
    models.models[m2_id].status = "VALIDATED"
    asyncio.run(service.promote_model(m2_id, promoted_by="admin"))

    # First model should be demoted to STAGING
    assert models.models[m1_id].status == "STAGING"
    assert models.models[m1_id].role == "none"
    assert models.models[m1_id].is_active is False

    # Second model should be champion
    assert models.models[m2_id].status == "PRODUCTION"
    assert models.models[m2_id].role == "champion"
    assert models.models[m2_id].is_active is True

    demoted_events = [e for e in lineage.events if e.event_type == "demoted"]
    assert len(demoted_events) == 1
    assert demoted_events[0].model_version_id == m1_id


def test_promote_non_validated_model_raises_value_error() -> None:
    service, models, evals, lineage, audit = _registry_service()

    model = asyncio.run(service.register_model(name="if", version="v1"))
    model_id = uuid.UUID(model["model_version_id"])

    with pytest.raises(ValueError, match="VALIDATED"):
        asyncio.run(service.promote_model(model_id))


def test_promote_nonexistent_model_raises_lookup_error() -> None:
    service, models, evals, lineage, audit = _registry_service()

    with pytest.raises(LookupError):
        asyncio.run(service.promote_model(uuid.uuid4()))


def test_rollback_champion_restores_previous() -> None:
    service, models, evals, lineage, audit = _registry_service()

    # Create and promote two models
    m1 = asyncio.run(service.register_model(name="if", version="v1"))
    m1_id = uuid.UUID(m1["model_version_id"])
    models.models[m1_id].status = "VALIDATED"
    asyncio.run(service.promote_model(m1_id))

    m2 = asyncio.run(service.register_model(name="if", version="v2"))
    m2_id = uuid.UUID(m2["model_version_id"])
    models.models[m2_id].status = "VALIDATED"
    asyncio.run(service.promote_model(m2_id))

    # Rollback m2
    result = asyncio.run(
        service.rollback_model(m2_id, reason="Performance degradation")
    )

    assert result["rolled_back"]["status"] == "ROLLED_BACK"
    assert result["rolled_back"]["role"] == "none"
    assert result["restored"]["status"] == "PRODUCTION"
    assert result["restored"]["role"] == "champion"

    rollback_events = [e for e in lineage.events if e.event_type == "rolled_back"]
    assert len(rollback_events) == 1
    restored_events = [e for e in lineage.events if e.event_type == "restored"]
    assert len(restored_events) == 1


def test_rollback_non_champion_raises_value_error() -> None:
    service, models, evals, lineage, audit = _registry_service()

    model = asyncio.run(service.register_model(name="if", version="v1"))
    model_id = uuid.UUID(model["model_version_id"])

    with pytest.raises(ValueError, match="champion"):
        asyncio.run(service.rollback_model(model_id))


def test_archive_model_sets_archived_status() -> None:
    service, models, evals, lineage, audit = _registry_service()

    model = asyncio.run(service.register_model(name="if", version="v1"))
    model_id = uuid.UUID(model["model_version_id"])

    result = asyncio.run(service.archive_model(model_id, performed_by="admin"))

    assert result["status"] == "ARCHIVED"
    archived_events = [e for e in lineage.events if e.event_type == "archived"]
    assert len(archived_events) == 1


def test_archive_champion_raises_value_error() -> None:
    service, models, evals, lineage, audit = _registry_service()

    model = asyncio.run(service.register_model(name="if", version="v1"))
    model_id = uuid.UUID(model["model_version_id"])
    models.models[model_id].status = "VALIDATED"
    asyncio.run(service.promote_model(model_id))

    with pytest.raises(ValueError, match="champion"):
        asyncio.run(service.archive_model(model_id))


def test_list_models_filters_by_status_and_role() -> None:
    service, models, evals, lineage, audit = _registry_service()

    asyncio.run(service.register_model(name="if", version="v1"))
    m2 = asyncio.run(service.register_model(name="if", version="v2"))
    m2_id = uuid.UUID(m2["model_version_id"])
    models.models[m2_id].status = "VALIDATED"

    all_models = asyncio.run(service.list_models())
    assert len(all_models) == 2

    draft_models = asyncio.run(service.list_models(status="DRAFT"))
    assert len(draft_models) == 1

    validated_models = asyncio.run(service.list_models(status="VALIDATED"))
    assert len(validated_models) == 1


def test_get_model_includes_evaluation_runs_and_lineage() -> None:
    service, models, evals, lineage, audit = _registry_service()

    model = asyncio.run(service.register_model(name="if", version="v1"))
    model_id = uuid.UUID(model["model_version_id"])

    asyncio.run(
        service.create_evaluation_run(
            model_id,
            dataset_name="test_set",
            sample_size=500,
            precision=0.90,
            recall=0.85,
            f1_score=0.87,
            false_positive_rate=0.10,
        )
    )

    detail = asyncio.run(service.get_model(model_id))

    assert detail is not None
    assert detail["name"] == "if"
    assert len(detail["evaluation_runs"]) == 1
    assert detail["evaluation_runs"][0]["precision"] == 0.90
    assert len(detail["lineage_events"]) >= 2  # created, validated, evaluated


def test_compare_models_returns_multiple_models_with_evaluations() -> None:
    service, models, evals, lineage, audit = _registry_service()

    m1 = asyncio.run(service.register_model(name="if", version="v1"))
    m1_id = uuid.UUID(m1["model_version_id"])
    asyncio.run(
        service.create_evaluation_run(
            m1_id,
            dataset_name="set_a",
            sample_size=500,
            precision=0.85,
            recall=0.80,
            f1_score=0.82,
            false_positive_rate=0.15,
        )
    )

    m2 = asyncio.run(service.register_model(name="if", version="v2"))
    m2_id = uuid.UUID(m2["model_version_id"])
    asyncio.run(
        service.create_evaluation_run(
            m2_id,
            dataset_name="set_a",
            sample_size=500,
            precision=0.92,
            recall=0.88,
            f1_score=0.90,
            false_positive_rate=0.08,
        )
    )

    comparison = asyncio.run(service.compare_models([m1_id, m2_id]))

    assert len(comparison) == 2
    assert comparison[0]["latest_evaluation"]["precision"] == 0.85
    assert comparison[1]["latest_evaluation"]["precision"] == 0.92


def test_champion_model_used_for_prediction_backward_compat() -> None:
    """Verify that get_champion() falls back to get_active() for backward compatibility."""
    from src.repositories.model_repository import ModelRepository

    repo = FakeModelRepository()

    # No champion set, but is_active model exists
    legacy_model = _model_version(is_active=True, status="DRAFT")
    repo.models[legacy_model.id] = legacy_model

    result = asyncio.run(repo.get_champion())
    assert result is not None
    assert result.id == legacy_model.id
    assert result.is_active is True


def test_champion_overrides_legacy_active() -> None:
    from src.repositories.model_repository import ModelRepository

    repo = FakeModelRepository()

    legacy = _model_version(is_active=True, status="DRAFT")
    repo.models[legacy.id] = legacy

    champion = _model_version(
        is_active=True, status="PRODUCTION", role="champion"
    )
    repo.models[champion.id] = champion

    result = asyncio.run(repo.get_champion())
    assert result is not None
    assert result.id == champion.id
    assert result.role == "champion"


def test_model_registry_endpoint_routes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that model registry API endpoints integrate correctly."""
    from src import app as app_module

    @asynccontextmanager
    async def fake_db_session() -> AsyncIterator[object]:
        yield object()

    class FakeRegistryService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def list_models(self, **kwargs: Any) -> list[dict[str, Any]]:
            return [{"model_version_id": str(uuid.uuid4()), "name": "if", "version": "v1"}]

        async def get_model(self, model_id: uuid.UUID) -> dict[str, Any] | None:
            return {"model_version_id": str(model_id), "name": "if"}

        async def register_model(self, **kwargs: Any) -> dict[str, Any]:
            return {"model_version_id": str(uuid.uuid4()), "name": kwargs["name"], "status": "DRAFT"}

    class FakeHealthService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def get_model_health(self) -> dict[str, Any]:
            return {"champion": None, "total_registered_models": 0}

    monkeypatch.setattr(app_module, "get_db_session", fake_db_session)
    monkeypatch.setattr(app_module, "ModelRegistryService", FakeRegistryService)
    monkeypatch.setattr(app_module, "ModelHealthService", FakeHealthService)

    # List models
    result = asyncio.run(app_module.list_models())
    assert result["success"] is True
    assert len(result["data"]) == 1

    # Get model
    model_id = uuid.uuid4()
    result = asyncio.run(app_module.get_model(model_id))
    assert result["success"] is True
    assert result["data"]["model_version_id"] == str(model_id)

    # Register model
    body = app_module.RegisterModelBody(name="if", version="v3")
    result = asyncio.run(app_module.register_model(body))
    assert result["success"] is True
    assert result["data"]["status"] == "DRAFT"

    # Model health
    result = asyncio.run(app_module.get_model_health())
    assert result["total_registered_models"] == 0
