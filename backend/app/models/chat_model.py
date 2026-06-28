"""
RAVAND OS – Chat Message ORM Model
Stores individual messages within a ChatSession.
"""

import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class ChatMessage(Base):
    """
    A single message exchanged within a ChatSession.
    role is either 'user' or 'assistant'.
    """

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )  # 'user' | 'assistant' | 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship – back-reference to parent session
    session: Mapped["ChatSession"] = relationship(  # noqa: F821
        "ChatSession",
        back_populates="messages",
    )

    def __repr__(self) -> str:
        preview = self.content[:40].replace("\n", " ")
        return f"<ChatMessage id={self.id!r} role={self.role!r} content={preview!r}>"
