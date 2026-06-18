import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, select

from src.db.models.model_evaluation_run import ModelEvaluationRun
from src.db.repositories.base import AsyncRepository


class ModelEvaluationRunRepository(AsyncRepository[ModelEvaluationRun]):
    model = ModelEvaluationRun

    async def create_run(
        self,
        *,
        model_version_id: uuid.UUID,
        dataset_name: str,
        dataset_version: str | None = None,
        sample_size: int,
        precision: float,
        recall: float,
        f1_score: float,
        false_positive_rate: float,
        additional_metrics: dict[str, Any] | None = None,
        evaluated_by: str | None = None,
    ) -> ModelEvaluationRun:
        now = datetime.now(UTC)
        run = ModelEvaluationRun(
            id=uuid.uuid4(),
            model_version_id=model_version_id,
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            sample_size=sample_size,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            false_positive_rate=false_positive_rate,
            additional_metrics=additional_metrics,
            evaluated_by=evaluated_by,
            evaluated_at=now,
            created_at=now,
        )
        return await self.add(run)

    async def list_by_model_version_id(
        self,
        model_version_id: uuid.UUID,
        *,
        limit: int = 50,
    ) -> list[ModelEvaluationRun]:
        statement = (
            select(ModelEvaluationRun)
            .where(ModelEvaluationRun.model_version_id == model_version_id)
            .order_by(desc(ModelEvaluationRun.evaluated_at))
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_latest_by_model_version_id(
        self,
        model_version_id: uuid.UUID,
    ) -> ModelEvaluationRun | None:
        runs = await self.list_by_model_version_id(model_version_id, limit=1)
        return runs[0] if runs else None
