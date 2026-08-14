"""
AquaGuard Observations API Routes
---------------------------------
Endpoints for querying historical satellite observations and latest valid observation.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.common import APIResponse
from backend.app.schemas.observation import ObservationLatestResponse, ObservationResponse
from backend.app.services.observation_service import ObservationService

router = APIRouter(prefix="/water-bodies", tags=["Observations"])


@router.get("/{water_body_id}/observations", response_model=APIResponse[List[ObservationResponse]])
def get_water_body_observations(
    water_body_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    satellite: Optional[str] = Query(None, description="Satellite name filter (e.g. Sentinel-2, Landsat-9)"),
    db: Session = Depends(get_db)
):
    """Return historical satellite and climate observations for a water body."""
    items = ObservationService.get_observations(db, water_body_id, start_date, end_date, satellite)
    return APIResponse(
        success=True,
        data=[ObservationResponse.from_orm(o) for o in items],
        message=f"Retrieved {len(items)} observations for water body '{water_body_id}'"
    )


@router.get("/{water_body_id}/latest", response_model=APIResponse[ObservationLatestResponse])
def get_latest_observation(water_body_id: str, db: Session = Depends(get_db)):
    """Return the latest valid available observation for a water body."""
    latest = ObservationService.get_latest_observation(db, water_body_id)
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No observations available for water body '{water_body_id}'."
        )

    return APIResponse(
        success=True,
        data=latest,
        message=f"Latest observation retrieved for water body '{water_body_id}' (Acquisition: {latest.acquisition_date})"
    )
