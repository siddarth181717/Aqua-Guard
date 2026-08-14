"""
AquaGuard - Daily Rainfall & Climate Data Acquisition Script
------------------------------------------------------------
Runs the daily rainfall pipeline for a target water body or coordinate location over a date range.
Saves raw payload under data/raw/rainfall/ and processed data under data/processed/climate/.

Usage:
    python geospatial/scripts/fetch_rainfall.py [--geometry_file PATH] [--start_date YYYY-MM-DD] [--end_date YYYY-MM-DD]
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from geospatial.climate.rainfall_pipeline import RainfallAcquisitionPipeline


def main():
    parser = argparse.ArgumentParser(
        description="AquaGuard Daily Rainfall Acquisition (Open-Meteo ERA5 / CHIRPS)"
    )
    parser.add_argument(
        "--geometry_file",
        type=str,
        default=str(PROJECT_ROOT / "data" / "raw" / "sample_waterbody.json"),
        help="Path to GeoJSON geometry file for the water body"
    )
    parser.add_argument(
        "--latitude",
        type=float,
        default=None,
        help="Optional target latitude (overrides centroid calculation)"
    )
    parser.add_argument(
        "--longitude",
        type=float,
        default=None,
        help="Optional target longitude (overrides centroid calculation)"
    )
    parser.add_argument(
        "--start_date",
        type=str,
        default=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        help="Start date in YYYY-MM-DD format (default: 30 days ago)"
    )
    parser.add_argument(
        "--end_date",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date in YYYY-MM-DD format (default: today)"
    )

    args = parser.parse_args()

    print("========================================================================")
    print(f" AQUAGUARD: Daily Rainfall Acquisition ({args.start_date} to {args.end_date})")
    print("========================================================================")

    # Step 1: Initialize Pipeline
    pipeline = RainfallAcquisitionPipeline()

    # Step 2: Acquire Data
    try:
        if args.latitude is not None and args.longitude is not None:
            raw_data, records = pipeline.fetch_rainfall(
                latitude=args.latitude,
                longitude=args.longitude,
                start_date=args.start_date,
                end_date=args.end_date
            )
        else:
            raw_data, records = pipeline.fetch_rainfall_for_water_body(
                geometry_input=args.geometry_file,
                start_date=args.start_date,
                end_date=args.end_date
            )
    except Exception as err:
        print(f"\n[ERROR] Rainfall acquisition failed: {err}")
        sys.exit(1)

    # Step 3: Compute Summary Metrics
    valid_rainfalls = [r["rainfall"] for r in records if r["rainfall"] is not None]
    total_precip = round(sum(valid_rainfalls), 2) if valid_rainfalls else 0.0
    rainy_days = sum(1 for r in valid_rainfalls if r > 0.1)

    wb_id = records[0]["water_body_id"] if records else "WB_001"
    lat = records[0]["latitude"] if records else 0.0
    lon = records[0]["longitude"] if records else 0.0
    source = records[0]["source"] if records else "Unknown"

    print("\n------------------------------------------------------------------------")
    print(f" DAILY RAINFALL ANALYSIS REPORT ({wb_id})")
    print("------------------------------------------------------------------------")
    print(f" Target Water Body ID    : {wb_id}")
    print(f" Location Centroid       : Lat {lat:.4f}, Lon {lon:.4f}")
    print(f" Date Range              : {args.start_date} to {args.end_date}")
    print(f" Data Source             : {source}")
    print(f" Total Days Analyzed     : {len(records)} days")
    print(f" Cumulative Rainfall     : {total_precip} mm")
    print(f" Rainy Days (>0.1mm)     : {rainy_days} days")

    print("\n Daily Precipitation Breakdown (Recent 10 Days):")
    print(f" {'DATE':<12} | {'RAINFALL (mm)':<15} | {'SOURCE':<20}")
    print("-" * 55)

    for rec in records[-10:]:
        d_str = rec["date"]
        rain_str = f"{rec['rainfall']:.2f} mm" if rec["rainfall"] is not None else "N/A"
        src_str = rec["source"]
        print(f" {d_str:<12} | {rain_str:<15} | {src_str:<20}")

    # Step 4: Save Datasets
    raw_dir = PROJECT_ROOT / "data" / "raw" / "rainfall"
    processed_dir = PROJECT_ROOT / "data" / "processed" / "climate"
    raw_json = raw_dir / "raw_rainfall_data.json"
    processed_json = processed_dir / "water_body_rainfall.json"
    processed_csv = processed_dir / "water_body_rainfall.csv"

    pipeline.save_json(raw_data, raw_json)
    pipeline.save_json({"water_body_id": wb_id, "summary": {"total_rainfall_mm": total_precip, "rainy_days": rainy_days}, "records": records}, processed_json)
    pipeline.export_to_csv(records, processed_csv)

    print("------------------------------------------------------------------------")
    print(f" Datasets Saved Successfully:")
    print(f"   1. Raw Payload   : {raw_json.resolve()}")
    print(f"   2. Processed JSON: {processed_json.resolve()}")
    print(f"   3. Processed CSV : {processed_csv.resolve()}")
    print("========================================================================\n")


if __name__ == "__main__":
    main()
