"""
AquaGuard AI/ML Inference & Ranking Service Layer
--------------------------------------------------
Loads trained ML model & preprocessor artifacts (once on application startup)
and executes explainable restoration priority predictions and priority rankings.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from ai.models.predict import AquaGuardPredictor
from backend.app.models.prediction import Prediction
from backend.app.schemas.prediction import PredictionResponse, PriorityRankingItem
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.water_body_service import WaterBodyService


class MLService:
    """Service layer for AI/ML inference and priority ranking."""

    _predictor: Optional[AquaGuardPredictor] = None

    @classmethod
    def get_predictor(cls) -> AquaGuardPredictor:
        """Singleton accessor for AquaGuardPredictor instance."""
        if cls._predictor is None:
            cls._predictor = AquaGuardPredictor()
        return cls._predictor

    @classmethod
    def get_prediction(cls, db: Session, water_body_id: str) -> Dict[str, Any]:
        """
        Retrieve or compute latest AI/ML restoration prediction for a water body.

        Returns:
            Dict[str, Any]: Prediction payload with priority class, probability, and factors.
        """
        # Step 1: Check if recent prediction exists in database
        existing_pred = (
            db.query(Prediction)
            .filter(Prediction.water_body_id == water_body_id)
            .order_by(Prediction.created_at.desc())
            .first()
        )

        wb = WaterBodyService.get_water_body_by_id(db, water_body_id)
        if not wb:
            return {
                "water_body_id": water_body_id,
                "health_class": "UNKNOWN",
                "priority": "LOW",
                "model_version": "1.0.0",
                "prediction_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "model_factors": ["No water body data found"]
            }

        analytics = AnalyticsService.get_analytics_summary(db, water_body_id)

        # Form feature dictionary matching ML pipeline requirements
        feature_dict = {
            "water_body_id": water_body_id,
            "water_area_mean": wb.area_m2 or 4215300.0,
            "water_area_current": analytics["current_water_area_m2"] if analytics else 4215300.0,
            "water_area_change": analytics["water_area_change_m2"] if analytics else 0.0,
            "water_area_change_percent": analytics["water_area_change_percent"] if analytics else 0.0,
            "mndwi_mean": analytics["mean_mndwi"] if analytics else 0.4285,
            "mndwi_trend": -0.01,
            "ndwi_mean": analytics["mean_ndwi"] if analytics else 0.3120,
            "ndvi_mean": analytics["mean_ndvi"] if analytics else -0.1542,
            "annual_rainfall": analytics["total_rainfall_mm"] if analytics else 12.4,
            "builtup_percentage": 25.0,
            "data_quality_score": 0.95
        }

        # Step 2: Run inference through AquaGuardPredictor
        predictor = cls.get_predictor()
        pred_payload = predictor.predict_single(feature_dict)

        # Step 3: Persist prediction to database
        db_pred = Prediction(
            water_body_id=water_body_id,
            prediction_date=pred_payload["prediction_date"],
            health_class=pred_payload["health_class"],
            priority=pred_payload["priority"],
            model_version=pred_payload["model_version"],
            probability_if_supported=pred_payload.get("model_probability")
        )
        db.add(db_pred)
        db.commit()

        return pred_payload

    @classmethod
    def get_priority_rankings(cls, db: Session) -> List[PriorityRankingItem]:
        """
        Return all water bodies ordered by restoration priority.
        Order: CRITICAL -> HIGH -> MEDIUM -> LOW.
        """
        all_wbs, _ = WaterBodyService.get_water_bodies(db, page=1, page_size=100)

        rankings = []
        priority_weights = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

        for wb in all_wbs:
            pred = cls.get_prediction(db, wb.water_body_id)
            rankings.append({
                "water_body_id": wb.water_body_id,
                "name": wb.name,
                "state": wb.state,
                "district": wb.district,
                "priority": pred["priority"],
                "health_class": pred["health_class"],
                "probability": pred.get("model_probability"),
                "latest_area_ha": wb.area_hectares,
                "weight": priority_weights.get(pred["priority"], 1)
            })

        # Sort descending by priority weight, then by area
        rankings.sort(key=lambda x: (x["weight"], x["latest_area_ha"] or 0), reverse=True)

        items = []
        for idx, item in enumerate(rankings, 1):
            items.append(PriorityRankingItem(
                rank=idx,
                water_body_id=item["water_body_id"],
                name=item["name"],
                state=item["state"],
                district=item["district"],
                priority=item["priority"],
                health_class=item["health_class"],
                probability=item["probability"],
                latest_area_ha=item["latest_area_ha"]
            ))

        return items
