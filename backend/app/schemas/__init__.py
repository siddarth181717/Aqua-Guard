"""
AquaGuard Pydantic Schemas Package
-----------------------------------
Exposes API common envelopes, WaterBody, Observation, and Prediction schemas.
"""

from backend.app.schemas.common import APIResponse, APIError, PaginatedResponse
from backend.app.schemas.water_body import (
    WaterBodyBase,
    WaterBodyCreate,
    WaterBodyResponse,
    WaterBodyGeoJSON,
    WaterBodyNearbyQuery
)
from backend.app.schemas.observation import (
    ObservationBase,
    ObservationCreate,
    ObservationResponse,
    ObservationLatestResponse
)
from backend.app.schemas.prediction import (
    PredictionBase,
    PredictionCreate,
    PredictionResponse,
    PriorityRankingItem
)

__all__ = [
    "APIResponse",
    "APIError",
    "PaginatedResponse",
    "WaterBodyBase",
    "WaterBodyCreate",
    "WaterBodyResponse",
    "WaterBodyGeoJSON",
    "WaterBodyNearbyQuery",
    "ObservationBase",
    "ObservationCreate",
    "ObservationResponse",
    "ObservationLatestResponse",
    "PredictionBase",
    "PredictionCreate",
    "PredictionResponse",
    "PriorityRankingItem"
]
