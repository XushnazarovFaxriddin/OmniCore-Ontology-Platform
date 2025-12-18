"""
OmniCore Platform v10 - Shared Pydantic Models
Complete data models with provenance tracking, audit trails, and v10 spec compliance
"""

from enum import Enum
from typing import Optional, Any, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
import hashlib
import json


# =============================================================================
# Enums (v10 Spec Compliant)
# =============================================================================


class RootType(str, Enum):
    """
    Four fundamental ontological root types from v10 spec.

    v10 Clarification:
    - "Sherlock Holmes" is FICTIVE, not MENTAL — existence depends on narrative context
    - "Pain" is MENTAL when experienced, but ABSTRACT when defined (e.g., in ICD-11)
    """
    EXTANT = "EXTANT"      # Entities with spatiotemporal location
    ABSTRACT = "ABSTRACT"  # Atemporal, mind-independent structures
    MENTAL = "MENTAL"      # Subjective, first-person accessible states
    FICTIVE = "FICTIVE"    # Context-dependent representations (fiction, simulation)


class CausalityType(str, Enum):
    """
    Five causality types from v10 spec (Aristotelian + Emergent).

    Predicates:
    - EFFICIENT: causesDirectly (hammer → nail_driving)
    - FINAL: servesPurpose (nest → offspring_protection)
    - MATERIAL: constitutedBy (statue → bronze)
    - FORMAL: structuredAs (organism → genome)
    - EMERGENT: emergesFrom (consciousness → neural_network_activity)
    """
    EFFICIENT = "EFFICIENT"  # causesDirectly
    FINAL = "FINAL"          # servesPurpose
    MATERIAL = "MATERIAL"    # constitutedBy
    FORMAL = "FORMAL"        # structuredAs
    EMERGENT = "EMERGENT"    # emergesFrom


class EpistemicBasis(str, Enum):
    """Epistemic basis types from v10 spec."""
    AXIOMATIC = "axiomatic"      # Self-evident truths
    EMPIRICAL = "empirical"      # Evidence-based
    CONSENSUS = "consensus"      # Community agreement
    SPECULATIVE = "speculative"  # Hypothetical


class ConflictType(str, Enum):
    """Types of conflicts in ontology merging"""
    ROOT_DISAGREEMENT = "root_disagreement"
    CAUSAL_CYCLE = "causal_cycle"
    EPISTEMIC_CONTRADICTION = "epistemic_contradiction"
    SEMANTIC_OVERLAP = "semantic_overlap"


class HealthStatus(str, Enum):
    """Service health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UP = "up"
    DOWN = "down"


class AIAgentRole(str, Enum):
    """AI agent roles for debate/conflict resolution"""
    PLATONIST = "platonist"
    NOMINALIST = "nominalist"
    PRAGMATIST = "pragmatist"
    MODERATOR = "moderator"
    SPECIALIST = "specialist"


# =============================================================================
# Provenance Models (v10 - Critical for Audit Trail)
# =============================================================================


class Provenance(BaseModel):
    """
    Complete provenance tracking for every entity (v10 spec requirement).
    Every entity retains: import_source, ai_enhancement_trace, resolution_path
    """
    source_ontology: Optional[str] = None  # e.g., "http://purl.obolibrary.org/obo/go.owl"
    parsed_by: str = "rdflib 7.0.0"
    enhanced_by: Optional[str] = None  # e.g., "Llama-3.2-1B (sha256:a1b2c3...)"
    ai_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    rationale_trace: Optional[str] = None
    conflict_resolution: Optional[str] = None  # e.g., "debate_20251205_1432Z"
    committed_at: datetime = Field(default_factory=datetime.utcnow)
    operation_id: Optional[str] = None  # Required for DELETE/UPDATE (v10 safety)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_ontology": self.source_ontology,
            "parsed_by": self.parsed_by,
            "enhanced_by": self.enhanced_by,
            "ai_confidence": self.ai_confidence,
            "rationale_trace": self.rationale_trace,
            "conflict_resolution": self.conflict_resolution,
            "committed_at": self.committed_at.isoformat() if self.committed_at else None,
            "operation_id": self.operation_id
        }


class AuditLogEntry(BaseModel):
    """Audit log entry for all operations"""
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    operation: str  # CREATE, UPDATE, DELETE, IMPORT, MERGE, etc.
    entity_type: str
    entity_id: str
    user_id: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    provenance: Optional[Provenance] = None


# =============================================================================
# Common Models
# =============================================================================


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=1000)


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    items: List[Any]
    total: int
    offset: int
    limit: int
    has_more: bool


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[Any] = None
    status_code: int
    operation_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: HealthStatus
    service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "10.0.0"
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
    services: Dict[str, ServiceHealthDetail]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# Root Models (v10 Enhanced)
# =============================================================================


class RootBase(BaseModel):
    """Base schema for root entities."""
    name: str = Field(..., min_length=1, max_length=255)
    root_type: RootType
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    iri: Optional[str] = None  # RDF IRI if from ontology


class RootCreate(RootBase):
    """Schema for creating a new root."""
    import_source: Optional[str] = None
    use_slm: bool = False  # Enable SLM enhancement


class RootUpdate(BaseModel):
    """Schema for updating a root."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    root_type: Optional[RootType] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    operation_id: str = Field(...)  # Required for v10 safety


