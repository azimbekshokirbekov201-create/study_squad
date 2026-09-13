from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import settings

# SQLite uchun check_same_thread=False kerak (FastAPI ko'p thread ishlatadi)
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Har bir so'rov uchun database session beradi, oxirida yopadi."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
