"""
Root-specific models for the Roots Service.

Re-exports common models and adds any service-specific extensions.
"""

from common.models import (
    RootType,
    RootBase,
    RootCreate,
    RootUpdate,
    Root,
    RootSummary,
    PaginationParams,
    PaginatedResponse,
    HealthResponse,
    HealthStatus,
)

__all__ = [
    "RootType",
    "RootBase",
    "RootCreate",
    "RootUpdate",
    "Root",
    "RootSummary",
    "PaginationParams",
    "PaginatedResponse",
    "HealthResponse",
    "HealthStatus",
]
