import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:

    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("FLASK_PORT", "5000"))

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1024"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.4"))
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))

    DATABASE_PATH: str = str(BASE_DIR / os.getenv("DATABASE_PATH", "data/chatbot.db"))
    STORE_CONFIG_PATH: str = str(BASE_DIR / os.getenv("STORE_CONFIG_PATH", "data/store_config.json"))

    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))

    @classmethod
    def validate(cls) -> None:
        if not cls.GROQ_API_KEY or cls.GROQ_API_KEY.startswith("gsk_your"):
            raise ValueError(
                "❌ GROQ_API_KEY is not configured. "
                "Get one from https://console.groq.com/keys and add it to .env"
            )
