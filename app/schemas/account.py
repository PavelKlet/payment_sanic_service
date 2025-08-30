from pydantic import BaseModel


class AccountOutWithUserId(BaseModel):
    id: int
    user_id: int
    balance: float


class AccountOut(BaseModel):
    id: int
    balance: float
