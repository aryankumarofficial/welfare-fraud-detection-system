from src.predict import predict_all

data_list = [
    {
        "income_in_rs": 122962,
        "land_owned_acres": 1.73,
        "vehicles_owned": 2,
        "electricity_consumption": 286,
        "pending_loans": 1,
        "business_ownership": 1,
        "caste": "OBC",
        "father_caste": "OBC",
        "avg_caste_population_per": 0.18,
        "officer_approvals_per_day": 14,
        "weekly_spending": 2504,
        "monthly_spending": 9853,
        "transaction_count": 56,
        "avg_transaction_value": 175,
        "luxury_items_bought": 2,
        "weekend_spending_ratio": 0.19,
        "hospital_visits_per_year": 2,
        "claim_frequency": 2,
        "medical_claim_amount": 3825,
        "avg_claim_amount": 1095,
        "chronic_disease": 1,
    },
    {
        "income_in_rs": 81498,
        "land_owned_acres": 0.55,
        "vehicles_owned": 0,
        "electricity_consumption": 179,
        "pending_loans": 0,
        "business_ownership": 1,
        "caste": "General",
        "father_caste": "General",
        "avg_caste_population_per": 0.28,
        "officer_approvals_per_day": 13,
        "weekly_spending": 5229,
        "monthly_spending": 21585,
        "transaction_count": 29,
        "avg_transaction_value": 744,
        "luxury_items_bought": 1,
        "weekend_spending_ratio": 0.16,
        "hospital_visits_per_year": 1,
        "claim_frequency": 3,
        "medical_claim_amount": 27893,
        "avg_claim_amount": 6995,
        "chronic_disease": 0,
    },
    {
        "income_in_rs": 68868,
        "land_owned_acres": 14.29,
        "vehicles_owned": 3,
        "electricity_consumption": 1117,
        "pending_loans": 2,
        "business_ownership": 1,
        "caste": "SC",
        "father_caste": "General",
        "avg_caste_population_per": 0.27,
        "officer_approvals_per_day": 13,
        "weekly_spending": 4553,
        "monthly_spending": 21585,
        "transaction_count": 28,
        "avg_transaction_value": 696,
        "luxury_items_bought": 1,
        "weekend_spending_ratio": 0.26,
        "hospital_visits_per_year": 5,
        "claim_frequency": 4,
        "medical_claim_amount": 18755,
        "avg_claim_amount": 3751,
        "chronic_disease": 1,
    },
]


def run_test_predictions():
    results = []
    for data in data_list:
        result = predict_all(data)
        print(result)
        results.append(result)

    return results


if __name__ == "__main__":
    run_test_predictions()
