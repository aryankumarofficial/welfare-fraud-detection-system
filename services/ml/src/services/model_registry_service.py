import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.model_evaluation_run import ModelEvaluationRun
from src.db.models.model_lineage_event import ModelLineageEvent
from src.db.models.model_version import ModelVersion
from src.repositories.audit_log_repository import AuditLogRepository
from src.repositories.model_evaluation_run_repository import ModelEvaluationRunRepository
from src.repositories.model_lineage_event_repository import ModelLineageEventRepository
from src.repositories.model_repository import ModelRepository


PROMOTABLE_STATUSES = ("VALIDATED", "STAGING")


class ModelRegistryService:
    """
    Orchestrates the full model lifecycle: registration, promotion,
    rollback, evaluation, lineage tracking, and comparison.

    Does NOT perform model training, artifact upload, or model serving.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._models = ModelRepository(session)
        self._evaluations = ModelEvaluationRunRepository(session)
        self._lineage = ModelLineageEventRepository(session)
        self._audit = AuditLogRepository(session)

    # ── Listing ──────────────────────────────────────────────────────

    async def list_models(
        self,
        *,
        status: str | None = None,
        role: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        models = await self._models.list_filtered(
            status=status,
            role=role,
            limit=limit,
        )
        return [_serialize_model(m) for m in models]

    async def get_model(self, model_id: uuid.UUID) -> dict[str, Any] | None:
        model = await self._models.get_by_id(model_id)
        if model is None:
            return None
        eval_runs = await self._evaluations.list_by_model_version_id(model_id)
        lineage = await self._lineage.list_by_model_version_id(model_id)
        result = _serialize_model(model)
        result["evaluation_runs"] = [_serialize_evaluation_run(r) for r in eval_runs]
        result["lineage_events"] = [_serialize_lineage_event(e) for e in lineage]
        return result

    # ── Registration ─────────────────────────────────────────────────

    async def register_model(
        self,
        *,
        name: str,
        version: str,
        description: str | None = None,
        artifact_uri: str | None = None,
        artifact_hash: str | None = None,
        configuration: dict | None = None,
        training_metadata: dict | None = None,
        feature_schema_version: str | None = None,
        parent_model_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        model = await self._models.create_model(
            name=name,
            version=version,
            description=description,
            artifact_uri=artifact_uri,
            artifact_hash=artifact_hash,
            configuration=configuration,
            training_metadata=training_metadata,
            feature_schema_version=feature_schema_version,
            parent_model_id=parent_model_id,
        )
        await self._lineage.create_event(
            model_version_id=model.id,
            event_type="created",
            to_status="DRAFT",
            to_role="none",
        )
        await self._audit.create_audit_log(
            action="model.registered",
            resource_type="model_version",
            resource_id=str(model.id),
            metadata={
                "name": name,
                "version": version,
                "status": "DRAFT",
            },
        )
        return _serialize_model(model)

    # ── Promotion ────────────────────────────────────────────────────

    async def promote_model(
        self,
        model_id: uuid.UUID,
        *,
        promoted_by: str | None = None,
    ) -> dict[str, Any]:
        model = await self._models.get_by_id(model_id)
        if model is None:
            raise LookupError("Model not found.")
        if model.status not in PROMOTABLE_STATUSES:
            raise ValueError(
                f"Model must be in {PROMOTABLE_STATUSES} to be promoted, "
                f"but current status is '{model.status}'."
            )

        old_status = model.status
        promoted, demoted = await self._models.promote_to_champion(
            model_id,
            promoted_by=promoted_by,
        )

        # Record lineage for promoted model
        await self._lineage.create_event(
            model_version_id=model_id,
            event_type="promoted",
            from_status=old_status,
            to_status="PRODUCTION",
            from_role=model.role,
            to_role="champion",
            performed_by=promoted_by,
            metadata={"demoted_model_id": str(demoted.id) if demoted else None},
        )

        # Record lineage for demoted model
        if demoted is not None:
            await self._lineage.create_event(
                model_version_id=demoted.id,
                event_type="demoted",
                from_status="PRODUCTION",
                to_status="STAGING",
                from_role="champion",
                to_role="none",
                performed_by=promoted_by,
                metadata={"promoted_model_id": str(model_id)},
            )

        await self._audit.create_audit_log(
            action="model.promoted",
            resource_type="model_version",
            resource_id=str(model_id),
            metadata={
                "promoted_by": promoted_by,
                "from_status": old_status,
                "demoted_model_id": str(demoted.id) if demoted else None,
            },
        )

        return _serialize_model(promoted)

    # ── Rollback ─────────────────────────────────────────────────────

    async def rollback_model(
        self,
        model_id: uuid.UUID,
        *,
        reason: str | None = None,
        performed_by: str | None = None,
    ) -> dict[str, Any]:
        model = await self._models.get_by_id(model_id)
        if model is None:
            raise LookupError("Model not found.")
        if model.role != "champion":
            raise ValueError("Only the current champion model can be rolled back.")

        # Find the previous champion from lineage
        previous_id = await self._lineage.get_previous_champion_model_id(model_id)

        rolled_back, restored = await self._models.rollback_champion(
            model_id,
            previous_champion_id=previous_id,
        )

        await self._lineage.create_event(
            model_version_id=model_id,
            event_type="rolled_back",
            from_status="PRODUCTION",
            to_status="ROLLED_BACK",
            from_role="champion",
            to_role="none",
            performed_by=performed_by,
            metadata={
                "reason": reason,
                "restored_model_id": str(restored.id) if restored else None,
            },
        )

        if restored is not None:
            await self._lineage.create_event(
                model_version_id=restored.id,
                event_type="restored",
                from_status="STAGING",
                to_status="PRODUCTION",
                from_role="none",
                to_role="champion",
                performed_by=performed_by,
                metadata={"rolled_back_model_id": str(model_id)},
            )

        await self._audit.create_audit_log(
            action="model.rolled_back",
            resource_type="model_version",
            resource_id=str(model_id),
            metadata={
                "reason": reason,
                "performed_by": performed_by,
                "restored_model_id": str(restored.id) if restored else None,
            },
        )

        return {
            "rolled_back": _serialize_model(rolled_back),
            "restored": _serialize_model(restored) if restored else None,
        }

    # ── Archival ──────────────────────────────────────────────────────

    async def archive_model(
        self,
        model_id: uuid.UUID,
        *,
        performed_by: str | None = None,
    ) -> dict[str, Any]:
        model = await self._models.get_by_id(model_id)
        if model is None:
            raise LookupError("Model not found.")
        if model.role == "champion":
            raise ValueError("Cannot archive the current champion model. Rollback first.")

        old_status = model.status
        model = await self._models.update_status(model_id, "ARCHIVED")
        await self._models.update_role(model_id, "none")

        await self._lineage.create_event(
            model_version_id=model_id,
            event_type="archived",
            from_status=old_status,
            to_status="ARCHIVED",
            performed_by=performed_by,
        )

        await self._audit.create_audit_log(
            action="model.archived",
            resource_type="model_version",
            resource_id=str(model_id),
            metadata={"from_status": old_status, "performed_by": performed_by},
        )

        return _serialize_model(model)

    # ── Evaluation ───────────────────────────────────────────────────

    async def create_evaluation_run(
        self,
        model_id: uuid.UUID,
        *,
        dataset_name: str,
        dataset_version: str | None = None,
        sample_size: int,
        precision: float,
        recall: float,
        f1_score: float,
        false_positive_rate: float,
        additional_metrics: dict | None = None,
        evaluated_by: str | None = None,
    ) -> dict[str, Any]:
        model = await self._models.get_by_id(model_id)
        if model is None:
            raise LookupError("Model not found.")

        run = await self._evaluations.create_run(
            model_version_id=model_id,
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            sample_size=sample_size,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            false_positive_rate=false_positive_rate,
            additional_metrics=additional_metrics,
            evaluated_by=evaluated_by,
        )

        # Auto-transition DRAFT → VALIDATED on first evaluation
        if model.status == "DRAFT":
            old_status = model.status
            await self._models.update_status(model_id, "VALIDATED")
            await self._lineage.create_event(
                model_version_id=model_id,
                event_type="validated",
                from_status=old_status,
                to_status="VALIDATED",
                metadata={"evaluation_run_id": str(run.id)},
            )

        await self._lineage.create_event(
            model_version_id=model_id,
            event_type="evaluated",
            metadata={
                "evaluation_run_id": str(run.id),
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "false_positive_rate": false_positive_rate,
            },
        )

        await self._audit.create_audit_log(
            action="model.evaluated",
            resource_type="model_evaluation_run",
            resource_id=str(run.id),
            metadata={
                "model_version_id": str(model_id),
                "dataset_name": dataset_name,
                "sample_size": sample_size,
                "precision": precision,
                "f1_score": f1_score,
            },
        )

        return _serialize_evaluation_run(run)

    # ── Comparison ───────────────────────────────────────────────────

    async def compare_models(
        self,
        model_ids: list[uuid.UUID],
    ) -> list[dict[str, Any]]:
        results = []
        for model_id in model_ids:
            model = await self._models.get_by_id(model_id)
            if model is None:
                continue
            latest_eval = await self._evaluations.get_latest_by_model_version_id(model_id)
            data = _serialize_model(model)
            data["latest_evaluation"] = (
                _serialize_evaluation_run(latest_eval) if latest_eval else None
            )
            results.append(data)
        return results


# ── Serialization ────────────────────────────────────────────────────


def _serialize_model(model: ModelVersion) -> dict[str, Any]:
    return {
        "model_version_id": str(model.id),
        "name": model.name,
        "version": model.version,
        "description": model.description,
        "artifact_uri": model.artifact_uri,
        "artifact_hash": model.artifact_hash,
        "configuration": model.configuration,
        "training_metadata": model.training_metadata,
        "feature_schema_version": model.feature_schema_version,
        "status": model.status,
        "role": model.role,
        "is_active": model.is_active,
        "parent_model_id": str(model.parent_model_id) if model.parent_model_id else None,
        "deployed_at": _dt(model.deployed_at),
        "promoted_at": _dt(model.promoted_at),
        "promoted_by": model.promoted_by,
        "rolled_back_at": _dt(model.rolled_back_at),
        "created_at": _dt(model.created_at),
    }


def _serialize_evaluation_run(run: ModelEvaluationRun) -> dict[str, Any]:
    return {
        "evaluation_run_id": str(run.id),
        "model_version_id": str(run.model_version_id),
        "dataset_name": run.dataset_name,
        "dataset_version": run.dataset_version,
        "sample_size": run.sample_size,
        "precision": run.precision,
        "recall": run.recall,
        "f1_score": run.f1_score,
        "false_positive_rate": run.false_positive_rate,
        "additional_metrics": run.additional_metrics,
        "evaluated_by": run.evaluated_by,
        "evaluated_at": _dt(run.evaluated_at),
        "created_at": _dt(run.created_at),
    }


def _serialize_lineage_event(event: ModelLineageEvent) -> dict[str, Any]:
    return {
        "lineage_event_id": str(event.id),
        "model_version_id": str(event.model_version_id),
        "event_type": event.event_type,
        "from_status": event.from_status,
        "to_status": event.to_status,
        "from_role": event.from_role,
        "to_role": event.to_role,
        "metadata": event.metadata_json,
        "performed_by": event.performed_by,
        "created_at": _dt(event.created_at),
    }


def _dt(value: Any) -> str | None:
    return value.isoformat() if value is not None else None
