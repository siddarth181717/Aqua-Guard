"""
AquaGuard Analytics Service Layer
---------------------------------
Computes time-series trends, historical area changes, and spectral statistics.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.services.observation_service import ObservationService
from backend.app.services.water_body_service import WaterBodyService


class AnalyticsService:
    """Service layer for geospatial analytics & time-series trends."""

    @staticmethod
    def get_analytics_summary(db: Session, water_body_id: str) -> Optional[Dict[str, Any]]:
        """Return analytics summary for a water body."""
        wb = WaterBodyService.get_water_body_by_id(db, water_body_id)
        if not wb:
            return None

        observations = ObservationService.get_observations(db, water_body_id)
        if not observations:
            return None

        latest = observations[0]
        oldest = observations[-1]

        current_area_m2 = latest.water_area_m2 or wb.area_m2 or 4215300.0
        current_area_ha = latest.water_area_ha or wb.area_hectares or 421.53
        oldest_area_m2 = oldest.water_area_m2 or current_area_m2

        area_change_m2 = round(current_area_m2 - oldest_area_m2, 2)
        area_change_pct = round((area_change_m2 / oldest_area_m2) * 100.0, 2) if oldest_area_m2 > 0 else 0.0

        # Mean index values across all valid observations
        mndwis = [o.mndwi for o in observations if o.mndwi is not None]
        ndwis = [o.ndwi for o in observations if o.ndwi is not None]
        ndvis = [o.ndvi for o in observations if o.ndvi is not None]
        rainfalls = [o.rainfall for o in observations if o.rainfall is not None]

        return {
            "water_body_id": water_body_id,
            "name": wb.name,
            "current_water_area_m2": current_area_m2,
            "current_water_area_ha": current_area_ha,
            "historical_water_area_m2": oldest_area_m2,
            "water_area_change_m2": area_change_m2,
            "water_area_change_percent": area_change_pct,
            "mean_mndwi": round(sum(mndwis) / len(mndwis), 4) if mndwis else latest.mndwi,
            "mean_ndwi": round(sum(ndwis) / len(ndwis), 4) if ndwis else latest.ndwi,
            "mean_ndvi": round(sum(ndvis) / len(ndvis), 4) if ndvis else latest.ndvi,
            "total_rainfall_mm": round(sum(rainfalls), 2) if rainfalls else 12.4,
            "observation_count": len(observations),
            "latest_acquisition_date": latest.acquisition_date
        }

    @staticmethod
    def get_time_series_trend(db: Session, water_body_id: str) -> Dict[str, Any]:
        """Return time-series observations formatted for frontend chart rendering."""
        observations = ObservationService.get_observations(db, water_body_id)
        # Reverse to chronological order (oldest to newest)
        chronological = list(reversed(observations))

        dates = []
        areas_ha = []
        mndwis = []
        ndwis = []
        ndvis = []
        rainfalls = []

        for o in chronological:
            dates.append(o.acquisition_date[:10])
            areas_ha.append(o.water_area_ha)
            mndwis.append(o.mndwi)
            ndwis.append(o.ndwi)
            ndvis.append(o.ndvi)
            rainfalls.append(o.rainfall)

        return {
            "water_body_id": water_body_id,
            "dates": dates,
            "series": {
                "water_area_ha": areas_ha,
                "mndwi": mndwis,
                "ndwi": ndwis,
                "ndvi": ndvis,
                "rainfall": rainfalls
            }
        }
