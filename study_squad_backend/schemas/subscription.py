from pydantic import BaseModel


class PlanOut(BaseModel):
    tier: str
    name: str
    price_usd: float
    ai_daily_limit: int | None
    features: list[str]
    how_to_get: str


class CheckoutRequest(BaseModel):
    tier: str  # "pro" yoki "master"


class CheckoutResponse(BaseModel):
    checkout_url: str


class MyPlanOut(BaseModel):
    tier: str
    is_premium: bool
    premium_expires_at: str | None
