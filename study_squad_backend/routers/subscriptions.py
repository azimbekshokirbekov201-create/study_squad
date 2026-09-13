from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.subscription import PlanOut, CheckoutRequest, CheckoutResponse, MyPlanOut
from services.pricing_plans import PLANS
from services.stripe_service import create_checkout_session, verify_webhook_event

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/plans", response_model=list[PlanOut])
def list_plans():
    return [
        PlanOut(
            tier=tier,
            name=data["name"],
            price_usd=data["price_usd"],
            ai_daily_limit=data["ai_daily_limit"],
            features=data["features"],
            how_to_get=data["how_to_get"],
        )
        for tier, data in PLANS.items()
    ]


@router.get("/me", response_model=MyPlanOut)
def my_plan(current_user: User = Depends(get_current_user)):
    return MyPlanOut(
        tier=current_user.subscription_tier,
        is_premium=current_user.is_premium,
        premium_expires_at=(
            current_user.premium_expires_at.isoformat()
            if current_user.premium_expires_at else None
        ),
    )


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
):
    if data.tier not in ("pro", "master"):
        raise HTTPException(status_code=400, detail="Faqat 'pro' yoki 'master' tanlash mumkin")

    if not current_user.email:
        raise HTTPException(status_code=400, detail="To'lov uchun email kerak")

    try:
        url = create_checkout_session(current_user.id, current_user.email, data.tier)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Stripe xatosi: {e}")

    return CheckoutResponse(checkout_url=url)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = verify_webhook_event(payload, sig_header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook tekshiruvi muvaffaqiyatsiz: {e}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = int(session["metadata"]["user_id"])
        tier = session["metadata"]["tier"]

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.subscription_tier = tier
            user.is_premium = True
            user.premium_expires_at = datetime.utcnow() + timedelta(days=30)
            user.stripe_customer_id = session.get("customer")
            db.commit()

    return {"status": "ok"}