class Root(RootBase):
    """Full root entity with provenance."""
    id: str
    created_at: datetime
    updated_at: datetime
    import_source: Optional[str] = None
    ai_enhancement_trace: Optional[str] = None
    ai_confidence: Optional[float] = None
    provenance: Optional[Provenance] = None

    class Config:
        from_attributes = True


class RootSummary(BaseModel):
    """Summary statistics for roots."""
    total_count: int
    by_type: Dict[str, int]


# =============================================================================
# Causality Models (v10 Enhanced with RDF Support)
# =============================================================================


class CausalEvent(BaseModel):
    """
    Causal event representation (v10 RDF format).

    Example RDF:
    :Hammer :causesDirectly [
        a :CausalEvent ;
        :hasAgent :Hammer ;
        :hasPatient :Nail ;
        :hasOutcome :NailDriven ;
        :causalityType :EFFICIENT
    ] .
    """
    agent: str
    patient: Optional[str] = None
    outcome: Optional[str] = None
    context: Optional[str] = None


class CausalityLinkBase(BaseModel):
    """Base schema for causality links."""
    source_entity_id: str
    target_entity_id: str
    causality_type: CausalityType
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    causal_event: Optional[CausalEvent] = None


class CausalityLinkCreate(CausalityLinkBase):
    """Schema for creating a causal link."""
    use_slm: bool = False  # Enable SLM for implicit causality extraction


class CausalityLinkUpdate(BaseModel):
    """Schema for updating a causality link."""
    source_entity_id: Optional[str] = None
    target_entity_id: Optional[str] = None
    causality_type: Optional[CausalityType] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    operation_id: str = Field(...)  # Required for v10 safety


class CausalityLink(CausalityLinkBase):
    """Full causality link entity with provenance."""
    id: str
    created_at: datetime
    updated_at: datetime
    ai_confidence: Optional[float] = None
    rationale_trace: Optional[str] = None
    provenance: Optional[Provenance] = None

    class Config:
        from_attributes = True


class CausalitySummary(BaseModel):
    """Summary statistics for causality links."""
    total_count: int
    by_type: Dict[str, int]
    avg_confidence: float


# =============================================================================
# Epistemic Models (v10 Enhanced)
# =============================================================================


class EpistemicAnnotationBase(BaseModel):
    """
    Base schema for epistemic annotations.
    v10 spec: certainty, basis, source (DOI, ontology IRI, model ID), timestamp
    """
    entity_id: str
    certainty: float = Field(ge=0.0, le=1.0)
    basis: EpistemicBasis
    source: Optional[str] = None  # DOI, ontology IRI, model ID
    note: Optional[str] = None


class EpistemicAnnotationCreate(EpistemicAnnotationBase):
    """Schema for creating an epistemic annotation."""
    use_slm: bool = False  # Enable SLM for epistemic hints extraction


class EpistemicAnnotationUpdate(BaseModel):
    """Schema for updating an epistemic annotation."""
    entity_id: Optional[str] = None
    certainty: Optional[float] = Field(None, ge=0.0, le=1.0)
    basis: Optional[EpistemicBasis] = None
    source: Optional[str] = None
    note: Optional[str] = None
    operation_id: str = Field(...)  # Required for v10 safety


class EpistemicAnnotation(EpistemicAnnotationBase):
    """Full epistemic annotation entity."""
    id: str
    timestamp: datetime
    provenance: Optional[Provenance] = None

    class Config:
        from_attributes = True


class EpistemicSummary(BaseModel):
    """Summary statistics for epistemic annotations."""
    total_count: int
    by_basis: Dict[str, int]
    avg_certainty: float
    certainty_distribution: Dict[str, int]


# =============================================================================
# MMO Models (v10 Self-Calibrating Metrics)
# =============================================================================


