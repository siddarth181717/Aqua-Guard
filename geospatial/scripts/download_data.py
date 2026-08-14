"""
AquaGuard - Sentinel-2 Historical Multi-Year Water Analysis Script (2021-2026)
--------------------------------------------------------------------------------
Runs multi-year seasonal water-spread and spectral index analysis over target years.
Exports results to data/processed/satellite/ and data/datasets/water_body_features.csv.

Usage:
    python geospatial/scripts/download_data.py [--geometry_file PATH] [--start_year 2021] [--end_year 2026] [--project_id GEE_PROJECT]
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from geospatial.gee.sentinel2_pipeline import Sentinel2AcquisitionPipeline


def main():
    parser = argparse.ArgumentParser(
        description="AquaGuard Sentinel-2 Historical Multi-Year Water Analysis (2021-2026)"
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
        help="Start year for historical trend analysis (default: 2021)"
    )
    parser.add_argument(
        "--end_year",
        type=int,
        default=2026,
        help="End year for historical trend analysis (default: 2026)"
    )
    parser.add_argument(
        "--season_start_month",
        type=int,
        default=10,
        help="Start month for seasonal alignment (default: 10 - October)"
    )
    parser.add_argument(
        "--season_end_month",
        type=int,
        default=11,
        help="End month for seasonal alignment (default: 11 - November)"
    )
    parser.add_argument(
        "--max_cloud",
        type=float,
        default=20.0,
        help="Maximum allowed cloud percentage (default: 20.0)"
    )
    parser.add_argument(
        "--mndwi_thresh",
        type=float,
        default=0.0,
        help="Configurable MNDWI threshold (default: 0.0)"
    )
    parser.add_argument(
        "--ndvi_thresh",
        type=float,
        default=0.2,
        help="Configurable upper NDVI threshold (default: 0.2)"
    )
    parser.add_argument(
        "--project_id",
        type=str,
        default=None,
        help="Google Cloud Project ID for Earth Engine initialization"
    )

    args = parser.parse_args()

    print("========================================================================")
    print(f" AQUAGUARD: Sentinel-2 Historical Multi-Year Water Analysis ({args.start_year}-{args.end_year})")
    print("========================================================================")

    # Step 1: Initialize Pipeline
    try:
        pipeline = Sentinel2AcquisitionPipeline(project_id=args.project_id, auto_init=True)
    except Exception as err:
        print(f"\n[ERROR] Pipeline Initialization Failed: {err}")
        sys.exit(1)

    # Step 2: Perform Historical Multi-Year Analysis
    try:
        history_results = pipeline.analyze_historical_trend(
            geometry=args.geometry_file,
            start_year=args.start_year,
            end_year=args.end_year,
            season_months=(args.season_start_month, args.season_end_month),
            max_cloud_percentage=args.max_cloud,
            mndwi_threshold=args.mndwi_thresh,
            ndvi_threshold=args.ndvi_thresh
        )
    except Exception as analysis_err:
        print(f"\n[ERROR] Historical trend analysis failed: {analysis_err}")
        sys.exit(1)

    records = history_results.get("records", [])

    # Step 3: Print Formatted Summary Table
    print("\n---------------------------------------------------------------------------------------------------")
    print(f" HISTORICAL WATER BODY TREND REPORT ({history_results.get('water_body_id')})")
    print("---------------------------------------------------------------------------------------------------")
    header = f"{'YEAR':<6} | {'OBS DATE':<20} | {'AREA (m²)':<12} | {'AREA (ha)':<10} | {'CHANGE %':<10} | {'MNDWI':<7} | {'NDWI':<7} | {'NDVI':<7} | {'QUALITY':<12}"
    print(header)
    print("-" * len(header))

    for rec in records:
        yr = rec["year"]
        obs_dt = rec["observation_date"][:10] if rec["observation_date"] != "UNAVAILABLE" else "UNAVAILABLE"
        a_m2 = f"{rec['water_area_m2']:,.0f}" if rec["water_area_m2"] is not None else "N/A"
        a_ha = f"{rec['water_area_ha']:,.2f}" if rec["water_area_ha"] is not None else "N/A"
        chg = f"{rec['water_area_change_percent']:+.2f}%" if rec["water_area_change_percent"] is not None else "N/A"
        mndwi = f"{rec['mndwi']:.4f}" if rec["mndwi"] is not None else "N/A"
        ndwi = f"{rec['ndwi']:.4f}" if rec["ndwi"] is not None else "N/A"
        ndvi = f"{rec['ndvi']:.4f}" if rec["ndvi"] is not None else "N/A"
        qual = rec["quality"]

        print(f"{yr:<6} | {obs_dt:<20} | {a_m2:<12} | {a_ha:<10} | {chg:<10} | {mndwi:<7} | {ndwi:<7} | {ndvi:<7} | {qual:<12}")

    print("---------------------------------------------------------------------------------------------------")

    # Step 4: Save Datasets
    processed_dir = PROJECT_ROOT / "data" / "processed" / "satellite"
    processed_json = processed_dir / "historical_water_analysis.json"
    processed_csv = processed_dir / "historical_water_analysis.csv"
    dataset_csv = PROJECT_ROOT / "data" / "datasets" / "water_body_features.csv"

    pipeline.save_metadata(history_results, processed_json)
    pipeline.export_to_csv(records, processed_csv)
    pipeline.export_to_csv(records, dataset_csv)

    print("---------------------------------------------------------------------------------------------------")
    print(f" Datasets Created Successfully:")
    print(f"   1. JSON Output : {processed_json.resolve()}")
    print(f"   2. CSV Output  : {processed_csv.resolve()}")
    print(f"   3. Feature Set : {dataset_csv.resolve()}")
    print("===================================================================================================\n")


if __name__ == "__main__":
    main()
