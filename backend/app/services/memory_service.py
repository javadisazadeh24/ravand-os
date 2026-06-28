"""
RAVAND OS – Memory Service
==========================
Provides a two-tier memory architecture:

  Tier 1 – Short-term memory (in-process dict, session-scoped)
    Fast, ephemeral. Lost when the process restarts.
    Used for within-session context window management.

  Tier 2 – Long-term memory (SQLite-persisted via MemoryRecord ORM)
    Durable across restarts.
    Stores summaries, facts, and notable moments.
    Designed to be swapped for a vector store (e.g., ChromaDB, FAISS)
    without changing the public API.

Architecture note:
  All public methods take a db: Session parameter.
  The service itself is stateless (except for the short-term cache).
  This makes it injectable, testable, and safe under concurrent requests.
"""

import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.models import MemoryRecord

logger = get_logger(__name__)
settings = get_settings()


# ── Short-term memory data structures ─────────────────────────────────────────

@dataclass
class ContextWindow:
    """
    Represents the working memory for a single session.
    Holds recent message turns and arbitrary key-value facts.
    """

    session_id: str
    turns: list[dict[str, str]] = field(default_factory=list)
    facts: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.monotonic)
    last_accessed: float = field(default_factory=time.monotonic)

    def touch(self) -> None:
        """Update last-accessed timestamp."""
        self.last_accessed = time.monotonic()

    def add_turn(self, role: str, content: str) -> None:
        """Append a message turn to the context window."""
        self.turns.append({"role": role, "content": content})
        self.touch()

    def get_recent_turns(self, limit: int = 20) -> list[dict[str, str]]:
        """Return the most recent `limit` turns, oldest first."""
        return self.turns[-limit:]

    def set_fact(self, key: str, value: Any) -> None:
        """Store an arbitrary named fact in this session's memory."""
        self.facts[key] = value
        self.touch()


# ── Memory Service ─────────────────────────────────────────────────────────────

