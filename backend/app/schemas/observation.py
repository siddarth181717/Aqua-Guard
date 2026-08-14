"""
AquaGuard Observation Pydantic Schemas
---------------------------------------
Request, Response, and Analytics schemas for satellite & climate observations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ObservationBase(BaseModel):
    """Base Observation attributes."""
    water_body_id: str
    acquisition_date: str = Field(..., example="2024-10-15T05:20:11Z")
    satellite: Optional[str] = Field(None, example="Sentinel-2B")
    sensor: Optional[str] = Field(None, example="MSI")
    source: str = Field(..., example="Sentinel-2 GEE")
    collection_id: Optional[str] = Field(None, example="COPERNICUS/S2_SR_HARMONIZED")
    cloud_percentage: Optional[float] = Field(None, example=2.14)
    water_area_m2: Optional[float] = Field(None, example=4215300.0)
    water_area_ha: Optional[float] = Field(None, example=421.53)
    mndwi: Optional[float] = Field(None, example=0.4285)
    ndwi: Optional[float] = Field(None, example=0.3120)
    ndvi: Optional[float] = Field(None, example=-0.1542)
    rainfall: Optional[float] = Field(None, example=12.4)
    data_quality: Optional[str] = Field(None, example="EXCELLENT")


class ObservationCreate(ObservationBase):
    """Schema for creating a new observation."""
    pass


class ObservationResponse(ObservationBase):
    """Schema for observation API responses."""
    id: int
    processing_date: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj: Any) -> "ObservationResponse":
        return cls.model_validate(obj)


class ObservationLatestResponse(BaseModel):
    """Response schema for latest valid observation endpoint."""
    water_body_id: str
    acquisition_date: str
    source: str
    satellite: Optional[str] = None
    water_area_ha: Optional[float] = None
    mndwi: Optional[float] = None
    ndwi: Optional[float] = None
    ndvi: Optional[float] = None
    cloud_percentage: Optional[float] = None
    data_quality: Optional[str] = None
    status: str = "latest_available"
