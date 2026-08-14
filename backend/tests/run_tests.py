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
from backend.tests.test_predictions import (
    test_get_water_body_prediction,
    test_get_priority_rankings
)


def run_all_tests():
    print("========================================================================")
    print(" AQUAGUARD BACKEND TEST SUITE")
    print("========================================================================")

    tests = [
        ("Health Check Endpoint", test_health_check_endpoint),
        ("List Water Bodies Endpoint", test_list_water_bodies),
        ("Get Water Body Details Endpoint", test_get_water_body_by_id),
        ("Get Water Body GeoJSON Geometry Endpoint", test_get_water_body_geometry),
        ("Water Body Not Found 404 Endpoint", test_invalid_water_body_not_found),
        ("Get AI/ML Prediction Endpoint", test_get_water_body_prediction),
        ("Get Priority Rankings Endpoint", test_get_priority_rankings),
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
