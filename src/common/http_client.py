"""
Async HTTP client wrapper for inter-service communication.
"""

import asyncio
from typing import Optional, Any
from datetime import datetime

import httpx

from .logging_config import get_logger
from .exceptions import ServiceUnavailableError

logger = get_logger(__name__)


class HttpClient:
    """
    Async HTTP client for inter-service communication.

    Features:
    - Connection pooling
    - Automatic retries
    - Timeout handling
    - Structured error handling
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize HTTP client.

        Args:
            base_url: Base URL for all requests
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> httpx.Response:
        """
        Make an HTTP request with retries.

        Args:
            method: HTTP method
            path: Request path
            **kwargs: Additional request arguments

        Returns:
            Response object

        Raises:
            ServiceUnavailableError: If service is unavailable after retries
        """
        client = await self._get_client()
        last_error = None

        for attempt in range(self.retries):
            try:
                response = await client.request(method, path, **kwargs)
                return response
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_error = e
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.retries}): {e}"
                )
                if attempt < self.retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        service_name = self.base_url
        raise ServiceUnavailableError(
            service=service_name,
            detail=str(last_error),
        )

    async def get(
        self,
        path: str,
        params: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        """
        Make a GET request.

        Args:
            path: Request path
            params: Query parameters
            **kwargs: Additional request arguments

        Returns:
            Response JSON as dictionary
        """
        response = await self._request("GET", path, params=params, **kwargs)
        response.raise_for_status()
        return response.json()

    async def post(
        self,
        path: str,
        data: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        """
        Make a POST request.

        Args:
            path: Request path
            data: Request body
            **kwargs: Additional request arguments

        Returns:
            Response JSON as dictionary
        """
        response = await self._request("POST", path, json=data, **kwargs)
        response.raise_for_status()
        return response.json()

    async def put(
        self,
        path: str,
        data: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        """
        Make a PUT request.

        Args:
            path: Request path
            data: Request body
            **kwargs: Additional request arguments

        Returns:
            Response JSON as dictionary
        """
        response = await self._request("PUT", path, json=data, **kwargs)
        response.raise_for_status()
        return response.json()

    async def delete(
        self,
        path: str,
        **kwargs,
    ) -> Optional[dict]:
        """
        Make a DELETE request.

        Args:
            path: Request path
            **kwargs: Additional request arguments

        Returns:
            Response JSON as dictionary or None
        """
        response = await self._request("DELETE", path, **kwargs)
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    async def health_check(self, timeout: float = 5.0) -> tuple[bool, float, Optional[str]]:
        """
        Perform a health check on the service.

        Args:
            timeout: Health check timeout in seconds

        Returns:
            Tuple of (is_healthy, latency_ms, error_message)
        """
        start_time = datetime.utcnow()
        try:
            client = await self._get_client()
            response = await client.get("/health", timeout=timeout)
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                return True, latency, None
            else:
                return False, latency, f"Status code: {response.status_code}"
        except Exception as e:
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            return False, latency, str(e)
