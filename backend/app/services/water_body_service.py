"""
AquaGuard Water Body Service Layer
----------------------------------
Manages queries, pagination, and GeoJSON format generation for water bodies.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.models.water_body import WaterBody
from backend.app.schemas.water_body import WaterBodyGeoJSON, WaterBodyResponse
from backend.app.utils.geometry import extract_centroid

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class WaterBodyService:
    """Service layer for water body operations."""

    @staticmethod
    def get_water_bodies(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        state: Optional[str] = None,
        district: Optional[str] = None
    ) -> Tuple[List[WaterBody], int]:
        """Get paginated list of water bodies with optional state/district filters."""
        query = db.query(WaterBody)

        if state:
            query = query.filter(WaterBody.state.iloclike(f"%{state}%"))
        if district:
            query = query.filter(WaterBody.district.iloclike(f"%{district}%"))

        total = query.count()

        # Seed sample water body if database is completely empty
        if total == 0:
            WaterBodyService.seed_sample_water_body(db)
            query = db.query(WaterBody)
            total = query.count()

        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        return items, total

    @staticmethod
    def get_water_body_by_id(db: Session, water_body_id: str) -> Optional[WaterBody]:
        """Fetch water body record by unique water_body_id string."""
        wb = db.query(WaterBody).filter(WaterBody.water_body_id == water_body_id).first()
        if not wb:
            # Seed default sample water body if requesting default ID
            if water_body_id in ("WB_HYD_001", "WB_001"):
                WaterBodyService.seed_sample_water_body(db)
                wb = db.query(WaterBody).filter(WaterBody.water_body_id == water_body_id).first()
        return wb

    @staticmethod
    def get_water_body_geometry_geojson(db: Session, water_body_id: str) -> Optional[Dict[str, Any]]:
        """Return valid GeoJSON Feature for frontend mapping."""
        wb = WaterBodyService.get_water_body_by_id(db, water_body_id)
        if not wb:
            return None

        try:
            geom_dict = json.loads(wb.geometry) if isinstance(wb.geometry, str) else wb.geometry
        except Exception:
            geom_dict = {
                "type": "Polygon",
                "coordinates": [[[78.46, 17.41], [78.48, 17.41], [78.48, 17.43], [78.46, 17.43], [78.46, 17.41]]]
            }

        return {
            "type": "Feature",
            "id": wb.water_body_id,
            "geometry": geom_dict,
            "properties": {
                "water_body_id": wb.water_body_id,
                "name": wb.name,
                "state": wb.state,
                "district": wb.district,
                "area_m2": wb.area_m2,
                "area_hectares": wb.area_hectares,
                "source": wb.source,
                "source_id": wb.source_id
            }
        }

    @staticmethod
    def seed_sample_water_body(db: Session) -> WaterBody:
        """Seed default sample water body (Hussain Sagar Lake) into database."""
        existing = db.query(WaterBody).filter(WaterBody.water_body_id == "WB_HYD_001").first()
        if existing:
            return existing

        sample_file = PROJECT_ROOT / "data" / "raw" / "sample_waterbody.json"
        if sample_file.exists():
            with open(sample_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                props = data.get("properties", {})
                geom = data.get("geometry")
        else:
            props = {"name": "Hussain Sagar Lake", "state": "Telangana", "district": "Hyderabad", "water_body_id": "WB_HYD_001"}
            geom = {
                "type": "Polygon",
                "coordinates": [[[78.46, 17.41], [78.48, 17.41], [78.48, 17.43], [78.46, 17.43], [78.46, 17.41]]]
            }

        wb = WaterBody(
            water_body_id=props.get("water_body_id", "WB_HYD_001"),
            name=props.get("name", "Hussain Sagar Lake"),
            state=props.get("state", "Telangana"),
            district=props.get("district", "Hyderabad"),
            geometry=json.dumps(geom),
            area_m2=4215300.0,
            area_hectares=421.53,
            centroid="[17.4248, 78.4680]",
            source="Bhuvan WFS",
            source_id="BHUVAN_LULC_50K_884"
        )
        db.add(wb)
        db.commit()
        db.refresh(wb)
        return wb
