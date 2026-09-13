from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from models.squad import SquadMember
from models.message import SquadMessage
from schemas.message import MessageCreate, MessageOut


router = APIRouter(
    prefix="/squads",
    tags=["Squad Chat"]
)


def check_membership(
    squad_id: int,
    user_id: int,
    db: Session
):
    membership = (
        db.query(SquadMember)
        .filter(
            SquadMember.squad_id == squad_id,
            SquadMember.user_id == user_id
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Siz bu squad a'zosi emassiz"
        )


@router.get(
    "/{squad_id}/messages",
    response_model=list[MessageOut]
)
def get_messages(
    squad_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_membership(squad_id, current_user.id, db)

    messages = (
        db.query(SquadMessage)
        .filter(SquadMessage.squad_id == squad_id)
        .order_by(SquadMessage.created_at.asc())
        .limit(100)
        .all()
    )

    return [
        MessageOut(
            id=m.id,
            squad_id=m.squad_id,
            user_id=m.user_id,
            full_name=m.user.full_name,
            message=m.message,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.post(
    "/{squad_id}/messages",
    response_model=MessageOut
)
def send_message(
    squad_id: int,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_membership(squad_id, current_user.id, db)

    message = SquadMessage(
        squad_id=squad_id,
        user_id=current_user.id,
        message=data.message.strip(),
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return MessageOut(
        id=message.id,
        squad_id=message.squad_id,
        user_id=message.user_id,
        full_name=current_user.full_name,
        message=message.message,
        created_at=message.created_at,
    )