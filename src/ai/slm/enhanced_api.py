"""
OmniCore Platform v10 - Enhanced SLM Service API
Professional-grade FastAPI endpoints with comprehensive features

Features:
- Chat session management
- Usage statistics & analytics
- Model configuration
- Rate limiting support
- Comprehensive health monitoring
- Chat history persistence
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import uuid
import asyncio
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import time

from common.config import get_settings, Settings
from common.logging_config import get_logger, setup_logging
from common.models import (
    SLMRequest, SLMResponse, HealthResponse, HealthStatus,
    RootType, Conflict, ConflictType
)
from .client import get_slm_client, SLMClient, SLMProvider
from .service import SLMService

logger = get_logger("slm.enhanced_api")

# Initialize FastAPI app
app = FastAPI(
    title="OmniCore Enhanced SLM Service",
    description="Professional-grade Small Language Model Service for OmniCore v10",
    version="10.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
# In-Memory Storage (Production: Use Redis/PostgreSQL)
# =============================================================================

class SessionStore:
    """In-memory session storage for chat history"""

    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=24)

    def create_session(self, user_id: Optional[str] = None) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "messages": [],
            "context": None,
            "model_preferences": {},
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        if session:
            # Check timeout
            if datetime.utcnow() - session["last_activity"] > self.session_timeout:
                del self.sessions[session_id]
                return None
            session["last_activity"] = datetime.utcnow()
        return session

    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None):
        session = self.get_session(session_id)
        if session:
            session["messages"].append({
                "id": str(uuid.uuid4()),
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            })

    def get_messages(self, session_id: str, limit: int = 50) -> List[Dict]:
        session = self.get_session(session_id)
        if session:
            return session["messages"][-limit:]
        return []

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def cleanup_expired(self):
        """Remove expired sessions"""
        now = datetime.utcnow()
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session["last_activity"] > self.session_timeout
        ]
        for sid in expired:
            del self.sessions[sid]


class UsageStats:
    """Track API usage statistics"""

    def __init__(self):
        self.stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "requests_by_endpoint": defaultdict(int),
            "requests_by_model": defaultdict(int),
            "errors": 0,
            "avg_latency_ms": 0.0,
            "latency_samples": [],
            "hourly_requests": defaultdict(int),
            "daily_requests": defaultdict(int),
            "start_time": datetime.utcnow().isoformat(),
        }

    def record_request(
        self,
        endpoint: str,
        model: str,
        tokens: int,
        latency_ms: float,
        success: bool = True
    ):
        self.stats["total_requests"] += 1
        self.stats["total_tokens"] += tokens
        self.stats["requests_by_endpoint"][endpoint] += 1
        self.stats["requests_by_model"][model] += 1

        if not success:
            self.stats["errors"] += 1

        # Rolling average latency (last 1000 samples)
        self.stats["latency_samples"].append(latency_ms)
        if len(self.stats["latency_samples"]) > 1000:
            self.stats["latency_samples"] = self.stats["latency_samples"][-1000:]
        self.stats["avg_latency_ms"] = sum(self.stats["latency_samples"]) / len(self.stats["latency_samples"])

        # Time-based stats
        now = datetime.utcnow()
        hour_key = now.strftime("%Y-%m-%d-%H")
        day_key = now.strftime("%Y-%m-%d")
        self.stats["hourly_requests"][hour_key] += 1
        self.stats["daily_requests"][day_key] += 1

    def get_summary(self) -> Dict[str, Any]:
        uptime = datetime.utcnow() - datetime.fromisoformat(self.stats["start_time"])
        return {
            "total_requests": self.stats["total_requests"],
            "total_tokens": self.stats["total_tokens"],
            "error_count": self.stats["errors"],
            "error_rate": self.stats["errors"] / max(1, self.stats["total_requests"]),
            "avg_latency_ms": round(self.stats["avg_latency_ms"], 2),
            "requests_per_endpoint": dict(self.stats["requests_by_endpoint"]),
            "requests_per_model": dict(self.stats["requests_by_model"]),
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime),
        }

    def get_detailed_stats(self) -> Dict[str, Any]:
        summary = self.get_summary()
        summary["hourly_requests"] = dict(self.stats["hourly_requests"])
        summary["daily_requests"] = dict(self.stats["daily_requests"])
        return summary


class ModelConfig:
    """Model configuration management"""

    def __init__(self):
        self.configs: Dict[str, Dict[str, Any]] = {
            "default": {
                "model": settings.slm_model_name,
                "temperature": settings.slm_temperature,
                "max_tokens": settings.slm_max_tokens,
                "provider": settings.slm_provider.value,
            }
        }

    def get_config(self, name: str = "default") -> Dict[str, Any]:
        return self.configs.get(name, self.configs["default"])

    def set_config(self, name: str, config: Dict[str, Any]):
        self.configs[name] = config

    def list_configs(self) -> Dict[str, Dict[str, Any]]:
        return self.configs


# Global stores
session_store = SessionStore()
usage_stats = UsageStats()
model_config = ModelConfig()


# =============================================================================
# Dependencies
# =============================================================================


def get_slm_service() -> SLMService:
    """Get SLM service instance"""
    return SLMService()


async def track_usage(request: Request, endpoint: str):
    """Middleware-style usage tracking"""
    start_time = time.time()
    return start_time, endpoint


# =============================================================================
# Request/Response Models
# =============================================================================


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role: user, assistant, system")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request with session support"""
    messages: List[ChatMessage]
    session_id: Optional[str] = None
    context: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False


