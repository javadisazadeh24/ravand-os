"""
RAVAND OS — Request & Response Models
"""

from pydantic import BaseModel
from typing import Optional


# ── Request ────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = ""

    class Config:
        json_schema_extra = {
            "example": {
                "message": "سلام، می‌تونی کمکم کنی؟",
                "context": ""
            }
        }


# ── Response ───────────────────────────────────────────────────────────────

class ChatResponse(BaseModel):
    input: str
    response: str
    model: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "input": "سلام",
                "response": "سلام! چطور می‌تونم کمکتون کنم؟",
                "model": "deepseek/deepseek-r1-0528"
            }
        }


class HealthResponse(BaseModel):
    status: str
    version: str
    app: str
