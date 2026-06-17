from typing import Any


class ExplainabilityService:
    """Generates deterministic metadata from model inputs and outputs.

    This does not alter model algorithms. It records human-readable context about
    which available input signals most strongly align with the produced risk score.
    """

    _FEATURE_LABELS = {
        "income_in_rs": "Reported income",
        "land_owned_acres": "Land ownership",
        "vehicles_owned": "Vehicle ownership",
        "electricity_consumption": "Electricity consumption",
        "pending_loans": "Pending loans",
        "weekly_spending": "Weekly spending",
        "monthly_spending": "Monthly spending",
        "transaction_count": "Transaction count",
        "avg_transaction_value": "Average transaction value",
        "luxury_items_bought": "Luxury purchases",
        "hospital_visits_per_year": "Hospital visits",
        "claim_frequency": "Claim frequency",
        "medical_claim_amount": "Medical claim amount",
        "avg_claim_amount": "Average claim amount",
        "chronic_disease": "Chronic disease flag",
        "avg_caste_population_per": "Caste population percentage",
        "officer_approvals_per_day": "Officer approvals per day",
    }

    _RISK_FEATURES = {
        "income_risk": [
            "income_in_rs",
            "land_owned_acres",
            "vehicles_owned",
            "electricity_consumption",
            "pending_loans",
            "business_ownership",
        ],
        "caste_risk": [
            "caste",
            "father_caste",
            "avg_caste_population_per",
            "officer_approvals_per_day",
        ],
        "transaction_risk": [
            "weekly_spending",
            "monthly_spending",
            "transaction_count",
            "avg_transaction_value",
            "luxury_items_bought",
            "weekend_spending_ratio",
        ],
        "medical_risk": [
            "hospital_visits_per_year",
            "claim_frequency",
            "medical_claim_amount",
            "avg_claim_amount",
            "chronic_disease",
        ],
    }

    def generate(
        self,
        *,
        features: dict[str, Any],
        risks: dict[str, float],
        risk_level: str,
    ) -> dict[str, Any]:
        contributions: list[dict[str, Any]] = []
        for risk_name, feature_names in self._RISK_FEATURES.items():
            risk_value = float(risks.get(risk_name, 0.0))
            if risk_value <= 0:
                continue
            weight = risk_value / max(len(feature_names), 1)
            for feature_name in feature_names:
                if feature_name not in features:
                    continue
                contributions.append(
                    {
                        "feature": feature_name,
                        "label": self._FEATURE_LABELS.get(feature_name, feature_name),
                        "value": features[feature_name],
                        "risk_component": risk_name,
                        "contribution_score": round(weight, 6),
                    }
                )

        contributions.sort(key=lambda item: item["contribution_score"], reverse=True)
        top_features = contributions[:5]
        summary = self._summary(top_features=top_features, risk_level=risk_level, risks=risks)
        return {
            "top_contributing_features": top_features,
            "feature_values": {
                feature["feature"]: feature["value"] for feature in top_features
            },
            "summary": summary,
            "method": "risk-component-attribution-v1",
        }

    def _summary(
        self,
        *,
        top_features: list[dict[str, Any]],
        risk_level: str,
        risks: dict[str, float],
    ) -> str:
        final_risk = round(float(risks.get("final_risk", 0.0)), 4)
        if not top_features:
            return f"Prediction classified as {risk_level} with final risk {final_risk}."
        labels = ", ".join(feature["label"] for feature in top_features[:3])
        return (
            f"Prediction classified as {risk_level} with final risk {final_risk}. "
            f"Primary contributing signals: {labels}."
        )
