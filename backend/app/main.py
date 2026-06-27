"""
RAVAND OS — Main Application Entry Point
Run with: python -m uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router as api_v1_router
from app.models.request_models import HealthResponse
from app.core.settings import settings


# ── App Init ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="RAVAND OS",
    description="AI-powered Business Operating System for TPE Co. | توسعه پردازان",
    version=settings.APP_VERSION,
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc"       # ReDoc
)


# ── CORS Middleware ────────────────────────────────────────────────────────
# اجازه می‌دیم از همه جا (frontend، curl، Postman) بشه call کرد

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ─────────────────────────────────────────────────────────────────

app.include_router(api_v1_router, prefix="/api/v1")


# ── Health Check ───────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """سرور در حال اجراست یا نه؟"""
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        app=settings.APP_NAME
    )


@app.get("/", tags=["System"])
async def root():
    """Root endpoint"""
    return {
        "message": "RAVAND OS is running 🚀",
        "docs": "/docs",
        "health": "/health"
    }
