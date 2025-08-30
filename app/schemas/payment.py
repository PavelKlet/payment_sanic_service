from pydantic import BaseModel


class PaymentOut(BaseModel):
    id: int
    transaction_id: str
    user_id: int
    account_id: int
    amount: float


class WebhookIn(BaseModel):
    transaction_id: str
    account_id: int
    user_id: int
    amount: float
    signature: str
