"""
RAVAND OS – Models Endpoint
GET /api/v1/models – list all locally available Ollama models.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.services.ai_service import AIService, OllamaConnectionError, get_ai_service

logger = get_logger(__name__)
router = APIRouter(tags=["Models"])


class ModelInfo(BaseModel):
    """Metadata for a single Ollama model."""

    name: str
    is_default: bool


class ModelsResponse(BaseModel):
    """Response for GET /api/v1/models."""

    ollama_host: str
    default_model: str
    models: list[ModelInfo]
    total: int


@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="List Available Models",
    description=(
        "Returns all models currently pulled in the local Ollama instance. "
        "The default model is determined by OLLAMA_MODEL in .env."
    ),
)
def list_models(
    settings: Settings = Depends(get_settings),
    ai_service: AIService = Depends(get_ai_service),
) -> ModelsResponse:
    """
    Query the local Ollama server for available models.
    Returns structured model info including which one is the current default.
    """
    try:
        health = ai_service.health()
    except OllamaConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot reach Ollama: {exc}",
        ) from exc

    if not health["reachable"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama server is not reachable. Run 'ollama serve'.",
        )

    available = health.get("available_models", [])
    models = [
        ModelInfo(
            name=name,
            is_default=(name == settings.OLLAMA_MODEL or settings.OLLAMA_MODEL in name),
        )
        for name in available
    ]

    logger.debug("Models listed | count=%d", len(models))

    return ModelsResponse(
        ollama_host=settings.OLLAMA_HOST,
        default_model=settings.OLLAMA_MODEL,
        models=models,
        total=len(models),
    )
