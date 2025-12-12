"""
MMO-specific models for the MMO Service.

Re-exports common models and adds any service-specific extensions.
"""

from common.models import (
    MMOClassBase,
    MMOClassCreate,
    MMOClassUpdate,
    MMOClass,
    MMOSlotBase,
    MMOSlotCreate,
    MMOSlot,
    MMOMetrics,
    MMOSchema,
    PaginationParams,
    PaginatedResponse,
    HealthResponse,
    HealthStatus,
)

__all__ = [
    "MMOClassBase",
    "MMOClassCreate",
    "MMOClassUpdate",
    "MMOClass",
    "MMOSlotBase",
    "MMOSlotCreate",
    "MMOSlot",
    "MMOMetrics",
    "MMOSchema",
    "PaginationParams",
    "PaginatedResponse",
    "HealthResponse",
    "HealthStatus",
]
