"""
AquaGuard Analytics API Routes
------------------------------
Endpoints for retrieving water area changes, MNDWI/NDWI/NDVI trends, and chart time-series data.
"""

from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.common import APIResponse
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/water-bodies", tags=["Analytics"])


@router.get("/{water_body_id}/analytics", response_model=APIResponse[dict])
def get_water_body_analytics(water_body_id: str, db: Session = Depends(get_db)):
    """Return analytics summary (area changes, mean spectral indices, rainfall context)."""
    analytics = AnalyticsService.get_analytics_summary(db, water_body_id)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analytics data for water body '{water_body_id}' not found."
        )

    return APIResponse(
        success=True,
        data=analytics,
        message=f"Analytics summary retrieved for water body '{water_body_id}'"
    )


@router.get("/{water_body_id}/trend", response_model=APIResponse[dict])
def get_water_body_trend(water_body_id: str, db: Session = Depends(get_db)):
    """Return time-series observation dataset formatted for frontend chart visualization."""
    trend_data = AnalyticsService.get_time_series_trend(db, water_body_id)
    return APIResponse(
        success=True,
        data=trend_data,
        message=f"Time-series trend data retrieved for water body '{water_body_id}'"
    )
