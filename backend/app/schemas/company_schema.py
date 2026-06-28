"""
RAVAND OS – Company & Health Pydantic Schemas
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Health ─────────────────────────────────────────────────────────────────────

class OllamaStatus(BaseModel):
    """Connectivity and version information from the local Ollama server."""

    reachable: bool
    version: str | None = None
    model_loaded: bool = False
    available_models: list[str] = Field(default_factory=list)


class DatabaseStatus(BaseModel):
    """SQLite / database health indicator."""

    reachable: bool
    url: str


class HealthResponse(BaseModel):
    """
    Response for GET /health.
    Reports the status of all subsystems.
    """

    status: str = Field(..., description="'ok' | 'degraded' | 'error'")
    app_name: str
    version: str
    environment: str
    timestamp: datetime
    uptime_seconds: float
    ollama: OllamaStatus
    database: DatabaseStatus


# ── Company ────────────────────────────────────────────────────────────────────

class CompanyInfo(BaseModel):
    """
    Response for GET /api/v1/company.
    Returns static knowledge about FabLab Ravand / TPE Co.
    """

    name: str
    tagline: str
    location: str
    services: list[str]
    ai_model: str
    system_info: dict[str, Any]
