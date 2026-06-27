import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENROUTER_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENROUTER_MODEL = "claude-haiku-4-5"


settings = Settings()