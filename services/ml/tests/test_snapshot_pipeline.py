import asyncio
import os
import sys
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

ML_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ML_ROOT))
os.chdir(ML_ROOT)

from src.db.models.feature_snapshot import FeatureSnapshot
from src.db.models.source_records import (
    StudentFinancialRecord,
    StudentMedicalSummary,
    StudentSocialRecord,
    StudentTransactionSummary,
)
from src.db.models.student_profile import StudentProfile
from src.exceptions import FeatureGenerationError, MissingSourceDataError
from src.services.feature_builder import FeatureSourceRecords
from src.services.prediction_service import PredictionResult
from src.services.snapshot_generator import GeneratedSnapshot, SnapshotGenerator


class FakeSingleRecordRepository:
    def __init__(self, record: object | None) -> None:
        self._record = record

    async def get_latest_by_profile_id(self, student_profile_id: uuid.UUID) -> object | None:
        return self._record


class FakeProfileRepository:
    def __init__(self, profile: StudentProfile | None) -> None:
        self._profile = profile

    async def get_by_id(self, profile_id: uuid.UUID) -> StudentProfile | None:
        return self._profile


class FakeSnapshotService:
    def __init__(self, snapshot: FeatureSnapshot) -> None:
        self.snapshot = snapshot
        self.created_features: dict[str, Any] | None = None

    async def create_snapshot(
        self,
        *,
        student_profile_id: uuid.UUID,
        features: dict[str, Any],
        source: str = "profile_snapshot",
    ) -> FeatureSnapshot:
        self.created_features = features
        return self.snapshot


class InvalidFeatureBuilder:
    def build(self, records: FeatureSourceRecords) -> dict[str, Any]:
        return {"income_in_rs": 1000.0}


def _now() -> datetime:
    return datetime.now(UTC)


def _profile(profile_id: uuid.UUID) -> StudentProfile:
    return StudentProfile(
        id=profile_id,
        external_id="student-1",
        name="Student One",
        created_at=_now(),
        updated_at=_now(),
    )


def _financial(profile_id: uuid.UUID) -> StudentFinancialRecord:
    return StudentFinancialRecord(
        id=uuid.uuid4(),
        student_profile_id=profile_id,
        income_in_rs=122962.0,
        land_owned_acres=1.2,
        vehicles_owned=1,
        electricity_consumption=205.0,
        pending_loans=1,
        business_ownership=0,
        created_at=_now(),
    )


def _social(profile_id: uuid.UUID) -> StudentSocialRecord:
    return StudentSocialRecord(
        id=uuid.uuid4(),
        student_profile_id=profile_id,
        caste="OBC",
        father_caste="OBC",
        avg_caste_population_per=0.18,
        officer_approvals_per_day=7.0,
        created_at=_now(),
    )


def _transaction(profile_id: uuid.UUID) -> StudentTransactionSummary:
    return StudentTransactionSummary(
        id=uuid.uuid4(),
        student_profile_id=profile_id,
        weekly_spending=4200.0,
        monthly_spending=16800.0,
        transaction_count=56,
        avg_transaction_value=175.0,
        luxury_items_bought=1,
        weekend_spending_ratio=0.27,
        created_at=_now(),
    )


def _medical(profile_id: uuid.UUID) -> StudentMedicalSummary:
    return StudentMedicalSummary(
        id=uuid.uuid4(),
        student_profile_id=profile_id,
        hospital_visits_per_year=2,
        claim_frequency=2,
        medical_claim_amount=3825.0,
        avg_claim_amount=1095.0,
        chronic_disease=0,
        created_at=_now(),
    )


def _snapshot(profile_id: uuid.UUID) -> FeatureSnapshot:
    return FeatureSnapshot(
        id=uuid.uuid4(),
        student_profile_id=profile_id,
        source="profile_snapshot",
        features={},
        feature_schema_version="v1",
        checksum="checksum",
        created_at=_now(),
    )


def _generator(
    *,
    profile: StudentProfile,
    financial: StudentFinancialRecord | None,
    social: StudentSocialRecord | None,
    transaction: StudentTransactionSummary | None,
    medical: StudentMedicalSummary | None,
    snapshot: FeatureSnapshot,
    feature_builder: object | None = None,
) -> SnapshotGenerator:
    generator = SnapshotGenerator(
        cast(AsyncSession, object()),
        feature_builder=feature_builder,  # type: ignore[arg-type]
    )
    generator._profiles = FakeProfileRepository(profile)  # type: ignore[assignment]
    generator._financial_records = FakeSingleRecordRepository(financial)  # type: ignore[assignment]
    generator._social_records = FakeSingleRecordRepository(social)  # type: ignore[assignment]
    generator._transaction_summaries = FakeSingleRecordRepository(transaction)  # type: ignore[assignment]
    generator._medical_summaries = FakeSingleRecordRepository(medical)  # type: ignore[assignment]
    generator._snapshot_service = FakeSnapshotService(snapshot)  # type: ignore[assignment]
    return generator


