"""
OmniCore Platform v10 - SLM Service API
FastAPI endpoints for SLM operations

Features:
- Automatic model download on startup
- Chat with OmniCore project context
- Root type inference, causality extraction
- Epistemic annotation, conflict resolution
- Strategic planning, quality assessment
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from common.config import get_settings, Settings
from common.logging_config import get_logger, setup_logging
from common.models import (
    SLMRequest, SLMResponse, HealthResponse, HealthStatus,
    RootType, Conflict, ConflictType
)
from .client import get_slm_client, SLMClient
from .service import SLMService
from .model_manager import get_model_manager, auto_setup_models

logger = get_logger("slm.api")

# OmniCore Project Context for AI Chat
OMNICORE_CONTEXT = """You are OmniCore AI Assistant - an expert in ontology management and knowledge engineering.

## About OmniCore Platform v10
OmniCore is an AI-Orchestrated Ontological Computing System for semantic knowledge management.

### Core Concepts:
1. **Root Types** (ontological classification):
   - EXTANT: Physical, observable entities (mountains, atoms, organisms)
   - ABSTRACT: Non-physical concepts (mathematics, justice, algorithms)
   - MENTAL: Mind-dependent entities (emotions, dreams, beliefs)
   - FICTIVE: Fictional entities (Sherlock Holmes, Hogwarts, unicorns)

2. **Causality Types** (Aristotelian + emergence):
   - EFFICIENT: Direct cause-effect (fire causes heat)
   - FINAL: Purpose/goal (heart beats to pump blood)
   - MATERIAL: What something is made of (house made of bricks)
   - FORMAL: Shape/pattern (DNA structure determines traits)
   - EMERGENT: Arises from complexity (consciousness from neurons)

3. **Epistemic Bases** (knowledge certainty):
   - axiomatic: Self-evident truths (mathematical axioms)
   - empirical: Based on observation/experiment
   - consensus: Agreed upon by experts
   - speculative: Hypothetical/uncertain

4. **MMO (Meta-Meta Ontology)** Quality Metrics:
   - Completeness: Coverage of domain
   - Coverage: Breadth across areas
   - Coherence: Internal consistency
   - Utility: Practical usefulness
   - Inclusivity: Diverse perspectives

### Services (Port 18xxx):
- API Gateway: 18000 (main entry point)
- Roots Service: 18001 (entity classification)
- Causality Service: 18002 (causal relationships)
- Epistemic Service: 18003 (knowledge annotations)
- MMO Service: 18004 (quality metrics)
- Global Service: 18005 (aggregation)
- SLM Service: 18006 (AI/language models)
- Dashboard: 3000 (web interface)

### Key Features:
- AI-powered root type classification
- Automatic causality extraction
- Epistemic annotation generation
- Multi-agent debate for conflict resolution
- Strategic planning with human oversight
- Ontology import from OWL/RDF/Turtle

When answering questions:
1. Be helpful and informative about ontologies
2. Reference OmniCore concepts when relevant
3. Provide practical examples
4. Explain technical terms simply
"""

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


class ChatMessage(BaseModel):
    """Chat message"""
    role: str = Field(..., description="Role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request with context"""
    messages: List[ChatMessage]
    include_omnicore_context: bool = True
    max_tokens: int = 1024
    temperature: float = 0.7


class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    model_used: str
    confidence: float
    tokens_used: int
    latency_ms: float


class ModelSetupResponse(BaseModel):
    """Model setup status"""
    ollama_available: bool
    models_available: List[str]
    primary_model: Optional[str]
    fallback_model: Optional[str]
    ready: bool
    message: str


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


