from datetime import date as date_type

from pydantic import BaseModel


class DailyProgressIn(BaseModel):
    tasks_total: int
    tasks_completed: int
    date: date_type | None = None  # kiritilmasa, bugungi sana ishlatiladi


class DailyProgressOut(BaseModel):
    date: date_type
    tasks_total: int
    tasks_completed: int
    progress_percent: float
    is_day_completed: bool

    class Config:
        from_attributes = True


class WeeklyProgressOut(BaseModel):
    week_start_date: date_type
    week_end_date: date_type
    streak_days: int
    avg_progress_percent: float
    days: list[DailyProgressOut]