class MMOClassBase(BaseModel):
    """Base schema for MMO classes."""
    name: str
    description: Optional[str] = None
    parent_class_id: Optional[str] = None
    properties: List[str] = []
    constraints: Optional[Dict[str, Any]] = None


class MMOClassCreate(MMOClassBase):
    """Schema for creating an MMO class."""
    pass


class MMOClassUpdate(BaseModel):
    """Schema for updating an MMO class."""
    name: Optional[str] = None
    description: Optional[str] = None
    parent_class_id: Optional[str] = None
    properties: Optional[List[str]] = None
    constraints: Optional[Dict[str, Any]] = None
    operation_id: str = Field(...)


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
    """
    MMO evaluation metrics from v10 spec (Self-Calibrating).

    Formula: MMO_Score = w₁·C + w₂·Cv + w₃·Ch + w₄·U + w₅·I
    where wᵢ = softmax(predictive_powerᵢ)
    """
    completeness: float = Field(ge=0.0, le=1.0, default=0.0)  # ≥0.85 target
    coverage: float = Field(ge=0.0, le=1.0, default=0.0)      # ≥0.70 target
    coherence: float = Field(ge=0.0, le=1.0, default=0.0)     # ≥0.95 target
    utility: float = Field(ge=0.0, le=1.0, default=0.0)       # ≥0.80 target (v10 new)
    inclusivity: float = Field(ge=0.0, le=1.0, default=0.0)   # ≥0.65 target (v10 new)
    mmo_score: float = Field(ge=0.0, le=1.0, default=0.0)

    # Dynamic weights (v10)
    weights: Dict[str, float] = Field(default_factory=lambda: {
        "completeness": 0.25,
        "coverage": 0.20,
        "coherence": 0.25,
        "utility": 0.15,
        "inclusivity": 0.15
    })

    last_updated: datetime = Field(default_factory=datetime.utcnow)
    evolution_triggers: List[str] = []  # Triggered improvements


