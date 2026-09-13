from datetime import datetime

from pydantic import BaseModel


class CoinBalanceOut(BaseModel):
    coin_balance: int
    is_premium: bool


class CoinTransactionOut(BaseModel):
    id: int
    amount: int
    type: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class RedeemResponse(BaseModel):
    success: bool
    new_balance: int
    message: str