# =============================================================================
# Chat Endpoint with OmniCore Context
# =============================================================================


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with OmniCore AI Assistant.

    Features:
    - Automatic OmniCore project context injection
    - Multi-turn conversation support
    - Knowledge about ontology concepts
    """
    import time
    start_time = time.time()

    # Build conversation prompt
    messages = request.messages

    # Add OmniCore context if requested
    if request.include_omnicore_context:
        system_context = OMNICORE_CONTEXT
    else:
        system_context = "You are a helpful AI assistant specializing in ontology and knowledge management."

    # Format conversation
    conversation = f"{system_context}\n\n"
    for msg in messages:
        role = msg.role.capitalize()
        conversation += f"{role}: {msg.content}\n"
    conversation += "Assistant:"

    # Generate response
    client = get_slm_client()
    slm_request = SLMRequest(
        prompt=conversation,
        task_type="chat",
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )

    response = await client.generate(slm_request)
    latency_ms = (time.time() - start_time) * 1000

    return ChatResponse(
        response=response.response.strip(),
        model_used=response.model_used,
        confidence=response.confidence,
        tokens_used=response.tokens_used,
        latency_ms=round(latency_ms, 2)
    )


# =============================================================================
# Model Management Endpoints
# =============================================================================


@app.get("/models/status", response_model=ModelSetupResponse)
async def get_model_status():
    """
    Get current model availability status.
    """
    manager = get_model_manager()

    ollama_available = await manager.check_ollama_available()
    models = await manager.list_local_models() if ollama_available else []
    model_names = [m.name for m in models]

    settings = get_settings()
    primary = settings.slm_model_name if settings.slm_model_name in model_names else None
    fallback = settings.slm_fallback_model if settings.slm_fallback_model in model_names else None

    ready = primary is not None

    if not ollama_available:
        message = "Ollama service not running. Please start Ollama first."
    elif not ready:
        message = f"Primary model '{settings.slm_model_name}' not found. Use /models/setup to download."
    else:
        message = f"Ready with {len(model_names)} model(s) available."

    return ModelSetupResponse(
        ollama_available=ollama_available,
        models_available=model_names,
        primary_model=primary,
        fallback_model=fallback,
        ready=ready,
        message=message
    )


@app.post("/models/setup")
async def setup_models(background_tasks: BackgroundTasks):
    """
    Automatically download required models.

    This endpoint triggers background download of:
    - Primary model (llama3.2:1b)
    - Fallback model (gemma2:2b)
    """
    manager = get_model_manager()

    if not await manager.check_ollama_available():
        raise HTTPException(
            status_code=503,
            detail="Ollama service not available. Please install and start Ollama first."
        )

    # Run setup in background
    async def run_setup():
        result = await manager.auto_setup()
        logger.info(f"Model setup completed: {result}")

    background_tasks.add_task(run_setup)

    return {
        "status": "started",
        "message": "Model setup started in background. Check /models/status for progress."
    }


@app.post("/models/pull/{model_name}")
async def pull_model(model_name: str, background_tasks: BackgroundTasks):
    """
    Pull a specific model from Ollama registry.

    Examples:
    - llama3.2:1b
    - gemma2:2b
    - mistral:7b
    - phi3:mini
    """
    manager = get_model_manager()

    if not await manager.check_ollama_available():
        raise HTTPException(
            status_code=503,
            detail="Ollama service not available"
        )

    # Check if already available
    if await manager.is_model_available(model_name):
        return {"status": "available", "message": f"Model {model_name} is already downloaded"}

    # Pull in background
    async def pull_task():
        success = await manager.pull_model(model_name)
        logger.info(f"Model pull {model_name}: {'success' if success else 'failed'}")

    background_tasks.add_task(pull_task)

    return {
        "status": "downloading",
        "message": f"Downloading {model_name}. This may take several minutes."
    }


@app.delete("/models/{model_name}")
async def delete_model(model_name: str):
    """
    Delete a model from local storage.
    """
    manager = get_model_manager()
    success = await manager.delete_model(model_name)

    if success:
        return {"status": "deleted", "message": f"Model {model_name} deleted"}
    else:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found or could not be deleted")


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
    """Initialize on startup with auto model setup"""
    setup_logging()
    logger.info("SLM Service starting...")

    # Check provider availability
    client = get_slm_client()
    status = await client.health_check()
    logger.info(f"SLM Providers: {status}")

    # Auto-setup models if Ollama is available
    manager = get_model_manager()
    if await manager.check_ollama_available():
        logger.info("Ollama available, checking models...")

        # Check if primary model exists, download if not
        settings = get_settings()
        if not await manager.is_model_available(settings.slm_model_name):
            logger.info(f"Primary model {settings.slm_model_name} not found, downloading...")
            success = await manager.pull_model(settings.slm_model_name)
            if success:
                logger.info(f"Successfully downloaded {settings.slm_model_name}")
            else:
                logger.warning(f"Failed to download {settings.slm_model_name}")
        else:
            logger.info(f"Primary model {settings.slm_model_name} is available")

        # List available models
        models = await manager.list_local_models()
        logger.info(f"Available models: {[m.name for m in models]}")
    else:
        logger.warning("Ollama not available - AI features will be limited")


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
