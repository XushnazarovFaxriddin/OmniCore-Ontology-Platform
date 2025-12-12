"""
Configuration management for OmniCore services.

Uses environment variables with sensible defaults.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # General
    omnicore_env: str = Field(default="development", alias="OMNICORE_ENV")
    omnicore_service: str = Field(default="unknown", alias="OMNICORE_SERVICE")
    omnicore_port: int = Field(default=8000, alias="OMNICORE_PORT")
    omnicore_log_level: str = Field(default="INFO", alias="OMNICORE_LOG_LEVEL")

    # Database
    database_path: str = Field(
        default="/mnt/extra/omnicore-shared/data", alias="DATABASE_PATH"
    )

    # Service URLs (for Gateway and Global Service)
    roots_service_url: str = Field(
        default="http://roots-service:8001", alias="ROOTS_SERVICE_URL"
    )
    causality_service_url: str = Field(
        default="http://causality-service:8002", alias="CAUSALITY_SERVICE_URL"
    )
    epistemic_service_url: str = Field(
        default="http://epistemic-service:8003", alias="EPISTEMIC_SERVICE_URL"
    )
    mmo_service_url: str = Field(
        default="http://mmo-service:8004", alias="MMO_SERVICE_URL"
    )
    global_service_url: str = Field(
        default="http://global-ontology-service:8005", alias="GLOBAL_SERVICE_URL"
    )

    # Authentication
    jwt_secret_key: str = Field(
        default="omnicore-dev-secret-key-change-in-production",
        alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, alias="JWT_EXPIRATION_HOURS")
    api_key_header: str = Field(default="X-API-Key", alias="API_KEY_HEADER")
    valid_api_keys: str = Field(default="", alias="VALID_API_KEYS")

    # Redis (for rate limiting)
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")

    # CORS
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def get_valid_api_keys(self) -> list[str]:
        """Parse valid API keys from comma-separated string."""
        if not self.valid_api_keys:
            return []
        return [key.strip() for key in self.valid_api_keys.split(",") if key.strip()]


# Global settings instance
settings = Settings()
