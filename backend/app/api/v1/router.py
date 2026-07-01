"""
RAVAND OS – API v1 Router
Aggregates all v1 endpoint routers under the /api/v1 prefix.

To add a new module:
  1. Create app/api/v1/endpoints/your_module.py with a `router` object.
  2. Import and include it here.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import agent, chat, company, memory, models
from app.api.v1.endpoints.health import router as health_router

# The v1 router is mounted in main.py with prefix /api/v1
api_v1_router = APIRouter()

api_v1_router.include_router(company.router)
api_v1_router.include_router(chat.router)
api_v1_router.include_router(models.router)
api_v1_router.include_router(agent.router)
api_v1_router.include_router(memory.router)

__all__ = ["api_v1_router", "health_router"]
