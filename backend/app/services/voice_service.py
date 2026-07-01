import speech_recognition as sr
import pyttsx3
from app.services.ai_service import get_ai_service


class VoiceService:

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts = pyttsx3.init()
        self.ai = get_ai_service()

    # 🎤 STT
    def speech_to_text(self, audio_file=None, use_mic=True):
        if use_mic:
            with sr.Microphone() as source:
                print("🎤 Listening...")
                audio = self.recognizer.listen(source)

        else:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)

        text = self.recognizer.recognize_google(audio)
        return text

    # 🤖 LLM
    def process_text(self, text: str):
        response = self.ai.generate(
            prompt=text
        )
        return response["content"]

    # 🔊 TTS
    def text_to_speech(self, text: str):
        self.tts.say(text)
        self.tts.runAndWait()
        return True

    # 🔥 PIPELINE کامل
    def run_pipeline(self, text: str):
        llm_response = self.process_text(text)
        self.text_to_speech(llm_response)

        return {
            "input": text,
            "output": llm_response
        }