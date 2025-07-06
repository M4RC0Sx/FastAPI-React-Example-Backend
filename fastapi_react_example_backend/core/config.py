from __future__ import annotations

from secrets import token_urlsafe
from typing import Literal

from pydantic import PostgresDsn
from pydantic import computed_field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    ENVIRONMENT: Literal["local", "development", "production"] = "local"
    PROJECT_NAME: str
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    SECRET_KEY: str = token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    ACCESS_TOKEN_ALGORITHM: str = "HS256"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fastapi_backend"

    def _build_postgres_uri(self, driver: Literal["asyncpg", "psycopg"]) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=f"postgresql+{driver}",
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def POSTGRES_ASYNC_URI(self) -> PostgresDsn:  # noqa: N802
        return self._build_postgres_uri("asyncpg")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def POSTGRES_SYNC_URI(self) -> PostgresDsn:  # noqa: N802
        return self._build_postgres_uri("psycopg")


settings = Settings()  # type: ignore[call-arg]
