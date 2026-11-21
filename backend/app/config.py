from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_JWT_DEFAULT = "dev_super_secret_jwt_key_change_in_production_12345"


class Settings(BaseSettings):
    PROJECT_NAME: str = "MirrorCV"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./mirrorcv.db"
    DATABASE_URL_SYNC: str = "sqlite:///./mirrorcv.db"

    # Auth
    JWT_SECRET: str = DEV_JWT_DEFAULT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Supabase Cloud
    SUPABASE_URL: str = "https://uwomilakkajzzbbnijeh.supabase.co"
    SUPABASE_KEY: str = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV3b21pbGFra2FqenpiYm5pamVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTQ3MjMwOTMsImV4cCI6MjExMDI5OTA5M30."
        "Kxi0-Wt8Yt-hXDRA1doyUKxwwk15Wncp41Zqc9L-UA0"
    )
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    def validate_production_settings(self) -> None:
        """Validates critical security settings when running in production."""
        if self.ENVIRONMENT.lower() == "production":
            if not self.SUPABASE_SERVICE_ROLE_KEY or not self.SUPABASE_SERVICE_ROLE_KEY.strip():
                raise RuntimeError(
                    "CRITICAL CONFIG ERROR: SUPABASE_SERVICE_ROLE_KEY is required in production environment."
                )
            if not self.JWT_SECRET or self.JWT_SECRET == DEV_JWT_DEFAULT:
                raise RuntimeError(
                    "CRITICAL CONFIG ERROR: Secure JWT_SECRET must be set in production environment."
                )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
