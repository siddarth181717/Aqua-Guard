"""
AquaGuard Health Check API Route
--------------------------------
GET /api/v1/health -> System health, database connection, and ML model status.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.schemas.common import APIResponse
from backend.app.services.ml_service import MLService

router = APIRouter(prefix="/health", tags=["Health"])



@router.get("", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint checking database connectivity and ML model availability."""
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as err:
        db_status = f"error: {str(err)}"

    ml_status = "ok"
    try:
        predictor = MLService.get_predictor()
        if predictor.use_baseline_fallback:
            ml_status = "ok" # Baseline scorer is active and functional
    except Exception as ml_err:
        ml_status = f"error: {str(ml_err)}"

    overall_ok = (db_status == "ok" and ml_status == "ok")

    return APIResponse(
        success=overall_ok,
        data={
            "backend": "ok",
            "database": db_status,
            "ml_model": ml_status,
            "status": "ok" if overall_ok else "degraded",
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0"
        },
        message="AquaGuard system components operational" if overall_ok else "One or more AquaGuard components are experiencing issues"
    )

