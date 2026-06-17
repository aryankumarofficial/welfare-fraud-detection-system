from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.prediction_review import PREDICTION_REVIEW_DECISIONS, PredictionReview
from src.repositories.audit_log_repository import AuditLogRepository
from src.repositories.prediction_repository import PredictionRepository
from src.repositories.prediction_review_repository import PredictionReviewRepository


class PredictionReviewService:
    def __init__(self, session: AsyncSession) -> None:
        self._predictions = PredictionRepository(session)
        self._reviews = PredictionReviewRepository(session)
        self._audit = AuditLogRepository(session)

    async def create_review(
        self,
        *,
        prediction_id: UUID,
        reviewer: str,
        decision: str,
        notes: str | None = None,
    ) -> PredictionReview:
        if decision not in PREDICTION_REVIEW_DECISIONS:
            raise ValueError("Invalid prediction review decision.")
        prediction = await self._predictions.get_by_id(prediction_id)
        if prediction is None:
            raise LookupError("Prediction not found.")

        review = await self._reviews.create_review(
            prediction_id=prediction_id,
            reviewer=reviewer,
            decision=decision,
            notes=notes,
        )
        await self._audit.create_audit_log(
            action="prediction.reviewed",
            resource_type="prediction_review",
            resource_id=str(review.id),
            metadata={
                "prediction_id": str(prediction_id),
                "reviewer": reviewer,
                "decision": decision,
            },
        )
        return review

    async def list_reviews(
        self,
        *,
        decision: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        reviews = await self._reviews.list_reviews(decision=decision, limit=limit)
        return [_serialize_review(review) for review in reviews]


def _serialize_review(review: PredictionReview) -> dict[str, Any]:
    return {
        "review_id": str(review.id),
        "prediction_id": str(review.prediction_id),
        "reviewer": review.reviewer,
        "decision": review.decision,
        "notes": review.notes,
        "created_at": review.created_at.isoformat(),
    }
