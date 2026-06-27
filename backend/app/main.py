from pathlib import Path

from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.core.config import settings


# -------------------------
# Project paths
# -------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"

COMPANY_FILE = KNOWLEDGE_DIR / "company.md"


# -------------------------
# Safe settings
# -------------------------

APP_NAME = getattr(settings, "APP_NAME", "Ravand OS")
APP_VERSION = getattr(settings, "APP_VERSION", "0.1.0")


# -------------------------
# FastAPI
# -------------------------

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered Business Operating System - MVP Backend",
)


# -------------------------
# Routers
# -------------------------

app.include_router(api_v1_router, prefix="/api/v1")


# -------------------------
# Root
# -------------------------

@app.get("/")
def root():
    return {
        "project": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
    }


# -------------------------
# Health
# -------------------------

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# -------------------------
# Company
# -------------------------

@app.get("/company")
def company():
    return {
        "project_root": str(PROJECT_ROOT),
        "knowledge_dir": str(KNOWLEDGE_DIR),
        "company_file": str(COMPANY_FILE),
        "exists": COMPANY_FILE.exists(),
        "content": COMPANY_FILE.read_text(encoding="utf-8") if COMPANY_FILE.exists() else None,
    }