"""
AquaGuard Database Setup & Connection Pool
------------------------------------------
Configures SQLAlchemy SessionLocal, Engine, and PostGIS/SQLite database session context.
"""

import sys
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.app.core.config import settings

# Determine DB Engine URL with fallback to SQLite for testing
db_url = settings.DATABASE_URL or "sqlite:///./aquaguard_test.db"

# Check driver availability for postgresql vs sqlite fallback
if db_url.startswith("postgresql"):
    try:
        import psycopg2  # type: ignore
        engine = create_engine(db_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
    except ImportError:
        # Fallback to local SQLite database when psycopg2 PostgreSQL driver is not installed
        db_url = "sqlite:///./aquaguard_test.db"
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    """Dependency for providing SQLAlchemy database session to API endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