class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    session_id: str
    model_id: str
    confidence: float
    tokens_used: int
    latency_ms: float
    cached: bool = False


class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    created_at: str
    message_count: int
    last_activity: str


class ModelInfo(BaseModel):
    """Model information"""
    id: str
    name: str
    provider: str
    size: Optional[str] = None
    capabilities: List[str] = []
    is_default: bool = False
    is_available: bool = True


class ConfigUpdate(BaseModel):
    """Configuration update request"""
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, ge=1, le=8192)
    provider: Optional[str] = None


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
# Health & Status Endpoints
# =============================================================================


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Comprehensive health check endpoint.
    Returns status of all SLM providers and system metrics.
    """
    client = get_slm_client()
    provider_status = await client.health_check()

    any_healthy = any(provider_status.values())
    status = HealthStatus.HEALTHY if any_healthy else HealthStatus.UNHEALTHY

    return HealthResponse(
        status=status,
        service="slm-service",
        version="10.1.0",
        details={
            "providers": provider_status,
            "default_model": settings.slm_model_name,
            "default_provider": settings.slm_provider.value,
            "active_sessions": len(session_store.sessions),
        }
    )


@app.get("/health/detailed", tags=["Health"])
async def detailed_health():
    """
    Detailed health check with provider-specific information.
    """
    client = get_slm_client()
    provider_status = await client.health_check()
    models = await client.list_models()

    return {
        "status": "healthy" if any(provider_status.values()) else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "providers": {
            provider: {
                "healthy": is_healthy,
                "models": models.get(provider, []),
            }
            for provider, is_healthy in provider_status.items()
        },
        "configuration": {
            "default_model": settings.slm_model_name,
            "default_provider": settings.slm_provider.value,
            "max_tokens": settings.slm_max_tokens,
            "temperature": settings.slm_temperature,
            "confidence_threshold": settings.slm_confidence_threshold,
        },
        "sessions": {
            "active": len(session_store.sessions),
            "timeout_hours": 24,
        }
    }


# =============================================================================
# Model Management Endpoints
# =============================================================================


@app.get("/models", response_model=List[ModelInfo], tags=["Models"])
async def list_models():
    """
    List all available models from all providers.
    """
    client = get_slm_client()
    models_by_provider = await client.list_models()

    result = []
    for provider, models in models_by_provider.items():
        for model in models:
            result.append(ModelInfo(
                id=model,
                name=model.split(":")[0],
                provider=provider,
                size=model.split(":")[-1] if ":" in model else None,
                capabilities=["text-generation", "chat"],
                is_default=model == settings.slm_model_name,
                is_available=True
            ))

    return result


@app.get("/models/{model_id}", tags=["Models"])
async def get_model_info(model_id: str):
    """
    Get detailed information about a specific model.
    """
    client = get_slm_client()
    models_by_provider = await client.list_models()

    for provider, models in models_by_provider.items():
        if model_id in models:
            return {
                "id": model_id,
                "name": model_id.split(":")[0],
                "provider": provider,
                "size": model_id.split(":")[-1] if ":" in model_id else None,
                "capabilities": ["text-generation", "chat", "reasoning"],
                "is_available": True,
                "parameters": {
                    "context_length": 4096,
                    "default_temperature": settings.slm_temperature,
                    "max_tokens": settings.slm_max_tokens,
                }
            }

    raise HTTPException(status_code=404, detail=f"Model {model_id} not found")


@app.post("/models/pull", tags=["Models"])
async def pull_model(model_name: str, background_tasks: BackgroundTasks):
    """
    Pull a model from Ollama registry (background task).
    """
    client = get_slm_client()
    ollama_client = client.get_client(SLMProvider.OLLAMA)

    if not ollama_client:
        raise HTTPException(status_code=503, detail="Ollama provider not available")

    async def pull_task():
        result = await ollama_client.pull_model(model_name)
        logger.info(f"Model pull completed: {model_name}, success: {result}")

    background_tasks.add_task(pull_task)

    return {"status": "pulling", "model": model_name, "message": "Model pull started in background"}


# =============================================================================
# Statistics Endpoints
# =============================================================================


@app.get("/stats", tags=["Statistics"])
async def get_usage_stats():
    """
    Get API usage statistics summary.
    """
    return usage_stats.get_summary()


@app.get("/stats/detailed", tags=["Statistics"])
async def get_detailed_stats():
    """
    Get detailed API usage statistics including time-series data.
    """
    return usage_stats.get_detailed_stats()


@app.post("/stats/reset", tags=["Statistics"])
async def reset_stats():
    """
    Reset usage statistics (admin only in production).
    """
    global usage_stats
    usage_stats = UsageStats()
    return {"status": "reset", "timestamp": datetime.utcnow().isoformat()}


# =============================================================================
# Configuration Endpoints
# =============================================================================


@app.get("/config", tags=["Configuration"])
async def get_configuration():
    """
    Get current model configuration.
    """
    return {
        "configs": model_config.list_configs(),
        "active": "default",
        "system": {
            "default_model": settings.slm_model_name,
            "default_provider": settings.slm_provider.value,
            "confidence_threshold": settings.slm_confidence_threshold,
            "cache_enabled": settings.slm_enable_caching,
            "cache_ttl": settings.slm_cache_ttl,
        }
    }


@app.put("/config/{config_name}", tags=["Configuration"])
async def update_configuration(config_name: str, config: ConfigUpdate):
    """
    Update model configuration.
    Note: In production, this would require admin authentication.
    """
    current = model_config.get_config(config_name)
    updated = {**current}

    if config.model:
        updated["model"] = config.model
    if config.temperature is not None:
        updated["temperature"] = config.temperature
    if config.max_tokens is not None:
        updated["max_tokens"] = config.max_tokens
    if config.provider:
        updated["provider"] = config.provider

    model_config.set_config(config_name, updated)

    return {"status": "updated", "config": updated}


# =============================================================================
# Chat Session Endpoints
# =============================================================================


@app.post("/sessions", response_model=SessionInfo, tags=["Sessions"])
async def create_session(user_id: Optional[str] = None):
    """
    Create a new chat session.
    """
    session_id = session_store.create_session(user_id)
    session = session_store.get_session(session_id)

    return SessionInfo(
        session_id=session_id,
        created_at=session["created_at"].isoformat(),
        message_count=0,
        last_activity=session["last_activity"].isoformat()
    )


@app.get("/sessions/{session_id}", tags=["Sessions"])
async def get_session(session_id: str):
    """
    Get session information and history.
    """
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    return {
        "session_id": session_id,
        "created_at": session["created_at"].isoformat(),
        "last_activity": session["last_activity"].isoformat(),
        "message_count": len(session["messages"]),
        "messages": session["messages"],
    }


@app.delete("/sessions/{session_id}", tags=["Sessions"])
async def delete_session(session_id: str):
    """
    Delete a chat session.
    """
    session_store.delete_session(session_id)
    return {"status": "deleted", "session_id": session_id}


@app.get("/sessions/{session_id}/messages", tags=["Sessions"])
async def get_session_messages(
    session_id: str,
    limit: int = Query(default=50, ge=1, le=200)
):
    """
    Get messages from a session.
    """
    messages = session_store.get_messages(session_id, limit)
    return {"session_id": session_id, "messages": messages, "count": len(messages)}


# =============================================================================
# Core Chat Endpoints
# =============================================================================


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat endpoint with session management.

    Features:
    - Automatic session creation/reuse
    - Context injection for OmniCore platform awareness
    - Message history tracking
    - Usage statistics
    """
    start_time = time.time()

    # Get or create session
    session_id = request.session_id
    if not session_id or not session_store.get_session(session_id):
        session_id = session_store.create_session()

    # Build prompt with context
    context = request.context or """You are OmniCore AI Assistant, an expert in ontology management and knowledge engineering.
You help users with the OmniCore Ontology Platform v10, which includes:
- Root type classification (EXTANT, ABSTRACT, MENTAL, FICTIVE)
- Causality tracking (EFFICIENT, FINAL, MATERIAL, FORMAL, EMERGENT)
- Epistemic annotations (certainty, basis, evidence)
- MMO quality metrics
Provide helpful, accurate responses about ontologies and the platform."""

    # Format conversation
    conversation = "\n".join([
        f"{msg.role}: {msg.content}"
        for msg in request.messages
    ])

    full_prompt = f"{context}\n\n{conversation}\nassistant:"

    # Get configuration
    config = model_config.get_config()

    # Generate response
    client = get_slm_client()
    slm_request = SLMRequest(
        prompt=full_prompt,
        task_type="chat",
        model=request.model or config["model"],
        max_tokens=request.max_tokens or config["max_tokens"],
        temperature=request.temperature or config["temperature"]
    )

    response = await client.generate(slm_request)
    latency_ms = (time.time() - start_time) * 1000

    # Store messages
    for msg in request.messages:
        session_store.add_message(session_id, msg.role, msg.content)

    session_store.add_message(
        session_id, "assistant", response.response,
        {"model": response.model_used, "confidence": response.confidence}
    )

    # Track usage
    usage_stats.record_request(
        endpoint="/chat",
        model=response.model_used,
        tokens=response.tokens_used,
        latency_ms=latency_ms,
        success=response.confidence > 0
    )

    return ChatResponse(
        response=response.response,
        session_id=session_id,
        model_id=response.model_used,
        confidence=response.confidence,
        tokens_used=response.tokens_used,
        latency_ms=round(latency_ms, 2),
        cached=response.cached
    )


