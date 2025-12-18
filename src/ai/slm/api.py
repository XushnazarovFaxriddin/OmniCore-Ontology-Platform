"""
OmniCore Platform v10 - SLM Service API
FastAPI endpoints for SLM operations
"""

from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.common.config import get_settings, Settings
from src.common.logging_config import get_logger, setup_logging
from src.common.models import (
    SLMRequest, SLMResponse, HealthResponse, HealthStatus,
    RootType, Conflict, ConflictType
)
from .client import get_slm_client, SLMClient
from .service import SLMService

logger = get_logger("slm.api")

# Initialize FastAPI app
app = FastAPI(
    title="OmniCore SLM Service",
    description="Small Language Model Service for OmniCore v10",
    version="10.0.0"
)

# CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Dependencies
# =============================================================================


def get_slm_service() -> SLMService:
    """Get SLM service instance"""
    return SLMService()


# =============================================================================
# Request/Response Models
# =============================================================================


class RootTypeInferenceRequest(BaseModel):
    """Request for root type inference"""
    entity_name: str
    description: str = ""
    context: str = ""
    source: str = ""


class RootTypeInferenceResponse(BaseModel):
    """Response for root type inference"""
    entity_name: str
    root_type: RootType
    confidence: float
    reasoning: str


class CausalityExtractionRequest(BaseModel):
    """Request for causality extraction"""
    entities: List[str]
    descriptions: List[str]
    context: str = ""


class EpistemicAnnotationRequest(BaseModel):
    """Request for epistemic annotation"""
    entity_name: str
    claim: str
    source: str = ""
    context: str = ""


class ConflictResolutionRequest(BaseModel):
    """Request for conflict resolution via debate"""
    conflict_id: str
    conflict_type: ConflictType
    entity_a: str
    entity_b: str
    description: str
    max_rounds: int = Field(default=5, ge=1, le=10)


class QualityAssessmentRequest(BaseModel):
    """Request for ontology quality assessment"""
    name: str
    source: str
    domain: str
    triple_count: int
    sample_classes: List[str]
    sample_properties: List[str]


class StrategicPlanRequest(BaseModel):
    """Request for strategic plan generation"""
    metrics: dict
    gaps: List[str]


class EntityEnhancementRequest(BaseModel):
    """Request for entity enhancement"""
    entity_id: str
    entity_name: str
    entity_description: str
    enhancement_types: List[str] = ["root_hint", "epistemic"]


# =============================================================================
# Health Endpoints
# =============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    client = get_slm_client()
    provider_status = await client.health_check()

    # Determine overall status
    any_healthy = any(provider_status.values())
    status = HealthStatus.HEALTHY if any_healthy else HealthStatus.UNHEALTHY

    return HealthResponse(
        status=status,
        service="slm-service",
        version="10.0.0",
        details={"providers": provider_status}
    )


@app.get("/models")
async def list_models():
    """List available models from all providers"""
    client = get_slm_client()
    return await client.list_models()


# =============================================================================
# Core SLM Endpoints
# =============================================================================


@app.post("/generate", response_model=SLMResponse)
async def generate(request: SLMRequest):
    """
    Generate response from SLM.

    Direct interface to SLM with automatic fallback.
    """
    client = get_slm_client()
    return await client.generate(request)


@app.post("/infer-root-type", response_model=RootTypeInferenceResponse)
async def infer_root_type(
    request: RootTypeInferenceRequest,
    service: SLMService = Depends(get_slm_service)
):
    """
    Infer root type for an entity.

    Uses SLM to classify entity into EXTANT, ABSTRACT, MENTAL, or FICTIVE.
    """
    root_type, confidence, reasoning = await service.infer_root_type(
        entity_name=request.entity_name,
        description=request.description,
        context=request.context,
        source=request.source
    )

    return RootTypeInferenceResponse(
        entity_name=request.entity_name,
        root_type=root_type,
        confidence=confidence,
        reasoning=reasoning
    )


