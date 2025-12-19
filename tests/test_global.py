"""
Tests for the Global Ontology Service.

Note: These tests verify the service structure.
Integration tests with backend services require all services to be running.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient


@pytest.fixture
def client(temp_db_path):
    """Create test client for Global Service."""
    # Set service URLs to localhost for testing
    os.environ['ROOTS_SERVICE_URL'] = 'http://localhost:18001'
    os.environ['CAUSALITY_SERVICE_URL'] = 'http://localhost:18002'
    os.environ['EPISTEMIC_SERVICE_URL'] = 'http://localhost:18003'
    os.environ['MMO_SERVICE_URL'] = 'http://localhost:18004'

    from core.global_srv.api import app
    return TestClient(app)


class TestGlobalHealth:
    """Test health endpoint."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "global-ontology-service"


class TestGlobalModels:
    """Test that models are properly defined."""

    def test_global_stats_model(self):
        from common.models import GlobalStats

        stats = GlobalStats(
            total_roots=10,
            total_causality_links=20,
            total_epistemic_annotations=15,
            total_mmo_classes=5,
            total_mmo_slots=12,
            total_ontologies_imported=3,
            roots_by_type={"EXTANT": 5, "ABSTRACT": 3, "MENTAL": 1, "FICTIVE": 1},
            causality_by_type={"EFFICIENT": 10, "FINAL": 5, "MATERIAL": 3, "FORMAL": 1, "EMERGENT": 1},
            epistemic_by_basis={"axiomatic": 3, "empirical": 7, "consensus": 3, "speculative": 2},
            avg_causality_confidence=0.85,
            avg_epistemic_certainty=0.75,
            mo_version="mo:v1.0.0-test",
            mmo_score=0.9,
        )

        assert stats.total_roots == 10
        assert stats.avg_causality_confidence == 0.85

    def test_system_health_model(self):
        from common.models import SystemHealthResponse, ServiceHealthDetail, HealthStatus
        from datetime import datetime

        service_health = ServiceHealthDetail(
            name="Test Service",
            status=HealthStatus.UP,
            latency_ms=15.5,
            last_check=datetime.utcnow()
        )

        system_health = SystemHealthResponse(
            status=HealthStatus.HEALTHY,
            services={"test": service_health}
        )

        assert system_health.status == HealthStatus.HEALTHY
        assert "test" in system_health.services


class TestGlobalService:
    """Test GlobalService class."""

    def test_service_initialization(self, temp_db_path):
        from core.global_srv.service import GlobalService

        service = GlobalService()
        assert service.roots_client is not None
        assert service.causality_client is not None
        assert service.epistemic_client is not None
        assert service.mmo_client is not None
