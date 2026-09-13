from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=True, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=False)

    coin_balance = Column(Integer, default=0)
    is_premium = Column(Boolean, default=False)
    premium_expires_at = Column(DateTime, nullable=True)

    # Tarif: "basic" (bepul/coin), "pro", "master"
    subscription_tier = Column(String, default="basic", nullable=False)
    stripe_customer_id = Column(String, nullable=True)

    # Basic tarifda kunlik AI Coach so'rovlarini cheklash uchun
    ai_requests_today = Column(Integer, default=0)
    ai_requests_date = Column(Date, nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow)  # individual hafta shu yerdan hisoblanadi
    created_at = Column(DateTime, default=datetime.utcnow)

    squad_memberships = relationship("SquadMember", back_populates="user")
    daily_progress = relationship("DailyProgress", back_populates="user")
    weekly_summaries = relationship("WeeklySummary", back_populates="user")
    coin_transactions = relationship("CoinTransaction", back_populates="user")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
