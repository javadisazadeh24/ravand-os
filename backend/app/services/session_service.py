"""
RAVAND OS – Session Service
Business logic for managing ChatSession lifecycle.
Separates persistence concerns from the API layer.
"""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.chat_model import ChatMessage
from app.models.session_model import ChatSession

logger = get_logger(__name__)


class SessionService:
    """
    Manages the lifecycle of ChatSession and ChatMessage records.

    Methods are stateless with respect to the database – they accept
    a Session object each time, making them easy to test and compatible
    with FastAPI's dependency-injected session pattern.
    """

    # ── Sessions ───────────────────────────────────────────────────────────────

    def create_session(
        self,
        db: Session,
        model: str,
        title: str = "New Chat",
    ) -> ChatSession:
        """
        Create and persist a new ChatSession.

        Args:
            db:    SQLAlchemy session.
            model: Ollama model name used in this session.
            title: Human-readable title (auto-updated after first exchange).

        Returns:
            The newly created ChatSession ORM instance.
        """
        session = ChatSession(
            id=str(uuid.uuid4()),
            title=title,
            model=model,
        )
        db.add(session)
        db.flush()  # get the ID without committing
        logger.debug("Session created | id=%s | model=%s", session.id, model)
        return session

    def get_session(self, db: Session, session_id: str) -> ChatSession | None:
        """Return a ChatSession by ID, or None if not found."""
        return db.get(ChatSession, session_id)

    def update_session_title(
        self,
        db: Session,
        session_id: str,
        title: str,
    ) -> None:
        """Update the display title of a session."""
        session = self.get_session(db, session_id)
        if session:
            session.title = title[:255]
            db.flush()

    def list_sessions(
        self,
        db: Session,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """
        Return a list of session summaries ordered by most recently updated.

        Returns list of dicts with:
            id, title, model, message_count, created_at, updated_at
        """
        stmt = (
            select(
                ChatSession.id,
                ChatSession.title,
                ChatSession.model,
                func.count(ChatMessage.id).label("message_count"),
                ChatSession.created_at,
                ChatSession.updated_at,
            )
            .outerjoin(ChatMessage, ChatMessage.session_id == ChatSession.id)
            .where(ChatSession.is_active.is_(True))
            .group_by(ChatSession.id)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = db.execute(stmt).all()
        return [row._asdict() for row in rows]

    def delete_session(self, db: Session, session_id: str) -> bool:
        """
        Soft-delete a session by setting is_active=False.
        Messages are preserved in the database for potential recovery.

        Returns True if found and deleted, False if not found.
        """
        session = self.get_session(db, session_id)
        if not session:
            return False
        session.is_active = False
        db.flush()
        logger.info("Session soft-deleted | id=%s", session_id)
        return True

    # ── Messages ───────────────────────────────────────────────────────────────

    def add_message(
        self,
        db: Session,
        session_id: str,
        role: str,
        content: str,
        model: str | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        duration_ms: int | None = None,
    ) -> ChatMessage:
        """
        Persist a single ChatMessage record.

        Args:
            db:                SQLAlchemy session.
            session_id:        Parent ChatSession ID.
            role:              'user' | 'assistant' | 'system'.
            content:           Message text.
            model:             Model that generated the message (for assistant).
            prompt_tokens:     Input token count.
            completion_tokens: Output token count.
            duration_ms:       Inference time for this message.

        Returns:
            The persisted ChatMessage instance.
        """
        message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            duration_ms=duration_ms,
        )
        db.add(message)
        db.flush()
        logger.debug(
            "Message saved | session=%s | role=%s | id=%s",
            session_id,
            role,
            message.id,
        )
        return message

    def get_conversation_history(
        self,
        db: Session,
        session_id: str,
        limit: int = 40,
    ) -> list[dict[str, str]]:
        """
        Return the last `limit` messages in Ollama chat format.
        Each dict has 'role' and 'content' keys.

        Args:
            db:         SQLAlchemy session.
            session_id: Target session ID.
            limit:      Maximum messages to include (most recent).

        Returns:
            List of {"role": ..., "content": ...} dicts, oldest first.
        """
        stmt = (
            select(ChatMessage.role, ChatMessage.content, ChatMessage.created_at)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        rows = db.execute(stmt).all()
        # Reverse so messages are chronological (oldest first)
        return [{"role": r.role, "content": r.content} for r in reversed(rows)]

    def get_messages(
        self,
        db: Session,
        session_id: str,
        limit: int = 100,
    ) -> list[ChatMessage]:
        """Return full ChatMessage records for a session, oldest first."""
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        return list(db.scalars(stmt).all())


# ── Singleton ──────────────────────────────────────────────────────────────────

_session_service_instance: SessionService | None = None


def get_session_service() -> SessionService:
    """FastAPI dependency for the SessionService singleton."""
    global _session_service_instance
    if _session_service_instance is None:
        _session_service_instance = SessionService()
    return _session_service_instance
