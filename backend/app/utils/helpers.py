"""
RAVAND OS – General Utilities
==============================
Standalone utility functions with no circular import risk.
Import freely from any layer.
"""

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


# ── Text Utilities ─────────────────────────────────────────────────────────────

def truncate_text(text: str, max_length: int = 100, suffix: str = "…") -> str:
    """
    Truncate text to max_length characters, appending suffix if cut.
    Does not cut in the middle of a word.

    Args:
        text:       Input string.
        max_length: Maximum character length of the result (including suffix).
        suffix:     String appended when text is truncated.

    Returns:
        Truncated string.
    """
    if len(text) <= max_length:
        return text
    cut_point = max_length - len(suffix)
    # Find the last space before the cut point to avoid mid-word cuts
    last_space = text.rfind(" ", 0, cut_point)
    cut = last_space if last_space > 0 else cut_point
    return text[:cut] + suffix


def sanitize_title(text: str, max_length: int = 80) -> str:
    """
    Convert arbitrary text into a clean session title.
    Strips excess whitespace and newlines.
    """
    clean = re.sub(r"\s+", " ", text).strip()
    return truncate_text(clean, max_length)


def estimate_tokens(text: str) -> int:
    """
    Rough token count estimate for a text string.
    Uses the ~4 characters per token heuristic for English / Latin text.
    Not accurate for Arabic/Persian – those average ~2 chars per token.
    Useful for guard-rail checks before sending to the model.

    Args:
        text: Input string.

    Returns:
        Estimated token count (integer).
    """
    if not text:
        return 0
    # Simple character-based estimate
    return max(1, len(text) // 4)


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 100,
) -> list[str]:
    """
    Split text into overlapping chunks for knowledge base ingestion.
    Tries to split on paragraph or sentence boundaries.

    Args:
        text:       Input text.
        chunk_size: Target characters per chunk.
        overlap:    Characters of overlap between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # Try to break on a paragraph boundary
            para_break = text.rfind("\n\n", start, end)
            if para_break > start + chunk_size // 2:
                end = para_break
            else:
                # Fall back to sentence boundary
                sentence_break = max(
                    text.rfind(". ", start, end),
                    text.rfind("! ", start, end),
                    text.rfind("? ", start, end),
                )
                if sentence_break > start + chunk_size // 2:
                    end = sentence_break + 1
        chunks.append(text[start:end].strip())
        start = end - overlap

    return [c for c in chunks if c]


# ── Hashing Utilities ──────────────────────────────────────────────────────────

def hash_content(content: str) -> str:
    """
    Return a SHA-256 hex digest of the content string.
    Used for deduplication in the knowledge base.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ── JSON Utilities ─────────────────────────────────────────────────────────────

def safe_json_loads(text: str, default: Any = None) -> Any:
    """
    Parse a JSON string, returning `default` on any error.
    Never raises.
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: Any = None) -> str:
    """
    Serialise an object to JSON string, returning str(default) on error.
    Never raises.
    """
    try:
        return json.dumps(obj, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(default) if default is not None else "null"


# ── Timing Utilities ───────────────────────────────────────────────────────────

def now_utc() -> datetime:
    """Return the current UTC datetime with timezone info."""
    return datetime.now(tz=timezone.utc)


def ms_since(start: float) -> int:
    """
    Return milliseconds elapsed since a perf_counter start time.

    Usage:
        t = time.perf_counter()
        # ... do work ...
        elapsed = ms_since(t)
    """
    return int((time.perf_counter() - start) * 1000)


# ── Decorator Utilities ────────────────────────────────────────────────────────

def log_duration(logger_fn: Callable[[str], None], label: str = ""):
    """
    Decorator that logs the wall-clock duration of a function call.

    Usage:
        @log_duration(logger.debug, "my_function")
        def my_function(): ...
    """
    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = fn(*args, **kwargs)
                duration = ms_since(start)
                logger_fn(f"{label or fn.__name__} completed in {duration}ms")
                return result
            except Exception as exc:
                duration = ms_since(start)
                logger_fn(f"{label or fn.__name__} failed after {duration}ms: {exc}")
                raise
        return wrapper  # type: ignore[return-value]
    return decorator


# ── Validation Utilities ───────────────────────────────────────────────────────

def is_valid_uuid(value: str) -> bool:
    """Return True if value is a valid UUID4 string."""
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    return bool(uuid_pattern.match(value))


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a float value between min_val and max_val."""
    return max(min_val, min(max_val, value))