def test_successful_snapshot_generation() -> None:
    profile_id = uuid.uuid4()
    snapshot = _snapshot(profile_id)
    snapshot.features = {}
    generator = _generator(
        profile=_profile(profile_id),
        financial=_financial(profile_id),
        social=_social(profile_id),
        transaction=_transaction(profile_id),
        medical=_medical(profile_id),
        snapshot=snapshot,
    )

    result = asyncio.run(generator.generate_for_profile(profile_id))

    assert result.snapshot.id == snapshot.id
    assert result.features["income_in_rs"] == 122962.0
    assert result.features["caste"] == "OBC"
    assert set(result.features) == {
        "income_in_rs",
        "land_owned_acres",
        "vehicles_owned",
        "electricity_consumption",
        "pending_loans",
        "business_ownership",
        "caste",
        "father_caste",
        "avg_caste_population_per",
        "officer_approvals_per_day",
        "weekly_spending",
        "monthly_spending",
        "transaction_count",
        "avg_transaction_value",
        "luxury_items_bought",
        "weekend_spending_ratio",
        "hospital_visits_per_year",
        "claim_frequency",
        "medical_claim_amount",
        "avg_claim_amount",
        "chronic_disease",
    }


def test_snapshot_generation_reports_missing_source_data() -> None:
    profile_id = uuid.uuid4()
    generator = _generator(
        profile=_profile(profile_id),
        financial=None,
        social=_social(profile_id),
        transaction=_transaction(profile_id),
        medical=_medical(profile_id),
        snapshot=_snapshot(profile_id),
    )

    with pytest.raises(MissingSourceDataError) as exc_info:
        asyncio.run(generator.generate_for_profile(profile_id))

    assert exc_info.value.missing_sources == ["student_financial_records"]


def test_snapshot_generation_rejects_invalid_generated_feature_set() -> None:
    profile_id = uuid.uuid4()
    generator = _generator(
        profile=_profile(profile_id),
        financial=_financial(profile_id),
        social=_social(profile_id),
        transaction=_transaction(profile_id),
        medical=_medical(profile_id),
        snapshot=_snapshot(profile_id),
        feature_builder=InvalidFeatureBuilder(),
    )

    with pytest.raises(FeatureGenerationError) as exc_info:
        asyncio.run(generator.generate_for_profile(profile_id))

    assert exc_info.value.details


def test_predict_generate_endpoint_generates_predicts_and_returns_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src import app as app_module

    profile_id = uuid.uuid4()
    snapshot = _snapshot(profile_id)
    generated_snapshot = GeneratedSnapshot(snapshot=snapshot, features={})
    prediction = PredictionResult(
        student_profile_id=profile_id,
        feature_snapshot_id=snapshot.id,
        prediction_id=uuid.uuid4(),
        model_version_id=None,
        risk_level="LOW",
        prediction_duration_ms=12,
        risks={
            "income_risk": 0.1,
            "caste_risk": 0.2,
            "transaction_risk": 0.3,
            "medical_risk": 0.4,
            "final_risk": 0.25,
        },
    )

    @asynccontextmanager
    async def fake_db_session() -> AsyncIterator[object]:
        yield object()

    class FakeGenerator:
        def __init__(self, session: object) -> None:
            self.session = session

        async def generate_for_profile(
            self,
            student_profile_id: uuid.UUID,
        ) -> GeneratedSnapshot:
            assert student_profile_id == profile_id
            return generated_snapshot

    class FakePredictionService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def predict_for_feature_snapshot(
            self,
            *,
            student_profile_id: uuid.UUID,
            feature_snapshot_id: uuid.UUID,
        ) -> PredictionResult:
            assert student_profile_id == profile_id
            assert feature_snapshot_id == snapshot.id
            return prediction

    monkeypatch.setattr(app_module, "get_db_session", fake_db_session)
    monkeypatch.setattr(app_module, "SnapshotGenerator", FakeGenerator)
    monkeypatch.setattr(app_module, "PredictionService", FakePredictionService)

    response = asyncio.run(
        app_module.predict_generated_snapshot(
            app_module.PredictProfileRequest(student_profile_id=profile_id)
        )
    )

    assert response["success"] is True
    assert response["data"]["prediction_id"] == str(prediction.prediction_id)
    assert response["data"]["feature_snapshot_id"] == str(snapshot.id)
    assert response["data"]["final_risk"] == 0.25
