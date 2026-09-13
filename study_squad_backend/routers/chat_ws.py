from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from database import SessionLocal
from dependencies import get_current_user
from models.user import User
from models.squad import SquadMember
from models.message import SquadMessage
from services.auth_service import decode_access_token


router = APIRouter(tags=["Squad WebSocket"])


active_connections: dict[int, list[WebSocket]] = {}


def get_user_from_token(token: str, db: Session):
    payload = decode_access_token(token)

    if not payload:
        return None

    user_id = payload.get("sub")

    if not user_id:
        return None

    return (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )


def is_member(
    squad_id: int,
    user_id: int,
    db: Session
):
    return (
        db.query(SquadMember)
        .filter(
            SquadMember.squad_id == squad_id,
            SquadMember.user_id == user_id
        )
        .first()
        is not None
    )


@router.websocket("/ws/squads/{squad_id}")
async def squad_chat(
    websocket: WebSocket,
    squad_id: int,
    token: str,
):
    await websocket.accept()

    db = SessionLocal()

    try:
        user = get_user_from_token(token, db)

        if not user:
            await websocket.close(code=1008)
            return

        if not is_member(squad_id, user.id, db):
            await websocket.close(code=1008)
            return

        if squad_id not in active_connections:
            active_connections[squad_id] = []

        active_connections[squad_id].append(websocket)

        while True:
            text = await websocket.receive_text()

            text = text.strip()

            if not text:
                continue

            message = SquadMessage(
                squad_id=squad_id,
                user_id=user.id,
                message=text,
            )

            db.add(message)
            db.commit()
            db.refresh(message)

            payload = {
                "id": message.id,
                "squad_id": squad_id,
                "user_id": user.id,
                "full_name": user.full_name,
                "message": message.message,
                "created_at": message.created_at.isoformat(),
            }

            for connection in active_connections.get(squad_id, []):
                await connection.send_json(payload)

    except WebSocketDisconnect:
        if squad_id in active_connections:
            if websocket in active_connections[squad_id]:
                active_connections[squad_id].remove(websocket)

    finally:
        db.close()