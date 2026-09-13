from datetime import date as date_type, datetime

from pydantic import BaseModel, Field


class TaskGenerateIn(BaseModel):
    goal: str = Field(min_length=3, max_length=2000)
    count: int = Field(default=4, ge=1, le=8)


class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    date: date_type
    status: str
    ai_reason: str | None = None
    proof_status: str
    proof_feedback: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class TaskProofOut(BaseModel):
    task_id: int
    status: str
    proof_status: str
    feedback: str
    task_completed: bool
