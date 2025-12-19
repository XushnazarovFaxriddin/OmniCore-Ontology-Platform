"""
OmniCore Common Module

Shared utilities for all OmniCore services.
"""

from .config import settings, get_settings
from .logging_config import get_logger, setup_logging
from .exceptions import (
    OmniCoreException,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    ServiceUnavailableError,
)
from .database import DatabaseManager, get_db_path
from .models import (
    RootType,
    CausalityType,
    EpistemicBasis,
    HealthStatus,
    PaginationParams,
)
from .http_client import HttpClient

# Auth module uses cryptography - import lazily to avoid issues
# when cryptography is not installed properly
def get_auth_service():
    """Get AuthService (lazy import)"""
    from .auth import auth_service
    return auth_service

__all__ = [
    # Config
    "settings",
    "get_settings",
    # Logging
    "get_logger",
    "setup_logging",
    # Exceptions
    "OmniCoreException",
    "NotFoundError",
    "ValidationError",
    "AuthenticationError",
    "ServiceUnavailableError",
    # Database
    "DatabaseManager",
    "get_db_path",
    # Models
    "RootType",
    "CausalityType",
    "EpistemicBasis",
    "HealthStatus",
    "PaginationParams",
    # HTTP Client
    "HttpClient",
    # Auth (lazy)
    "get_auth_service",
]
