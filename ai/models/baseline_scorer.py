"""
AquaGuard - Transparent Baseline Priority Scoring System
--------------------------------------------------------
Implements a transparent, rule-based baseline scoring system when ground-truth
supervised training labels do not exist.

IMPORTANT:
This module is explicitly documented as a "Rule-based prototype baseline"
and is NOT presented as a trained supervised ML model.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


class BaselinePriorityScorer:
    """Rule-based prototype scoring system for water body restoration prioritization."""

    def __init__(
        self,
        water_area_decline_weight: float = 0.35,
        mndwi_decline_weight: float = 0.25,
        builtup_growth_weight: float = 0.15,
        vegetation_change_weight: float = 0.15,
        rainfall_deficit_weight: float = 0.10
    ):
        """
        Initialize baseline scoring weights. Total weights should sum to ~1.0.
        """
        self.w_area = water_area_decline_weight
        self.w_mndwi = mndwi_decline_weight
        self.w_builtup = builtup_growth_weight
        self.w_veg = vegetation_change_weight
        self.w_rain = rainfall_deficit_weight

    def compute_priority_score(self, row: Union[pd.Series, Dict[str, Any]]) -> Tuple[float, str, List[str]]:
        """
        Calculate baseline priority score (0.0 to 1.0) and class for a water body record.

        Returns:
            Tuple[float, str, List[str]]: (score_0_to_1, priority_class, contributing_factors)
        """
        factors = []
        sub_scores = []

        # 1. Water Area Decline Factor
        area_pct_change = float(row.get("water_area_change_percent", 0.0) or 0.0)
        area_trend = float(row.get("water_area_trend", 0.0) or 0.0)

        area_subscore = 0.0
        if area_pct_change < -10.0 or area_trend < -500.0:
            area_subscore = 1.0
            factors.append("Severe water-area decline detected")
        elif area_pct_change < -3.0 or area_trend < 0.0:
            area_subscore = 0.6
            factors.append("Moderate water-area shrinkage")
        else:
            area_subscore = 0.1

        sub_scores.append(self.w_area * area_subscore)

        # 2. MNDWI Water Clarity/Extent Factor
        mndwi_val = float(row.get("mndwi_mean", 0.4) or 0.4)
        mndwi_trend = float(row.get("mndwi_trend", 0.0) or 0.0)

        mndwi_subscore = 0.0
        if mndwi_val < 0.1 or mndwi_trend < -0.05:
            mndwi_subscore = 1.0
            factors.append("Significant negative MNDWI index drop (water quality/extent loss)")
        elif mndwi_val < 0.3 or mndwi_trend < 0.0:
            mndwi_subscore = 0.5
            factors.append("Subtle negative MNDWI trend")
        else:
            mndwi_subscore = 0.1

        sub_scores.append(self.w_mndwi * mndwi_subscore)

        # 3. Built-up Expansion Factor
        builtup_pct = float(row.get("builtup_percentage", 20.0) or 20.0)
        builtup_subscore = min(1.0, builtup_pct / 50.0)
        if builtup_pct > 30.0:
            factors.append("High surrounding built-up encroachment")
        sub_scores.append(self.w_builtup * builtup_subscore)

        # 4. Vegetation Encroachment / Change Factor
        ndvi_val = float(row.get("ndvi_mean", 0.0) or 0.0)
        ndvi_subscore = max(0.0, min(1.0, (ndvi_val + 0.2) / 0.8))
        if ndvi_val > 0.3:
            factors.append("High weed/algal vegetation encroachment (high NDVI)")
        sub_scores.append(self.w_veg * ndvi_subscore)

        # 5. Rainfall Deficit Factor
        annual_rain = float(row.get("annual_rainfall", 50.0) or 50.0)
        rain_subscore = 0.7 if annual_rain < 20.0 else 0.2
        sub_scores.append(self.w_rain * rain_subscore)

        total_score = round(float(sum(sub_scores)), 4)
        total_score = min(1.0, max(0.0, total_score))

        # Map to Priority Class
        if total_score >= 0.75:
            priority_class = "CRITICAL"
        elif total_score >= 0.50:
            priority_class = "HIGH"
        elif total_score >= 0.25:
            priority_class = "MEDIUM"
        else:
            priority_class = "LOW"

        if not factors:
            factors.append("Stable environmental conditions observed")

        return total_score, priority_class, factors

    def evaluate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply baseline priority scoring to an entire DataFrame."""
        df_out = df.copy()
        scores = []
        classes = []

        for _, row in df_out.iterrows():
            score, p_class, _ = self.compute_priority_score(row)
            scores.append(score)
            classes.append(p_class)

        df_out["baseline_priority_score"] = scores
        df_out["restoration_priority"] = classes
        df_out["methodology"] = "Rule-based prototype baseline"
        return df_out
