from datetime import datetime

from pydantic import BaseModel


class SquadCreate(BaseModel):
    name: str
    goal: str | None = None


class SquadOut(BaseModel):
    id: int
    name: str
    goal: str | None
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class SquadMemberOut(BaseModel):
    user_id: int
    full_name: str
    joined_at: datetime

    class Config:
        from_attributes = True


class SquadDetailOut(SquadOut):
    members: list[SquadMemberOut] = []
