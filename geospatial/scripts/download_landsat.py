"""
AquaGuard - Landsat Satellite Data Acquisition & Water Analysis Script
-----------------------------------------------------------------------
Runs the Landsat pipeline for a target water body over historical periods (2013-2026).
Saves raw data under data/raw/landsat/ and processed results under data/processed/satellite/.

Usage:
    python geospatial/scripts/download_landsat.py [--geometry_file PATH] [--start_year 2013] [--end_year 2026] [--project_id GEE_PROJECT]
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from geospatial.gee.landsat_pipeline import LandsatAcquisitionPipeline


def main():
    parser = argparse.ArgumentParser(
        description="AquaGuard Landsat Data Acquisition & Historical Water Analysis (GEE)"
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
        default=2013,
        help="Start year for Landsat historical analysis (default: 2013)"
    )
    parser.add_argument(
        "--end_year",
        type=int,
        default=2026,
        help="End year for Landsat historical analysis (default: 2026)"
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
        "--project_id",
        type=str,
        default=None,
        help="Google Cloud Project ID for Earth Engine initialization"
    )

    args = parser.parse_args()

    print("========================================================================")
    print(f" AQUAGUARD: Landsat Historical Water Analysis ({args.start_year}-{args.end_year})")
    print("========================================================================")

    # Step 1: Initialize Landsat Pipeline
    try:
        pipeline = LandsatAcquisitionPipeline(project_id=args.project_id, auto_init=True)
    except Exception as err:
        print(f"\n[ERROR] Pipeline Initialization Failed: {err}")
        sys.exit(1)

    # Step 2: Fetch Raw Observations Metadata
    raw_dir = PROJECT_ROOT / "data" / "raw" / "landsat"
    raw_metadata_path = raw_dir / "landsat_metadata.json"
    
    try:
        raw_obs = pipeline.fetch_observations(
            geometry=args.geometry_file,
            start_date=f"{args.start_year}-01-01",
            end_date=f"{args.end_year}-12-31",
            max_cloud_percentage=args.max_cloud,
            satellites=("L8", "L9")
        )
        pipeline.save_metadata(raw_obs, raw_metadata_path)
    except Exception as raw_err:
        print(f"[WARNING] Could not fetch raw metadata: {raw_err}")

    # Step 3: Run Historical Analysis
    try:
        history_results = pipeline.analyze_historical_trend(
            geometry=args.geometry_file,
            start_year=args.start_year,
            end_year=args.end_year,
            season_months=(args.season_start_month, args.season_end_month),
            max_cloud_percentage=args.max_cloud,
            satellites=("L8", "L9")
        )
    except Exception as analysis_err:
        print(f"\n[ERROR] Landsat historical analysis failed: {analysis_err}")
        sys.exit(1)

    records = history_results.get("records", [])

    # Step 4: Display Formatted Table
    print("\n---------------------------------------------------------------------------------------------------")
    print(f" LANDSAT HISTORICAL WATER BODY TREND REPORT ({history_results.get('water_body_id')})")
    print("---------------------------------------------------------------------------------------------------")
    header = f"{'YEAR':<6} | {'OBS DATE':<20} | {'AREA (m²)':<12} | {'AREA (ha)':<10} | {'MNDWI':<7} | {'NDWI':<7} | {'NDVI':<7} | {'SOURCE':<18}"
    print(header)
    print("-" * len(header))

    for rec in records:
        yr = rec["year"]
        obs_dt = rec["observation_date"][:10] if rec["observation_date"] != "UNAVAILABLE" else "UNAVAILABLE"
        a_m2 = f"{rec['water_area_m2']:,.0f}" if rec["water_area_m2"] is not None else "N/A"
        a_ha = f"{rec['water_area_ha']:,.2f}" if rec["water_area_ha"] is not None else "N/A"
        mndwi = f"{rec['mndwi']:.4f}" if rec["mndwi"] is not None else "N/A"
        ndwi = f"{rec['ndwi']:.4f}" if rec["ndwi"] is not None else "N/A"
        ndvi = f"{rec['ndvi']:.4f}" if rec["ndvi"] is not None else "N/A"
        src = rec["source"]

        print(f"{yr:<6} | {obs_dt:<20} | {a_m2:<12} | {a_ha:<10} | {mndwi:<7} | {ndwi:<7} | {ndvi:<7} | {src:<18}")

    print("---------------------------------------------------------------------------------------------------")

    # Step 5: Save Output Files
    processed_dir = PROJECT_ROOT / "data" / "processed" / "satellite"
    processed_json = processed_dir / "landsat_water_analysis.json"
    processed_csv = processed_dir / "landsat_water_analysis.csv"
    dataset_csv = PROJECT_ROOT / "data" / "datasets" / "water_body_features.csv"

    pipeline.save_metadata(history_results, processed_json)
    pipeline.export_to_csv(records, processed_csv)
    pipeline.export_to_csv(records, dataset_csv, append=True)

    print("---------------------------------------------------------------------------------------------------")
    print(f" Landsat Datasets Saved Successfully:")
    print(f"   1. Raw Metadata : {raw_metadata_path.resolve()}")
    print(f"   2. Processed JSON: {processed_json.resolve()}")
    print(f"   3. Processed CSV : {processed_csv.resolve()}")
    print(f"   4. Combined Dataset: {dataset_csv.resolve()}")
    print("===================================================================================================\n")


if __name__ == "__main__":
    main()
