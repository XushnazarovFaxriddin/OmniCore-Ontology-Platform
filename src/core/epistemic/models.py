"""
Epistemic-specific models for the Epistemic Service.

Re-exports common models and adds any service-specific extensions.
"""

from common.models import (
    EpistemicBasis,
    EpistemicAnnotationBase,
    EpistemicAnnotationCreate,
    EpistemicAnnotationUpdate,
    EpistemicAnnotation,
    EpistemicSummary,
    PaginationParams,
    PaginatedResponse,
    HealthResponse,
    HealthStatus,
)

__all__ = [
    "EpistemicBasis",
    "EpistemicAnnotationBase",
    "EpistemicAnnotationCreate",
    "EpistemicAnnotationUpdate",
    "EpistemicAnnotation",
    "EpistemicSummary",
    "PaginationParams",
    "PaginatedResponse",
    "HealthResponse",
    "HealthStatus",
]
