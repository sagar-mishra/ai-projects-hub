from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GROQ_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "llama-3.1-8b-instant"
    OLLAMA_BASE_URL: Optional[str] = None
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    DATABASE_URL: str = "sqlite:///./platform.db"
    SECRET_KEY: str = "your-default-secret-key-change-it-in-prod-1234567"
    BACKEND_PORT: Optional[int] = 8000
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    LOG_LEVEL: str = "INFO"
    MAX_RUN_COST_USD: float = 0.10
    AGENT_TIMEOUT_SECONDS: float = 180.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
