"""
RAVAND OS — FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.database.database import Base, engine

# ── Logging ──────────────────────────────────────────────────────────────────
setup_logging()
logger = get_logger(__name__)

# ── Database ──────────────────────────────────────────────────────────────────
# Creates all tables on startup (MVP approach; replace with Alembic for prod).
Base.metadata.create_all(bind=engine)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Business Operating System — MVP backend",
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(api_v1_router)


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    """Health check — confirms the API is running."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} started")
