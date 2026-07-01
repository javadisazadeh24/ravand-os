from fastapi import APIRouter
from pydantic import BaseModel
from app.services.voice_service import VoiceService

router = APIRouter()
voice = VoiceService()


class VoiceRequest(BaseModel):
    text: str


@router.post("/voice/run")
def voice_run(req: VoiceRequest):
    return voice.run_pipeline(req.text)