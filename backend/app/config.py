from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_SECRET_KEY = "dev-secret-change-me"
MIN_SECRET_KEY_LENGTH = 32


def normalize_database_url(url: str) -> str:
    # Managed Postgres (Render/Heroku/Supabase) hands out `postgres://` or `postgresql://`,
    # but the app and Alembic use the psycopg3 driver, so pin it in the scheme.
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


class Settings:
    app_name = "FitCoach Pro 2 API"
    api_prefix = "/api/v1"

    def __init__(self) -> None:
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
        self.database_url = normalize_database_url(
            os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg://fitcoach:fitcoach@localhost:5432/fitcoach",
            )
        )
        self.secret_key = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
        self.frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000,http://127.0.0.1:3000")
        self.frontend_origins = [origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()]
        self.secure_cookies = os.getenv("SECURE_COOKIES", "false").lower() == "true"
        self._validate_config()

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    def _has_weak_secret(self) -> bool:
        return self.secret_key == DEFAULT_SECRET_KEY or len(self.secret_key) < MIN_SECRET_KEY_LENGTH

    def _validate_config(self) -> None:
        # A strong secret is mandatory everywhere except local development, so a forgotten
        # ENVIRONMENT=production (staging/demo/CI) can never run on the public default key.
        if not self.is_development and self._has_weak_secret():
            raise ValueError(
                "SECRET_KEY must be set to a strong random value (>= "
                f"{MIN_SECRET_KEY_LENGTH} chars) outside development."
            )
        if self.environment != "production":
            return
        if not self.secure_cookies:
            raise ValueError("Production SECURE_COOKIES must be true.")
        if "localhost" in self.frontend_origin or "127.0.0.1" in self.frontend_origin:
            raise ValueError("Production FRONTEND_ORIGIN must use deployed HTTPS origins, not localhost.")
        if self.database_url.startswith("sqlite") or "localhost" in self.database_url:
            raise ValueError("Production DATABASE_URL must point to a managed database.")


@lru_cache
def get_settings() -> Settings:
    return Settings()
