"""
RAVAND OS – Database ORM Models
================================
All SQLAlchemy ORM models for RAVAND OS are defined here.

Tables:
  - users          – system users (local, offline, no auth required currently)
  - chat_sessions  – groups of messages forming a conversation
  - chat_messages  – individual messages within a session
  - memory_records – long-term memory storage
  - tasks          – task automation engine records
  - logs           – structured application event log

Design notes:
  - All primary keys use UUID strings for portability.
  - All timestamps include timezone info.
  - Designed for SQLite; all types are PostgreSQL-compatible for future migration.
  - Foreign keys use CASCADE delete to keep the database self-cleaning.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


# ── Users ──────────────────────────────────────────────────────────────────────

class User(Base):
    """
    Local system user.
    RAVAND OS is a single-machine, offline OS. Authentication is minimal.
    This table is designed to support multiple local profiles in the future.
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    preferred_language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    preferred_agent: Mapped[str] = mapped_column(String(64), nullable=False, default="general")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User username={self.username!r}>"


# ── Chat Sessions ──────────────────────────────────────────────────────────────

class ChatSession(Base):
    """
    A logical conversation container.
    Groups multiple ChatMessage rows under a shared context.
    """

    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New Chat")
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    agent: Mapped[str] = mapped_column(String(64), nullable=False, default="general")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User | None"] = relationship("User", back_populates="sessions")
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def __repr__(self) -> str:
        return f"<ChatSession id={self.id!r} title={self.title!r}>"


# ── Chat Messages ──────────────────────────────────────────────────────────────

class ChatMessage(Base):
    """
    A single message within a ChatSession.
    Stores content, metadata, and token usage.
    """

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    agent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")

    __table_args__ = (
        Index("ix_chat_messages_session_created", "session_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id!r} role={self.role!r}>"


# ── Memory Records ─────────────────────────────────────────────────────────────

class MemoryRecord(Base):
    """
    Long-term memory storage.
    Stores facts, summaries, and notable conversation moments.

    Future upgrade:
      Add an embedding BLOB column to store vector representations
      when a local embedding model becomes available.
    """

    __tablename__ = "memory_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    memory_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="general"
    )  # 'fact' | 'summary' | 'preference' | 'general'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    tags: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON array
    # Reserved for future vector embedding storage
    # embedding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_memory_records_type_importance", "memory_type", "importance"),
    )

    def __repr__(self) -> str:
        return f"<MemoryRecord id={self.id!r} type={self.memory_type!r}>"


# ── Tasks ──────────────────────────────────────────────────────────────────────

class Task(Base):
    """
    Task automation engine record.
    Represents a unit of work created by the TaskAutomationAgent
    or submitted directly via the tasks API.
    """

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="pending"
    )  # 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled'
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)  # 1=highest
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_tasks_status_priority", "status", "priority"),
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id!r} title={self.title!r} status={self.status!r}>"


# ── Application Logs ───────────────────────────────────────────────────────────

class AppLog(Base):
    """
    Structured application event log stored in SQLite.
    Complements file-based logging with queryable, persistent records.
    Useful for debugging, auditing, and dashboard display.
    """

    __tablename__ = "app_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String(10), nullable=False)
    logger_name: Mapped[str] = mapped_column(String(128), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    extra: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_app_logs_level_created", "level", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AppLog level={self.level!r} message={self.message[:40]!r}>"
