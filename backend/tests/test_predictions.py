"""
Unit tests for Predictions & Priority Ranking endpoints
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_get_water_body_prediction():
    """Test GET /api/v1/water-bodies/{id}/prediction returns AI/ML prediction."""
    response = client.get("/api/v1/water-bodies/WB_HYD_001/prediction")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["water_body_id"] == "WB_HYD_001"
    assert "priority" in data["data"]
    assert "health_class" in data["data"]


def test_get_priority_rankings():
    """Test GET /api/v1/priorities returns ordered priority list."""
    response = client.get("/api/v1/priorities")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    if len(data["data"]) > 0:
        assert "rank" in data["data"][0]
        assert "priority" in data["data"][0]
