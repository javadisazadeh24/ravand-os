"""
RAVAND OS – Memory Endpoint
GET  /api/v1/memory/search – search long-term memory
POST /api/v1/memory        – store a long-term memory record
GET  /api/v1/memory/stats  – memory system statistics
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.database import get_db
from app.services.memory_service import MemoryService, get_memory_service

logger = get_logger(__name__)
router = APIRouter(tags=["Memory"])


# ── Schemas ────────────────────────────────────────────────────────────────────

class MemoryWriteRequest(BaseModel):
    """Request to persist a new long-term memory."""

    session_id: str | None = None
    content: str = Field(..., min_length=1, max_length=16_000)
    memory_type: str = Field(
        default="general",
        description="Category: 'fact', 'summary', 'preference', 'general'",
    )
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)


class MemoryRecord(BaseModel):
    """Representation of a single long-term memory record."""

    id: str
    session_id: str | None
    memory_type: str
    content: str
    importance: float
    tags: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MemoryWriteResponse(BaseModel):
    """Confirmation after storing a memory."""

    id: str
    memory_type: str
    importance: float
    created_at: datetime


class MemorySearchResponse(BaseModel):
    """Search results from long-term memory."""

    query: str
    total: int
    results: list[MemoryRecord]


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post(
    "/memory",
    response_model=MemoryWriteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Store Long-Term Memory",
    description="Persist a fact, summary, or preference to the long-term memory store.",
)
def store_memory(
    request: MemoryWriteRequest,
    db: Session = Depends(get_db),
    memory_service: MemoryService = Depends(get_memory_service),
) -> MemoryWriteResponse:
    """Write a new record to long-term memory."""
    record = memory_service.write_long_term(
        db=db,
        session_id=request.session_id,
        content=request.content,
        memory_type=request.memory_type,
        importance=request.importance,
        tags=request.tags,
    )
    return MemoryWriteResponse(
        id=record.id,
        memory_type=record.memory_type,
        importance=record.importance,
        created_at=datetime.now(tz=timezone.utc),
    )


@router.get(
    "/memory/search",
    response_model=MemorySearchResponse,
    summary="Search Long-Term Memory",
    description="Full-text search across stored long-term memory records.",
)
def search_memory(
    query: str = Query(..., min_length=1, max_length=512),
    session_id: str | None = Query(default=None),
    memory_type: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    min_importance: float = Query(default=0.0, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    memory_service: MemoryService = Depends(get_memory_service),
) -> MemorySearchResponse:
    """Search long-term memory and return matching records."""
    records = memory_service.search_long_term(
        db=db,
        query=query,
        session_id=session_id,
        memory_type=memory_type,
        limit=limit,
        min_importance=min_importance,
    )
    return MemorySearchResponse(
        query=query,
        total=len(records),
        results=[MemoryRecord.model_validate(r) for r in records],
    )


@router.delete(
    "/memory/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Memory Record",
    description="Permanently delete a long-term memory record by ID.",
)
def delete_memory(
    memory_id: str,
    db: Session = Depends(get_db),
    memory_service: MemoryService = Depends(get_memory_service),
) -> None:
    """Delete the specified memory record."""
    deleted = memory_service.delete_long_term(db=db, memory_id=memory_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory record '{memory_id}' not found.",
        )


@router.get(
    "/memory/stats",
    summary="Memory Statistics",
    description="Return short-term and long-term memory system statistics.",
)
def memory_stats(
    db: Session = Depends(get_db),
    memory_service: MemoryService = Depends(get_memory_service),
) -> dict:
    """Return memory system statistics for diagnostics."""
    return memory_service.get_stats(db=db)
