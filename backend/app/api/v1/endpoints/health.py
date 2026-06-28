"""
RAVAND OS – Health Endpoint
GET /health – system status check for all subsystems.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.database.database import verify_db_connection
from app.schemas.company_schema import DatabaseStatus, HealthResponse, OllamaStatus
from app.services.ai_service import AIService, get_ai_service

logger = get_logger(__name__)
router = APIRouter(tags=["Health"])

# Application start time – used to calculate uptime
_START_TIME: float = time.monotonic()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health Check",
    description=(
        "Returns the operational status of all RAVAND OS subsystems: "
        "Ollama AI engine, SQLite database, and application runtime."
    ),
)
def health_check(
    settings: Settings = Depends(get_settings),
    ai_service: AIService = Depends(get_ai_service),
) -> HealthResponse:
    """
    Probe all critical subsystems and return a consolidated health report.
    This endpoint never raises – it always returns 200 with status details.
    """
    uptime = time.monotonic() - _START_TIME

    # ── Ollama status ──────────────────────────────────────────────────────────
    ollama_raw = ai_service.health()
    ollama_status = OllamaStatus(
        reachable=ollama_raw["reachable"],
        version=ollama_raw.get("version"),
        model_loaded=ollama_raw.get("model_loaded", False),
        available_models=ollama_raw.get("available_models", []),
    )

    # ── Database status ────────────────────────────────────────────────────────
    db_ok = verify_db_connection()
    db_status = DatabaseStatus(
        reachable=db_ok,
        url=settings.DATABASE_URL,
    )

    # ── Overall status ─────────────────────────────────────────────────────────
    if ollama_status.reachable and db_ok:
        overall = "ok"
    elif db_ok:
        overall = "degraded"  # DB ok, but Ollama unreachable
    else:
        overall = "error"

    logger.debug(
        "Health check completed | status=%s | ollama=%s | db=%s",
        overall,
        ollama_status.reachable,
        db_ok,
    )

    return HealthResponse(
        status=overall,
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(tz=timezone.utc),
        uptime_seconds=round(uptime, 2),
        ollama=ollama_status,
        database=db_status,
    )
