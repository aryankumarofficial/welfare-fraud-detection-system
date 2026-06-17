import uuid
from datetime import UTC, datetime

from sqlalchemy import desc, select

from src.db.models.prediction_review import PredictionReview
from src.db.repositories.base import AsyncRepository


class PredictionReviewRepository(AsyncRepository[PredictionReview]):
    model = PredictionReview

    async def create_review(
        self,
        *,
        prediction_id: uuid.UUID,
        reviewer: str,
        decision: str,
        notes: str | None = None,
    ) -> PredictionReview:
        review = PredictionReview(
            id=uuid.uuid4(),
            prediction_id=prediction_id,
            reviewer=reviewer,
            decision=decision,
            notes=notes,
            created_at=datetime.now(UTC),
        )
        return await self.add(review)

    async def list_reviews(
        self,
        *,
        decision: str | None = None,
        limit: int = 100,
    ) -> list[PredictionReview]:
        statement = select(PredictionReview).order_by(desc(PredictionReview.created_at)).limit(limit)
        if decision is not None:
            statement = statement.where(PredictionReview.decision == decision)
        result = await self.session.execute(statement)
        return list(result.scalars().all())
