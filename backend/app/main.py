"""
RAVAND OS – Application Entry Point
=====================================
Initialises and exposes the FastAPI application instance.

Run with:
    cd backend
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Or via the helper script:
    python run.py
"""

import time
from contextlib import asynccontextmanager
from typing import Any
from app.api.v1.endpoints.system import router as system_router
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.voice import router as voice_router
from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.database.database import init_db, verify_db_connection
from app.services.ai_service import (
    OllamaConnectionError,
    OllamaModelError,
    OllamaTimeoutError,
)
from app.services.plugin_service import get_plugin_service

# ── Bootstrap ──────────────────────────────────────────────────────────────────

configure_logging()
logger = get_logger(__name__)
settings = get_settings()


# ── Lifespan ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle manager.
    Runs once at startup; cleanup code (after yield) runs at shutdown.
    """
    logger.info("=" * 60)
    logger.info("  %s v%s starting up", settings.APP_NAME, settings.APP_VERSION)
    logger.info("  Environment : %s", settings.ENVIRONMENT)
    logger.info("  Ollama Host : %s", settings.OLLAMA_HOST)
    logger.info("  Ollama Model: %s", settings.OLLAMA_MODEL)
    logger.info("  Database    : %s", settings.DATABASE_URL)
    logger.info("=" * 60)

    # Initialise database tables
    try:
        init_db()
        logger.info("Database initialised successfully.")
    except Exception as exc:
        logger.critical("Database initialisation failed: %s", exc, exc_info=True)
        raise

    # Verify database connectivity
    if not verify_db_connection():
        logger.error("Database connectivity check failed at startup.")

    # Load plugins
    plugin_service = get_plugin_service()
    loaded_plugins = plugin_service.startup()
    logger.info(
        "Plugin system ready | loaded=%d | plugins=%s",
        len(loaded_plugins),
        loaded_plugins,
    )

    yield  # Application is now running

    # Shutdown
    plugin_service.shutdown()
    logger.info("%s shutting down gracefully.", settings.APP_NAME)


# ── FastAPI Application ────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ── CORS Middleware ────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Timing Middleware ──────────────────────────────────────────────────

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Attach X-Process-Time-Ms header to every response."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Process-Time-Ms"] = str(duration_ms)
    return response


# ── Global Exception Handlers ──────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return structured 422 responses for Pydantic validation failures."""
    errors = [
        {
            "field": " → ".join(str(loc) for loc in err.get("loc", [])),
            "message": err.get("msg", "Validation error"),
            "type": err.get("type", "unknown"),
        }
        for err in exc.errors()
    ]
    logger.warning(
        "Validation error | %s %s | errors=%s",
        request.method,
        request.url.path,
        errors,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation failed", "detail": errors},
    )


@app.exception_handler(OllamaConnectionError)
async def ollama_connection_handler(
    request: Request, exc: OllamaConnectionError
) -> JSONResponse:
    logger.error("OllamaConnectionError | %s | %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "AI engine unavailable",
            "detail": str(exc),
            "hint": "Run 'ollama serve' to start the local AI engine.",
        },
    )


@app.exception_handler(OllamaTimeoutError)
async def ollama_timeout_handler(
    request: Request, exc: OllamaTimeoutError
) -> JSONResponse:
    logger.error("OllamaTimeoutError | %s | %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={
            "error": "AI response timeout",
            "detail": str(exc),
            "hint": "Increase OLLAMA_TIMEOUT in .env or send a shorter prompt.",
        },
    )


@app.exception_handler(OllamaModelError)
async def ollama_model_handler(
    request: Request, exc: OllamaModelError
) -> JSONResponse:
    logger.error("OllamaModelError | %s | %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "AI model not found",
            "detail": str(exc),
            "hint": f"Run 'ollama pull {settings.OLLAMA_MODEL}' to download the model.",
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all handler – prevents raw stack traces leaking to clients."""
    logger.error(
        "Unhandled exception | %s %s | %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Check server logs for details.",
        },
    )


# ── Router Registration ────────────────────────────────────────────────────────

app.include_router(health_router)
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
app.include_router(voice_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")
# ── Root ───────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root() -> dict[str, Any]:
    """Root route – returns navigation links."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api": settings.API_V1_PREFIX,
        "endpoints": {
            "health": "/health",
            "company": f"{settings.API_V1_PREFIX}/company",
            "chat": f"{settings.API_V1_PREFIX}/chat",
            "models": f"{settings.API_V1_PREFIX}/models",
            "agent": f"{settings.API_V1_PREFIX}/agent",
            "memory": f"{settings.API_V1_PREFIX}/memory",
            "voice": "/api/v1/voice/run",
        },
    }