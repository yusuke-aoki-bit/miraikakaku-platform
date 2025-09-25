import os
from functools import lru_cache
from typing import Optional

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    # Database
    database_url: str = ""
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = ""
    db_name: str = "miraikakaku"

    # Redis Cache
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 300  # 5 minutes default

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    debug: bool = False
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # External APIs
    yfinance_timeout: int = 30
    max_concurrent_requests: int = 10

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Security
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @validator('database_url', pre=True)
    def build_db_url(cls, v, values):
        if v:
            return v

        return (
            f"postgresql://{values.get('db_user')}:{values.get('db_password')}"
            f"@{values.get('db_host')}:{values.get('db_port')}/{values.get('db_name')}"
        )

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_prefix": "",
        "extra": "ignore"  # Allow extra environment variables
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Global settings instance
settings = get_settings()