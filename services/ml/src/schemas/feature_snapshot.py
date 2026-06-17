from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError

FEATURE_SCHEMA_VERSION_V1 = "v1"

CasteCategory = Literal["General", "OBC", "SC", "ST"]
BinaryFlag = Literal[0, 1]


class FeatureSnapshotV1(BaseModel):
    """Canonical v1 feature set required by predict_all()."""

    model_config = ConfigDict(extra="forbid")

    income_in_rs: float
    land_owned_acres: float
    vehicles_owned: int
    electricity_consumption: float
    pending_loans: int
    business_ownership: BinaryFlag

    caste: CasteCategory
    father_caste: CasteCategory
    avg_caste_population_per: float
    officer_approvals_per_day: float

    weekly_spending: float
    monthly_spending: float
    transaction_count: int
    avg_transaction_value: float
    luxury_items_bought: int
    weekend_spending_ratio: float

    hospital_visits_per_year: int
    claim_frequency: int
    medical_claim_amount: float
    avg_claim_amount: float
    chronic_disease: BinaryFlag


class InvalidFeatureSetError(ValueError):
    """Raised when feature_snapshots.features fails schema validation."""

    def __init__(self, message: str, *, details: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message)
        self.details = details or []


def validate_feature_snapshot(
    features: dict[str, Any],
    *,
    feature_schema_version: str,
) -> dict[str, Any]:
    """
    Validate snapshot payload before inference.

    Returns a plain dict compatible with predict_all().
    """
    if feature_schema_version != FEATURE_SCHEMA_VERSION_V1:
        raise InvalidFeatureSetError(
            f"Unsupported feature_schema_version: {feature_schema_version!r}. "
            f"Expected {FEATURE_SCHEMA_VERSION_V1!r}."
        )

    try:
        validated = FeatureSnapshotV1.model_validate(features)
    except ValidationError as exc:
        raise InvalidFeatureSetError(
            "Feature snapshot failed validation.",
            details=exc.errors(),
        ) from exc

    return validated.model_dump()
