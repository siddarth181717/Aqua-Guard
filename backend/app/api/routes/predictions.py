"""
AquaGuard Predictions & Priorities API Routes
----------------------------------------------
Endpoints for retrieving AI/ML predictions and restoration priority rankings.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.common import APIResponse
from backend.app.schemas.prediction import PriorityRankingItem
from backend.app.services.ml_service import MLService

router = APIRouter(tags=["Predictions & Priorities"])


@router.get("/water-bodies/{water_body_id}/prediction", response_model=APIResponse[dict])
def get_water_body_prediction(water_body_id: str, db: Session = Depends(get_db)):
    """Return the latest validated AI/ML restoration prediction for a water body."""
    pred = MLService.get_prediction(db, water_body_id)
    return APIResponse(
        success=True,
        data=pred,
        message=f"AI/ML prediction retrieved for water body '{water_body_id}'"
    )


@router.get("/priorities", response_model=APIResponse[List[PriorityRankingItem]])
def get_restoration_priorities(db: Session = Depends(get_db)):
    """Return list of all water bodies ordered by restoration priority."""
    rankings = MLService.get_priority_rankings(db)
    return APIResponse(
        success=True,
        data=rankings,
        message=f"Retrieved {len(rankings)} ranked water bodies for restoration priority"
    )
