from fastapi import APIRouter
from app.schemas import BeneficiaryData
from app.models.isolation_forest import predict

router = APIRouter()

@router.post("/analyze")
def analyze(data: BeneficiaryData):

    result = predict(data)

    return {
        "risk_score": result["anomaly_score"],
        "fraud_label": result["label"]
    }