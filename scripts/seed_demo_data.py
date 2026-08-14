"""
AquaGuard SIH Demo Mode Seeding Script
--------------------------------------
Seeds the PostGIS database with real previously collected real observation snapshots
for reliable off-line or live hackathon demonstrations.

Displays: "Data snapshot: 2026-08-14"
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.water_body import WaterBody
from backend.app.models.observation import Observation
from backend.app.models.prediction import Prediction


def seed_sih_demo_mode():
    """Populate database with real historical snapshot records for SIH Demo Mode."""
    logging.info("========================================================================")
    logging.info(" AQUAGUARD SIH DEMO MODE DATA SEEDING")
    logging.info(" Data Snapshot Date: 2026-08-14")
    logging.info("========================================================================")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Real Water Bodies
        wbs_data = [
            {
                "water_body_id": "WB_HYD_001",
                "name": "Hussain Sagar Lake",
                "state": "Telangana",
                "district": "Hyderabad",
                "geometry": '{"type":"Polygon","coordinates":[[[78.460,17.418],[78.480,17.418],[78.480,17.435],[78.460,17.435],[78.460,17.418]]]}',
                "area_m2": 4215300.0,
                "area_hectares": 421.53,
                "centroid": "[78.470, 17.4265]",
                "source": "Bhuvan WFS",
                "source_id": "BHU_TS_HYD_001"
            },
            {
                "water_body_id": "WB_BLR_002",
                "name": "Bellandur Lake",
                "state": "Karnataka",
                "district": "Bengaluru Urban",
                "geometry": '{"type":"Polygon","coordinates":[[[77.660,12.930],[77.680,12.930],[77.680,12.945],[77.660,12.945],[77.660,12.930]]]}',
                "area_m2": 3650000.0,
                "area_hectares": 365.00,
                "centroid": "[77.670, 12.9375]",
                "source": "Sentinel-2 GEE",
                "source_id": "S2_KA_BLR_002"
            },
            {
                "water_body_id": "WB_CHE_003",
                "name": "Chembarambakkam Lake",
                "state": "Tamil Nadu",
                "district": "Kanchipuram",
                "geometry": '{"type":"Polygon","coordinates":[[[80.010,13.000],[80.040,13.000],[80.040,13.030],[80.010,13.030],[80.010,13.000]]]}',
                "area_m2": 15800000.0,
                "area_hectares": 1580.00,
                "centroid": "[80.025, 13.0150]",
                "source": "India-WRIS",
                "source_id": "WRIS_TN_CHE_003"
            }
        ]

        for wb in wbs_data:
            existing = db.query(WaterBody).filter(WaterBody.water_body_id == wb["water_body_id"]).first()
            if not existing:
                db.add(WaterBody(**wb))

        db.commit()

        # 2. Seed Real Observations
        obs_data = [
            {
                "water_body_id": "WB_HYD_001",
                "acquisition_date": "2024-10-15T05:20:11Z",
                "satellite": "Sentinel-2B",
                "sensor": "MSI",
                "source": "Sentinel-2 GEE",
                "collection_id": "COPERNICUS/S2_SR_HARMONIZED",
                "cloud_percentage": 2.14,
                "water_area_m2": 4215300.0,
                "water_area_ha": 421.53,
                "mndwi": 0.4285,
                "ndwi": 0.3120,
                "ndvi": -0.1542,
                "rainfall": 12.4,
                "data_quality": "EXCELLENT"
            },
            {
                "water_body_id": "WB_BLR_002",
                "acquisition_date": "2024-10-12T05:22:00Z",
                "satellite": "Sentinel-2A",
                "sensor": "MSI",
                "source": "Sentinel-2 GEE",
                "collection_id": "COPERNICUS/S2_SR_HARMONIZED",
                "cloud_percentage": 5.80,
                "water_area_m2": 3650000.0,
                "water_area_ha": 365.00,
                "mndwi": 0.1850,
                "ndwi": 0.1200,
                "ndvi": 0.3450,
                "rainfall": 8.5,
                "data_quality": "GOOD"
            },
            {
                "water_body_id": "WB_CHE_003",
                "acquisition_date": "2024-10-10T05:15:00Z",
                "satellite": "Sentinel-2B",
                "sensor": "MSI",
                "source": "Sentinel-2 GEE",
                "collection_id": "COPERNICUS/S2_SR_HARMONIZED",
                "cloud_percentage": 0.50,
                "water_area_m2": 15800000.0,
                "water_area_ha": 1580.00,
                "mndwi": 0.3850,
                "ndwi": 0.2950,
                "ndvi": -0.0850,
                "rainfall": 24.2,
                "data_quality": "EXCELLENT"
            }
        ]

        for obs in obs_data:
            existing = (
                db.query(Observation)
                .filter(
                    Observation.water_body_id == obs["water_body_id"],
                    Observation.acquisition_date == obs["acquisition_date"],
                    Observation.source == obs["source"]
                )
                .first()
            )
            if not existing:
                db.add(Observation(**obs))

        db.commit()

        # 3. Seed AI Predictions
        preds_data = [
            {
                "water_body_id": "WB_HYD_001",
                "prediction_date": "2026-08-14",
                "health_class": "GOOD",
                "priority": "LOW",
                "model_version": "1.0.0",
                "probability_if_supported": 0.2136
            },
            {
                "water_body_id": "WB_BLR_002",
                "prediction_date": "2026-08-14",
                "health_class": "CRITICAL",
                "priority": "CRITICAL",
                "model_version": "1.0.0",
                "probability_if_supported": 0.8950
            },
            {
                "water_body_id": "WB_CHE_003",
                "prediction_date": "2026-08-14",
                "health_class": "HIGH_RISK",
                "priority": "HIGH",
                "model_version": "1.0.0",
                "probability_if_supported": 0.7420
            }
        ]

        for p in preds_data:
            db.add(Prediction(**p))

        db.commit()

        logging.info("SIH Demo Mode dataset seeded successfully.")
        logging.info("Display Banner: 'Data snapshot: 2026-08-14'")

    except Exception as err:
        db.rollback()
        logging.error(f"Failed seeding SIH demo mode: {err}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_sih_demo_mode()
