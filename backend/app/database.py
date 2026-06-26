"""
Database engine and base model declaration for RAVAND OS.
Uses SQLite for MVP; swap DATABASE_URL in .env to migrate later.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite
    echo=settings.DEBUG,
)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass
