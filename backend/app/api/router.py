"""
AquaGuard API Router Index
--------------------------
Combines health, water_bodies, observations, analytics, and predictions routers under /api/v1.
"""

from fastapi import APIRouter

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.water_bodies import router as water_bodies_router
from backend.app.api.routes.observations import router as observations_router
from backend.app.api.routes.analytics import router as analytics_router
from backend.app.api.routes.predictions import router as predictions_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(water_bodies_router)
api_router.include_router(observations_router)
api_router.include_router(analytics_router)
api_router.include_router(predictions_router)
