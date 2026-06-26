from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Ravand OS"
    APP_VERSION: str = "1.0.0"

    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "change-this-in-production"

    class Config:
        env_file = ".env"


settings = Settings()