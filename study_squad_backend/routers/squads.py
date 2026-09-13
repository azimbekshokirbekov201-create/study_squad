from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from models.squad import Squad, SquadMember
from schemas.squad import SquadCreate, SquadOut, SquadDetailOut, SquadMemberOut

router = APIRouter(prefix="/squads", tags=["Squads"])


@router.post("", response_model=SquadOut, status_code=status.HTTP_201_CREATED)
def create_squad(
    data: SquadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    squad = Squad(name=data.name, goal=data.goal, created_by=current_user.id)
    db.add(squad)
    db.commit()
    db.refresh(squad)

    # Yaratuvchi avtomatik a'zo bo'ladi
    membership = SquadMember(squad_id=squad.id, user_id=current_user.id)
    db.add(membership)
    db.commit()

    return squad


@router.post("/{squad_id}/join", status_code=status.HTTP_204_NO_CONTENT)
def join_squad(
    squad_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    squad = db.query(Squad).filter(Squad.id == squad_id).first()
    if not squad:
        raise HTTPException(status_code=404, detail="Squad topilmadi")

    existing = (
        db.query(SquadMember)
        .filter(SquadMember.squad_id == squad_id, SquadMember.user_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Siz allaqachon shu squadga a'zosiz")

    membership = SquadMember(squad_id=squad_id, user_id=current_user.id)
    db.add(membership)
    db.commit()


@router.get("/{squad_id}", response_model=SquadDetailOut)
def get_squad(
    squad_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    squad = db.query(Squad).filter(Squad.id == squad_id).first()
    if not squad:
        raise HTTPException(status_code=404, detail="Squad topilmadi")

    members = [
        SquadMemberOut(
            user_id=m.user.id,
            full_name=m.user.full_name,
            joined_at=m.joined_at,
        )
        for m in squad.members
    ]

    return SquadDetailOut(
        id=squad.id,
        name=squad.name,
        goal=squad.goal,
        created_by=squad.created_by,
        created_at=squad.created_at,
        members=members,
    )
