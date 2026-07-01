"""
RAVAND OS — FastAPI application entry point.

Run with:
    python -m uvicorn app.main:app --reload

Knowledge files are loaded from:
    ravand-os/knowledge/
"""

from pathlib import Path
from fastapi import FastAPI
from app.api.v1.router import router as api_v1_router
from app.core.config import settings

# ── Paths ─────────────────────────────────────────────────────────────────────
# __file__ = ravand-os/backend/app/main.py
# .parent        → ravand-os/backend/app
# .parent.parent → ravand-os/backend
# .parent.parent.parent → ravand-os  ✅

BASE_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
COMPANY_FILE = KNOWLEDGE_DIR / "company.md"

# ── Settings ──────────────────────────────────────────────────────────────────
APP_NAME = getattr(settings, "APP_NAME", "Ravand OS")
APP_VERSION = getattr(settings, "APP_VERSION", "0.1.0")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered Business Operating System — MVP backend",
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(api_v1_router, prefix="/api/v1")

# ── Root endpoints ────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "project": "RAVAND OS",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
    }


@app.get("/company", tags=["Knowledge"])
def company():
    if COMPANY_FILE.exists():
        return {
            "content": COMPANY_FILE.read_text(encoding="utf-8")
        }
    return {
        "error": "company.md not found",
        "looked_at": str(COMPANY_FILE),
    }