from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class Squad(Base):
    __tablename__ = "squads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    goal = Column(String, nullable=True)  # masalan: "IELTS 7.0 uchun 30 kun"
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("SquadMember", back_populates="squad")


class SquadMember(Base):
    __tablename__ = "squad_members"
    __table_args__ = (UniqueConstraint("squad_id", "user_id", name="uq_squad_user"),)

    id = Column(Integer, primary_key=True, index=True)
    squad_id = Column(Integer, ForeignKey("squads.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    joined_at = Column(DateTime, default=datetime.utcnow)

    squad = relationship("Squad", back_populates="members")
    user = relationship("User", back_populates="squad_memberships")
