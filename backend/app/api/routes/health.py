"""
AquaGuard Health Check API Route
--------------------------------
GET /api/v1/health -> System health, database connection, and ML model status.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.common import APIResponse
from backend.app.services.ml_service import MLService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint checking database connectivity and ML model availability."""
    db_status = "connected"
    try:
        db.execute("SELECT 1")
    except Exception as err:
        db_status = f"error: {str(err)}"

    ml_status = "available"
    try:
        predictor = MLService.get_predictor()
        if predictor.use_baseline_fallback:
            ml_status = "baseline_prototype_active"
    except Exception as ml_err:
        ml_status = f"unavailable: {str(ml_err)}"

    return APIResponse(
        success=True,
        data={
            "status": "ok",
            "environment": "development",
            "database": db_status,
            "ml_model": ml_status,
            "version": "1.0.0"
        },
        message="AquaGuard backend system is healthy"
    )
