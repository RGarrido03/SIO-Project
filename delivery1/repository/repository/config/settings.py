import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )
    PRODUCTION: bool = os.getenv("ENV") == "production"

    STATIC_PATH: str = "/static"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8080"]

    # Database
    DATABASE_FILENAME: str = "database.db"
    DATABASE_URI: str = f"sqlite+aiosqlite:///{DATABASE_FILENAME}"


settings = Settings()
