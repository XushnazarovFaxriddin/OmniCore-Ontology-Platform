"""
Tests for the Causality Service.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient


@pytest.fixture
def client(temp_db_path):
    """Create test client for Causality Service."""
    from core.causality.api import app
    return TestClient(app)


class TestCausalityHealth:
    """Test health endpoint."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "causality-service"


class TestCausalityCRUD:
    """Test CRUD operations."""

    def test_create_link(self, client):
        response = client.post("/causality-links", json={
            "source_entity_id": "entity-1",
            "target_entity_id": "entity-2",
            "causality_type": "EFFICIENT",
            "confidence": 0.9
        })
        assert response.status_code == 201
        data = response.json()
        assert data["source_entity_id"] == "entity-1"
        assert data["target_entity_id"] == "entity-2"
        assert data["causality_type"] == "EFFICIENT"
        assert data["confidence"] == 0.9

    def test_list_links(self, client):
        # Create a link first
        client.post("/causality-links", json={
            "source_entity_id": "entity-1",
            "target_entity_id": "entity-2",
            "causality_type": "FINAL"
        })

        response = client.get("/causality-links")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_link(self, client):
        # Create a link first
        create_response = client.post("/causality-links", json={
            "source_entity_id": "entity-1",
            "target_entity_id": "entity-2",
            "causality_type": "MATERIAL"
        })
        link_id = create_response.json()["id"]

        response = client.get(f"/causality-links/{link_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == link_id

    def test_update_link(self, client):
        # Create a link first
        create_response = client.post("/causality-links", json={
            "source_entity_id": "entity-1",
            "target_entity_id": "entity-2",
            "causality_type": "FORMAL",
            "confidence": 0.5
        })
        link_id = create_response.json()["id"]

        response = client.put(f"/causality-links/{link_id}", json={
            "confidence": 0.95,
            "description": "Updated"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["confidence"] == 0.95
        assert data["description"] == "Updated"

    def test_delete_link(self, client):
        # Create a link first
        create_response = client.post("/causality-links", json={
            "source_entity_id": "entity-1",
            "target_entity_id": "entity-2",
            "causality_type": "EMERGENT"
        })
        link_id = create_response.json()["id"]

        response = client.delete(f"/causality-links/{link_id}")
        assert response.status_code == 204


class TestCausalitySummary:
    """Test summary endpoint."""

    def test_get_summary(self, client):
        # Create some links
        for ctype in ["EFFICIENT", "FINAL", "MATERIAL"]:
            client.post("/causality-links", json={
                "source_entity_id": f"source-{ctype}",
                "target_entity_id": f"target-{ctype}",
                "causality_type": ctype
            })

        response = client.get("/causality-summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_count" in data
        assert "by_type" in data
        assert "avg_confidence" in data


class TestCausalityFiltering:
    """Test filtering endpoints."""

    def test_filter_by_type(self, client):
        # Create links of different types
        client.post("/causality-links", json={
            "source_entity_id": "s1",
            "target_entity_id": "t1",
            "causality_type": "EFFICIENT"
        })
        client.post("/causality-links", json={
            "source_entity_id": "s2",
            "target_entity_id": "t2",
            "causality_type": "FINAL"
        })

        response = client.get("/causality-links/by-type/EFFICIENT")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["causality_type"] == "EFFICIENT"

    def test_filter_by_entity(self, client):
        entity_id = "test-entity-123"
        # Create links involving the entity
        client.post("/causality-links", json={
            "source_entity_id": entity_id,
            "target_entity_id": "other-1",
            "causality_type": "EFFICIENT"
        })
        client.post("/causality-links", json={
            "source_entity_id": "other-2",
            "target_entity_id": entity_id,
            "causality_type": "FINAL"
        })

        response = client.get(f"/causality-links/by-entity/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
