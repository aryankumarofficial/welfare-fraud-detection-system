from uuid import UUID

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.db.session import get_db_session
from src.exceptions import (
    PredictionFailedError,
    ProfileNotFoundError,
    SnapshotNotFoundError,
)
from src.predict import predict_all
from src.schemas.feature_snapshot import InvalidFeatureSetError
from src.services.prediction_service import PredictionService
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


@app.get("/test")
def test():
    pridictions = run_test_predictions()

    return {"success": True, "result": pridictions}
