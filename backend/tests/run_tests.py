"""
AquaGuard Test Runner Script
----------------------------
Executes backend API unit tests via FastAPI TestClient.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.tests.test_health import test_health_check_endpoint
from backend.tests.test_water_bodies import (
    test_list_water_bodies,
    test_get_water_body_by_id,
    test_get_water_body_geometry,
    test_invalid_water_body_not_found
)
from backend.tests.test_analysis import (
    test_get_water_body_observations,
    test_get_water_body_analytics,
    test_get_water_body_trend
)
from backend.tests.test_predictions import (
    test_get_water_body_prediction,
    test_get_priority_rankings
)
from backend.tests.test_end_to_end import test_full_end_to_end_pipeline


def run_all_tests():
    print("========================================================================")
    print(" AQUAGUARD BACKEND & INTEGRATION TEST SUITE")
    print("========================================================================")

    tests = [
        ("Health Check Endpoint (/api/v1/health)", test_health_check_endpoint),
        ("List Water Bodies Endpoint (/api/v1/water-bodies)", test_list_water_bodies),
        ("Get Water Body Details Endpoint (/api/v1/water-bodies/{id})", test_get_water_body_by_id),
        ("Get Water Body GeoJSON Geometry Endpoint (/api/v1/water-bodies/{id}/geometry)", test_get_water_body_geometry),
        ("Water Body Not Found 404 Endpoint", test_invalid_water_body_not_found),
        ("Get Water Body Observations Endpoint", test_get_water_body_observations),
        ("Get Water Body Analytics Endpoint", test_get_water_body_analytics),
        ("Get Water Body Trend Endpoint", test_get_water_body_trend),
        ("Get AI/ML Prediction Endpoint (/api/v1/water-bodies/{id}/prediction)", test_get_water_body_prediction),
        ("Get Priority Rankings Endpoint (/api/v1/priorities)", test_get_priority_rankings),
        ("End-to-End Pipeline & Integration Test", test_full_end_to_end_pipeline),
    ]


    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            print(f" [PASS] {name}")
            passed += 1
        except Exception as err:
            print(f" [FAIL] {name}: {err}")
            failed += 1

    print("------------------------------------------------------------------------")
    print(f" Summary: {passed} PASSED, {failed} FAILED.")
    print("========================================================================\n")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
