"""
AquaGuard - Unified Feature Dataset Builder & 10-Point Data Validation Script
-----------------------------------------------------------------------------
Integrates Sentinel-2, Landsat, Bhuvan, India-WRIS, and Rainfall data sources.
Outputs:
- CSV: data/datasets/water_body_features.csv
- GeoJSON: data/datasets/water_body_features.geojson
- Validation Report: data/processed/integration_validation_report.json

Usage:
    python geospatial/scripts/build_unified_dataset.py [--geometry_file PATH] [--start_year 2021] [--end_year 2026] [--project_id GEE_PROJECT]
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from geospatial.integration import AquaGuardDataValidator, AquaGuardDatasetBuilder


def main():
    parser = argparse.ArgumentParser(
        description="AquaGuard Unified Feature Dataset Builder & 10-Point Validator"
    )
    parser.add_argument(
        "--geometry_file",
        type=str,
        default=str(PROJECT_ROOT / "data" / "raw" / "sample_waterbody.json"),
        help="Path to GeoJSON geometry file for the water body"
    )
    parser.add_argument(
        "--start_year",
        type=int,
        default=2021,
        help="Start year for historical multi-source integration (default: 2021)"
    )
    parser.add_argument(
        "--end_year",
        type=int,
        default=2026,
        help="End year for historical multi-source integration (default: 2026)"
    )
    parser.add_argument(
        "--project_id",
        type=str,
        default=None,
        help="Google Cloud Project ID for Earth Engine initialization"
    )

    args = parser.parse_args()

    print("========================================================================")
    print(" AQUAGUARD: Unified Multi-Source Dataset Integration & Validation")
    print("========================================================================")

    # Step 1: Initialize Builder & Validator
    builder = AquaGuardDatasetBuilder(project_id=args.project_id)
    validator = AquaGuardDataValidator()

    # Step 2: Build Unified Dataset
    try:
        unified_records, raw_sources_meta = builder.build_unified_dataset(
            geometry_file=args.geometry_file,
            start_year=args.start_year,
            end_year=args.end_year
        )
    except Exception as build_err:
        print(f"\n[ERROR] Dataset building failed: {build_err}")
        sys.exit(1)

    # Step 3: Run 10-Point Data Validation Pipeline
    print("\n[INFO] Running Mandatory 10-Point Data Validation Pipeline...")
    val_report = validator.validate_dataset(unified_records)

    # Step 4: Export Files
    dataset_dir = PROJECT_ROOT / "data" / "datasets"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    dataset_csv = dataset_dir / "water_body_features.csv"
    dataset_geojson = dataset_dir / "water_body_features.geojson"
    val_report_json = processed_dir / "integration_validation_report.json"

    builder.export_to_csv(unified_records, dataset_csv)
    builder.export_to_geojson(unified_records, dataset_geojson)

    with open(val_report_json, "w", encoding="utf-8") as f:
        json.dump(val_report, f, indent=2)

    # Step 5: Print Summary
    print("\n------------------------------------------------------------------------")
    print(" 10-POINT DATA VALIDATION AUDIT REPORT")
    print("------------------------------------------------------------------------")
    print(f" Overall Status               : {val_report['overall_status']}")
    print(f" Total Records Audited        : {val_report['summary']['total_records_checked']}")
    print(f" Checks Passed                : {val_report['summary']['passed_checks']} / {val_report['summary']['total_checks']}")
    print(f" Checks Warning               : {val_report['summary']['warning_checks']}")
    print(f" Checks Failed                : {val_report['summary']['failed_checks']}")

    print("\n Detailed Check Results:")
    for check_name, check_data in val_report["detailed_checks"].items():
        name_clean = check_name.replace("check_", "").replace("_", " ").title()
        st = check_data["status"]
        desc = check_data["description"]
        print(f"   - [{st:<7}] {name_clean:<30} : {desc}")

    print("\n------------------------------------------------------------------------")
    print(" AQUAGUARD UNIFIED DATASET CREATED SUCCESSFULLY")
    print("------------------------------------------------------------------------")
    print(f" 1. CSV Feature Set           : {dataset_csv.resolve()}")
    print(f" 2. GeoJSON Spatial Dataset    : {dataset_geojson.resolve()}")
    print(f" 3. Validation Report         : {val_report_json.resolve()}")
    print(" Ready for next phase: AI/ML Feature Engineering!")
    print("========================================================================\n")


if __name__ == "__main__":
    main()
