"""
FastAPI application for the API Gateway.
"""

from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from common.config import settings
from common.logging_config import setup_logging, get_logger
from common.auth import auth_service, TokenResponse
from common.models import HealthResponse, HealthStatus, SystemHealthResponse

from .proxy import ServiceProxy
from .router import router
from .admin import router as admin_router
from ai.strategic.api import router as strategic_router
from .middleware import (
    AuthMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    ErrorHandlerMiddleware,
)

# Setup logging
setup_logging(service_name="api-gateway", level=settings.omnicore_log_level)
logger = get_logger(__name__)

# Service proxy instance
proxy: ServiceProxy = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global proxy
    logger.info("API Gateway starting up...")
    logger.info(f"Environment: {settings.omnicore_env}")
    proxy = ServiceProxy()
    app.state.proxy = proxy
    yield
    logger.info("API Gateway shutting down...")
    await proxy.close()


# Initialize FastAPI app
app = FastAPI(
    title="OmniCore API Gateway",
    description="Unified API entry point for OmniCore Ontology Platform",
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

# Add custom middleware (order matters - last added is first executed)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, redis_url=settings.redis_url)
app.add_middleware(AuthMiddleware)


# ==================== Auth Endpoints ====================

class TokenRequest(BaseModel):
    """Request model for token generation."""
    username: str
    scopes: list[str] = []


@app.post("/api/auth/token", response_model=TokenResponse, tags=["Auth"])
async def create_token(request: TokenRequest):
    """
    Generate a JWT access token.

    In production, this would validate credentials against a user database.
    For MVP, it generates tokens for any username.
    """
    token_response = auth_service.create_access_token(
        username=request.username,
        scopes=request.scopes,
    )
    logger.info(f"Generated token for user: {request.username}")
    return token_response


# ==================== Health Endpoints ====================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Gateway health check endpoint."""
    return HealthResponse(
        status=HealthStatus.HEALTHY,
        service="api-gateway",
        timestamp=datetime.utcnow(),
        version="1.0.0",
    )


@app.get("/api/health/overview", response_model=SystemHealthResponse, tags=["Health"])
async def health_overview():
    """
    Get health status of all backend services.

    This endpoint aggregates health checks from all services.
    """
    services_health = await app.state.proxy.health_check_all()

    # Determine overall status
    all_up = all(s.status == HealthStatus.UP for s in services_health.values())
    all_down = all(s.status == HealthStatus.DOWN for s in services_health.values())

    if all_up:
        overall_status = HealthStatus.HEALTHY
    elif all_down:
        overall_status = HealthStatus.UNHEALTHY
    else:
        overall_status = HealthStatus.DEGRADED

    return SystemHealthResponse(
        status=overall_status,
        services=services_health,
        timestamp=datetime.utcnow(),
    )


# Include API router with prefix
app.include_router(router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(strategic_router, prefix="/api")


# ==================== Error Handlers ====================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "path": request.url.path},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )
