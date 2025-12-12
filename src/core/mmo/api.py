"""
FastAPI application for the MMO Service.
"""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware

from common.config import settings
from common.database import get_db_path
from common.logging_config import setup_logging, get_logger
from common.exceptions import NotFoundError, OmniCoreException
from common.models import PaginatedResponse, HealthResponse, HealthStatus

from .models import MMOClass, MMOClassCreate, MMOClassUpdate, MMOSlot, MMOSlotCreate, MMOMetrics, MMOSchema
from .service import MMOService

# Setup logging
setup_logging(service_name="mmo-service", level=settings.omnicore_log_level)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="OmniCore MMO Service",
    description="Manages Meta-Meta-Ontology (classes, slots, metrics)",
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

service: MMOService | None = None
_service_db_path: str | None = None


def get_service() -> MMOService:
    """Return an initialized MMO service."""
    global service, _service_db_path

    current_db_path = get_db_path("mmo.db")
    needs_new_service = service is None or _service_db_path != current_db_path

    if needs_new_service:
        service = MMOService()
        _service_db_path = current_db_path
    else:
        if not service.store.db.table_exists("mmo_classes"):
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
        service="mmo-service",
        timestamp=datetime.utcnow(),
        version="1.0.0",
    )


# ==================== Class Endpoints ====================

@app.get("/classes", response_model=PaginatedResponse, tags=["Classes"])
async def list_classes(
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum items to return"),
):
    """List all MMO classes with pagination."""
    return get_service().list_classes(offset=offset, limit=limit)


@app.get("/classes/{class_id}", response_model=MMOClass, tags=["Classes"])
async def get_class(
    class_id: str = Path(..., description="Class ID"),
):
    """Get an MMO class by ID."""
    return get_service().get_class(class_id)


@app.post("/classes", response_model=MMOClass, status_code=201, tags=["Classes"])
async def create_class(class_data: MMOClassCreate):
    """Create a new MMO class."""
    return get_service().create_class(class_data)


@app.put("/classes/{class_id}", response_model=MMOClass, tags=["Classes"])
async def update_class(
    class_id: str = Path(..., description="Class ID"),
    update_data: MMOClassUpdate = ...,
):
    """Update an MMO class."""
    return get_service().update_class(class_id, update_data)


@app.delete("/classes/{class_id}", status_code=204, tags=["Classes"])
async def delete_class(
    class_id: str = Path(..., description="Class ID"),
):
    """Delete an MMO class."""
    get_service().delete_class(class_id)
    return None


# ==================== Slot Endpoints ====================

@app.get("/slots", response_model=PaginatedResponse, tags=["Slots"])
async def list_slots(
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum items to return"),
):
    """List all MMO slots with pagination."""
    return get_service().list_slots(offset=offset, limit=limit)


@app.get("/slots/{slot_id}", response_model=MMOSlot, tags=["Slots"])
async def get_slot(
    slot_id: str = Path(..., description="Slot ID"),
):
    """Get an MMO slot by ID."""
    return get_service().get_slot(slot_id)


@app.post("/slots", response_model=MMOSlot, status_code=201, tags=["Slots"])
async def create_slot(slot_data: MMOSlotCreate):
    """Create a new MMO slot."""
    return get_service().create_slot(slot_data)


@app.delete("/slots/{slot_id}", status_code=204, tags=["Slots"])
async def delete_slot(
    slot_id: str = Path(..., description="Slot ID"),
):
    """Delete an MMO slot."""
    get_service().delete_slot(slot_id)
    return None


# ==================== Metrics Endpoints ====================

@app.get("/metrics", response_model=MMOMetrics, tags=["Metrics"])
async def get_metrics():
    """Get current MMO metrics."""
    return get_service().get_metrics()


@app.post("/metrics/recalculate", response_model=MMOMetrics, tags=["Metrics"])
async def recalculate_metrics():
    """Trigger metrics recalculation."""
    return get_service().recalculate_metrics()


# ==================== Schema Endpoints ====================

@app.get("/schema", response_model=MMOSchema, tags=["Schema"])
async def get_schema():
    """Get full MMO schema including classes, slots, and metrics."""
    return get_service().get_schema()


# Startup event
@app.on_event("startup")
async def startup_event():
    global service, _service_db_path
    service = MMOService()
    _service_db_path = get_db_path("mmo.db")
    logger.info("MMO Service starting up...")
    logger.info(f"Environment: {settings.omnicore_env}")
    logger.info(f"Database path: {settings.database_path}")


@app.on_event("shutdown")
async def shutdown_event():
    global service, _service_db_path
    service = None
    _service_db_path = None
    logger.info("MMO Service shutting down...")
