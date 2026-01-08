
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from core.gateway.api import app

client = TestClient(app)

# Mock the SLM service to avoid actual AI calls
@pytest.fixture
def mock_strategic_ai():
    with patch("ai.strategic.api.StrategicMetaAI") as MockClass:
        mock_instance = MockClass.return_value
        
        # Mock immediate review response
        mock_instance.run_immediate_review = AsyncMock(return_value={
            "review_id": "test-review-id",
            "timestamp": "2023-01-01T00:00:00",
            "current_metrics": {
                "ontologies_integrated": 100,
                "mmo_prediction_r2": 0.8,
                "task_success_rate": 0.9,
                "human_interventions_last_quarter": 5,
                "unresolved_ethical_alerts": 0
            },
            "goals_met": {
                "ontology_coverage": False,
                "mmo_accuracy": False,
                "ai_task_success": False,
                "human_intervention": True,
                "ethical_flags": True
            },
            "gaps": ["coverage gap"],
            "plan": {
                "actions": ["import more ontologies"],
                "rationale": "need more data",
                "rollback_plan": "stop importing",
                "requires_human_approval": False,
                "affected_components": ["importer"]
            },
            "status": "completed"
        })
        
        # Mock get reviews
        mock_instance.get_reviews.return_value = []
        
        # Mock oversight
        mock_instance.get_oversight_status.return_value = {
            "pending_approvals": 0,
            "unresolved_alerts": 0
        }
        
        yield mock_instance

def test_get_strategic_oversight(mock_strategic_ai):
    """Test getting oversight status."""
    response = client.get("/api/strategic/oversight")
    assert response.status_code == 200
    data = response.json()
    assert "pending_approvals" in data
    assert data["pending_approvals"] == 0

def test_trigger_strategic_review(mock_strategic_ai):
    """Test triggering a strategic review."""
    response = client.post("/api/strategic/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert data["review_id"] == "test-review-id"
    assert data["status"] == "completed"

def test_get_strategic_reviews(mock_strategic_ai):
    """Test listing reviews."""
    response = client.get("/api/strategic/reviews")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
