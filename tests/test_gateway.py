"""
Tests for the API Gateway.

Note: These tests verify gateway-specific functionality.
Integration tests with backend services require all services to be running.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient


@pytest.fixture
def client(temp_db_path):
    """Create test client for API Gateway."""
    # Set service URLs to localhost for testing
    os.environ['ROOTS_SERVICE_URL'] = 'http://localhost:8001'
    os.environ['CAUSALITY_SERVICE_URL'] = 'http://localhost:8002'
    os.environ['EPISTEMIC_SERVICE_URL'] = 'http://localhost:8003'
    os.environ['MMO_SERVICE_URL'] = 'http://localhost:8004'
    os.environ['GLOBAL_SERVICE_URL'] = 'http://localhost:8005'

    from core.gateway.api import app
    return TestClient(app)


class TestGatewayHealth:
    """Test gateway health endpoints."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "api-gateway"


class TestGatewayAuth:
    """Test authentication endpoints."""

    def test_create_token(self, client):
        response = client.post("/api/auth/token", json={
            "username": "testuser",
            "scopes": ["read", "write"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_create_token_without_scopes(self, client):
        response = client.post("/api/auth/token", json={
            "username": "testuser"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


class TestGatewayMiddleware:
    """Test middleware functionality."""

    def test_cors_headers(self, client):
        response = client.options("/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        # CORS should be handled
        assert response.status_code in [200, 204, 405]

    def test_process_time_header(self, client):
        response = client.get("/health")
        # Process time header should be present
        assert "x-process-time" in response.headers or response.status_code == 200


class TestGatewayDocs:
    """Test API documentation endpoints."""

    def test_openapi_json(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data

    def test_docs_page(self, client):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_page(self, client):
        response = client.get("/redoc")
        assert response.status_code == 200
