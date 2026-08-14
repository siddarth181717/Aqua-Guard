"""
Unit tests for /api/v1/health endpoint
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Test GET /api/v1/health returns 200 OK and valid status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "ok"
    assert "database" in json_data["data"]
    assert "ml_model" in json_data["data"]
