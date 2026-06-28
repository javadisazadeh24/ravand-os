"""
RAVAND OS – Company Endpoint
GET /api/v1/company – returns static company knowledge and system metadata.
"""

import platform
import sys

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.schemas.company_schema import CompanyInfo
from app.services.knowledge_service import KnowledgeService, get_knowledge_service

logger = get_logger(__name__)
router = APIRouter(tags=["Company"])


@router.get(
    "/company",
    response_model=CompanyInfo,
    summary="Company Information",
    description=(
        "Returns the company profile for FabLab Ravand / TPE Co., "
        "including services offered and current AI model configuration."
    ),
)
def get_company_info(
    settings: Settings = Depends(get_settings),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> CompanyInfo:
    """
    Return static company knowledge and runtime system information.
    This endpoint is unauthenticated and suitable for embedding in
    front-end landing pages or status dashboards.
    """
    context = knowledge_service.get_company_context()

    system_info = {
        "python_version": sys.version.split()[0],
        "platform": platform.system(),
        "architecture": platform.machine(),
        "ollama_host": settings.OLLAMA_HOST,
        "environment": settings.ENVIRONMENT,
        "app_version": settings.APP_VERSION,
    }

    logger.debug("Company info requested.")

    return CompanyInfo(
        name=context["name"],
        tagline=context["tagline"],
        location=context["location"],
        services=context["services"],
        ai_model=settings.OLLAMA_MODEL,
        system_info=system_info,
    )
