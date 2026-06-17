from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.prediction_review import PredictionReview


class ModelEvaluationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_model_performance(self) -> dict[str, Any]:
        counts = await self._decision_counts()
        reviewed_predictions = sum(counts.values())
        confirmed_fraud = counts.get("confirmed_fraud", 0)
        false_positives = counts.get("false_positive", 0)
        pending = counts.get("pending", 0)
        under_investigation = counts.get("under_investigation", 0)
        decisive_reviews = confirmed_fraud + false_positives
        precision = (
            round(confirmed_fraud / decisive_reviews, 4) if decisive_reviews else 0.0
        )
        review_agreement_rate = (
            round(confirmed_fraud / reviewed_predictions, 4)
            if reviewed_predictions
            else 0.0
        )

        return {
            "reviewed_predictions": reviewed_predictions,
            "confirmed_fraud_count": confirmed_fraud,
            "false_positives": false_positives,
            "pending_reviews": pending,
            "under_investigation": under_investigation,
            "precision": precision,
            "review_agreement_rate": review_agreement_rate,
            "decision_counts": counts,
        }

    async def _decision_counts(self) -> dict[str, int]:
        statement = (
            select(PredictionReview.decision, func.count(PredictionReview.id))
            .group_by(PredictionReview.decision)
        )
        result = await self._session.execute(statement)
        return {decision: int(count) for decision, count in result.all()}
