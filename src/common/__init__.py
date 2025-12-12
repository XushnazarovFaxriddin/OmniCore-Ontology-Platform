"""
OmniCore Common Module

Shared utilities for all OmniCore services.
"""

from .config import settings
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
from .auth import AuthService, TokenData

__all__ = [
    # Config
    "settings",
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
    # Auth
    "AuthService",
    "TokenData",
]
