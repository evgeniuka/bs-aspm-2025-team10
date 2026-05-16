from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    app_name = "FitCoach Pro 2 API"
    api_prefix = "/api/v1"
    environment = os.getenv("ENVIRONMENT", "development").lower()
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://fitcoach:fitcoach@localhost:5432/fitcoach",
    )
    secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")
    access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000,http://127.0.0.1:3000")
    frontend_origins = [origin.strip() for origin in frontend_origin.split(",") if origin.strip()]
    secure_cookies = os.getenv("SECURE_COOKIES", "false").lower() == "true"

    def __init__(self) -> None:
        self._validate_production_config()

    def _validate_production_config(self) -> None:
        if self.environment != "production":
            return
        if self.secret_key == "dev-secret-change-me" or len(self.secret_key) < 32:
            raise ValueError("Production SECRET_KEY must be set and at least 32 characters long.")
        if not self.secure_cookies:
            raise ValueError("Production SECURE_COOKIES must be true.")
        if "localhost" in self.frontend_origin or "127.0.0.1" in self.frontend_origin:
            raise ValueError("Production FRONTEND_ORIGIN must use deployed HTTPS origins, not localhost.")
        if self.database_url.startswith("sqlite") or "localhost" in self.database_url:
            raise ValueError("Production DATABASE_URL must point to a managed database.")


@lru_cache
def get_settings() -> Settings:
    return Settings()
