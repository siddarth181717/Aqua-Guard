"""
AquaGuard - Model Inference & Explainable Prediction Pipeline
--------------------------------------------------------------
Provides AquaGuardPredictor for model inference, priority probability estimation,
and transparent model factor explanations.

Exports predictions to data/datasets/predictions.csv.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd

# Add project root to path
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.data_processing.preprocess import AquaGuardPreprocessor
from ai.models.baseline_scorer import BaselinePriorityScorer


class AquaGuardPredictor:
    """Inference predictor for AquaGuard restoration priority model."""

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        scaler_path: Optional[Union[str, Path]] = None,
        metadata_path: Optional[Union[str, Path]] = None
    ):
        self.model_path = Path(model_path) if model_path else (PROJECT_ROOT / "models" / "restoration_priority_model.pkl")
        self.scaler_path = Path(scaler_path) if scaler_path else (PROJECT_ROOT / "models" / "scaler.pkl")
        self.metadata_path = Path(metadata_path) if metadata_path else (PROJECT_ROOT / "models" / "model_metadata.json")

        self.model = None
        self.preprocessor = None
        self.metadata = {}
        self.use_baseline_fallback = False

        self._load_artifacts()

    def _load_artifacts(self):
        """Load trained model, fitted scaler, and metadata JSON."""
        if self.model_path.exists() and self.scaler_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                self.preprocessor = AquaGuardPreprocessor.load_scaler(self.scaler_path)
                if self.metadata_path.exists():
                    with open(self.metadata_path, "r", encoding="utf-8") as f:
                        self.metadata = json.load(f)
                print(f"[INFO] AquaGuardPredictor loaded '{self.metadata.get('model_name', 'Model')}' (v{self.metadata.get('version', '1.0.0')}).")
                
                # Check if loaded model is a BaselinePriorityScorer
                if hasattr(self.model, "compute_priority_score"):
                    self.use_baseline_fallback = True
                    self.baseline_scorer = self.model
                return
            except Exception as err:
                print(f"[WARNING] Failed loading ML model artifacts ({err}). Using baseline scoring fallback.")

        print("[INFO] Model artifacts not found or unavailable. Using transparent Baseline Priority Scorer fallback.")
        self.use_baseline_fallback = True
        self.baseline_scorer = BaselinePriorityScorer()

    def predict_single(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict restoration priority and explain contributing model factors for a single record.

        Returns:
            Dict[str, Any]: Prediction payload.
        """
        wb_id = record.get("water_body_id", "WB_001")
        pred_date = datetime.now().strftime("%Y-%m-%d")

        if self.use_baseline_fallback or not hasattr(self.model, "predict"):
            score, priority, factors = self.baseline_scorer.compute_priority_score(record)
            health_class = f"{priority}_RISK"
            return {
                "water_body_id": wb_id,
                "health_class": health_class,
                "priority": priority,
                "model_probability": round(score, 4),
                "model_version": self.metadata.get("version", "1.0.0-prototype-baseline"),
                "prediction_date": pred_date,
                "methodology": "Rule-based prototype baseline",
                "model_factors": factors
            }

        # ML Model Inference Path
        df_single = pd.DataFrame([record])
        X_scaled = self.preprocessor.transform(df_single)

        priority = self.model.predict(X_scaled)[0]

        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X_scaled)[0]
            prob_val = round(float(np.max(probs)), 4)
        else:
            prob_val = 0.85

        health_class = f"{priority}_RISK"
        factors = self._generate_model_factors(record)

        return {
            "water_body_id": wb_id,
            "health_class": health_class,
            "priority": priority,
            "model_probability": prob_val,
            "model_version": self.metadata.get("version", "1.0.0"),
            "prediction_date": pred_date,
            "methodology": f"Supervised ML ({self.metadata.get('model_name', 'Random Forest')})",
            "model_factors": factors
        }

    def predict_dataset(
        self,
        df: pd.DataFrame,
        output_csv_path: Optional[Union[str, Path]] = None
    ) -> List[Dict[str, Any]]:
        """Predict restoration priority across a dataset and optionally export predictions.csv."""
        predictions = []
        for _, row in df.iterrows():
            pred = self.predict_single(row.to_dict())
            predictions.append(pred)

        if output_csv_path:
            out_file = Path(output_csv_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            
            fieldnames = [
                "water_body_id", "prediction_date", "health_class",
                "priority", "model_version", "model_probability"
            ]

            with open(out_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for p in predictions:
                    row = {k: p.get(k, "") for k in fieldnames}
                    writer.writerow(row)

            print(f"[INFO] Model predictions exported to CSV: {out_file.resolve()}")

        return predictions

    def _generate_model_factors(self, record: Dict[str, Any]) -> List[str]:
        """Generate top contributing model factor descriptions."""
        factors = []
        area_chg = float(record.get("water_area_change_percent", 0.0) or 0.0)
        mndwi_val = float(record.get("mndwi_mean", 0.4) or 0.4)
        mndwi_trend = float(record.get("mndwi_trend", 0.0) or 0.0)
        builtup_pct = float(record.get("builtup_percentage", 20.0) or 20.0)

        if area_chg < -3.0:
            factors.append(f"Persistent water-area decline ({area_chg:.1f}%)")
        if mndwi_trend < -0.01 or mndwi_val < 0.2:
            factors.append(f"Negative MNDWI trend ({mndwi_trend:.4f})")
        if builtup_pct > 25.0:
            factors.append(f"High surrounding built-up area ({builtup_pct:.1f}%)")

        if not factors:
            factors.append("Stable environmental feature indicators")

        return factors


def main():
    ml_features_file = PROJECT_ROOT / "data" / "datasets" / "ml_features.csv"
    if not ml_features_file.exists():
        fe_file = PROJECT_ROOT / "data" / "datasets" / "water_body_features.csv"
        from ai.data_processing.feature_engineering import FeatureEngineer
        fe = FeatureEngineer(fe_file)
        df = fe.build_ml_features(output_csv_path=ml_features_file)
    else:
        df = pd.read_csv(ml_features_file)

    predictor = AquaGuardPredictor()
    pred_path = PROJECT_ROOT / "data" / "datasets" / "predictions.csv"
    preds = predictor.predict_dataset(df, output_csv_path=pred_path)

    print("\n------------------------------------------------------------------------")
    print(" AQUAGUARD PRIORITY PREDICTIONS REPORT")
    print("------------------------------------------------------------------------")
    for p in preds:
        print(f" Water Body ID : {p['water_body_id']}")
        print(f" Priority      : {p['priority']} ({p['health_class']})")
        print(f" Score/Prob    : {p['model_probability']}")
        print(f" Model Version : {p['model_version']}")
        print(f" Methodology   : {p['methodology']}")
        print(f" Model Factors : {', '.join(p['model_factors'])}\n")
    print("========================================================================\n")


if __name__ == "__main__":
    main()
