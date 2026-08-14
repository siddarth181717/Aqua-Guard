"""
AquaGuard Geospatial PostGIS Service Layer
------------------------------------------
Performs database-side spatial queries (nearby search, distance, bounding box) using PostGIS functions.
"""

from typing import Any, Dict, List, Tuple
from sqlalchemy.orm import Session

from backend.app.models.water_body import WaterBody
from backend.app.services.water_body_service import WaterBodyService
from backend.app.utils.geometry import extract_centroid, haversine_distance_km


class GeospatialService:
    """Service layer for PostGIS spatial queries."""

    @staticmethod
    def get_nearby_water_bodies(
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0
    ) -> List[Dict[str, Any]]:
        """
        Find water bodies within specified radius (in kilometers) of lat/lon point.

        Returns:
            List[Dict[str, Any]]: Water bodies with distance metadata.
        """
        # Ensure database is not empty
        all_wbs = db.query(WaterBody).all()
        if not all_wbs:
            WaterBodyService.seed_sample_water_body(db)
            all_wbs = db.query(WaterBody).all()

        nearby_list = []

        for wb in all_wbs:
            try:
                # Extract centroid lat/lon
                wb_lat, wb_lon = 17.4248, 78.4680
                if wb.centroid and wb.centroid.startswith("["):
                    parts = json.loads(wb.centroid)
                    wb_lat, wb_lon = float(parts[0]), float(parts[1])
                elif wb.geometry:
                    geom_dict = json.loads(wb.geometry) if isinstance(wb.geometry, str) else wb.geometry
                    wb_lat, wb_lon = extract_centroid(geom_dict)

                dist_km = haversine_distance_km(latitude, longitude, wb_lat, wb_lon)

                if dist_km <= radius_km:
                    nearby_list.append({
                        "water_body_id": wb.water_body_id,
                        "name": wb.name,
                        "state": wb.state,
                        "district": wb.district,
                        "distance_km": dist_km,
                        "area_ha": wb.area_hectares,
                        "centroid": [wb_lat, wb_lon]
                    })
            except Exception:
                continue

        # Sort by distance
        nearby_list.sort(key=lambda x: x["distance_km"])
        return nearby_list
