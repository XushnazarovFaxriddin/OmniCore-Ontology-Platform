"""
Causality-specific models for the Causality Service.

Re-exports common models and adds any service-specific extensions.
"""

from common.models import (
    CausalityType,
    CausalityLinkBase,
    CausalityLinkCreate,
    CausalityLinkUpdate,
    CausalityLink,
    CausalitySummary,
    PaginationParams,
    PaginatedResponse,
    HealthResponse,
    HealthStatus,
)

__all__ = [
    "CausalityType",
    "CausalityLinkBase",
    "CausalityLinkCreate",
    "CausalityLinkUpdate",
    "CausalityLink",
    "CausalitySummary",
    "PaginationParams",
    "PaginatedResponse",
    "HealthResponse",
    "HealthStatus",
]
