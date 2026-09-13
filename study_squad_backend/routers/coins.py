from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from models.coin import CoinTransaction
from schemas.coin import CoinBalanceOut, CoinTransactionOut, RedeemResponse
from services.coin_calculator import PREMIUM_COST
from services.weekly_coin_service import process_completed_week

router = APIRouter(prefix="/coins", tags=["Coins"])


@router.get("/balance", response_model=CoinBalanceOut)
def get_balance(current_user: User = Depends(get_current_user)):
    return CoinBalanceOut(
        coin_balance=current_user.coin_balance,
        is_premium=current_user.is_premium,
    )


@router.get("/history", response_model=list[CoinTransactionOut])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transactions = (
        db.query(CoinTransaction)
        .filter(CoinTransaction.user_id == current_user.id)
        .order_by(CoinTransaction.created_at.desc())
        .all()
    )
    return transactions


@router.post("/redeem-premium", response_model=RedeemResponse)
def redeem_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.coin_balance < PREMIUM_COST:
        raise HTTPException(
            status_code=400,
            detail=f"Yetarli coin yo'q. Kerak: {PREMIUM_COST}, sizda: {current_user.coin_balance}",
        )

    current_user.coin_balance -= PREMIUM_COST
    current_user.is_premium = True

    # premium 30 kunga uzaytiriladi (agar allaqachon premium bo'lsa, davomiga qo'shiladi)
    base_date = current_user.premium_expires_at or datetime.utcnow()
    if base_date < datetime.utcnow():
        base_date = datetime.utcnow()
    current_user.premium_expires_at = base_date + timedelta(days=30)

    transaction = CoinTransaction(
        user_id=current_user.id,
        amount=-PREMIUM_COST,
        type="premium_purchase",
        description="1 oylik premium obuna sotib olindi",
    )
    db.add(transaction)
    db.commit()
    db.refresh(current_user)

    return RedeemResponse(
        success=True,
        new_balance=current_user.coin_balance,
        message="Premium muvaffaqiyatli faollashtirildi",
    )


@router.post("/process-weekly-test")
def process_weekly_test(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """FAQAT TEST UCHUN: haftani kutmasdan, joriy haftani hoziroq yakunlab coin beradi.

    Production'da bu endpoint olib tashlanishi yoki admin-only qilinishi kerak,
    chunki u haqiqiy haftani tugatmasdan turib coin berib yuboradi.
    """
    summary = process_completed_week(current_user, db, force=True)
    db.refresh(current_user)
    return {
        "week_summary": {
            "week_start_date": summary.week_start_date,
            "week_end_date": summary.week_end_date,
            "streak_days": summary.streak_days,
            "avg_progress_percent": summary.avg_progress_percent,
            "coins_earned": summary.coins_earned,
        },
        "new_coin_balance": current_user.coin_balance,
    }
