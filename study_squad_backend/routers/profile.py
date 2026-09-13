from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from models.onboarding import UserOnboarding
from schemas.profile import ProfileOut


router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.get("/me", response_model=ProfileOut)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    onboarding = (
        db.query(UserOnboarding)
        .filter(UserOnboarding.user_id == current_user.id)
        .first()
    )

    return ProfileOut(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        coin_balance=current_user.coin_balance,
        is_premium=current_user.is_premium,
        subscription_tier=current_user.subscription_tier,
        goal=onboarding.goal if onboarding else None,
        study_subject=onboarding.study_subject if onboarding else None,
        current_level=onboarding.current_level if onboarding else None,
        daily_study_minutes=(
            onboarding.daily_study_minutes
            if onboarding
            else 60
        ),
        onboarding_completed=(
            bool(onboarding.completed)
            if onboarding
            else False
        ),
    )


@router.put("/me")
def update_profile(
    full_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.full_name = full_name

    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": "Profil yangilandi",
        "full_name": current_user.full_name,
    }