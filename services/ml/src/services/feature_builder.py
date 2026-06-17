from dataclasses import dataclass
from typing import Any

from src.db.models.source_records import (
    StudentFinancialRecord,
    StudentMedicalSummary,
    StudentSocialRecord,
    StudentTransactionSummary,
)
from src.db.models.student_profile import StudentProfile
from src.exceptions import MissingSourceDataError


@dataclass(frozen=True)
class FeatureSourceRecords:
    profile: StudentProfile
    financial: StudentFinancialRecord | None
    social: StudentSocialRecord | None
    transaction: StudentTransactionSummary | None
    medical: StudentMedicalSummary | None


class FeatureBuilder:
    """Builds the canonical v1 ML feature payload from domain source records."""

    def build(self, records: FeatureSourceRecords) -> dict[str, Any]:
        missing_sources = self._missing_sources(records)
        if missing_sources:
            raise MissingSourceDataError(records.profile.id, missing_sources)

        financial = records.financial
        social = records.social
        transaction = records.transaction
        medical = records.medical

        if (
            financial is None
            or social is None
            or transaction is None
            or medical is None
        ):
            raise MissingSourceDataError(records.profile.id, missing_sources)

        return {
            "income_in_rs": float(financial.income_in_rs),
            "land_owned_acres": float(financial.land_owned_acres),
            "vehicles_owned": int(financial.vehicles_owned),
            "electricity_consumption": float(financial.electricity_consumption),
            "pending_loans": int(financial.pending_loans),
            "business_ownership": int(financial.business_ownership),
            "caste": social.caste,
            "father_caste": social.father_caste,
            "avg_caste_population_per": float(social.avg_caste_population_per),
            "officer_approvals_per_day": float(social.officer_approvals_per_day),
            "weekly_spending": float(transaction.weekly_spending),
            "monthly_spending": float(transaction.monthly_spending),
            "transaction_count": int(transaction.transaction_count),
            "avg_transaction_value": float(transaction.avg_transaction_value),
            "luxury_items_bought": int(transaction.luxury_items_bought),
            "weekend_spending_ratio": float(transaction.weekend_spending_ratio),
            "hospital_visits_per_year": int(medical.hospital_visits_per_year),
            "claim_frequency": int(medical.claim_frequency),
            "medical_claim_amount": float(medical.medical_claim_amount),
            "avg_claim_amount": float(medical.avg_claim_amount),
            "chronic_disease": int(medical.chronic_disease),
        }

    def _missing_sources(self, records: FeatureSourceRecords) -> list[str]:
        missing_sources: list[str] = []
        if records.financial is None:
            missing_sources.append("student_financial_records")
        if records.social is None:
            missing_sources.append("student_social_records")
        if records.transaction is None:
            missing_sources.append("student_transaction_summaries")
        if records.medical is None:
            missing_sources.append("student_medical_summaries")
        return missing_sources
