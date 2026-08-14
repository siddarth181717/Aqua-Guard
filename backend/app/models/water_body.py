"""
AquaGuard WaterBody SQLAlchemy ORM Model
-----------------------------------------
Represents the water_bodies PostGIS database table.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class WaterBody(Base):
    """WaterBody ORM Model for water_bodies database table."""

    __tablename__ = "water_bodies"

    id = Column(Integer, primary_key=True, index=True)
    water_body_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), index=True, nullable=False)
    state = Column(String(100), index=True, nullable=False)
    district = Column(String(100), index=True, nullable=False)
    geometry = Column(Text, nullable=False)  # GeoJSON / WKT Geometry representation
    area_m2 = Column(Float, nullable=True)
    area_hectares = Column(Float, nullable=True)
    centroid = Column(Text, nullable=True)   # Centroid point [lon, lat] string
    source = Column(String(100), nullable=True)
    source_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    observations = relationship("Observation", back_populates="water_body", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="water_body", cascade="all, delete-orphan")
