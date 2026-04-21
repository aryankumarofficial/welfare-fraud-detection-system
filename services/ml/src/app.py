from fastapi import FastAPI
from pydantic import BaseModel
from src.predict import predict_all
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


@app.get("/")
def home():
    return {"message": "Welfare Fraud Detection API is running"}


@app.post("/predict")
def predict(data: UserData):

    result = predict_all(data.dict())

    return {"success": True, "data": result}


@app.get("/test")
def test():
    pridictions = run_test_predictions()

    return {"success": True, "result": pridictions}
