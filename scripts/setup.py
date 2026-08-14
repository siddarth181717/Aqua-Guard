"""
AquaGuard Project Workspace Setup Script
----------------------------------------
Executes initial database initialization, data directory creation, and verification.
"""

import sys
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

from backend.app.core.database import SessionLocal, engine, Base
from backend.app.database.init_db import init_db


def setup_workspace():
    logging.info("Initializing AquaGuard workspace directories...")
    dirs = [
        PROJECT_ROOT / "data" / "raw",
        PROJECT_ROOT / "data" / "processed",
        PROJECT_ROOT / "data" / "datasets",
        PROJECT_ROOT / "models",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        logging.info(f"Verified directory: {d}")

    logging.info("Initializing database schema & baseline data...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    init_db(db)
    db.close()

    logging.info("AquaGuard workspace setup complete!")


if __name__ == "__main__":
    setup_workspace()
