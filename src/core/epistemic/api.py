"""
FastAPI application for the Epistemic Service.
"""

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware

from common.config import settings
from common.logging_config import setup_logging, get_logger
from common.exceptions import NotFoundError, OmniCoreException
from common.models import PaginatedResponse, HealthResponse, HealthStatus

from .models import EpistemicAnnotation, EpistemicAnnotationCreate, EpistemicAnnotationUpdate, EpistemicBasis, EpistemicSummary
from .service import EpistemicService

# Setup logging
setup_logging(service_name="epistemic-service", level=settings.omnicore_log_level)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="OmniCore Epistemic Service",
    description="Manages epistemic annotations (axiomatic, empirical, consensus, speculative)",
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
service = EpistemicService()


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
        service="epistemic-service",
        timestamp=datetime.utcnow(),
        version="1.0.0",
    )


# Epistemic CRUD endpoints
@app.get("/annotations", response_model=PaginatedResponse, tags=["Epistemic"])
async def list_annotations(
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
    basis: Optional[EpistemicBasis] = Query(None, description="Filter by epistemic basis"),
):
    """List all epistemic annotations with pagination."""
    return service.list_annotations(offset=offset, limit=limit, basis=basis)


@app.get("/annotations/summary", response_model=EpistemicSummary, tags=["Epistemic"])
async def get_summary():
    """Get summary statistics for epistemic annotations."""
    return service.get_summary()


@app.get("/annotations/by-basis/{basis}", response_model=PaginatedResponse, tags=["Epistemic"])
async def get_annotations_by_basis(
    basis: EpistemicBasis = Path(..., description="Epistemic basis to filter by"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
):
    """Get annotations filtered by epistemic basis."""
    return service.get_annotations_by_basis(basis=basis, offset=offset, limit=limit)


@app.get("/entities/{entity_id}/annotations", response_model=PaginatedResponse, tags=["Epistemic"])
async def get_entity_annotations(
    entity_id: str = Path(..., description="Entity ID"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
):
    """Get annotations for a specific entity."""
    return service.get_annotations_for_entity(entity_id=entity_id, offset=offset, limit=limit)


@app.get("/annotations/{annotation_id}", response_model=EpistemicAnnotation, tags=["Epistemic"])
async def get_annotation(
    annotation_id: str = Path(..., description="Annotation ID"),
):
    """Get an epistemic annotation by ID."""
    return service.get_annotation(annotation_id)


@app.post("/annotations", response_model=EpistemicAnnotation, status_code=201, tags=["Epistemic"])
async def create_annotation(annotation_data: EpistemicAnnotationCreate):
    """Create a new epistemic annotation."""
    return service.create_annotation(annotation_data)


@app.put("/annotations/{annotation_id}", response_model=EpistemicAnnotation, tags=["Epistemic"])
async def update_annotation(
    annotation_id: str = Path(..., description="Annotation ID"),
    update_data: EpistemicAnnotationUpdate = ...,
):
    """Update an epistemic annotation."""
    return service.update_annotation(annotation_id, update_data)


@app.delete("/annotations/{annotation_id}", status_code=204, tags=["Epistemic"])
async def delete_annotation(
    annotation_id: str = Path(..., description="Annotation ID"),
):
    """Delete an epistemic annotation."""
    service.delete_annotation(annotation_id)
    return None


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Epistemic Service starting up...")
    logger.info(f"Environment: {settings.omnicore_env}")
    logger.info(f"Database path: {settings.database_path}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Epistemic Service shutting down...")
