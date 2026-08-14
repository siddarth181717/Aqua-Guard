"""
AquaGuard WaterBody Pydantic Schemas
-----------------------------------
Request, Response, and GeoJSON schemas for water body resources.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WaterBodyBase(BaseModel):
    """Base WaterBody attributes."""
    water_body_id: str = Field(..., example="WB_HYD_001")
    name: str = Field(..., example="Hussain Sagar Lake")
    state: str = Field(..., example="Telangana")
    district: str = Field(..., example="Hyderabad")
    area_m2: Optional[float] = Field(None, example=4215300.0)
    area_hectares: Optional[float] = Field(None, example=421.53)
    source: Optional[str] = Field(None, example="Bhuvan WFS")
    source_id: Optional[str] = Field(None, example="BHUVAN_LULC_50K_884")


class WaterBodyCreate(WaterBodyBase):
    """Schema for creating a new water body."""
    geometry: Dict[str, Any]  # GeoJSON dict


class WaterBodyResponse(WaterBodyBase):
    """Schema for water body endpoint responses."""
    id: int
    centroid: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj: Any) -> "WaterBodyResponse":
        return cls.model_validate(obj)


class WaterBodyGeoJSON(BaseModel):
    """GeoJSON Feature representation compliant with RFC 7946."""
    type: str = "Feature"
    id: str
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


class WaterBodyNearbyQuery(BaseModel):
    """Schema for spatial radius query."""
    latitude: float = Field(..., ge=-90.0, le=90.0, example=17.4248)
    longitude: float = Field(..., ge=-180.0, le=180.0, example=78.4680)
    radius_km: float = Field(10.0, gt=0.0, le=500.0, example=10.0)
