"""
RAVAND OS – Chat Pydantic Schemas
Request/response models for the chat endpoint.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# ── Request ────────────────────────────────────────────────────────────────────

class ChatMessageIn(BaseModel):
    """A single message in a chat request."""

    role: Literal["user", "assistant", "system"] = "user"
    content: str = Field(..., min_length=1, max_length=32_000)


class ChatRequest(BaseModel):
    """
    Incoming payload for POST /api/v1/chat.
    Supports single-turn and multi-turn conversation.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=32_000,
        description="The user's message to send to the AI.",
    )
    session_id: str | None = Field(
        default=None,
        description="Existing session ID to continue a conversation. "
                    "Omit to start a new session.",
    )
    model: str | None = Field(
        default=None,
        description="Override the default Ollama model for this request.",
    )
    system_prompt: str | None = Field(
        default=None,
        max_length=8_000,
        description="Optional system-level instruction to prepend.",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature. Higher = more creative.",
    )
    max_tokens: int = Field(
        default=2048,
        ge=1,
        le=32_000,
        description="Maximum tokens in the AI response.",
    )

    @field_validator("message")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Message must not be blank.")
        return stripped


# ── Response ───────────────────────────────────────────────────────────────────

class TokenUsage(BaseModel):
    """Token consumption statistics returned by Ollama."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    """
    Response payload for POST /api/v1/chat.
    """

    session_id: str = Field(..., description="Session ID (new or continued).")
    message_id: str = Field(..., description="Unique ID of the assistant message.")
    role: Literal["assistant"] = "assistant"
    content: str = Field(..., description="The AI-generated response text.")
    model: str = Field(..., description="Ollama model that produced the response.")
    usage: TokenUsage = Field(default_factory=TokenUsage)
    duration_ms: int = Field(..., description="Wall-clock inference time in milliseconds.")
    created_at: datetime = Field(..., description="Timestamp of the response.")


# ── Session Schemas ────────────────────────────────────────────────────────────

class SessionSummary(BaseModel):
    """Lightweight session summary for listing endpoints."""

    id: str
    title: str
    model: str
    message_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageRecord(BaseModel):
    """Single message record for history retrieval."""

    id: str
    session_id: str
    role: str
    content: str
    model: str | None
    duration_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
