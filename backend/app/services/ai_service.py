import requests
from app.core.config import settings


class AIService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.url = "https://api.anthropic.com/v1/messages"

    def ask(self, message: str, context: str = "") -> str:
        if not self.api_key:
            return "ERROR: missing API key"

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": "claude-haiku-4-5",
            "max_tokens": 1024,
            "system": "You are RAVAND OS, the AI assistant of TPE Co. (توسعه پردازان). Answer in the same language the user writes.",
            "messages": [
                {"role": "user", "content": message}
            ]
        }

        try:
            response = requests.post(self.url, json=payload, headers=headers, timeout=30)
            data = response.json()

            if response.status_code != 200:
                return f"ERROR: {data}"

            return data["content"][0]["text"]

        except Exception as e:
            return f"ERROR: {str(e)}"


ai_service = AIService()