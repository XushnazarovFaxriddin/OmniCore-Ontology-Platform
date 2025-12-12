"""
FastAPI application for the Roots Service.
"""

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware

from common.config import settings
from common.database import get_db_path
from common.logging_config import setup_logging, get_logger
from common.exceptions import NotFoundError, ValidationError, OmniCoreException
from common.models import PaginatedResponse, HealthResponse, HealthStatus

from .models import Root, RootCreate, RootUpdate, RootType, RootSummary
from .service import RootsService

# Setup logging
setup_logging(service_name="roots-service", level=settings.omnicore_log_level)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="OmniCore Roots Service",
    description="Manages fundamental ontological root types (EXTANT, ABSTRACT, MENTAL, FICTIVE)",
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

service: RootsService | None = None
_service_db_path: str | None = None


def get_service() -> RootsService:
    """Return an initialized roots service."""
    global service, _service_db_path

    current_db_path = get_db_path("roots.db")
    needs_new_service = service is None or _service_db_path != current_db_path

    if needs_new_service:
        service = RootsService()
        _service_db_path = current_db_path
    else:
        if not service.store.db.table_exists("roots"):
            service.store._init_schema()

    return service


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
        service="roots-service",
        timestamp=datetime.utcnow(),
        version="1.0.0",
    )


# Root CRUD endpoints
@app.get("/roots", response_model=PaginatedResponse, tags=["Roots"])
async def list_roots(
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
    root_type: Optional[RootType] = Query(None, description="Filter by root type"),
):
    """List all roots with pagination."""
    return get_service().list_roots(offset=offset, limit=limit, root_type=root_type)


@app.get("/roots/summary", response_model=RootSummary, tags=["Roots"])
async def get_summary():
    """Get summary statistics for roots."""
    return get_service().get_summary()


@app.get("/roots/by-type/{root_type}", response_model=PaginatedResponse, tags=["Roots"])
async def get_roots_by_type(
    root_type: RootType = Path(..., description="Root type to filter by"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
):
    """Get roots filtered by type."""
    return get_service().get_roots_by_type(root_type=root_type, offset=offset, limit=limit)


@app.get("/roots/{root_id}", response_model=Root, tags=["Roots"])
async def get_root(
    root_id: str = Path(..., description="Root ID"),
):
    """Get a root by ID."""
    return get_service().get_root(root_id)


@app.post("/roots", response_model=Root, status_code=201, tags=["Roots"])
async def create_root(root_data: RootCreate):
    """Create a new root."""
    return get_service().create_root(root_data)


@app.put("/roots/{root_id}", response_model=Root, tags=["Roots"])
async def update_root(
    root_id: str = Path(..., description="Root ID"),
    update_data: RootUpdate = ...,
):
    """Update a root."""
    return get_service().update_root(root_id, update_data)


@app.delete("/roots/{root_id}", status_code=204, tags=["Roots"])
async def delete_root(
    root_id: str = Path(..., description="Root ID"),
):
    """Delete a root."""
    get_service().delete_root(root_id)
    return None


# Startup event
@app.on_event("startup")
async def startup_event():
    global service, _service_db_path
    service = RootsService()
    _service_db_path = get_db_path("roots.db")
    logger.info("Roots Service starting up...")
    logger.info(f"Environment: {settings.omnicore_env}")
    logger.info(f"Database path: {settings.database_path}")


@app.on_event("shutdown")
async def shutdown_event():
    global service, _service_db_path
    service = None
    _service_db_path = None
    logger.info("Roots Service shutting down...")
