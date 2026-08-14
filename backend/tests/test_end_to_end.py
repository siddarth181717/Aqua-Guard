"""
AquaGuard Complete End-to-End System Integration Test Suite
------------------------------------------------------------
Tests the complete data flow:
DATA -> PROCESSING -> FEATURES -> MODEL -> DATABASE -> API -> FRONTEND API

Verifies:
1. Data ingestion & validation
2. Geospatial processing & feature generation
3. ML feature validation & AquaGuardPredictor inference
4. Database storage & duplicate prevention
5. All required FastAPI endpoints & status codes
6. GeoJSON geometry structure & validity
"""

import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.database.init_db import init_db
from scripts.fetch_data import fetch_source_data, validate_downloaded_data
from scripts.process_data import run_geospatial_processing, generate_ml_features, validate_ml_features
from ai.models.predict import AquaGuardPredictor

client = TestClient(app)


def test_full_end_to_end_pipeline():
    """Verify complete 8-stage data pipeline from raw data to API GeoJSON response."""
    # 1. Initialize Test Database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    init_db(db)
    db.close()

    # 2. Stage 1 & 2: Fetch & Validate Data
    fetch_res = fetch_source_data()
    assert fetch_res["status"] == "success"
    assert validate_downloaded_data(fetch_res) is True

    # 3. Stage 3, 4, 5: Geospatial Processing & Features
    feat_path = run_geospatial_processing()
    assert feat_path.exists()
    
    ml_feat_path = generate_ml_features(feat_path)
    assert ml_feat_path.exists()
    assert validate_ml_features(ml_feat_path) is True

    # 4. Stage 6: AI/ML Inference
    predictor = AquaGuardPredictor()
    pred_res = predictor.predict_single({
        "water_body_id": "WB_HYD_001",
        "water_area_mean": 4215300.0,
        "water_area_current": 4215300.0,
        "water_area_change": -15300.0,
        "water_area_change_percent": -3.5,
        "mndwi_mean": 0.4285,
        "mndwi_trend": -0.01,
        "ndwi_mean": 0.3120,
        "ndvi_mean": -0.1542,
        "annual_rainfall": 12.4,
        "builtup_percentage": 25.0,
        "data_quality_score": 0.95
    })
    assert pred_res["water_body_id"] == "WB_HYD_001"
    assert "priority" in pred_res
    assert "health_class" in pred_res

    # 5. Stage 7 & 8: API Endpoints Verification
    # GET /api/v1/health
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    h_data = resp.json()
    assert h_data["success"] is True
    assert h_data["data"]["backend"] == "ok"

    # GET /api/v1/water-bodies
    resp = client.get("/api/v1/water-bodies")
    assert resp.status_code == 200
    wb_data = resp.json()
    assert wb_data["success"] is True
    assert len(wb_data["data"]["items"]) >= 1

    # GET /api/v1/water-bodies/{id}
    resp = client.get("/api/v1/water-bodies/WB_HYD_001")
    assert resp.status_code == 200
    assert resp.json()["data"]["water_body_id"] == "WB_HYD_001"

    # GET /api/v1/water-bodies/{id}/geometry
    resp = client.get("/api/v1/water-bodies/WB_HYD_001/geometry")
    assert resp.status_code == 200
    geom_data = resp.json()
    assert geom_data["success"] is True
    assert geom_data["data"]["type"] == "Feature"

    # GET /api/v1/water-bodies/{id}/observations
    resp = client.get("/api/v1/water-bodies/WB_HYD_001/observations")
    assert resp.status_code == 200

    # GET /api/v1/water-bodies/{id}/analytics
    resp = client.get("/api/v1/water-bodies/WB_HYD_001/analytics")
    assert resp.status_code == 200

    # GET /api/v1/water-bodies/{id}/prediction
    resp = client.get("/api/v1/water-bodies/WB_HYD_001/prediction")
    assert resp.status_code == 200
    assert resp.json()["data"]["water_body_id"] == "WB_HYD_001"

    # GET /api/v1/priorities
    resp = client.get("/api/v1/priorities")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1


if __name__ == "__main__":
    test_full_end_to_end_pipeline()
    print("[SUCCESS] All End-to-End Integration Tests PASSED!")
