"""
Pytest configuration and shared fixtures.
"""

import os
import sys
import tempfile
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set test environment
os.environ['OMNICORE_ENV'] = 'test'
os.environ['OMNICORE_LOG_LEVEL'] = 'WARNING'


@pytest.fixture
def temp_db_path():
    """Create a temporary directory for test databases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['DATABASE_PATH'] = tmpdir
        yield tmpdir


@pytest.fixture
def test_client():
    """Create a test client factory."""
    from fastapi.testclient import TestClient

    def _create_client(app):
        return TestClient(app)

    return _create_client
