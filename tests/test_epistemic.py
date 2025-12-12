"""
Tests for the Epistemic Service.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient


@pytest.fixture
def client(temp_db_path):
    """Create test client for Epistemic Service."""
    from core.epistemic.api import app
    return TestClient(app)


class TestEpistemicHealth:
    """Test health endpoint."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "epistemic-service"


class TestEpistemicCRUD:
    """Test CRUD operations."""

    def test_create_annotation(self, client):
        response = client.post("/annotations", json={
            "entity_id": "entity-1",
            "certainty": 0.85,
            "basis": "empirical",
            "source": "DOI:10.1234/test"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["entity_id"] == "entity-1"
        assert data["certainty"] == 0.85
        assert data["basis"] == "empirical"

    def test_list_annotations(self, client):
        # Create an annotation first
        client.post("/annotations", json={
            "entity_id": "entity-1",
            "certainty": 0.7,
            "basis": "consensus"
        })

        response = client.get("/annotations")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_annotation(self, client):
        # Create an annotation first
        create_response = client.post("/annotations", json={
            "entity_id": "entity-1",
            "certainty": 0.9,
            "basis": "axiomatic"
        })
        annotation_id = create_response.json()["id"]

        response = client.get(f"/annotations/{annotation_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == annotation_id
        assert data["basis"] == "axiomatic"

    def test_update_annotation(self, client):
        # Create an annotation first
        create_response = client.post("/annotations", json={
            "entity_id": "entity-1",
            "certainty": 0.5,
            "basis": "speculative"
        })
        annotation_id = create_response.json()["id"]

        response = client.put(f"/annotations/{annotation_id}", json={
            "certainty": 0.75,
            "note": "Updated after review"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["certainty"] == 0.75
        assert data["note"] == "Updated after review"

    def test_delete_annotation(self, client):
        # Create an annotation first
        create_response = client.post("/annotations", json={
            "entity_id": "entity-1",
            "certainty": 0.6,
            "basis": "empirical"
        })
        annotation_id = create_response.json()["id"]

        response = client.delete(f"/annotations/{annotation_id}")
        assert response.status_code == 204


class TestEpistemicSummary:
    """Test summary endpoint."""

    def test_get_summary(self, client):
        # Create some annotations
        for basis in ["axiomatic", "empirical", "consensus"]:
            client.post("/annotations", json={
                "entity_id": f"entity-{basis}",
                "certainty": 0.8,
                "basis": basis
            })

        response = client.get("/annotations/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_count" in data
        assert "by_basis" in data
        assert "avg_certainty" in data
        assert "certainty_distribution" in data


class TestEpistemicFiltering:
    """Test filtering endpoints."""

    def test_filter_by_basis(self, client):
        # Create annotations with different bases
        client.post("/annotations", json={
            "entity_id": "e1",
            "certainty": 0.9,
            "basis": "axiomatic"
        })
        client.post("/annotations", json={
            "entity_id": "e2",
            "certainty": 0.8,
            "basis": "empirical"
        })

        response = client.get("/annotations/by-basis/axiomatic")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["basis"] == "axiomatic"

    def test_filter_by_entity(self, client):
        entity_id = "test-entity-456"
        # Create annotations for the entity
        client.post("/annotations", json={
            "entity_id": entity_id,
            "certainty": 0.8,
            "basis": "empirical"
        })
        client.post("/annotations", json={
            "entity_id": entity_id,
            "certainty": 0.9,
            "basis": "consensus"
        })

        response = client.get(f"/entities/{entity_id}/annotations")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        for item in data["items"]:
            assert item["entity_id"] == entity_id