class MMOEvaluation(BaseModel):
    """MMO evaluation result"""
    ontology_version: str
    metrics: MMOMetrics
    recommendations: List[str] = []
    radar_chart_data: Optional[Dict[str, float]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MMOSchema(BaseModel):
    """Full MMO schema response."""
    classes: List[MMOClass]
    slots: List[MMOSlot]
    metrics: MMOMetrics


# =============================================================================
# Ontology Import Models (v10 Pipeline)
# =============================================================================


class OntologyImportRequest(BaseModel):
    """Request to import an ontology"""
    source_url: Optional[str] = None  # URL to fetch
    content: Optional[str] = None     # Direct content
    format: str = "turtle"            # xml, turtle, n3, nt, json-ld
    use_slm: bool = True              # Enable SLM enhancement
    conflict_resolution: str = "auto"  # auto, manual, skip


class OntologyImportResult(BaseModel):
    """Result of ontology import"""
    success: bool
    ontology_id: str
    version: str  # mo:vX.Y.Z-timestamp
    triples_imported: int
    entities_created: int
    causality_links_created: int
    epistemic_annotations_created: int
    conflicts_detected: int
    conflicts_resolved: int
    slm_enhancements: int
    processing_time_ms: float
    provenance: Provenance
    errors: List[str] = []
    warnings: List[str] = []


class ParsedEntity(BaseModel):
    """Entity parsed from RDF/OWL"""
    iri: str
    name: str
    entity_type: str  # Class, Property, Individual
    inferred_root_type: Optional[RootType] = None
    labels: List[str] = []
    comments: List[str] = []
    parent_iris: List[str] = []
    metadata: Dict[str, Any] = {}


# =============================================================================
# Conflict Resolution Models (v10)
# =============================================================================


class Conflict(BaseModel):
    """Detected conflict during ontology merge"""
    id: str
    conflict_type: ConflictType
    entity_a: str
    entity_b: str
    description: str
    severity: float = Field(ge=0.0, le=1.0)
    resolution_options: List[str] = []
    resolved: bool = False
    resolution: Optional[str] = None


class DebateRound(BaseModel):
    """Single round in AI debate"""
    round_number: int
    agent_role: AIAgentRole
    argument: str
    confidence: float
    supporting_evidence: List[str] = []


class DebateResult(BaseModel):
    """Result of AI debate for conflict resolution"""
    conflict_id: str
    rounds: List[DebateRound]
    consensus_reached: bool
    consensus_threshold: float
    final_resolution: str
    supporting_agents: List[AIAgentRole]
    contextual_axiom: Optional[str] = None  # RDF representation


class ConflictResolutionResult(BaseModel):
    """Overall conflict resolution result"""
    total_conflicts: int
    auto_resolved: int
    debate_resolved: int
    manual_required: int
    debates: List[DebateResult] = []


# =============================================================================
# SLM Models (v10)
# =============================================================================


class SLMRequest(BaseModel):
    """Request to SLM service"""
    prompt: str
    model: Optional[str] = None  # Use default if not specified
    max_tokens: int = 1024
    temperature: float = 0.1
    task_type: str = "general"  # general, causality, epistemic, root_mapping, conflict


class SLMResponse(BaseModel):
    """Response from SLM service"""
    response: str
    model_used: str
    confidence: float
    rationale: Optional[str] = None
    tokens_used: int
    latency_ms: float
    cached: bool = False


class SLMEnhancement(BaseModel):
    """SLM enhancement result for an entity"""
    entity_id: str
    enhancement_type: str  # causality, epistemic, root_hint
    original_value: Optional[str] = None
    enhanced_value: str
    confidence: float
    rationale: str
    model_id: str


# =============================================================================
# Strategic AI Models (v10 Phase 5)
# =============================================================================


class StrategicGoals(BaseModel):
    """Strategic goals for quarterly evaluation"""
    ontology_coverage: bool = False      # >= 1000 ontologies
    mmo_accuracy: bool = False           # >= 0.90 R²
    ai_task_success: bool = False        # >= 0.92 success rate
    human_intervention: bool = False     # <= 20 interventions
    ethical_flags: bool = False          # == 0 unresolved


class StrategicPlan(BaseModel):
    """AI-generated strategic plan"""
    actions: List[str]
    rationale: str
    rollback_plan: str
    requires_human_approval: bool = False
    affected_components: List[str] = []


class QuarterlyReview(BaseModel):
    """Quarterly strategic review"""
    review_id: str
    timestamp: datetime
    current_metrics: Dict[str, float]
    goals_met: StrategicGoals
    gaps: List[str]
    plan: StrategicPlan
    status: str = "pending"  # pending, approved, rejected, implemented


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
    total_ontologies_imported: int

    roots_by_type: Dict[str, int]
    causality_by_type: Dict[str, int]
    epistemic_by_basis: Dict[str, int]

    avg_causality_confidence: float
    avg_epistemic_certainty: float

    mo_version: str
    mmo_score: float

    last_updated: datetime = Field(default_factory=datetime.utcnow)


class GlobalSample(BaseModel):
    """Sample data from all services."""
    sample_roots: List[Root]
    sample_causality_links: List[CausalityLink]
    sample_annotations: List[EpistemicAnnotation]
    sample_mmo_classes: List[MMOClass]


class GlobalSummary(BaseModel):
    """Comprehensive global summary."""
    stats: GlobalStats
    sample: GlobalSample
    health: SystemHealthResponse


class MOVersion(BaseModel):
    """Meta-Ontology version information"""
    version: str  # mo:vX.Y.Z-timestamp
    created_at: datetime
    snapshot_path: Optional[str] = None
    entities_count: int
    triples_count: int
    changelog: List[str] = []


# =============================================================================
# Safety & Rollback Models (v10)
# =============================================================================


class RollbackRequest(BaseModel):
    """Request to rollback to a previous MO version"""
    target_version: str  # e.g., "mo:v3.2.0"
    dry_run: bool = True
    reason: str


class RollbackResult(BaseModel):
    """Result of rollback operation"""
    success: bool
    from_version: str
    to_version: str
    entities_restored: int
    entities_removed: int
    dry_run: bool
    changes_preview: Optional[List[str]] = None


class EthicalAlert(BaseModel):
    """Ethical alert for human oversight"""
    id: str
    timestamp: datetime
    alert_type: str  # new_root_type, mmo_weight_shift, high_bias_source
    severity: float
    description: str
    affected_entities: List[str]
    requires_approval: bool = True
    resolved: bool = False
    resolution: Optional[str] = None
    resolver_id: Optional[str] = None


# =============================================================================
# Utility Functions
# =============================================================================


def generate_operation_id() -> str:
    """Generate unique operation ID for audit trail"""
    import uuid
    return f"op_{uuid.uuid4().hex[:12]}_{int(datetime.utcnow().timestamp())}"


def generate_version_string(major: int = 1, minor: int = 0, patch: int = 0) -> str:
    """Generate MO version string"""
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return f"mo:v{major}.{minor}.{patch}-{timestamp}"


def compute_entity_hash(entity: BaseModel) -> str:
    """Compute hash for entity deduplication"""
    data = entity.model_dump_json(exclude={'id', 'created_at', 'updated_at'})
    return hashlib.sha256(data.encode()).hexdigest()[:16]
