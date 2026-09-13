from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from models.progress import DailyProgress
from schemas.ai_coach import ChatRequest, ChatResponse, DailyTipResponse
from services.ai_coach_service import get_ai_response, get_daily_tip
from services.pricing_plans import PLANS

router = APIRouter(prefix="/ai-coach", tags=["AI Coach"])


def _enforce_daily_limit(user: User, db: Session):
    """Basic tarifda kunlik AI so'rovlar sonini cheklaydi. Pro/Master uchun cheklov yo'q."""
    limit = PLANS.get(user.subscription_tier, PLANS["basic"])["ai_daily_limit"]
    if limit is None:
        return  # cheklanmagan tarif

    today = date.today()
    if user.ai_requests_date != today:
        # yangi kun boshlandi, hisoblagichni tozalash
        user.ai_requests_date = today
        user.ai_requests_today = 0

    if user.ai_requests_today >= limit:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Bugungi AI Coach so'rovlar limiti ({limit} ta) tugadi. "
                "Cheklanmagan foydalanish uchun Pro yoki Master tarifiga o'ting."
            ),
        )

    user.ai_requests_today += 1
    db.commit()


def _build_user_context(user: User, db: Session) -> str:
    """Foydalanuvchining oxirgi 7 kunlik progressidan AI uchun qisqa xulosa tuzadi."""
    week_ago = date.today() - timedelta(days=7)
    records = (
        db.query(DailyProgress)
        .filter(DailyProgress.user_id == user.id, DailyProgress.date >= week_ago)
        .order_by(DailyProgress.date)
        .all()
    )

    if not records:
        return f"{user.full_name} hali hech qanday progress kiritmagan, yangi foydalanuvchi."

    avg_progress = sum(r.progress_percent for r in records) / len(records)
    completed_days = sum(1 for r in records if r.is_day_completed)

    return (
        f"{user.full_name}, oxirgi {len(records)} kun ichida o'rtacha progress "
        f"{avg_progress:.0f}%, to'liq bajarilgan kunlar soni: {completed_days}."
    )


@router.post("/chat", response_model=ChatResponse)
def chat_with_coach(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _enforce_daily_limit(current_user, db)
    context = _build_user_context(current_user, db)
    try:
        reply = get_ai_response(data.message, context=context)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return ChatResponse(reply=reply)


@router.get("/daily-tip", response_model=DailyTipResponse)
def daily_tip(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _enforce_daily_limit(current_user, db)
    context = _build_user_context(current_user, db)
    try:
        tip = get_daily_tip(context)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return DailyTipResponse(tip=tip)
