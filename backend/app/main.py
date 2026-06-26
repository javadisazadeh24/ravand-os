from pathlib import Path

from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.core.config import settings


# -------------------------
# Paths
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
COMPANY_FILE = BASE_DIR / "knowledge" / "company.md"


# -------------------------
# Safe settings access
# (جلوگیری از کرش اگر env ناقص بود)
# -------------------------
APP_NAME = getattr(settings, "APP_NAME", "Ravand OS")
APP_VERSION = getattr(settings, "APP_VERSION", "0.1.0")


# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered Business Operating System — MVP backend",
)


# -------------------------
# Routers
# -------------------------
app.include_router(api_v1_router, prefix="/api/v1")


# -------------------------
# Root endpoints
# -------------------------
@app.get("/")
def root():
    return {
        "project": "RAVAND OS",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/company")
def company():
    if COMPANY_FILE.exists():
        return {
            "content": COMPANY_FILE.read_text(encoding="utf-8")
        }

    return {
        "error": "company.md not found"
    }