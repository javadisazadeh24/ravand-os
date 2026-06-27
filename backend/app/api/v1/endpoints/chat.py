from fastapi import APIRouter
from app.services.ai_service import ai_service

router = APIRouter()

@router.post("/")
def chat(payload: dict):
    message = payload.get("message")
    response = ai_service.ask(message)
    return {"input": message, "response": response}