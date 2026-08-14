"""
AquaGuard User SQLAlchemy ORM Model
-----------------------------------
Represents the users database table for authentication.
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String

from backend.app.core.database import Base


class User(Base):
    """User ORM Model for users database table."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
