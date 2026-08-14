"""
AquaGuard - Candidate Model Comparison Suite
---------------------------------------------
Benchmarks multiple candidate classification models (Logistic Regression, Decision Tree,
Random Forest, Gradient Boosting) and outputs side-by-side comparative metrics.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

# Add project root to path
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.models.train import ModelTrainer


def compare_candidate_models():
    """Run model comparison and print benchmark report."""
    print("========================================================================")
    print(" AQUAGUARD: Candidate Model Benchmark & Comparison Suite")
    print("========================================================================")

    trainer = ModelTrainer()
    best_model, metadata = trainer.train_and_select_best()

    print("\n------------------------------------------------------------------------")
    print(" BENCHMARK SUMMARY")
    print("------------------------------------------------------------------------")
    print(f" Best Model Selected         : {metadata['model_name']} (v{metadata['version']})")
    print(f" Test Set Accuracy           : {metadata['test_metrics']['accuracy']:.4f}")
    print(f" Test Set Weighted F1        : {metadata['test_metrics']['f1_weighted']:.4f}")
    print(f" Critical Priority Recall    : {metadata['test_metrics']['critical_class_recall']:.4f}")

    print("\n Top Model Feature Importances / Factors:")
    for feat, imp in list(metadata["feature_importances"].items())[:5]:
        print(f"   - {feat:<25} : {imp:.4f}")

    print("========================================================================\n")


if __name__ == "__main__":
    compare_candidate_models()
