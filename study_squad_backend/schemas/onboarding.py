from pydantic import BaseModel, Field


class OnboardingCreate(BaseModel):
    goal: str = Field(min_length=2, max_length=200)
    study_subject: str = Field(min_length=2, max_length=100)
    current_level: str | None = None
    daily_study_minutes: int = Field(default=60, ge=15, le=720)
    interests: list[str] = []


class OnboardingOut(BaseModel):
    goal: str | None
    study_subject: str | None
    current_level: str | None
    daily_study_minutes: int
    interests: list[str]
    completed: bool