@app.post("/generate", response_model=SLMResponse, tags=["Generation"])
async def generate(request: SLMRequest):
    """
    Direct generation endpoint without session management.
    """
    start_time = time.time()

    client = get_slm_client()
    response = await client.generate(request)

    latency_ms = (time.time() - start_time) * 1000

    # Track usage
    usage_stats.record_request(
        endpoint="/generate",
        model=response.model_used,
        tokens=response.tokens_used,
        latency_ms=latency_ms,
        success=response.confidence > 0
    )

    return response


# =============================================================================
# Ontology AI Endpoints
# =============================================================================


@app.post("/infer-root-type", response_model=RootTypeInferenceResponse, tags=["Ontology AI"])
async def infer_root_type(
    request: RootTypeInferenceRequest,
    service: SLMService = Depends(get_slm_service)
):
    """
    Infer root type for an entity using AI.
    Classifies into: EXTANT, ABSTRACT, MENTAL, or FICTIVE.
    """
    start_time = time.time()

    root_type, confidence, reasoning = await service.infer_root_type(
        entity_name=request.entity_name,
        description=request.description,
        context=request.context,
        source=request.source
    )

    usage_stats.record_request(
        endpoint="/infer-root-type",
        model=settings.slm_model_name,
        tokens=100,  # Estimated
        latency_ms=(time.time() - start_time) * 1000
    )

    return RootTypeInferenceResponse(
        entity_name=request.entity_name,
        root_type=root_type,
        confidence=confidence,
        reasoning=reasoning
    )


