"""
AquaGuard ORM Models Package
----------------------------
Exposes WaterBody, Observation, Prediction, and User models.
"""

from backend.app.models.water_body import WaterBody
from backend.app.models.observation import Observation
from backend.app.models.prediction import Prediction
from backend.app.models.user import User

__all__ = [
    "WaterBody",
    "Observation",
    "Prediction",
    "User"
]
