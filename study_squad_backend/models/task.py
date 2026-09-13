from datetime import date, datetime

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship

from database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=False, index=True)
    status = Column(String(30), default="pending", nullable=False)
    ai_reason = Column(Text, nullable=True)
    proof_status = Column(String(30), default="none", nullable=False)
    proof_feedback = Column(Text, nullable=True)
    proof_image = Column(LargeBinary, nullable=True)
    proof_mime_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="tasks")
