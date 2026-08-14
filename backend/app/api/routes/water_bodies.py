"""
AquaGuard Water Bodies API Routes
---------------------------------
Endpoints for searching, fetching details, GeoJSON geometry, and nearby PostGIS spatial queries.
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.common import APIResponse, PaginatedResponse
from backend.app.schemas.water_body import WaterBodyResponse
from backend.app.services.geospatial_service import GeospatialService
from backend.app.services.water_body_service import WaterBodyService
from backend.app.utils.validation import validate_coordinates

router = APIRouter(prefix="/water-bodies", tags=["Water Bodies"])


@router.get("", response_model=APIResponse[PaginatedResponse[WaterBodyResponse]])
def list_water_bodies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    state: Optional[str] = Query(None, description="Filter by state name"),
    district: Optional[str] = Query(None, description="Filter by district name"),
    db: Session = Depends(get_db)
):
    """Return paginated list of water bodies with optional state/district filters."""
    items, total = WaterBodyService.get_water_bodies(db, page, page_size, state, district)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    paginated_data = PaginatedResponse(
        items=[WaterBodyResponse.from_orm(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

    return APIResponse(
        success=True,
        data=paginated_data,
        message=f"Retrieved {len(items)} water bodies"
    )


@router.get("/nearby", response_model=APIResponse[List[dict]])
def get_nearby_water_bodies(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Centroid latitude"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Centroid longitude"),
    radius_km: float = Query(10.0, gt=0.0, le=500.0, description="Radius in kilometers"),
    db: Session = Depends(get_db)
):
    """Find nearby water bodies within specified radius using PostGIS spatial functions."""
    validate_coordinates(latitude, longitude)
    nearby_items = GeospatialService.get_nearby_water_bodies(db, latitude, longitude, radius_km)

    return APIResponse(
        success=True,
        data=nearby_items,
        message=f"Found {len(nearby_items)} nearby water bodies within {radius_km} km radius"
    )


@router.get("/{water_body_id}", response_model=APIResponse[WaterBodyResponse])
def get_water_body_by_id(water_body_id: str, db: Session = Depends(get_db)):
    """Return detailed information about one water body by ID."""
    wb = WaterBodyService.get_water_body_by_id(db, water_body_id)
    if not wb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water body with ID '{water_body_id}' not found."
        )

    return APIResponse(
        success=True,
        data=WaterBodyResponse.from_orm(wb),
        message=f"Water body '{water_body_id}' retrieved successfully"
    )


@router.get("/{water_body_id}/geometry", response_model=APIResponse[dict])
def get_water_body_geometry(water_body_id: str, db: Session = Depends(get_db)):
    """Return GeoJSON Feature representation of water body geometry."""
    geojson_feature = WaterBodyService.get_water_body_geometry_geojson(db, water_body_id)
    if not geojson_feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Geometry for water body ID '{water_body_id}' not found."
        )

    return APIResponse(
        success=True,
        data=geojson_feature,
        message=f"GeoJSON geometry for water body '{water_body_id}' retrieved"
    )
