"""
Tests for the MMO Service.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient


@pytest.fixture
def client(temp_db_path):
    """Create test client for MMO Service."""
    from core.mmo.api import app
    return TestClient(app)


class TestMMOHealth:
    """Test health endpoint."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mmo-service"


class TestMMOClasses:
    """Test class operations."""

    def test_create_class(self, client):
        response = client.post("/classes", json={
            "name": "Entity",
            "description": "Base entity class"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Entity"
        assert "id" in data

    def test_list_classes(self, client):
        # Create a class first
        client.post("/classes", json={"name": "TestClass"})

        response = client.get("/classes")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_class(self, client):
        # Create a class first
        create_response = client.post("/classes", json={
            "name": "TestClass2",
            "description": "Test description"
        })
        class_id = create_response.json()["id"]

        response = client.get(f"/classes/{class_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == class_id
        assert data["name"] == "TestClass2"

    def test_update_class(self, client):
        # Create a class first
        create_response = client.post("/classes", json={"name": "OriginalName"})
        class_id = create_response.json()["id"]

        response = client.put(f"/classes/{class_id}", json={
            "name": "UpdatedName",
            "description": "Updated description"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "UpdatedName"

    def test_delete_class(self, client):
        # Create a class first
        create_response = client.post("/classes", json={"name": "ToDelete"})
        class_id = create_response.json()["id"]

        response = client.delete(f"/classes/{class_id}")
        assert response.status_code == 204

    def test_create_class_with_parent(self, client):
        # Create parent class
        parent_response = client.post("/classes", json={"name": "Parent"})
        parent_id = parent_response.json()["id"]

        # Create child class
        response = client.post("/classes", json={
            "name": "Child",
            "parent_class_id": parent_id
        })
        assert response.status_code == 201
        data = response.json()
        assert data["parent_class_id"] == parent_id


class TestMMOSlots:
    """Test slot operations."""

    def test_create_slot(self, client):
        # Create a class first
        class_response = client.post("/classes", json={"name": "SlotTestClass"})
        class_id = class_response.json()["id"]

        response = client.post("/slots", json={
            "name": "testProperty",
            "domain_class_id": class_id,
            "range_type": "string",
            "cardinality": "0..*"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "testProperty"
        assert data["domain_class_id"] == class_id

    def test_list_slots(self, client):
        # Create class and slot
        class_response = client.post("/classes", json={"name": "SlotListClass"})
        class_id = class_response.json()["id"]
        client.post("/slots", json={
            "name": "prop1",
            "domain_class_id": class_id,
            "range_type": "int"
        })

        response = client.get("/slots")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_delete_slot(self, client):
        # Create class and slot
        class_response = client.post("/classes", json={"name": "SlotDeleteClass"})
        class_id = class_response.json()["id"]
        slot_response = client.post("/slots", json={
            "name": "toDelete",
            "domain_class_id": class_id,
            "range_type": "string"
        })
        slot_id = slot_response.json()["id"]

        response = client.delete(f"/slots/{slot_id}")
        assert response.status_code == 204


class TestMMOMetrics:
    """Test metrics operations."""

    def test_get_metrics(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "completeness" in data
        assert "coverage" in data
        assert "coherence" in data
        assert "utility" in data
        assert "inclusivity" in data
        assert "mmo_score" in data

    def test_recalculate_metrics(self, client):
        # Create some classes and slots
        class_response = client.post("/classes", json={"name": "MetricsClass"})
        class_id = class_response.json()["id"]
        client.post("/slots", json={
            "name": "prop",
            "domain_class_id": class_id,
            "range_type": "string"
        })

        response = client.post("/metrics/recalculate")
        assert response.status_code == 200
        data = response.json()
        assert "mmo_score" in data


class TestMMOSchema:
    """Test schema endpoint."""

    def test_get_schema(self, client):
        # Create some data
        client.post("/classes", json={"name": "SchemaClass"})

        response = client.get("/schema")
        assert response.status_code == 200
        data = response.json()
        assert "classes" in data
        assert "slots" in data
        assert "metrics" in data
