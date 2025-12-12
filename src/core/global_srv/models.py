"""
Global-specific models for the Global Service.

Re-exports common models and adds any service-specific extensions.
"""

from common.models import (
    GlobalStats,
    GlobalSample,
    GlobalSummary,
    SystemHealthResponse,
    ServiceHealthDetail,
    HealthResponse,
    HealthStatus,
    Root,
    CausalityLink,
    EpistemicAnnotation,
    MMOClass,
)

__all__ = [
    "GlobalStats",
    "GlobalSample",
    "GlobalSummary",
    "SystemHealthResponse",
    "ServiceHealthDetail",
    "HealthResponse",
    "HealthStatus",
    "Root",
    "CausalityLink",
    "EpistemicAnnotation",
    "MMOClass",
]
