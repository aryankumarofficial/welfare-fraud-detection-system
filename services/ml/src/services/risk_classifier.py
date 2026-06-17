from dataclasses import dataclass


LOW_RISK_MAX = 0.30
MEDIUM_RISK_MAX = 0.60


@dataclass(frozen=True)
class RiskClassification:
    score: float
    level: str


class RiskClassifier:
    """Centralized score-to-label classification for prediction outputs."""

    @staticmethod
    def classify(score: float) -> RiskClassification:
        bounded_score = max(0.0, min(1.0, float(score)))

        if bounded_score <= LOW_RISK_MAX:
            level = "LOW"
        elif bounded_score <= MEDIUM_RISK_MAX:
            level = "MEDIUM"
        else:
            level = "HIGH"

        return RiskClassification(score=bounded_score, level=level)
