from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class SquadMessage(Base):
    __tablename__ = "squad_messages"

    id = Column(Integer, primary_key=True, index=True)

    squad_id = Column(
        Integer,
        ForeignKey("squads.id"),
        nullable=False,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    message = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User")
    squad = relationship("Squad")