class MemoryService:
    """
    Two-tier memory manager for RAVAND OS.

    Short-term: in-memory ContextWindow per session_id.
    Long-term:  MemoryRecord rows in SQLite.

    Future upgrade path:
      Replace _write_long_term / _search_long_term implementations
      with calls to a vector store without touching callers.
    """

    # Maximum number of sessions to keep in short-term cache
    _MAX_SHORT_TERM_SESSIONS: int = 200
    # Maximum age (seconds) of an idle short-term session before eviction
    _SHORT_TERM_TTL: float = 3600.0  # 1 hour

    def __init__(self) -> None:
        # session_id → ContextWindow
        self._short_term: dict[str, ContextWindow] = {}
        logger.info("MemoryService initialised.")

    # ── Short-term memory ──────────────────────────────────────────────────────

    def _get_or_create_context(self, session_id: str) -> ContextWindow:
        """Return the ContextWindow for a session, creating it if missing."""
        if session_id not in self._short_term:
            self._evict_stale_sessions()
            self._short_term[session_id] = ContextWindow(session_id=session_id)
            logger.debug("Short-term context created | session=%s", session_id)
        return self._short_term[session_id]

    def _evict_stale_sessions(self) -> None:
        """
        Remove idle sessions to prevent unbounded memory growth.
        Evicts sessions that have not been accessed within TTL, or,
        if the cache is over the size limit, the oldest sessions.
        """
        now = time.monotonic()
        stale = [
            sid
            for sid, ctx in self._short_term.items()
            if now - ctx.last_accessed > self._SHORT_TERM_TTL
        ]
        for sid in stale:
            del self._short_term[sid]
            logger.debug("Short-term context evicted (TTL) | session=%s", sid)

        if len(self._short_term) >= self._MAX_SHORT_TERM_SESSIONS:
            # Evict the oldest session by last_accessed
            oldest = min(self._short_term, key=lambda s: self._short_term[s].last_accessed)
            del self._short_term[oldest]
            logger.debug("Short-term context evicted (capacity) | session=%s", oldest)

    def add_to_short_term(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        """
        Append a message turn to the session's short-term context window.

        Args:
            session_id: The active session ID.
            role:       'user' | 'assistant' | 'system'
            content:    Message text.
        """
        ctx = self._get_or_create_context(session_id)
        ctx.add_turn(role, content)
        logger.debug(
            "Short-term turn added | session=%s | role=%s | turns=%d",
            session_id,
            role,
            len(ctx.turns),
        )

    def get_short_term_context(
        self,
        session_id: str,
        limit: int = 20,
    ) -> list[dict[str, str]]:
        """
        Retrieve recent turns from the session's short-term memory.

        Args:
            session_id: Session to retrieve context for.
            limit:      Maximum number of turns to return (most recent).

        Returns:
            List of {"role": ..., "content": ...} dicts, oldest first.
        """
        ctx = self._get_or_create_context(session_id)
        turns = ctx.get_recent_turns(limit)
        logger.debug(
            "Short-term context retrieved | session=%s | turns=%d",
            session_id,
            len(turns),
        )
        return turns

    def set_session_fact(
        self,
        session_id: str,
        key: str,
        value: Any,
    ) -> None:
        """
        Store an arbitrary named fact in the session's short-term context.
        Useful for agent tools to share state within a session.
        """
        ctx = self._get_or_create_context(session_id)
        ctx.set_fact(key, value)

    def get_session_fact(self, session_id: str, key: str) -> Any | None:
        """Retrieve a named fact from short-term memory, or None if absent."""
        ctx = self._short_term.get(session_id)
        if ctx is None:
            return None
        return ctx.facts.get(key)

    def clear_short_term(self, session_id: str) -> None:
        """Discard all short-term memory for a session."""
        if session_id in self._short_term:
            del self._short_term[session_id]
            logger.info("Short-term context cleared | session=%s", session_id)

    # ── Long-term memory ───────────────────────────────────────────────────────

    def write_long_term(
        self,
        db: Session,
        session_id: str,
        content: str,
        memory_type: str = "general",
        importance: float = 0.5,
        tags: list[str] | None = None,
    ) -> MemoryRecord:
        """
        Persist a memory to long-term storage (SQLite).

        Args:
            db:          SQLAlchemy session.
            session_id:  Source session ID.
            content:     The text content to remember.
            memory_type: Category label ('fact', 'summary', 'preference', etc.).
            importance:  Salience score 0.0–1.0 (higher = more important).
            tags:        Optional list of string tags for retrieval filtering.

        Returns:
            The persisted MemoryRecord ORM instance.
        """
        import json

        record = MemoryRecord(
            id=str(uuid.uuid4()),
            session_id=session_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            tags=json.dumps(tags or []),
        )
        db.add(record)
        db.flush()
        logger.info(
            "Long-term memory written | id=%s | session=%s | type=%s | importance=%.2f",
            record.id,
            session_id,
            memory_type,
            importance,
        )
        return record

    def search_long_term(
        self,
        db: Session,
        query: str,
        session_id: str | None = None,
        memory_type: str | None = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> list[MemoryRecord]:
        """
        Full-text search over long-term memories.

        Currently uses SQLite LIKE search. The return value and call
        signature are designed so this method can be replaced with a
        vector similarity search without changing callers.

        Args:
            db:             SQLAlchemy session.
            query:          Search string (substring match).
            session_id:     Restrict to a specific session (optional).
            memory_type:    Filter by type label (optional).
            limit:          Maximum results to return.
            min_importance: Only return records with importance >= this value.

        Returns:
            List of MemoryRecord instances ordered by importance descending.
        """
        stmt = (
            select(MemoryRecord)
            .where(MemoryRecord.content.ilike(f"%{query}%"))
            .where(MemoryRecord.importance >= min_importance)
        )

        if session_id:
            stmt = stmt.where(MemoryRecord.session_id == session_id)

        if memory_type:
            stmt = stmt.where(MemoryRecord.memory_type == memory_type)

        stmt = stmt.order_by(MemoryRecord.importance.desc()).limit(limit)

        results = list(db.scalars(stmt).all())
        logger.debug(
            "Long-term search | query=%r | results=%d",
            query,
            len(results),
        )
        return results

    def get_long_term_context_string(
        self,
        db: Session,
        query: str,
        session_id: str | None = None,
        limit: int = 5,
    ) -> str:
        """
        Convenience wrapper: search long-term memory and return a formatted
        string ready for injection into an AI system prompt.

        Returns empty string if no relevant memories are found.
        """
        records = self.search_long_term(
            db=db,
            query=query,
            session_id=session_id,
            limit=limit,
        )
        if not records:
            return ""

        lines = ["[Relevant memories from long-term storage:]"]
        for rec in records:
            lines.append(f"  • [{rec.memory_type}] {rec.content}")
        return "\n".join(lines)

    def delete_long_term(self, db: Session, memory_id: str) -> bool:
        """
        Delete a specific long-term memory record by ID.

        Returns True if deleted, False if not found.
        """
        record = db.get(MemoryRecord, memory_id)
        if not record:
            return False
        db.delete(record)
        db.flush()
        logger.info("Long-term memory deleted | id=%s", memory_id)
        return True

    def summarise_and_compress(
        self,
        session_id: str,
        db: Session,
        ai_service: Any,
        keep_last_turns: int = 6,
    ) -> str:
        """
        Compress old short-term context into a long-term summary.

        Workflow:
          1. Take all but the last `keep_last_turns` turns from short-term.
          2. Ask the AI to summarise them in 2-3 sentences.
          3. Store the summary in long-term memory.
          4. Prune the compressed turns from short-term.

        Returns:
            The summary text, or empty string if nothing to compress.
        """
        ctx = self._short_term.get(session_id)
        if not ctx or len(ctx.turns) <= keep_last_turns:
            return ""

        turns_to_compress = ctx.turns[:-keep_last_turns]
        ctx.turns = ctx.turns[-keep_last_turns:]

        dialogue_text = "\n".join(
            f"{t['role'].upper()}: {t['content']}" for t in turns_to_compress
        )

        summary_prompt = (
            "Summarise the following conversation in 2-3 concise sentences. "
            "Focus on key facts, decisions, and context that may be relevant "
            "in a future conversation.\n\n"
            f"{dialogue_text}"
        )

        try:
            result = ai_service.generate(prompt=summary_prompt, max_tokens=256)
            summary = result["content"].strip()
        except Exception as exc:
            logger.error("Memory compression AI call failed: %s", exc)
            summary = f"[Compressed {len(turns_to_compress)} turns – summary unavailable]"

        self.write_long_term(
            db=db,
            session_id=session_id,
            content=summary,
            memory_type="summary",
            importance=0.7,
        )
        logger.info(
            "Memory compressed | session=%s | turns_compressed=%d",
            session_id,
            len(turns_to_compress),
        )
        return summary

    # ── Statistics ─────────────────────────────────────────────────────────────

    def get_stats(self, db: Session) -> dict[str, Any]:
        """Return memory system statistics for diagnostics."""
        total_long_term = db.execute(
            text("SELECT COUNT(*) FROM memory_records")
        ).scalar_one()

        return {
            "short_term_sessions": len(self._short_term),
            "long_term_records": total_long_term,
            "short_term_ttl_seconds": self._SHORT_TERM_TTL,
            "max_short_term_sessions": self._MAX_SHORT_TERM_SESSIONS,
        }


# ── Singleton ──────────────────────────────────────────────────────────────────

_memory_service_instance: MemoryService | None = None


def get_memory_service() -> MemoryService:
    """FastAPI dependency for the MemoryService singleton."""
    global _memory_service_instance
    if _memory_service_instance is None:
        _memory_service_instance = MemoryService()
    return _memory_service_instance
