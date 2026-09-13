from datetime import date as date_type, timedelta

from sqlalchemy.orm import Session

from models.user import User
from models.progress import DailyProgress, WeeklySummary
from models.coin import CoinTransaction
from services.coin_calculator import calculate_weekly_coins


def _week_bounds_for(user: User, week_offset: int = 0) -> tuple[date_type, date_type]:
    """Foydalanuvchining individual haftasi chegaralarini hisoblaydi.

    week_offset=0 - joriy hafta, week_offset=-1 - o'tgan hafta va h.k.
    """
    start_date = user.started_at.date()
    today = date_type.today()
    days_since_start = (today - start_date).days
    current_cycle = days_since_start // 7
    target_cycle = current_cycle + week_offset
    week_start = start_date + timedelta(days=target_cycle * 7)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def _calculate_streak_for_week(user_id: int, week_start: date_type, week_end: date_type, db: Session) -> tuple[int, float]:
    """Berilgan hafta uchun streak_days va avg_progress_percent hisoblaydi.

    Kelajakdagi (hali kelmagan) kunlar streak'ni buzmaydi - faqat bugungi
    kungacha bo'lgan kunlar hisobga olinadi.
    """
    effective_end = min(week_end, date_type.today())

    records = (
        db.query(DailyProgress)
        .filter(
            DailyProgress.user_id == user_id,
            DailyProgress.date >= week_start,
            DailyProgress.date <= effective_end,
        )
        .order_by(DailyProgress.date)
        .all()
    )
    records_by_date = {r.date: r for r in records}

    streak_days = 0
    day = week_start
    while day <= effective_end:
        record = records_by_date.get(day)
        if record and record.is_day_completed:
            streak_days += 1
        else:
            streak_days = 0
        day += timedelta(days=1)

    avg_progress = sum(r.progress_percent for r in records) / len(records) if records else 0.0
    return streak_days, avg_progress


def process_completed_week(user: User, db: Session, force: bool = False) -> WeeklySummary | None:
    """Foydalanuvchining o'tgan haftasini yakunlab, coin beradi.

    Agar hafta hali tugamagan bo'lsa va force=False bo'lsa, hech narsa qilmaydi.
    Agar shu hafta uchun allaqachon yakun chiqarilgan bo'lsa, qayta ishlamaydi.
    """
    week_start, week_end = _week_bounds_for(user, week_offset=0 if force else -1)

    if not force and date_type.today() <= week_end:
        return None  # hafta hali tugamagan

    existing = (
        db.query(WeeklySummary)
        .filter(WeeklySummary.user_id == user.id, WeeklySummary.week_start_date == week_start)
        .first()
    )
    if existing:
        return existing  # bu hafta uchun allaqachon yakunlangan

    streak_days, avg_progress = _calculate_streak_for_week(user.id, week_start, week_end, db)
    coins = calculate_weekly_coins(streak_days, avg_progress)

    summary = WeeklySummary(
        user_id=user.id,
        week_start_date=week_start,
        week_end_date=week_end,
        streak_days=streak_days,
        avg_progress_percent=avg_progress,
        coins_earned=coins,
    )
    db.add(summary)

    if coins > 0:
        user.coin_balance += coins
        db.add(CoinTransaction(
            user_id=user.id,
            amount=coins,
            type="weekly_reward",
            description=f"{week_start} - {week_end} haftasi uchun mukofot ({streak_days} kun streak, {avg_progress:.0f}% progress)",
        ))

    db.commit()
    db.refresh(summary)
    return summary


def process_all_users_weekly(db: Session) -> list[WeeklySummary]:
    """Barcha foydalanuvchilarning tugagan haftalarini tekshirib, coin beradi.
    Bu funksiya har kuni scheduler orqali chaqiriladi."""
    results = []
    users = db.query(User).all()
    for user in users:
        summary = process_completed_week(user, db, force=False)
        if summary:
            results.append(summary)
    return results
