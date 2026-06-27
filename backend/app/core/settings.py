"""
RAVAND OS — Core Settings
Reads all config from .env file
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1-0528")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1/chat/completions"

    # App
    APP_NAME: str = "RAVAND OS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # CORS
    ALLOWED_ORIGINS: list = ["*"]


settings = Settings()
