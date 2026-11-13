from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Committed example / placeholder secrets — never allow outside APP_ENV=local.
_WEAK_JWT_SECRETS = frozenset(
    {
        "change-me-to-a-long-random-secret",
        "changeme",
        "secret",
        "local-dev-only-change-me-32chars-min",
        "replace-with-a-unique-random-secret-at-least-32-chars",
        "BFwiMx8o59jwmWmOh8ADiHuKc7NmAV8qJKjpr0D8ahxv5d5TbpFt1eYcM2e4ymAB",
    }
)


class Settings(BaseSettings):
    APP_ENV: Literal["local", "development", "staging", "production"] = "local"
    FRONTEND_URL: str
    DATABASE_URL: str

    JWT_SECRET_KEY: SecretStr = Field(min_length=32)
    JWT_ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    REFRESH_COOKIE_NAME: str = "refresh_token"
    REFRESH_COOKIE_PATH: str = "/api/v1/auth"
    REFRESH_COOKIE_SECURE: bool = False
    REFRESH_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    AI_PROVIDER: Literal["openai", "gemini"] = "openai"
    OPENAI_API_KEY: SecretStr | None = None
    GEMINI_API_KEY: SecretStr | None = None
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    GEMINI_CHAT_MODEL: str = "gemini-flash-lite-latest"

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_CHAT_PER_MINUTE: int = 20
    RATE_LIMIT_AUTH_PER_MINUTE: int = 20
    # Required when APP_ENV != local (shared limits across workers). Optional in local.
    RATE_LIMIT_REDIS_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def jwt_secret(self) -> str:
        return self.JWT_SECRET_KEY.get_secret_value()

    @property
    def openai_api_key(self) -> str | None:
        if self.OPENAI_API_KEY is None:
            return None
        value = self.OPENAI_API_KEY.get_secret_value().strip()
        return value or None

    @property
    def gemini_api_key(self) -> str | None:
        if self.GEMINI_API_KEY is None:
            return None
        value = self.GEMINI_API_KEY.get_secret_value().strip()
        return value or None

    @property
    def chat_model(self) -> str:
        if self.AI_PROVIDER == "gemini":
            return self.GEMINI_CHAT_MODEL
        return self.OPENAI_CHAT_MODEL

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        if self.REFRESH_COOKIE_SAMESITE == "none" and not self.REFRESH_COOKIE_SECURE:
            raise ValueError(
                "REFRESH_COOKIE_SAMESITE=none requires REFRESH_COOKIE_SECURE=true"
            )

        if self.APP_ENV != "local" and self.jwt_secret in _WEAK_JWT_SECRETS:
            raise ValueError(
                "JWT_SECRET_KEY must be a strong unique secret in non-local environments"
            )

        # AI keys / Redis readiness are validated at API startup (see main.py),
        # not here — Alembic/migrate must boot with only DATABASE_URL + JWT settings.
        return self

    def require_ai_provider_key(self) -> None:
        if self.AI_PROVIDER == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai")
        if self.AI_PROVIDER == "gemini" and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when AI_PROVIDER=gemini")

    def require_rate_limit_backend(self) -> None:
        if not self.RATE_LIMIT_ENABLED or self.APP_ENV == "local":
            return
        if not (self.RATE_LIMIT_REDIS_URL or "").strip():
            raise ValueError(
                "RATE_LIMIT_REDIS_URL is required when APP_ENV is not local "
                "(multi-worker / shared rate limits)"
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
