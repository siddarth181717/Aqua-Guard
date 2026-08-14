"""
Unit tests for Water Bodies endpoints
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_list_water_bodies():
    """Test GET /api/v1/water-bodies returns paginated list."""
    response = client.get("/api/v1/water-bodies?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert len(data["data"]["items"]) >= 1


def test_get_water_body_by_id():
    """Test GET /api/v1/water-bodies/{id} returns details."""
    response = client.get("/api/v1/water-bodies/WB_HYD_001")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["water_body_id"] == "WB_HYD_001"
    assert data["data"]["name"] == "Hussain Sagar Lake"


def test_get_water_body_geometry():
    """Test GET /api/v1/water-bodies/{id}/geometry returns GeoJSON Feature."""
    response = client.get("/api/v1/water-bodies/WB_HYD_001/geometry")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["type"] == "Feature"
    assert "geometry" in data["data"]


def test_invalid_water_body_not_found():
    """Test GET /api/v1/water-bodies/NON_EXISTENT returns 404."""
    response = client.get("/api/v1/water-bodies/NON_EXISTENT_WB_999")
    assert response.status_code == 404
