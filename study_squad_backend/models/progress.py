from datetime import datetime

from sqlalchemy import Column, Integer, Float, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class DailyProgress(Base):
    __tablename__ = "daily_progress"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_date"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, nullable=False)
    tasks_total = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    progress_percent = Column(Float, default=0)
    is_day_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="daily_progress")


class WeeklySummary(Base):
    __tablename__ = "weekly_summary"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    week_start_date = Column(Date, nullable=False)
    week_end_date = Column(Date, nullable=False)
    streak_days = Column(Integer, default=0)
    avg_progress_percent = Column(Float, default=0)
    coins_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="weekly_summaries")
