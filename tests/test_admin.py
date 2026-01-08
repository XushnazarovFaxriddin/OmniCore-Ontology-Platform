
import pytest
import shutil
import os
import sys
# Explicitly add src to path for test collection
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
print(f"DEBUG: sys.path in test_admin: {sys.path}")
from fastapi.testclient import TestClient
from common.config import settings
from core.gateway.api import app

client = TestClient(app)

# Use a separate test DB path to avoid wiping dev data
TEST_DB_DIR = "test_data_admin"

@pytest.fixture(scope="module", autouse=True)
def setup_test_env():
    original_db_path = settings.database_path
    
    # Create test dir
    os.makedirs(TEST_DB_DIR, exist_ok=True)
    settings.database_path = TEST_DB_DIR
    
    yield
    
    # Cleanup
    settings.database_path = original_db_path
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR)

def test_seed_database():
    """Test the database seeding endpoint."""
    response = client.post("/api/admin/database/seed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "classes" in data["details"]
    assert data["details"]["classes"] >= 1

def test_reset_database():
    """Test the database reset endpoint."""
    # First ensure some data exists (via seed)
    client.post("/api/admin/database/seed")
    
    # Verify file exists
    db_file = os.path.join(TEST_DB_DIR, "mmo.db")
    assert os.path.exists(db_file)
    
    # Reset
    response = client.post("/api/admin/database/reset")
    assert response.status_code == 200
    
    # Verify file is gone
    assert not os.path.exists(db_file)
