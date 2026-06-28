"""
RAVAND OS – Core Configuration
Loads all settings from environment variables / .env file.
Designed for offline, local-only execution.
"""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration object for RAVAND OS backend.
    All values are loaded from environment variables or .env file.
    No secrets. No cloud keys. No API tokens.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────────
    APP_NAME: str = "RAVAND OS"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "RAVAND OS – Offline AI Operating System. "
        "Powered by Ollama. Runs entirely on Windows."
    )
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # ── Ollama AI Engine ───────────────────────────────────────────────────────
    OLLAMA_HOST: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "gpt-oss:20b"
    OLLAMA_TIMEOUT: int = 120          # seconds – long inference can take time
    OLLAMA_MAX_RETRIES: int = 3
    OLLAMA_RETRY_DELAY: float = 1.5    # seconds between retries
    OLLAMA_STREAM: bool = False

    # ── Database ───────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./ravand_os.db"
    DATABASE_ECHO: bool = False        # set True to log all SQL statements

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_DIR: str = "logs"
    LOG_MAX_BYTES: int = 10_485_760    # 10 MB per log file
    LOG_BACKUP_COUNT: int = 5

    # ── Company Knowledge ──────────────────────────────────────────────────────
    COMPANY_NAME: str = "FabLab Ravand"
    COMPANY_TAGLINE: str = "جایی که ایده‌ها جان می‌گیرن"
    COMPANY_LOCATION: str = "Zahedan, Iran – Nogam Science and Technology Park"
    COMPANY_SERVICES: list[str] = [
        "3D Printing",
        "CNC Machining",
        "Industrial Design",
        "Reverse Engineering",
        "Prototyping",
        "Technical Consulting",
    ]

    # ── API ────────────────────────────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("OLLAMA_HOST")
    @classmethod
    def validate_ollama_host(cls, v: str) -> str:
        """Ensure Ollama host starts with http:// or https://."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("OLLAMA_HOST must start with http:// or https://")
        return v.rstrip("/")

    @property
    def ollama_api_generate(self) -> str:
        """Full URL for Ollama generate endpoint."""
        return f"{self.OLLAMA_HOST}/api/generate"

    @property
    def ollama_api_chat(self) -> str:
        """Full URL for Ollama chat endpoint."""
        return f"{self.OLLAMA_HOST}/api/chat"

    @property
    def ollama_api_health(self) -> str:
        """Full URL for Ollama health/version endpoint."""
        return f"{self.OLLAMA_HOST}/api/version"

    @property
    def ollama_api_tags(self) -> str:
        """Full URL to list available models."""
        return f"{self.OLLAMA_HOST}/api/tags"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the singleton Settings instance.
    Cached after first call – safe to import and call anywhere.
    """
    return Settings()
