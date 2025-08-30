from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field
from .account import AccountOut


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None


class UserWithAccountsOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    accounts: List[AccountOut] = Field(default_factory=list)
