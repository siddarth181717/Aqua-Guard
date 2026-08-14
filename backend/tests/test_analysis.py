"""
Unit tests for Observations and Analytics API endpoints
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_get_water_body_observations():
    """Test GET /api/v1/water-bodies/{id}/observations returns satellite observation records."""
    response = client.get("/api/v1/water-bodies/WB_HYD_001/observations")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


def test_get_water_body_analytics():
    """Test GET /api/v1/water-bodies/{id}/analytics returns water area and MNDWI summary."""
    response = client.get("/api/v1/water-bodies/WB_HYD_001/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "water_body_id" in data["data"]


def test_get_water_body_trend():
    """Test GET /api/v1/water-bodies/{id}/trend returns time-series chart data."""
    response = client.get("/api/v1/water-bodies/WB_HYD_001/trend")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "dates" in data["data"]
    assert "series" in data["data"]
