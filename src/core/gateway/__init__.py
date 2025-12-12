"""
OmniCore API Gateway (Group F)

Provides:
- Unified API entry point for all services
- JWT and API key authentication
- Rate limiting via Redis
- Request/Response logging
- CORS handling
- Error normalization
"""

from .router import router
from .proxy import ServiceProxy
from .middleware import AuthMiddleware, RateLimitMiddleware

__all__ = ["router", "ServiceProxy", "AuthMiddleware", "RateLimitMiddleware"]
