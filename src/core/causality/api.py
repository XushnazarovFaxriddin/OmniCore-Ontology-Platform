"""
FastAPI application for the Causality Service.
"""

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware

from common.config import settings
from common.logging_config import setup_logging, get_logger
from common.exceptions import NotFoundError, OmniCoreException
from common.models import PaginatedResponse, HealthResponse, HealthStatus

from .models import CausalityLink, CausalityLinkCreate, CausalityLinkUpdate, CausalityType, CausalitySummary
from .service import CausalityService

# Setup logging
setup_logging(service_name="causality-service", level=settings.omnicore_log_level)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="OmniCore Causality Service",
    description="Manages causality links (EFFICIENT, FINAL, MATERIAL, FORMAL, EMERGENT)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service
service = CausalityService()


# Exception handlers
@app.exception_handler(OmniCoreException)
async def omnicore_exception_handler(request, exc: OmniCoreException):
    raise HTTPException(status_code=exc.status_code, detail=exc.message)


@app.exception_handler(NotFoundError)
async def not_found_handler(request, exc: NotFoundError):
    raise HTTPException(status_code=404, detail=exc.message)


# Health endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status=HealthStatus.HEALTHY,
        service="causality-service",
        timestamp=datetime.utcnow(),
        version="1.0.0",
    )


# Causality CRUD endpoints
@app.get("/causality-links", response_model=PaginatedResponse, tags=["Causality"])
async def list_links(
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
    causality_type: Optional[CausalityType] = Query(None, description="Filter by causality type"),
):
    """List all causality links with pagination."""
    return service.list_links(offset=offset, limit=limit, causality_type=causality_type)


@app.get("/causality-summary", response_model=CausalitySummary, tags=["Causality"])
async def get_summary():
    """Get summary statistics for causality links."""
    return service.get_summary()


@app.get("/causality-links/by-type/{causality_type}", response_model=PaginatedResponse, tags=["Causality"])
async def get_links_by_type(
    causality_type: CausalityType = Path(..., description="Causality type to filter by"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
):
    """Get causality links filtered by type."""
    return service.get_links_by_type(causality_type=causality_type, offset=offset, limit=limit)


@app.get("/causality-links/by-entity/{entity_id}", response_model=PaginatedResponse, tags=["Causality"])
async def get_links_by_entity(
    entity_id: str = Path(..., description="Entity ID"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
):
    """Get causality links involving a specific entity."""
    return service.get_links_by_entity(entity_id=entity_id, offset=offset, limit=limit)


@app.get("/causality-links/{link_id}", response_model=CausalityLink, tags=["Causality"])
async def get_link(
    link_id: str = Path(..., description="Link ID"),
):
    """Get a causality link by ID."""
    return service.get_link(link_id)


@app.post("/causality-links", response_model=CausalityLink, status_code=201, tags=["Causality"])
async def create_link(link_data: CausalityLinkCreate):
    """Create a new causality link."""
    return service.create_link(link_data)


@app.put("/causality-links/{link_id}", response_model=CausalityLink, tags=["Causality"])
async def update_link(
    link_id: str = Path(..., description="Link ID"),
    update_data: CausalityLinkUpdate = ...,
):
    """Update a causality link."""
    return service.update_link(link_id, update_data)


@app.delete("/causality-links/{link_id}", status_code=204, tags=["Causality"])
async def delete_link(
    link_id: str = Path(..., description="Link ID"),
):
    """Delete a causality link."""
    service.delete_link(link_id)
    return None


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Causality Service starting up...")
    logger.info(f"Environment: {settings.omnicore_env}")
    logger.info(f"Database path: {settings.database_path}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Causality Service shutting down...")
