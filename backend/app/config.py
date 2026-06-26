"""
Core configuration for RAVAND OS.
Reads from environment variables with sensible defaults for MVP.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "RAVAND OS"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./ravand.db"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
