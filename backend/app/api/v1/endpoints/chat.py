"""
RAVAND OS – Chat Endpoint
POST /api/v1/chat – AI conversation with session persistence.

Flow:
  1. Validate request.
  2. Resolve or create a ChatSession.
  3. Persist the user message.
  4. Load conversation history from the session.
  5. Inject system prompt from KnowledgeService.
  6. Call AIService.chat() → Ollama.
  7. Persist the assistant response.
  8. Auto-update session title on first exchange.
  9. Return structured ChatResponse.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.database.database import get_db
from app.schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
    MessageRecord,
    SessionSummary,
    TokenUsage,
)
from app.services.ai_service import (
    AIService,
    OllamaConnectionError,
    OllamaModelError,
    OllamaTimeoutError,
    get_ai_service,
)
from app.services.knowledge_service import KnowledgeService, get_knowledge_service
from app.services.session_service import SessionService, get_session_service

logger = get_logger(__name__)
router = APIRouter(tags=["Chat"])


# ── Chat ───────────────────────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="AI Chat",
    description=(
        "Send a message to the RAVAND OS AI engine (local Ollama). "
        "Supports multi-turn conversation via session_id. "
        "A new session is created automatically if session_id is omitted."
    ),
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    ai_service: AIService = Depends(get_ai_service),
    session_service: SessionService = Depends(get_session_service),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> ChatResponse:
    """
    Main conversational endpoint.
    Handles session management, history retrieval, AI inference, and persistence.
    """
    target_model = request.model or settings.OLLAMA_MODEL

    # ── 1. Resolve or create session ───────────────────────────────────────────
    if request.session_id:
        chat_session = session_service.get_session(db, request.session_id)
        if not chat_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{request.session_id}' not found. "
                       "Omit session_id to start a new conversation.",
            )
        is_new_session = False
    else:
        chat_session = session_service.create_session(
            db=db,
            model=target_model,
            title="New Chat",
        )
        is_new_session = True

    session_id = chat_session.id

    # ── 2. Persist user message ────────────────────────────────────────────────
    session_service.add_message(
        db=db,
        session_id=session_id,
        role="user",
        content=request.message,
    )

    # ── 3. Build conversation history ──────────────────────────────────────────
    history = session_service.get_conversation_history(
        db=db,
        session_id=session_id,
        limit=40,
    )

    # ── 4. Build system prompt ─────────────────────────────────────────────────
    system_prompt = request.system_prompt or knowledge_service.get_system_prompt()

    # ── 5. AI inference ────────────────────────────────────────────────────────
    try:
        ai_result = ai_service.chat(
            messages=history,
            model=target_model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=system_prompt,
        )
    except OllamaConnectionError as exc:
        logger.error("Ollama unreachable during chat | session=%s | %s", session_id, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The local AI engine (Ollama) is not reachable. "
                "Please ensure Ollama is running: 'ollama serve'"
            ),
        ) from exc
    except OllamaModelError as exc:
        logger.error("Ollama model error | model=%s | %s", target_model, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Model '{target_model}' is not available in Ollama. "
                f"Pull it first: 'ollama pull {target_model}'"
            ),
        ) from exc
    except OllamaTimeoutError as exc:
        logger.error("Ollama timeout | session=%s | %s", session_id, exc)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=(
                "The AI model took too long to respond. "
                "Try a shorter message or increase OLLAMA_TIMEOUT in .env."
            ),
        ) from exc

    # ── 6. Persist assistant response ──────────────────────────────────────────
    assistant_msg = session_service.add_message(
        db=db,
        session_id=session_id,
        role="assistant",
        content=ai_result["content"],
        model=ai_result["model"],
        prompt_tokens=ai_result.get("prompt_tokens"),
        completion_tokens=ai_result.get("completion_tokens"),
        duration_ms=ai_result.get("duration_ms"),
    )

    # ── 7. Auto-title new sessions after first exchange ────────────────────────
    if is_new_session:
        title = request.message[:80].strip().replace("\n", " ")
        session_service.update_session_title(db=db, session_id=session_id, title=title)

    logger.info(
        "Chat complete | session=%s | model=%s | tokens=%d | duration=%dms",
        session_id,
        ai_result["model"],
        ai_result.get("total_tokens", 0),
        ai_result.get("duration_ms", 0),
    )

    return ChatResponse(
        session_id=session_id,
        message_id=assistant_msg.id,
        role="assistant",
        content=ai_result["content"],
        model=ai_result["model"],
        usage=TokenUsage(
            prompt_tokens=ai_result.get("prompt_tokens", 0),
            completion_tokens=ai_result.get("completion_tokens", 0),
            total_tokens=ai_result.get("total_tokens", 0),
        ),
        duration_ms=ai_result.get("duration_ms", 0),
        created_at=datetime.now(tz=timezone.utc),
    )


# ── Session History ─────────────────────────────────────────────────────────────

@router.get(
    "/chat/sessions",
    response_model=list[SessionSummary],
    summary="List Chat Sessions",
    description="Return a paginated list of active conversation sessions.",
)
def list_sessions(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
) -> list[SessionSummary]:
    """Return paginated active sessions ordered by most recently updated."""
    rows = session_service.list_sessions(db=db, limit=limit, offset=offset)
    return [SessionSummary(**row) for row in rows]


@router.get(
    "/chat/sessions/{session_id}/messages",
    response_model=list[MessageRecord],
    summary="Get Session Messages",
    description="Return all messages within a specific session.",
)
def get_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
) -> list[MessageRecord]:
    """Return full message history for the specified session."""
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )
    messages = session_service.get_messages(db=db, session_id=session_id)
    return [MessageRecord.model_validate(msg) for msg in messages]


@router.delete(
    "/chat/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Chat Session",
    description="Soft-delete a session. Messages are retained in the database.",
)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
) -> None:
    """Soft-delete the session identified by session_id."""
    deleted = session_service.delete_session(db=db, session_id=session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )
