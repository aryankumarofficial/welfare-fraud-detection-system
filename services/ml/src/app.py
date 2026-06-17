from uuid import UUID

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.db.session import get_db_session
from src.exceptions import (
    FeatureGenerationError,
    MissingSourceDataError,
    PredictionFailedError,
    ProfileNotFoundError,
    SnapshotGenerationError,
    SnapshotNotFoundError,
    SnapshotProfileMismatchError,
)
from src.predict import predict_all
from src.schemas.feature_snapshot import InvalidFeatureSetError
from src.services.prediction_service import PredictionService
from src.services.snapshot_generator import SnapshotGenerator
from src.test import run_test_predictions

app = FastAPI()


class UserData(BaseModel):
    income_in_rs: float
    land_owned_acres: float
    vehicles_owned: int
    electricity_consumption: float
    pending_loans: int
    business_ownership: int

    caste: str
    father_caste: str
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
    chronic_disease: int


class PredictProfileRequest(BaseModel):
    student_profile_id: UUID = Field(description="Beneficiary profile UUID")


class GenerateSnapshotRequest(BaseModel):
    student_profile_id: UUID = Field(description="Beneficiary profile UUID")


@app.get("/")
def home():
    return {"message": "Welfare Fraud Detection API is running"}


@app.post("/predict")
def predict(data: UserData):
    result = predict_all(data.model_dump())

    return {"success": True, "data": result}


@app.post("/predict/profile")
async def predict_profile(body: PredictProfileRequest):
    async with get_db_session() as session:
        service = PredictionService(session)

        try:
            result = await service.predict_for_snapshot(body.student_profile_id)
        except ProfileNotFoundError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PROFILE_NOT_FOUND"},
            )
        except SnapshotNotFoundError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "SNAPSHOT_NOT_FOUND"},
            )
        except InvalidFeatureSetError:
            return JSONResponse(
                status_code=422,
                content={"success": False, "error": "INVALID_FEATURE_SET"},
            )
        except PredictionFailedError:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "PREDICTION_FAILED"},
            )

        return {
            "success": True,
            "data": {
                "prediction_id": str(result.prediction_id),
                "student_profile_id": str(result.student_profile_id),
                "feature_snapshot_id": str(result.feature_snapshot_id),
                "model_version_id": (
                    str(result.model_version_id) if result.model_version_id else None
                ),
                **result.risks,
            },
        }


@app.post("/snapshot/generate")
async def generate_snapshot(body: GenerateSnapshotRequest):
    async with get_db_session() as session:
        generator = SnapshotGenerator(session)

        try:
            result = await generator.generate_for_profile(body.student_profile_id)
        except ProfileNotFoundError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PROFILE_NOT_FOUND"},
            )
        except MissingSourceDataError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": "MISSING_SOURCE_DATA",
                    "missing_sources": exc.missing_sources,
                },
            )
        except FeatureGenerationError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": "FEATURE_GENERATION_FAILED",
                    "details": exc.details,
                },
            )
        except SnapshotGenerationError:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "SNAPSHOT_GENERATION_FAILED"},
            )

        return {
            "success": True,
            "data": {
                "feature_snapshot_id": str(result.snapshot.id),
                "student_profile_id": str(result.snapshot.student_profile_id),
                "feature_schema_version": result.snapshot.feature_schema_version,
                "source": result.snapshot.source,
                "checksum": result.snapshot.checksum,
                "features": result.features,
            },
        }


@app.post("/predict/generate")
async def predict_generated_snapshot(body: PredictProfileRequest):
    async with get_db_session() as session:
        generator = SnapshotGenerator(session)
        prediction_service = PredictionService(session)

        try:
            generated = await generator.generate_for_profile(body.student_profile_id)
            result = await prediction_service.predict_for_feature_snapshot(
                student_profile_id=body.student_profile_id,
                feature_snapshot_id=generated.snapshot.id,
            )
        except ProfileNotFoundError:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "PROFILE_NOT_FOUND"},
            )
        except MissingSourceDataError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": "MISSING_SOURCE_DATA",
                    "missing_sources": exc.missing_sources,
                },
            )
        except FeatureGenerationError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": "FEATURE_GENERATION_FAILED",
                    "details": exc.details,
                },
            )
        except SnapshotGenerationError:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "SNAPSHOT_GENERATION_FAILED"},
            )
        except InvalidFeatureSetError:
            return JSONResponse(
                status_code=422,
                content={"success": False, "error": "INVALID_FEATURE_SET"},
            )
        except (SnapshotNotFoundError, SnapshotProfileMismatchError):
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "SNAPSHOT_NOT_FOUND"},
            )
        except PredictionFailedError:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "PREDICTION_FAILED"},
            )

        return {
            "success": True,
            "data": {
                "prediction_id": str(result.prediction_id),
                "student_profile_id": str(result.student_profile_id),
                "feature_snapshot_id": str(generated.snapshot.id),
                "model_version_id": (
                    str(result.model_version_id) if result.model_version_id else None
                ),
                **result.risks,
            },
        }


@app.get("/test")
def test():
    pridictions = run_test_predictions()

    return {"success": True, "result": pridictions}
