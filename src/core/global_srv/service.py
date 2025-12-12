"""
Business logic for the Global Ontology Service.
"""

from datetime import datetime
from typing import Optional

from common.config import settings
from common.logging_config import get_logger
from common.http_client import HttpClient
from common.models import (
    GlobalStats,
    GlobalSample,
    GlobalSummary,
    SystemHealthResponse,
    ServiceHealthDetail,
    HealthStatus,
    Root,
    CausalityLink,
    EpistemicAnnotation,
    MMOClass,
)

logger = get_logger(__name__)


class GlobalService:
    """
    Aggregates data from all other services.
    """

    def __init__(self):
        """Initialize the global service with HTTP clients for each service."""
        self.roots_client = HttpClient(settings.roots_service_url)
        self.causality_client = HttpClient(settings.causality_service_url)
        self.epistemic_client = HttpClient(settings.epistemic_service_url)
        self.mmo_client = HttpClient(settings.mmo_service_url)

        self.services = {
            "roots": self.roots_client,
            "causality": self.causality_client,
            "epistemic": self.epistemic_client,
            "mmo": self.mmo_client,
        }

    async def close(self):
        """Close all HTTP clients."""
        for client in self.services.values():
            await client.close()

    async def get_global_stats(self) -> GlobalStats:
        """
        Get global statistics from all services.

        Returns:
            GlobalStats with aggregated statistics
        """
        stats = GlobalStats(
            total_roots=0,
            total_causality_links=0,
            total_epistemic_annotations=0,
            total_mmo_classes=0,
            total_mmo_slots=0,
            roots_by_type={},
            causality_by_type={},
            epistemic_by_basis={},
            avg_causality_confidence=0.0,
            avg_epistemic_certainty=0.0,
            last_updated=datetime.utcnow(),
        )

        # Get roots summary
        try:
            roots_summary = await self.roots_client.get("/roots/summary")
            stats.total_roots = roots_summary.get("total_count", 0)
            stats.roots_by_type = roots_summary.get("by_type", {})
        except Exception as e:
            logger.warning(f"Failed to get roots summary: {e}")

        # Get causality summary
        try:
            causality_summary = await self.causality_client.get("/causality-summary")
            stats.total_causality_links = causality_summary.get("total_count", 0)
            stats.causality_by_type = causality_summary.get("by_type", {})
            stats.avg_causality_confidence = causality_summary.get("avg_confidence", 0.0)
        except Exception as e:
            logger.warning(f"Failed to get causality summary: {e}")

        # Get epistemic summary
        try:
            epistemic_summary = await self.epistemic_client.get("/annotations/summary")
            stats.total_epistemic_annotations = epistemic_summary.get("total_count", 0)
            stats.epistemic_by_basis = epistemic_summary.get("by_basis", {})
            stats.avg_epistemic_certainty = epistemic_summary.get("avg_certainty", 0.0)
        except Exception as e:
            logger.warning(f"Failed to get epistemic summary: {e}")

        # Get MMO schema counts
        try:
            mmo_schema = await self.mmo_client.get("/schema")
            stats.total_mmo_classes = len(mmo_schema.get("classes", []))
            stats.total_mmo_slots = len(mmo_schema.get("slots", []))
        except Exception as e:
            logger.warning(f"Failed to get MMO schema: {e}")

        return stats

    async def get_global_sample(self, sample_size: int = 5) -> GlobalSample:
        """
        Get sample data from all services.

        Args:
            sample_size: Number of samples to get from each service

        Returns:
            GlobalSample with sample data
        """
        sample_roots = []
        sample_causality = []
        sample_annotations = []
        sample_mmo_classes = []

        # Get sample roots
        try:
            roots_response = await self.roots_client.get("/roots", params={"limit": sample_size})
            sample_roots = [Root(**r) for r in roots_response.get("items", [])]
        except Exception as e:
            logger.warning(f"Failed to get sample roots: {e}")

        # Get sample causality links
        try:
            causality_response = await self.causality_client.get("/causality-links", params={"limit": sample_size})
            sample_causality = [CausalityLink(**c) for c in causality_response.get("items", [])]
        except Exception as e:
            logger.warning(f"Failed to get sample causality links: {e}")

        # Get sample epistemic annotations
        try:
            epistemic_response = await self.epistemic_client.get("/annotations", params={"limit": sample_size})
            sample_annotations = [EpistemicAnnotation(**a) for a in epistemic_response.get("items", [])]
        except Exception as e:
            logger.warning(f"Failed to get sample annotations: {e}")

        # Get sample MMO classes
        try:
            mmo_response = await self.mmo_client.get("/classes", params={"limit": sample_size})
            sample_mmo_classes = [MMOClass(**c) for c in mmo_response.get("items", [])]
        except Exception as e:
            logger.warning(f"Failed to get sample MMO classes: {e}")

        return GlobalSample(
            sample_roots=sample_roots,
            sample_causality_links=sample_causality,
            sample_annotations=sample_annotations,
            sample_mmo_classes=sample_mmo_classes,
        )

    async def get_system_health(self) -> SystemHealthResponse:
        """
        Get health status of all services.

        Returns:
            SystemHealthResponse with health status of each service
        """
        services_health = {}
        overall_status = HealthStatus.HEALTHY

        service_names = {
            "roots": "Roots Service",
            "causality": "Causality Service",
            "epistemic": "Epistemic Service",
            "mmo": "MMO Service",
        }

        for service_key, client in self.services.items():
            is_healthy, latency_ms, error = await client.health_check()

            status = HealthStatus.UP if is_healthy else HealthStatus.DOWN

            if not is_healthy:
                overall_status = HealthStatus.DEGRADED

            services_health[service_key] = ServiceHealthDetail(
                name=service_names[service_key],
                status=status,
                latency_ms=latency_ms,
                last_check=datetime.utcnow(),
                error=error,
            )

        # Check if all services are down
        all_down = all(s.status == HealthStatus.DOWN for s in services_health.values())
        if all_down:
            overall_status = HealthStatus.UNHEALTHY

        return SystemHealthResponse(
            status=overall_status,
            services=services_health,
            timestamp=datetime.utcnow(),
        )

    async def get_global_summary(self) -> GlobalSummary:
        """
        Get comprehensive global summary including stats, samples, and health.

        Returns:
            GlobalSummary with all aggregated data
        """
        stats = await self.get_global_stats()
        sample = await self.get_global_sample()
        health = await self.get_system_health()

        return GlobalSummary(
            stats=stats,
            sample=sample,
            health=health,
        )
