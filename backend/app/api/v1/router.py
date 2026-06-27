"""
RAVAND OS — API v1 Router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import chat

router = APIRouter()

router.include_router(chat.router, prefix="/chat", tags=["Chat"])
