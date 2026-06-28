"""
RAVAND OS – Agent Endpoint
POST /api/v1/agent – invoke a named RAVAND OS agent.
GET  /api/v1/agent/list – list all available agents.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.database import get_db
from app.services.agent_service import AgentService, get_agent_service
from app.services.ai_service import (
    OllamaConnectionError,
    OllamaModelError,
    OllamaTimeoutError,
)

logger = get_logger(__name__)
router = APIRouter(tags=["Agents"])


# ── Schemas ────────────────────────────────────────────────────────────────────

class AgentRequest(BaseModel):
    """Request payload for POST /api/v1/agent."""

    agent: str = Field(
        ...,
        description=(
            "Agent to invoke. "
            "Available: general, coding, engineering, design, task_automation"
        ),
    )
    message: str = Field(..., min_length=1, max_length=32_000)
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Session ID for memory continuity. Auto-generated if omitted.",
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=32_000)
    extra_context: str | None = Field(
        default=None,
        max_length=8_000,
        description="Optional runtime context appended to the agent's system prompt.",
    )


class AgentResponse(BaseModel):
    """Response payload for POST /api/v1/agent."""

    agent: str
    session_id: str
    content: str
    model: str
    duration_ms: int
    prompt_tokens: int
    completion_tokens: int
    created_at: datetime


class AgentInfo(BaseModel):
    """Summary of a single registered agent."""

    name: str
    class_name: str
    description: str


class AgentListResponse(BaseModel):
    """Response payload for GET /api/v1/agent/list."""

    total: int
    agents: list[AgentInfo]


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post(
    "/agent",
    response_model=AgentResponse,
    summary="Run Agent",
    description=(
        "Invoke a named RAVAND OS agent with a user message. "
        "The agent injects its expert system prompt and memory context "
        "before calling the local Ollama model."
    ),
)
def run_agent(
    request: AgentRequest,
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
) -> AgentResponse:
    """
    Route a user message to the appropriate specialised agent.
    Memory context from previous turns in the same session is injected automatically.
    """
    try:
        result = agent_service.run_agent(
            agent_name=request.agent,
            message=request.message,
            session_id=request.session_id,
            db=db,
            extra_context=request.extra_context,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except OllamaConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI engine unavailable: {exc}",
        ) from exc
    except OllamaTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"AI response timed out: {exc}",
        ) from exc
    except OllamaModelError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Model error: {exc}",
        ) from exc

    return AgentResponse(
        agent=result["agent"],
        session_id=result["session_id"],
        content=result["content"],
        model=result["model"],
        duration_ms=result.get("duration_ms", 0),
        prompt_tokens=result.get("prompt_tokens", 0),
        completion_tokens=result.get("completion_tokens", 0),
        created_at=datetime.now(tz=timezone.utc),
    )


@router.get(
    "/agent/list",
    response_model=AgentListResponse,
    summary="List Available Agents",
    description="Returns all registered RAVAND OS agents with their descriptions.",
)
def list_agents(
    agent_service: AgentService = Depends(get_agent_service),
) -> AgentListResponse:
    """Return metadata for all registered agents."""
    info = agent_service.list_agents()
    agents = [
        AgentInfo(
            name=a["name"],
            class_name=a["class"],
            description=a["description"],
        )
        for a in info
    ]
    return AgentListResponse(total=len(agents), agents=agents)
