"""
AquaGuard Backend Services Package
-----------------------------------
Exposes WaterBodyService, ObservationService, GeospatialService, AnalyticsService, and MLService.
"""

from backend.app.services.water_body_service import WaterBodyService
from backend.app.services.observation_service import ObservationService
from backend.app.services.geospatial_service import GeospatialService
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.ml_service import MLService

__all__ = [
    "WaterBodyService",
    "ObservationService",
    "GeospatialService",
    "AnalyticsService",
    "MLService"
]
