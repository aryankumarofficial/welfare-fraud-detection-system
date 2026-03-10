from pydantic import BaseModel

class BeneficiaryData(BaseModel):
    income: float
    transactions: int
    age: int