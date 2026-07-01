from .stt import STTService
from .tts import TTSService
from app.services.ai_service import get_ai_service


class VoicePipeline:
    def __init__(self):
        self.stt = STTService()
        self.tts = TTSService()
        self.ai = get_ai_service()

    def run_once(self):
        text = self.stt.from_microphone()
        print("🧠 User said:", text)

        response = self.ai.generate(prompt=text)
        answer = response["content"]

        self.tts.speak(answer)
        return answer