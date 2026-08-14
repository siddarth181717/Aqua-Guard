"""
AquaGuard - Leakage-Free Preprocessing Pipeline
------------------------------------------------
Provides AquaGuardPreprocessor to handle missing values, numerical feature scaling,
and categorical encoding without data leakage.

Data Leakage Prevention Rules:
1. Imputers and scalers are fitted ONLY on training split data.
2. Transformations are then applied to validation and test sets.
3. Scaler saved to models/scaler.pkl.
"""

import joblib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class AquaGuardPreprocessor:
    """Leakage-free preprocessing manager for AquaGuard ML features."""

    def __init__(self, scaler_path: Optional[Union[str, Path]] = None):
        self.scaler = StandardScaler()
        self.feature_cols: List[str] = []
        self.impute_values: Dict[str, float] = {}
        self.is_fitted = False
        self.scaler_path = Path(scaler_path) if scaler_path else None

    def fit(self, df: pd.DataFrame, feature_cols: List[str]) -> "AquaGuardPreprocessor":
        """
        Fit imputers and scaler strictly on training DataFrame.

        Args:
            df: Training DataFrame.
            feature_cols: List of numeric feature column names.

        Returns:
            AquaGuardPreprocessor: Fitted preprocessor instance.
        """
        self.feature_cols = [c for c in feature_cols if c in df.columns]

        if not self.feature_cols:
            raise ValueError(f"None of the target feature columns {feature_cols} exist in DataFrame.")

        # Step 1: Calculate column means on training set only for imputation
        for col in self.feature_cols:
            col_vals = pd.to_numeric(df[col], errors="coerce")
            mean_val = float(col_vals.mean()) if not col_vals.dropna().empty else 0.0
            self.impute_values[col] = mean_val

        # Step 2: Impute training copy & fit StandardScaler
        df_imputed = df[self.feature_cols].copy()
        for col in self.feature_cols:
            df_imputed[col] = pd.to_numeric(df_imputed[col], errors="coerce").fillna(self.impute_values[col])

        self.scaler.fit(df_imputed[self.feature_cols].values)
        self.is_fitted = True

        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Apply fitted imputation and scaling to DataFrame (train, val, or test).

        Args:
            df: DataFrame to transform.

        Returns:
            np.ndarray: Scaled feature matrix.
        """
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted on training data before calling transform().")

        df_imputed = df.copy()
        for col in self.feature_cols:
            if col in df_imputed.columns:
                df_imputed[col] = pd.to_numeric(df_imputed[col], errors="coerce").fillna(self.impute_values[col])
            else:
                df_imputed[col] = self.impute_values[col]

        return self.scaler.transform(df_imputed[self.feature_cols].values)

    def fit_transform(self, df: pd.DataFrame, feature_cols: List[str]) -> np.ndarray:
        """Fit on training data and return scaled matrix."""
        return self.fit(df, feature_cols).transform(df)

    def save_scaler(self, output_path: Optional[Union[str, Path]] = None) -> Path:
        """Save fitted scaler object to disk (models/scaler.pkl)."""
        if not self.is_fitted:
            raise RuntimeError("Cannot save scaler before fitting.")

        target_path = Path(output_path) if output_path else (self.scaler_path or Path("models/scaler.pkl"))
        target_path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump({
            "scaler": self.scaler,
            "feature_cols": self.feature_cols,
            "impute_values": self.impute_values
        }, target_path)

        print(f"[INFO] Fitted preprocessor saved to: {target_path.resolve()}")
        return target_path.resolve()

    @classmethod
    def load_scaler(cls, model_path: Union[str, Path]) -> "AquaGuardPreprocessor":
        """Load fitted scaler object from disk."""
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"Scaler file not found: {path}")

        data = joblib.load(path)
        instance = cls()
        instance.scaler = data["scaler"]
        instance.feature_cols = data["feature_cols"]
        instance.impute_values = data["impute_values"]
        instance.is_fitted = True
        return instance
