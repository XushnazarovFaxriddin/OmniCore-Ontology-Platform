"""
Service proxy for forwarding requests to backend services.
"""

from typing import Optional, Any
from datetime import datetime
from urllib.parse import urlparse

import httpx

from common.config import settings
from common.logging_config import get_logger
from common.exceptions import ServiceUnavailableError
from common.models import ServiceHealthDetail, HealthStatus

logger = get_logger(__name__)


class ServiceProxy:
    """
    Proxy for forwarding requests to backend services.
    """

    def __init__(self):
        """Initialize the service proxy with HTTP clients."""
        def _localize(url: str, fallback_port: int) -> str:
            """If running locally, rewrite container hostnames to localhost."""
            parsed = urlparse(url)
            host = parsed.hostname or ""
            if settings.omnicore_env.lower() == "development" and host not in {"localhost", "127.0.0.1", "0.0.0.0"}:
                return f"http://localhost:{fallback_port}"
            return url

        self.services = {
            "roots": _localize(settings.roots_service_url, settings.roots_service_port),
            "causality": _localize(settings.causality_service_url, settings.causality_service_port),
            "epistemic": _localize(settings.epistemic_service_url, settings.epistemic_service_port),
            "mmo": _localize(settings.mmo_service_url, settings.mmo_service_port),
            "global": _localize(settings.global_service_url, settings.global_service_port),
        }
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _get_service_url(self, service: str) -> str:
        """Get the base URL for a service."""
        if service not in self.services:
            raise ValueError(f"Unknown service: {service}")
        return self.services[service]

    async def forward_request(
        self,
        service: str,
        method: str,
        path: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        body: Optional[Any] = None,
    ) -> httpx.Response:
        """
        Forward a request to a backend service.

        Args:
            service: Target service name
            method: HTTP method
            path: Request path
            headers: Request headers
            params: Query parameters
            body: Request body

        Returns:
            Response from the backend service
        """
        base_url = self._get_service_url(service)
        url = f"{base_url}{path}"

        client = await self._get_client()

        # Filter headers (remove hop-by-hop headers)
        forward_headers = {}
        if headers:
            skip_headers = {
                "host", "connection", "keep-alive", "transfer-encoding",
                "te", "trailer", "upgrade", "proxy-authorization",
                "proxy-authenticate", "content-length",
            }
            forward_headers = {
                k: v for k, v in headers.items()
                if k.lower() not in skip_headers
            }

        try:
            logger.debug(f"Forwarding {method} {url}")
            response = await client.request(
                method=method,
                url=url,
                headers=forward_headers,
                params=params,
                json=body if body and method in ["POST", "PUT", "PATCH"] else None,
            )
            return response
        except httpx.ConnectError as e:
            logger.error(f"Connection error to {service}: {e}")
            raise ServiceUnavailableError(service, str(e))
        except httpx.TimeoutException as e:
            logger.error(f"Timeout connecting to {service}: {e}")
            raise ServiceUnavailableError(service, f"Timeout: {e}")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error talking to {service}: {e}")
            raise ServiceUnavailableError(service, str(e))

    async def health_check(self, service: str) -> ServiceHealthDetail:
        """
        Perform a health check on a specific service.

        Args:
            service: Service name

        Returns:
            ServiceHealthDetail with health status
        """
        start_time = datetime.utcnow()
        service_names = {
            "roots": "Roots Service",
            "causality": "Causality Service",
            "epistemic": "Epistemic Service",
            "mmo": "MMO Service",
            "global": "Global Ontology Service",
        }

        try:
            response = await self.forward_request(
                service=service,
                method="GET",
                path="/health",
            )
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                return ServiceHealthDetail(
                    name=service_names.get(service, service),
                    status=HealthStatus.UP,
                    latency_ms=latency,
                    last_check=datetime.utcnow(),
                    error=None,
                )
            else:
                return ServiceHealthDetail(
                    name=service_names.get(service, service),
                    status=HealthStatus.DOWN,
                    latency_ms=latency,
                    last_check=datetime.utcnow(),
                    error=f"Status code: {response.status_code}",
                )
        except Exception as e:
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            return ServiceHealthDetail(
                name=service_names.get(service, service),
                status=HealthStatus.DOWN,
                latency_ms=latency,
                last_check=datetime.utcnow(),
                error=str(e),
            )

    async def health_check_all(self) -> dict[str, ServiceHealthDetail]:
        """
        Perform health checks on all services.

        Returns:
            Dictionary of service health details
        """
        health_results = {}
        for service in self.services:
            health_results[service] = await self.health_check(service)
        return health_results
