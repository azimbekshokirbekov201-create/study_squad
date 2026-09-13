from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    full_name: str | None = None


class ProfileOut(BaseModel):
    id: int
    full_name: str
    email: str | None

    coin_balance: int
    is_premium: bool
    subscription_tier: str

    goal: str | None
    study_subject: str | None
    current_level: str | None
    daily_study_minutes: int

    onboarding_completed: bool