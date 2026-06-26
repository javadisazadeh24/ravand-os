"""
SQLAlchemy session factory and FastAPI dependency for RAVAND OS.
"""

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.database.database import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per request
    and ensures it is closed afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
