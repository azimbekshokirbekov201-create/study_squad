from datetime import date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.task import Task
from models.user import User
from schemas.task import TaskGenerateIn, TaskOut, TaskProofOut
from services.task_ai_service import generate_tasks, check_proof

router = APIRouter(prefix="/tasks", tags=["Tasks"])

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 8 * 1024 * 1024


@router.post("/generate", response_model=list[TaskOut])
def generate_today_tasks(
    data: TaskGenerateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        items = generate_tasks(data.goal, data.count)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    today = date.today()
    created = []
    for item in items:
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        task = Task(
            user_id=current_user.id,
            title=title[:300],
            description=str(item.get("description", ""))[:5000],
            ai_reason=str(item.get("ai_reason", ""))[:5000],
            date=today,
        )
        db.add(task)
        created.append(task)
    db.commit()
    for task in created:
        db.refresh(task)
    return created


@router.get("/today", response_model=list[TaskOut])
def get_today_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Task)
        .filter(Task.user_id == current_user.id, Task.date == date.today())
        .order_by(Task.id)
        .all()
    )


@router.post("/{task_id}/proof", response_model=TaskProofOut)
def submit_task_proof(
    task_id: int,
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Vazifa topilmadi")
    if image.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Faqat JPG, PNG yoki WEBP rasm yuboring.")

    data = image.file.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Rasm hajmi 8 MB dan oshmasin.")

    try:
        status, feedback = check_proof(task.title, task.description or "", data, image.content_type)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    task.proof_status = status
    task.proof_feedback = feedback
    task.proof_image = data
    task.proof_mime_type = image.content_type
    if status == "approved":
        task.status = "completed"
        task.completed_at = datetime.utcnow()
    else:
        task.status = "pending"
    db.commit()

    return TaskProofOut(
        task_id=task.id,
        status=status,
        proof_status=status,
        feedback=feedback,
        task_completed=status == "approved",
    )
