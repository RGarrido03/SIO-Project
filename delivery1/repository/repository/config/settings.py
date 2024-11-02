import os
from dataclasses import field

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )
    PRODUCTION: bool = os.getenv("ENV") == "production"

    STATIC_PATH: str = "/static"
    BACKEND_CORS_ORIGINS: list[str] = field(
        default_factory=lambda: ["http://localhost:8080"]
    )

    # Database
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "postgres")
    DATABASE_URI: str = f"postgresql+asyncpg://postgres:{DATABASE_PASSWORD}@db:5432/sio"

    # Auth
    AUTH_SECRET_KEY: str = (
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    )
    AUTH_ALGORITHM: str = "HS256"


settings = Settings()
