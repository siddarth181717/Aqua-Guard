"""
AquaGuard Observation SQLAlchemy ORM Model
-------------------------------------------
Represents the observations database table.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class Observation(Base):
    """Observation ORM Model for observations database table."""

    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    water_body_id = Column(String(64), ForeignKey("water_bodies.water_body_id"), index=True, nullable=False)
    acquisition_date = Column(String(50), index=True, nullable=False)
    satellite = Column(String(100), nullable=True)
    sensor = Column(String(100), nullable=True)
    source = Column(String(100), nullable=False)
    collection_id = Column(String(100), nullable=True)
    cloud_percentage = Column(Float, nullable=True)
    water_area_m2 = Column(Float, nullable=True)
    water_area_ha = Column(Float, nullable=True)
    mndwi = Column(Float, nullable=True)
    ndwi = Column(Float, nullable=True)
    ndvi = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)
    data_quality = Column(String(50), nullable=True)
    processing_date = Column(DateTime, default=datetime.utcnow)

    water_body = relationship("WaterBody", back_populates="observations")