@app.post("/batch-infer-root-types", tags=["Ontology AI"])
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


@app.post("/extract-causality", tags=["Ontology AI"])
async def extract_causality(
    request: CausalityExtractionRequest,
    service: SLMService = Depends(get_slm_service)
):
    """
    Extract causal relationships from entities.
    Returns causality types: EFFICIENT, FINAL, MATERIAL, FORMAL, EMERGENT.
    """
    relationships = await service.extract_causality(
        entities=request.entities,
        descriptions=request.descriptions,
        context=request.context
    )

    return {"relationships": relationships}


@app.post("/annotate-epistemic", tags=["Ontology AI"])
async def annotate_epistemic(
    request: EpistemicAnnotationRequest,
    service: SLMService = Depends(get_slm_service)
):
    """
    Generate epistemic annotation for a claim.
    Returns certainty, basis (axiomatic/empirical/consensus/speculative), and reasoning.
    """
    annotation = await service.generate_epistemic_annotation(
        entity_name=request.entity_name,
        claim=request.claim,
        source=request.source,
        context=request.context
    )

    return annotation


@app.post("/resolve-conflict", tags=["Ontology AI"])
async def resolve_conflict(
    request: ConflictResolutionRequest,
    service: SLMService = Depends(get_slm_service)
):
    """
    Resolve ontological conflict via multi-agent AI debate.

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


@app.post("/assess-quality", tags=["Ontology AI"])
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


@app.post("/strategic-plan", tags=["Ontology AI"])
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


@app.post("/enhance-entity", tags=["Ontology AI"])
async def enhance_entity(
    request: EntityEnhancementRequest,
    service: SLMService = Depends(get_slm_service)
):
    """
    Enhance entity with AI-derived insights.
    Enhancement types: root_hint, causality, epistemic.
    """
    enhancements = await service.enhance_entity(
        entity_id=request.entity_id,
        entity_name=request.entity_name,
        entity_description=request.entity_description,
        enhancement_types=request.enhancement_types
    )

    return {"enhancements": [e.model_dump() for e in enhancements]}


# =============================================================================
# Startup & Shutdown
# =============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    setup_logging()
    logger.info("Enhanced SLM Service starting...")

    # Check provider availability
    client = get_slm_client()
    status = await client.health_check()
    logger.info(f"SLM Providers: {status}")

    # Start session cleanup task
    async def cleanup_loop():
        while True:
            await asyncio.sleep(3600)  # Every hour
            session_store.cleanup_expired()
            logger.info("Cleaned up expired sessions")

    asyncio.create_task(cleanup_loop())


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Enhanced SLM Service shutting down...")
    logger.info(f"Final stats: {usage_stats.get_summary()}")


# =============================================================================
# Main
# =============================================================================


def main():
    """Run enhanced SLM service"""
    import uvicorn
    uvicorn.run(
        "src.ai.slm.enhanced_api:app",
        host="0.0.0.0",
        port=settings.slm_service_port,
        reload=settings.debug
    )


if __name__ == "__main__":
    main()
