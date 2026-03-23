"""Core configuration for the AI Wrapper backend."""

import secrets

from pydantic_settings import BaseSettings


def _default_secret_key() -> str:
    return secrets.token_urlsafe(32)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "AI Wrapper"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_wrapper"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/ai_wrapper"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # AI
    openai_api_key: str = ""
    openai_model: str = "gpt-4"

    # Docker sandbox
    sandbox_image: str = "node:20-slim"
    sandbox_timeout: int = 300
    sandbox_memory_limit: str = "512m"
    sandbox_cpu_limit: float = 1.0

    # Auth
    secret_key: str = _default_secret_key()
    access_token_expire_minutes: int = 60

    # Deployment
    vercel_token: str = ""
    cloudflare_token: str = ""
    aws_access_key: str = ""
    aws_secret_key: str = ""

    # Billing
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # Limits
    free_plan_generations: int = 10
    pro_plan_generations: int = -1  # unlimited

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
