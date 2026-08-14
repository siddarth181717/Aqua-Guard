"""
AquaGuard Prediction SQLAlchemy ORM Model
------------------------------------------
Represents the predictions database table.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class Prediction(Base):
    """Prediction ORM Model for predictions database table."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    water_body_id = Column(String(64), ForeignKey("water_bodies.water_body_id"), index=True, nullable=False)
    prediction_date = Column(String(50), index=True, nullable=False)
    health_class = Column(String(50), nullable=False)
    priority = Column(String(50), index=True, nullable=False)
    model_version = Column(String(50), nullable=False)
    probability_if_supported = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    water_body = relationship("WaterBody", back_populates="predictions")
