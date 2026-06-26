from pathlib import Path

from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.core.config import settings

print("=" * 60)
print("THIS IS THE NEW MAIN.PY")
print("=" * 60)


# ==========================
# FastAPI
# ==========================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Business Operating System — MVP backend",
)

# ==========================
# Paths
# ==========================

# پروژه:
# ravand-os/
# ├── backend/
# │   └── app/
# │       └── main.py
# └── knowledge/
#
# از main.py باید دو پوشه برویم بالا تا ravand-os

PROJECT_ROOT = Path(__file__).resolve().parents[2]

KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"

COMPANY_FILE = KNOWLEDGE_DIR / "company.md"

print("=" * 60)
print("PROJECT_ROOT :", PROJECT_ROOT)
print("KNOWLEDGE_DIR:", KNOWLEDGE_DIR)
print("COMPANY_FILE :", COMPANY_FILE)
print("FILE EXISTS  :", COMPANY_FILE.exists())
print("=" * 60)

# ==========================
# Routers
# ==========================

app.include_router(api_v1_router, prefix="/api/v1")

# ==========================
# Root
# ==========================

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }

# ==========================
# Health
# ==========================

@app.get("/health")
def health():
    return {
        "status": "ok"
    }

# ==========================
# Company
# ==========================

@app.get("/company")
def company():

    if not COMPANY_FILE.exists():
        return {
            "error": "company.md not found",
            "searched_path": str(COMPANY_FILE),
            "project_root": str(PROJECT_ROOT),
        }

    return {
        "path": str(COMPANY_FILE),
        "content": COMPANY_FILE.read_text(encoding="utf-8")
    }