"""
FastAPI application for the Global Ontology Service.
"""

from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from common.config import settings
from common.logging_config import setup_logging, get_logger
from common.models import HealthResponse, HealthStatus

from .models import GlobalStats, GlobalSample, GlobalSummary, SystemHealthResponse
from .service import GlobalService

# Setup logging
setup_logging(service_name="global-ontology-service", level=settings.omnicore_log_level)
logger = get_logger(__name__)

# Initialize service
service: GlobalService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage service lifecycle."""
    global service
    logger.info("Global Ontology Service starting up...")
    logger.info(f"Environment: {settings.omnicore_env}")
    service = GlobalService()
    yield
    logger.info("Global Ontology Service shutting down...")
    await service.close()


# Initialize FastAPI app
app = FastAPI(
    title="OmniCore Global Ontology Service",
    description="Aggregates data and health from all OmniCore services",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status=HealthStatus.HEALTHY,
        service="global-ontology-service",
        timestamp=datetime.utcnow(),
        version="1.0.0",
    )


# Global endpoints
@app.get("/global/stats", response_model=GlobalStats, tags=["Global"])
async def get_global_stats():
    """Get global statistics from all services."""
    return await service.get_global_stats()


@app.get("/global/sample", response_model=GlobalSample, tags=["Global"])
async def get_global_sample(
    sample_size: int = Query(5, ge=1, le=20, description="Number of samples per service"),
):
    """Get sample data from all services."""
    return await service.get_global_sample(sample_size=sample_size)


@app.get("/global/summary", response_model=GlobalSummary, tags=["Global"])
async def get_global_summary():
    """Get comprehensive summary including stats, samples, and health."""
    return await service.get_global_summary()


# System health endpoint
@app.get("/system/health", response_model=SystemHealthResponse, tags=["System"])
async def get_system_health():
    """Get health status of all services."""
    return await service.get_system_health()
