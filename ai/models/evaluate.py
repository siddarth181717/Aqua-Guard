"""
AquaGuard - AI/ML Model Evaluator
----------------------------------
Computes comprehensive classification and regression metrics for model assessment.

Emphasis:
- Classification: Focuses on Recall for HIGH and CRITICAL priority classes.
  A missed severely degraded water body is worse than a false alarm.
- Regression: MAE (Mean Absolute Error), RMSE, R².
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score
)


class ModelEvaluator:
    """Evaluation toolkit for AquaGuard candidate models."""

    @staticmethod
    def evaluate_classification(
        y_true: Union[List, np.ndarray],
        y_pred: Union[List, np.ndarray],
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compute classification metrics with special attention to HIGH/CRITICAL Recall.

        Returns:
            Dict[str, Any]: Classification metrics dictionary.
        """
        acc = float(accuracy_score(y_true, y_pred))
        prec_w = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
        rec_w = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
        f1_w = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

        target_labels = labels or sorted(list(set(y_true) | set(y_pred)))
        cm = confusion_matrix(y_true, y_pred, labels=target_labels).tolist()

        # Per-class recall metrics
        per_class_rec = recall_score(y_true, y_pred, labels=target_labels, average=None, zero_division=0)
        per_class_f1 = f1_score(y_true, y_pred, labels=target_labels, average=None, zero_division=0)

        per_class_metrics = {}
        for lbl, r_val, f_val in zip(target_labels, per_class_rec, per_class_f1):
            per_class_metrics[str(lbl)] = {
                "recall": round(float(r_val), 4),
                "f1_score": round(float(f_val), 4)
            }

        critical_recall = per_class_metrics.get("CRITICAL", {}).get("recall", rec_w)
        high_recall = per_class_metrics.get("HIGH", {}).get("recall", rec_w)

        return {
            "accuracy": round(acc, 4),
            "precision_weighted": round(prec_w, 4),
            "recall_weighted": round(rec_w, 4),
            "f1_weighted": round(f1_w, 4),
            "critical_class_recall": round(critical_recall, 4),
            "high_class_recall": round(high_recall, 4),
            "per_class_metrics": per_class_metrics,
            "confusion_matrix": cm,
            "labels": target_labels
        }

    @staticmethod
    def evaluate_regression(
        y_true: Union[List, np.ndarray],
        y_pred: Union[List, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Compute regression metrics (MAE, MSE, RMSE, R²).

        Returns:
            Dict[str, Any]: Regression metrics dictionary.
        """
        mae = float(mean_absolute_error(y_true, y_pred))
        mse = float(mean_squared_error(y_true, y_pred))
        rmse = float(np.sqrt(mse))
        r2 = float(r2_score(y_true, y_pred))

        return {
            "mae": round(mae, 4),
            "mse": round(mse, 4),
            "rmse": round(rmse, 4),
            "r2_score": round(r2, 4),
            "mae_explanation": "MAE represents average absolute prediction error in target score units."
        }
