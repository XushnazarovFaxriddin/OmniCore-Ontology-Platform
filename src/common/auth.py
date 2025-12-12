"""
JWT authentication utilities for OmniCore services.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from .logging_config import get_logger
from .config import settings
from .exceptions import AuthenticationError

logger = get_logger(__name__)


class TokenData(BaseModel):
    """JWT token payload data."""

    username: str
    scopes: list[str] = []
    exp: datetime


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthService:
    """
    Authentication service for JWT token management.
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
        expiration_hours: Optional[int] = None,
    ):
        """
        Initialize authentication service.

        Args:
            secret_key: JWT secret key
            algorithm: JWT algorithm
            expiration_hours: Token expiration in hours
        """
        self.secret_key = secret_key or settings.jwt_secret_key
        self.algorithm = algorithm or settings.jwt_algorithm
        self.expiration_hours = expiration_hours or settings.jwt_expiration_hours

    def create_access_token(
        self,
        username: str,
        scopes: list[str] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> TokenResponse:
        """
        Create a new JWT access token.

        Args:
            username: Username for the token
            scopes: List of permission scopes
            expires_delta: Custom expiration time

        Returns:
            TokenResponse with access token
        """
        if scopes is None:
            scopes = []

        if expires_delta is None:
            expires_delta = timedelta(hours=self.expiration_hours)

        expire = datetime.utcnow() + expires_delta

        to_encode = {
            "username": username,
            "scopes": scopes,
            "exp": expire,
        }

        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm,
        )

        return TokenResponse(
            access_token=encoded_jwt,
            token_type="bearer",
            expires_in=int(expires_delta.total_seconds()),
        )

    def verify_token(self, token: str) -> TokenData:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            TokenData with decoded payload

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return TokenData(
                username=payload["username"],
                scopes=payload.get("scopes", []),
                exp=datetime.fromtimestamp(payload["exp"]),
            )
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            raise AuthenticationError("Invalid or expired token")

    def verify_api_key(self, api_key: str) -> bool:
        """
        Verify an API key.

        Args:
            api_key: API key to verify

        Returns:
            True if valid, False otherwise
        """
        valid_keys = settings.get_valid_api_keys()
        if not valid_keys:
            # If no API keys are configured, accept any non-empty key in dev mode
            if settings.omnicore_env == "development":
                return bool(api_key)
            return False
        return api_key in valid_keys

    def has_scope(self, token_data: TokenData, required_scope: str) -> bool:
        """
        Check if token has a required scope.

        Args:
            token_data: Decoded token data
            required_scope: Required scope to check

        Returns:
            True if scope is present
        """
        return required_scope in token_data.scopes or "admin" in token_data.scopes


# Global auth service instance
auth_service = AuthService()
