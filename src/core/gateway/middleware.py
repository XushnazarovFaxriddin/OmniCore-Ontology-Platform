"""
Middleware for authentication, rate limiting, and error handling.
"""

import time
from typing import Optional, Callable
from datetime import datetime

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from common.config import settings
from common.logging_config import get_logger
from common.auth import auth_service, TokenData
from common.exceptions import (
    AuthenticationError,
    RateLimitError,
    OmniCoreException,
    ServiceUnavailableError,
)

logger = get_logger(__name__)

# Try to import redis, but make it optional
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, rate limiting disabled")


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for JWT and API key verification.
    """

    # Paths that don't require authentication
    PUBLIC_PATHS = {
        "/health",
        "/api/health/overview",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/auth/token",
    }

    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request through authentication."""
        path = request.url.path

        # Skip auth for public paths
        if path in self.PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        # Check for API key
        api_key = request.headers.get(settings.api_key_header)
        if api_key:
            if auth_service.verify_api_key(api_key):
                request.state.auth_type = "api_key"
                return await call_next(request)

        # Check for JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                token_data = auth_service.verify_token(token)
                request.state.user = token_data
                request.state.auth_type = "jwt"
                return await call_next(request)
            except AuthenticationError:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid or expired token"},
                )

        # In development mode, allow unauthenticated requests
        if settings.omnicore_env == "development":
            request.state.auth_type = "none"
            return await call_next(request)

        return JSONResponse(
            status_code=401,
            content={"error": "Authentication required"},
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis.
    """

    def __init__(self, app, redis_url: Optional[str] = None):
        super().__init__(app)
        self.redis_url = redis_url or settings.redis_url
        self.limit = settings.rate_limit_requests
        self.window = settings.rate_limit_window
        self._redis: Optional[redis.Redis] = None
        self._disabled = False  # Disable after first failed attempt to avoid per-request hangs

    async def _get_redis(self):
        """Get or create Redis connection."""
        if not REDIS_AVAILABLE or self._disabled:
            return None
        if self._redis is None:
            try:
                # Use short timeouts so missing Redis doesn't block requests
                self._redis = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_timeout=0.5,
                    socket_connect_timeout=0.5,
                )
                await self._redis.ping()
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self._redis = None
                # In development, permanently disable after first failure to prevent request stalls
                if settings.omnicore_env == "development":
                    self._disabled = True
        return self._redis

    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request through rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health/overview"]:
            return await call_next(request)

        redis_client = await self._get_redis()

        if redis_client is None:
            # Redis not available, skip rate limiting
            return await call_next(request)

        # Get client identifier (IP address or API key)
        client_id = request.headers.get(settings.api_key_header) or request.client.host
        key = f"rate_limit:{client_id}"

        try:
            current = await redis_client.incr(key)
            if current == 1:
                await redis_client.expire(key, self.window)

            remaining = max(0, self.limit - current)

            if current > self.limit:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded"},
                    headers={
                        "X-RateLimit-Limit": str(self.limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(self.window),
                    },
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            return response

        except Exception as e:
            logger.warning(f"Rate limiting error: {e}")
            # On error, allow the request through
            return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """Log request and response information."""
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request failed: {request.method} {request.url.path} - {e}")
            raise

        # Calculate processing time
        process_time = (time.time() - start_time) * 1000

        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.2f}ms"
        )

        # Add timing header
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler middleware.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """Handle exceptions and return proper error responses."""
        try:
            return await call_next(request)
        except OmniCoreException as e:
            logger.warning(f"Handled OmniCoreException: {e.message}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.message,
                    "detail": e.detail if settings.omnicore_env == "development" else None,
                },
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Unhandled error: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "detail": str(e) if settings.omnicore_env == "development" else None,
                },
            )
