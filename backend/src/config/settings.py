from pydantic_settings import BaseSettings
import os
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Todo API"
    DEBUG: bool = False

    # Dapr Configuration
    DAPR_HTTP_ENDPOINT: str = os.getenv("DAPR_HTTP_ENDPOINT", "http://localhost:3500")
    DAPR_GRPC_ENDPOINT: str = os.getenv("DAPR_GRPC_ENDPOINT", "http://localhost:50001")
    USE_DAPR_SECRETS: bool = os.getenv("USE_DAPR_SECRETS", "true").lower() == "true"

    # Authentication
    BETTER_AUTH_SECRET: str = os.getenv("BETTER_AUTH_SECRET", "")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/todo_app_dev")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # JWT Configuration
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DELTA: int = 86400  # 24 hours in seconds

    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    class Config:
        env_file = ".env"


settings = Settings()