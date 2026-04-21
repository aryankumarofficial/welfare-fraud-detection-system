import warnings

import joblib

warnings.filterwarnings("ignore", category=UserWarning)
import numpy as np
from src.preprocess import (
    preprocess_caste,
    preprocess_income,
    preprocess_medical,
    preprocess_transaction,
)

# =========================
# LOAD MODELS
# =========================

income_model = joblib.load("models/income_model.pkl")
caste_model = joblib.load("models/caste_model.pkl")
transaction_model = joblib.load("models/transaction_model.pkl")
medical_model = joblib.load("models/medical_model.pkl")

# =========================
# NORMALIZATION FUNCTION
# =========================


def normalize_score(score):
    return 1 / (1 + np.exp(-5 * score))


# =========================
# MAIN PREDICTION FUNCTION
# =========================


def predict_all(data: dict):

    # Preprocess each part
    inc = preprocess_income(data)
    cs = preprocess_caste(data)
    txn = preprocess_transaction(data)
    med = preprocess_medical(data)

    # Get anomaly scores
    income_score = -income_model.decision_function(inc)[0]
    caste_score = -caste_model.decision_function(cs)[0]
    transaction_score = -transaction_model.decision_function(txn)[0]
    medical_score = -medical_model.decision_function(med)[0]

    # Normalize
    income_risk = normalize_score(income_score)
    caste_risk = normalize_score(caste_score)
    transaction_risk = normalize_score(transaction_score)
    medical_risk = normalize_score(medical_score)

    # Final combined risk
    final_risk = (income_risk + caste_risk + transaction_risk + medical_risk) / 4

    return {
        "income_risk": float(income_risk),
        "caste_risk": float(caste_risk),
        "transaction_risk": float(transaction_risk),
        "medical_risk": float(medical_risk),
        "final_risk": float(final_risk),
    }
