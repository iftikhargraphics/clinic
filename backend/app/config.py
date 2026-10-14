import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./clinic.db")
    secret_key: str = os.getenv("SECRET_KEY", "")
    admin_email: str = os.getenv("SEED_ADMIN_EMAIL", "admin@example.test")
    admin_password: str = os.getenv("SEED_ADMIN_PASSWORD", "")
    allowed_origins: tuple[str, ...] = tuple(x.strip() for x in os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000").split(",") if x.strip())
    token_minutes: int = int(os.getenv("TOKEN_MINUTES", "30"))

settings = Settings()
if not settings.secret_key and os.getenv("APP_ENV", "development") == "production":
    raise RuntimeError("SECRET_KEY must be configured in production")
