from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from urllib.parse import urlparse, urlencode, parse_qs


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "AI-IDS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    RENDER: bool = False
    VERCEL: bool = False

    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    WORKERS: int = 1

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "aids"
    POSTGRES_PASSWORD: str = "aids_secret_2024"
    POSTGRES_DB: str = "aids_db"
    DATABASE_URL: Optional[str] = None

    JWT_SECRET_KEY: str = "change-this-to-a-very-long-secure-random-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = None

    MAX_PACKET_CAPTURE_SIZE: int = 65535
    PACKET_BUFFER_SIZE: int = 10000
    FLOW_IDLE_TIMEOUT: int = 60
    FLOW_LIFETIME: int = 3600

    FRONTEND_DIST_PATH: str = "../frontend/dist"

    CONFIDENCE_THRESHOLD: float = 0.85
    ML_MODEL_PATH: str = "trained_models/best_model.pkl"
    FEATURE_CACHE_SIZE: int = 1000

    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = None
    DISCORD_WEBHOOK_URL: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    ENABLE_PACKET_CAPTURE: bool = False
    CAPTURE_INTERFACE: Optional[str] = None
    ENABLE_REALTIME_PREDICTION: bool = True
    ENABLE_NOTIFICATIONS: bool = True
    ENABLE_AUTO_RETRAINING: bool = False
    RETRAINING_INTERVAL_HOURS: int = 24

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            params.pop("channel_binding", None)
            
            # Map sslmode to ssl (asyncpg expects 'ssl' rather than 'sslmode')
            sslmode = params.pop("sslmode", None)
            if sslmode and "ssl" not in params:
                params["ssl"] = sslmode
                
            # If database is external Render PG (contains render.com) and ssl is not set, force ssl=require
            if "render.com" in parsed.netloc and "ssl" not in params:
                params["ssl"] = ["require"]
                
            query = urlencode(params, doseq=True)
            clean = parsed._replace(query=query).geturl()
            if "+asyncpg" not in clean:
                if clean.startswith("postgres://"):
                    clean = clean.replace("postgres://", "postgresql+asyncpg://", 1)
                elif clean.startswith("postgresql://"):
                    clean = clean.replace("postgresql://", "postgresql+asyncpg://", 1)
            return clean
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def is_serverless(self) -> bool:
        return self.VERCEL or (self.ENVIRONMENT == "production" and self.RENDER)


settings = Settings()
