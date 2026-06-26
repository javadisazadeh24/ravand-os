from fastapi import APIRouter

from app.api.v1.endpoints import company

router = APIRouter()

router.include_router(
    company.router,
    prefix="/company",
    tags=["company"],
)