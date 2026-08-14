"""
AquaGuard Prediction & Ranking Pydantic Schemas
------------------------------------------------
Schemas for AI/ML priority predictions and priority ranking list endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PredictionBase(BaseModel):
    """Base Prediction attributes."""
    water_body_id: str
    prediction_date: str = Field(..., example="2026-08-13")
    health_class: str = Field(..., example="HIGH_RISK")
    priority: str = Field(..., example="HIGH")
    model_version: str = Field(..., example="1.0.0")
    probability_if_supported: Optional[float] = Field(None, example=0.84)


class PredictionCreate(PredictionBase):
    """Schema for creating a prediction."""
    pass


class PredictionResponse(PredictionBase):
    """Schema for prediction API response."""
    id: int
    created_at: datetime
    model_factors: Optional[List[str]] = Field(None, example=["Persistent water-area decline (-3.4%)", "Negative MNDWI trend"])

    class Config:
        from_attributes = True


class PriorityRankingItem(BaseModel):
    """Item schema for restoration priority ranking list API."""
    rank: int
    water_body_id: str
    name: str
    state: str
    district: str
    priority: str
    health_class: str
    probability: Optional[float] = None
    latest_area_ha: Optional[float] = None
