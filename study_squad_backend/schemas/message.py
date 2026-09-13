from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    message: str


class MessageOut(BaseModel):
    id: int
    squad_id: int
    user_id: int
    full_name: str
    message: str
    created_at: datetime
