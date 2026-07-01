"""
Central API v1 router.
Register all resource routers here.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import company

router = APIRouter(prefix="/api/v1")

router.include_router(
    company.router,
    prefix="/company",
    tags=["company"],
)