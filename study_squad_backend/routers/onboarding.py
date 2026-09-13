from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from models.onboarding import UserOnboarding
from schemas.onboarding import OnboardingCreate, OnboardingOut


router = APIRouter(
    prefix="/onboarding",
    tags=["Onboarding"]
)


@router.post("", response_model=OnboardingOut)
def save_onboarding(
    data: OnboardingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    onboarding = (
        db.query(UserOnboarding)
        .filter(UserOnboarding.user_id == current_user.id)
        .first()
    )

    interests_text = ",".join(data.interests)

    if onboarding:
        onboarding.goal = data.goal
        onboarding.study_subject = data.study_subject
        onboarding.current_level = data.current_level
        onboarding.daily_study_minutes = data.daily_study_minutes
        onboarding.interests = interests_text
        onboarding.completed = 1
    else:
        onboarding = UserOnboarding(
            user_id=current_user.id,
            goal=data.goal,
            study_subject=data.study_subject,
            current_level=data.current_level,
            daily_study_minutes=data.daily_study_minutes,
            interests=interests_text,
            completed=1,
        )

        db.add(onboarding)

    db.commit()
    db.refresh(onboarding)

    return {
        "goal": onboarding.goal,
        "study_subject": onboarding.study_subject,
        "current_level": onboarding.current_level,
        "daily_study_minutes": onboarding.daily_study_minutes,
        "interests": (
            onboarding.interests.split(",")
            if onboarding.interests
            else []
        ),
        "completed": bool(onboarding.completed),
    }


@router.get("/me", response_model=OnboardingOut)
def get_my_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    onboarding = (
        db.query(UserOnboarding)
        .filter(UserOnboarding.user_id == current_user.id)
        .first()
    )

    if not onboarding:
        return OnboardingOut(
            goal=None,
            study_subject=None,
            current_level=None,
            daily_study_minutes=60,
            interests=[],
            completed=False,
        )

    return {
        "goal": onboarding.goal,
        "study_subject": onboarding.study_subject,
        "current_level": onboarding.current_level,
        "daily_study_minutes": onboarding.daily_study_minutes,
        "interests": (
            onboarding.interests.split(",")
            if onboarding.interests
            else []
        ),
        "completed": bool(onboarding.completed),
    }