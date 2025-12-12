"""
Shared Pydantic models for OmniCore services.
"""

from enum import Enum
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================


class RootType(str, Enum):
    """Four fundamental ontological root types from v10 spec."""

    EXTANT = "EXTANT"  # Entities with spatiotemporal location
    ABSTRACT = "ABSTRACT"  # Atemporal, mind-independent structures
    MENTAL = "MENTAL"  # Subjective, first-person accessible states
    FICTIVE = "FICTIVE"  # Context-dependent representations


class CausalityType(str, Enum):
    """Five causality types from v10 spec (Aristotelian + Emergent)."""

    EFFICIENT = "EFFICIENT"  # causesDirectly
    FINAL = "FINAL"  # servesPurpose
    MATERIAL = "MATERIAL"  # constitutedBy
    FORMAL = "FORMAL"  # structuredAs
    EMERGENT = "EMERGENT"  # emergesFrom


class EpistemicBasis(str, Enum):
    """Epistemic basis types from v10 spec."""

    AXIOMATIC = "axiomatic"
    EMPIRICAL = "empirical"
    CONSENSUS = "consensus"
    SPECULATIVE = "speculative"


class HealthStatus(str, Enum):
    """Service health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UP = "up"
    DOWN = "down"


# =============================================================================
# Common Models
# =============================================================================


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=1000)


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    items: list[Any]
    total: int
    offset: int
    limit: int
    has_more: bool


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: Optional[Any] = None
    status_code: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: HealthStatus
    service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    details: Optional[dict] = None


class ServiceHealthDetail(BaseModel):
    """Individual service health detail."""

    name: str
    status: HealthStatus
    latency_ms: float
    last_check: datetime
    error: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """System-wide health status."""

    status: HealthStatus
    services: dict[str, ServiceHealthDetail]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# Root Models
# =============================================================================


class RootBase(BaseModel):
    """Base schema for root entities."""

    name: str = Field(..., min_length=1, max_length=255)
    root_type: RootType
    description: Optional[str] = None
    metadata: Optional[dict] = None


class RootCreate(RootBase):
    """Schema for creating a new root."""

    import_source: Optional[str] = None


class RootUpdate(BaseModel):
    """Schema for updating a root."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    root_type: Optional[RootType] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


class Root(RootBase):
    """Full root entity."""

    id: str
    created_at: datetime
    updated_at: datetime
    import_source: Optional[str] = None
    ai_enhancement_trace: Optional[str] = None

    class Config:
        from_attributes = True


class RootSummary(BaseModel):
    """Summary statistics for roots."""

    total_count: int
    by_type: dict[str, int]


# =============================================================================
# Causality Models
# =============================================================================


class CausalityLinkBase(BaseModel):
    """Base schema for causality links."""

    source_entity_id: str
    target_entity_id: str
    causality_type: CausalityType
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    description: Optional[str] = None
    metadata: Optional[dict] = None


class CausalityLinkCreate(CausalityLinkBase):
    """Schema for creating a causal link."""

    pass


class CausalityLinkUpdate(BaseModel):
    """Schema for updating a causality link."""

    source_entity_id: Optional[str] = None
    target_entity_id: Optional[str] = None
    causality_type: Optional[CausalityType] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    description: Optional[str] = None
    metadata: Optional[dict] = None


class CausalityLink(CausalityLinkBase):
    """Full causality link entity."""

    id: str
    created_at: datetime
    updated_at: datetime
    ai_confidence: Optional[float] = None
    rationale_trace: Optional[str] = None

    class Config:
        from_attributes = True


class CausalitySummary(BaseModel):
    """Summary statistics for causality links."""

    total_count: int
    by_type: dict[str, int]
    avg_confidence: float


# =============================================================================
# Epistemic Models
# =============================================================================


class EpistemicAnnotationBase(BaseModel):
    """Base schema for epistemic annotations."""

    entity_id: str
    certainty: float = Field(ge=0.0, le=1.0)
    basis: EpistemicBasis
    source: Optional[str] = None
    note: Optional[str] = None


class EpistemicAnnotationCreate(EpistemicAnnotationBase):
    """Schema for creating an epistemic annotation."""

    pass


class EpistemicAnnotationUpdate(BaseModel):
    """Schema for updating an epistemic annotation."""

    entity_id: Optional[str] = None
    certainty: Optional[float] = Field(None, ge=0.0, le=1.0)
    basis: Optional[EpistemicBasis] = None
    source: Optional[str] = None
    note: Optional[str] = None


class EpistemicAnnotation(EpistemicAnnotationBase):
    """Full epistemic annotation entity."""

    id: str
    timestamp: datetime

    class Config:
        from_attributes = True


class EpistemicSummary(BaseModel):
    """Summary statistics for epistemic annotations."""

    total_count: int
    by_basis: dict[str, int]
    avg_certainty: float
    certainty_distribution: dict[str, int]


# =============================================================================
# MMO Models
# =============================================================================


class MMOClassBase(BaseModel):
    """Base schema for MMO classes."""

    name: str
    description: Optional[str] = None
    parent_class_id: Optional[str] = None
    properties: list[str] = []
    constraints: Optional[dict] = None


class MMOClassCreate(MMOClassBase):
    """Schema for creating an MMO class."""

    pass


class MMOClassUpdate(BaseModel):
    """Schema for updating an MMO class."""

    name: Optional[str] = None
    description: Optional[str] = None
    parent_class_id: Optional[str] = None
    properties: Optional[list[str]] = None
    constraints: Optional[dict] = None


class MMOClass(MMOClassBase):
    """Full MMO class entity."""

    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class MMOSlotBase(BaseModel):
    """Base schema for MMO slots."""

    name: str
    domain_class_id: str
    range_type: str
    cardinality: str = "0..*"
    description: Optional[str] = None


class MMOSlotCreate(MMOSlotBase):
    """Schema for creating an MMO slot."""

    pass


class MMOSlot(MMOSlotBase):
    """Full MMO slot entity."""

    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class MMOMetrics(BaseModel):
    """MMO evaluation metrics from v10 spec."""

    completeness: float = Field(ge=0.0, le=1.0, default=0.0)
    coverage: float = Field(ge=0.0, le=1.0, default=0.0)
    coherence: float = Field(ge=0.0, le=1.0, default=0.0)
    utility: float = Field(ge=0.0, le=1.0, default=0.0)
    inclusivity: float = Field(ge=0.0, le=1.0, default=0.0)
    mmo_score: float = Field(ge=0.0, le=1.0, default=0.0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class MMOSchema(BaseModel):
    """Full MMO schema response."""

    classes: list[MMOClass]
    slots: list[MMOSlot]
    metrics: MMOMetrics


# =============================================================================
# Global Models
# =============================================================================


class GlobalStats(BaseModel):
    """Global ontology statistics."""

    total_roots: int
    total_causality_links: int
    total_epistemic_annotations: int
    total_mmo_classes: int
    total_mmo_slots: int

    roots_by_type: dict[str, int]
    causality_by_type: dict[str, int]
    epistemic_by_basis: dict[str, int]

    avg_causality_confidence: float
    avg_epistemic_certainty: float

    last_updated: datetime = Field(default_factory=datetime.utcnow)


class GlobalSample(BaseModel):
    """Sample data from all services."""

    sample_roots: list[Root]
    sample_causality_links: list[CausalityLink]
    sample_annotations: list[EpistemicAnnotation]
    sample_mmo_classes: list[MMOClass]


class GlobalSummary(BaseModel):
    """Comprehensive global summary."""

    stats: GlobalStats
    sample: GlobalSample
    health: SystemHealthResponse
