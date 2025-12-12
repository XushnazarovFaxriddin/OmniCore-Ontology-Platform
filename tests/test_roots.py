"""
Tests for the Roots Service.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient


@pytest.fixture
def client(temp_db_path):
    """Create test client for Roots Service."""
    from core.roots.api import app
    return TestClient(app)


class TestRootsHealth:
    """Test health endpoint."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "roots-service"


class TestRootsCRUD:
    """Test CRUD operations."""

    def test_create_root(self, client):
        response = client.post("/roots", json={
            "name": "Test Entity",
            "root_type": "EXTANT",
            "description": "A test entity"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Entity"
        assert data["root_type"] == "EXTANT"
        assert "id" in data

    def test_list_roots(self, client):
        # Create a root first
        client.post("/roots", json={
            "name": "Test Entity",
            "root_type": "EXTANT"
        })

        response = client.get("/roots")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_root(self, client):
        # Create a root first
        create_response = client.post("/roots", json={
            "name": "Test Entity",
            "root_type": "ABSTRACT"
        })
        root_id = create_response.json()["id"]

        response = client.get(f"/roots/{root_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == root_id
        assert data["root_type"] == "ABSTRACT"

    def test_get_nonexistent_root(self, client):
        response = client.get("/roots/nonexistent-id")
        assert response.status_code == 404

    def test_update_root(self, client):
        # Create a root first
        create_response = client.post("/roots", json={
            "name": "Test Entity",
            "root_type": "MENTAL"
        })
        root_id = create_response.json()["id"]

        response = client.put(f"/roots/{root_id}", json={
            "name": "Updated Entity",
            "description": "Updated description"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Entity"
        assert data["description"] == "Updated description"

    def test_delete_root(self, client):
        # Create a root first
        create_response = client.post("/roots", json={
            "name": "Test Entity",
            "root_type": "FICTIVE"
        })
        root_id = create_response.json()["id"]

        response = client.delete(f"/roots/{root_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/roots/{root_id}")
        assert get_response.status_code == 404


class TestRootsSummary:
    """Test summary endpoint."""

    def test_get_summary(self, client):
        # Create some roots
        for root_type in ["EXTANT", "ABSTRACT", "MENTAL"]:
            client.post("/roots", json={
                "name": f"Test {root_type}",
                "root_type": root_type
            })

        response = client.get("/roots/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_count" in data
        assert "by_type" in data
        assert data["total_count"] >= 3


class TestRootsFiltering:
    """Test filtering by type."""

    def test_filter_by_type(self, client):
        # Create roots of different types
        client.post("/roots", json={"name": "Extant 1", "root_type": "EXTANT"})
        client.post("/roots", json={"name": "Abstract 1", "root_type": "ABSTRACT"})
        client.post("/roots", json={"name": "Extant 2", "root_type": "EXTANT"})

        response = client.get("/roots/by-type/EXTANT")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["root_type"] == "EXTANT"
