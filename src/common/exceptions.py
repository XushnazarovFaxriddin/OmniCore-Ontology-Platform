"""
Custom exceptions for OmniCore services.
"""

from typing import Optional, Any


class OmniCoreException(Exception):
    """Base exception for all OmniCore errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundError(OmniCoreException):
    """Resource not found error."""

    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with id '{identifier}' not found"
        super().__init__(message=message, status_code=404)


class ValidationError(OmniCoreException):
    """Data validation error."""

    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(message=message, status_code=422, detail=detail)


class AuthenticationError(OmniCoreException):
    """Authentication failed error."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, status_code=401)


class AuthorizationError(OmniCoreException):
    """Authorization failed error."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, status_code=403)


class ServiceUnavailableError(OmniCoreException):
    """External service unavailable error."""

    def __init__(self, service: str, detail: Optional[str] = None):
        message = f"Service '{service}' is unavailable"
        super().__init__(message=message, status_code=503, detail=detail)


class RateLimitError(OmniCoreException):
    """Rate limit exceeded error."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message=message, status_code=429)


class DatabaseError(OmniCoreException):
    """Database operation error."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message=message, status_code=500, detail=detail)