@app.post("/batch-infer-root-types")
async def batch_infer_root_types(
    entities: List[RootTypeInferenceRequest],
    service: SLMService = Depends(get_slm_service)
):
    """
    Batch infer root types for multiple entities.
    """
    entity_dicts = [
        {
            "name": e.entity_name,
            "description": e.description,
            "context": e.context,
            "source": e.source
        }
        for e in entities
    ]

    results = await service.batch_infer_root_types(entity_dicts)

    return [
        {
            "entity_name": name,
            "root_type": rt.value,
            "confidence": conf,
            "reasoning": reason
        }
        for name, rt, conf, reason in results
    ]


@app.post("/extract-causality")
async def extract_causality(
    request: CausalityExtractionRequest,
    service: SLMService = Depends(get_slm_service)
):
    """
    Extract implicit causal relationships from entities.

    Returns list of causality relationships with types and confidence.
    """
    relationships = await service.extract_causality(
        entities=request.entities,
        descriptions=request.descriptions,
        context=request.context
    )

    return {"relationships": relationships}


@app.post("/annotate-epistemic")
async def annotate_epistemic(
    request: EpistemicAnnotationRequest,
    service: SLMService = Depends(get_slm_service)
):
    """
    Generate epistemic annotation for a claim.

    Returns certainty, basis, and reasoning.
    """
    annotation = await service.generate_epistemic_annotation(
        entity_name=request.entity_name,
        claim=request.claim,
        source=request.source,
        context=request.context
    )

    return annotation


# =============================================================================
# Conflict Resolution Endpoints
# =============================================================================


@app.post("/resolve-conflict")
async def resolve_conflict(
    request: ConflictResolutionRequest,
    service: SLMService = Depends(get_slm_service)
):
    """
    Resolve ontological conflict via AI debate.

    v10 Protocol:
    - Multi-agent debate (Platonist, Nominalist, Pragmatist)
    - Moderator synthesis
    - Consensus threshold: 75%
    """
    conflict = Conflict(
        id=request.conflict_id,
        conflict_type=request.conflict_type,
        entity_a=request.entity_a,
        entity_b=request.entity_b,
        description=request.description,
        severity=0.5,
        resolved=False
    )

    result = await service.resolve_conflict_via_debate(
        conflict=conflict,
        max_rounds=request.max_rounds
    )

    return result


# =============================================================================
# Quality & Strategy Endpoints
# =============================================================================


@app.post("/assess-quality")
async def assess_quality(
    request: QualityAssessmentRequest,
    service: SLMService = Depends(get_slm_service)
):
    """
    Assess ontology quality for integration.

    Returns quality scores and recommendation (integrate/review/reject).
    """
    assessment = await service.assess_ontology_quality(
        name=request.name,
        source=request.source,
        domain=request.domain,
        triple_count=request.triple_count,
        sample_classes=request.sample_classes,
        sample_properties=request.sample_properties
    )

    return assessment


@app.post("/strategic-plan")
async def generate_strategic_plan(
    request: StrategicPlanRequest,
    service: SLMService = Depends(get_slm_service)
):
    """
    Generate strategic plan for quarterly review.

    v10 Phase 5: Autonomous planning with human oversight.
    """
    plan = await service.generate_strategic_plan(
        metrics=request.metrics,
        gaps=request.gaps
    )

    return plan


@app.post("/enhance-entity")
async def enhance_entity(
    request: EntityEnhancementRequest,
    service: SLMService = Depends(get_slm_service)
):
    """
    Enhance entity with SLM-derived insights.

    Enhancement types: root_hint, causality, epistemic
    """
    enhancements = await service.enhance_entity(
        entity_id=request.entity_id,
        entity_name=request.entity_name,
        entity_description=request.entity_description,
        enhancement_types=request.enhancement_types
    )

    return {"enhancements": [e.model_dump() for e in enhancements]}


# =============================================================================
# Startup
# =============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    setup_logging()
    logger.info("SLM Service starting...")

    # Check provider availability
    client = get_slm_client()
    status = await client.health_check()
    logger.info(f"SLM Providers: {status}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("SLM Service shutting down...")


# =============================================================================
# Main
# =============================================================================


def main():
    """Run SLM service"""
    import uvicorn
    uvicorn.run(
        "src.ai.slm.api:app",
        host="0.0.0.0",
        port=settings.slm_service_port,
        reload=settings.debug
    )


if __name__ == "__main__":
    main()
