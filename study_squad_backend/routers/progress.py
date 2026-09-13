from datetime import date as date_type, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from models.progress import DailyProgress
from schemas.progress import DailyProgressIn, DailyProgressOut, WeeklyProgressOut

router = APIRouter(prefix="/progress", tags=["Progress"])

DAY_COMPLETED_THRESHOLD = 70.0  # foiz - kelishilgan minimal progress


def _current_week_bounds(user: User) -> tuple[date_type, date_type]:
    """Foydalanuvchining individual haftasi chegaralarini hisoblaydi
    (started_at sanasidan boshlab, 7 kunlik davrlar)."""
    start_date = user.started_at.date()
    today = date_type.today()
    days_since_start = (today - start_date).days
    current_cycle = days_since_start // 7
    week_start = start_date + timedelta(days=current_cycle * 7)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


@router.post("/daily", response_model=DailyProgressOut)
def submit_daily_progress(
    data: DailyProgressIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_date = data.date or date_type.today()
    progress_percent = (
        (data.tasks_completed / data.tasks_total * 100) if data.tasks_total > 0 else 0
    )
    is_completed = progress_percent >= DAY_COMPLETED_THRESHOLD

    record = (
        db.query(DailyProgress)
        .filter(DailyProgress.user_id == current_user.id, DailyProgress.date == target_date)
        .first()
    )

    if record:
        record.tasks_total = data.tasks_total
        record.tasks_completed = data.tasks_completed
        record.progress_percent = progress_percent
        record.is_day_completed = is_completed
    else:
        record = DailyProgress(
            user_id=current_user.id,
            date=target_date,
            tasks_total=data.tasks_total,
            tasks_completed=data.tasks_completed,
            progress_percent=progress_percent,
            is_day_completed=is_completed,
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return record


@router.get("/weekly/me", response_model=WeeklyProgressOut)
def get_my_weekly_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    week_start, week_end = _current_week_bounds(current_user)

    records = (
        db.query(DailyProgress)
        .filter(
            DailyProgress.user_id == current_user.id,
            DailyProgress.date >= week_start,
            DailyProgress.date <= week_end,
        )
        .order_by(DailyProgress.date)
        .all()
    )

    # streak: hafta boshidan e'tiboran ketma-ket bajarilgan kunlar soni
    streak_days = 0
    records_by_date = {r.date: r for r in records}
    day = week_start
    while day <= min(week_end, date_type.today()):
        record = records_by_date.get(day)
        if record and record.is_day_completed:
            streak_days += 1
        else:
            streak_days = 0  # uzilish bo'lsa qayta boshlanadi
        day += timedelta(days=1)

    avg_progress = (
        sum(r.progress_percent for r in records) / len(records) if records else 0
    )

    return WeeklyProgressOut(
        week_start_date=week_start,
        week_end_date=week_end,
        streak_days=streak_days,
        avg_progress_percent=avg_progress,
        days=records,
    )
