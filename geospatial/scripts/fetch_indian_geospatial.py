"""
AquaGuard - Bhuvan & India-WRIS Data Acquisition Script
---------------------------------------------------------
Queries official Bhuvan (ISRO/NRSC) and India-WRIS (Ministry of Jal Shakti) geospatial services,
saves raw payloads under data/raw/bhuvan/ and data/raw/india_wris/, and normalizes features
into the unified AquaGuard schema.

Usage:
    python geospatial/scripts/fetch_indian_geospatial.py [--state TELANGANA] [--district HYDERABAD]
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from geospatial.indian_sources import (
    BhuvanGeospatialClient,
    IndiaWRISClient,
    normalize_feature_collection
)


def main():
    parser = argparse.ArgumentParser(
        description="AquaGuard Indian Geospatial Data Acquisition (Bhuvan & India-WRIS)"
    )
    parser.add_argument(
        "--state",
        type=str,
        default="TELANGANA",
        help="Target State name (default: TELANGANA)"
    )
    parser.add_argument(
        "--district",
        type=str,
        default="HYDERABAD",
        help="Target District name (default: HYDERABAD)"
    )
    parser.add_argument(
        "--bbox",
        type=float,
        nargs=4,
        default=[78.46, 17.41, 78.48, 17.43],
        help="Target bounding box [min_lon, min_lat, max_lon, max_lat]"
    )

    args = parser.parse_args()

    print("========================================================================")
    print(" AQUAGUARD: Official Indian Geospatial Data Sources (Bhuvan & WRIS)")
    print("========================================================================")

    # Prepare Directories
    bhuvan_raw_dir = PROJECT_ROOT / "data" / "raw" / "bhuvan"
    wris_raw_dir = PROJECT_ROOT / "data" / "raw" / "india_wris"
    processed_dir = PROJECT_ROOT / "data" / "processed" / "geospatial"
    bhuvan_raw_dir.mkdir(parents=True, exist_ok=True)
    wris_raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # 1. Bhuvan (NRSC / ISRO) Data Acquisition
    # -------------------------------------------------------------------------
    print("\n[1/3] Querying Bhuvan (NRSC / ISRO)...")
    bhuvan_client = BhuvanGeospatialClient()
    bhuvan_raw = bhuvan_client.query_water_bodies(
        bbox=args.bbox,
        state=args.state,
        district=args.district
    )
    
    bhuvan_raw_file = bhuvan_raw_dir / "bhuvan_waterbodies.json"
    with open(bhuvan_raw_file, "w", encoding="utf-8") as f:
        json.dump(bhuvan_raw, f, indent=2)
    print(f"   [+] Bhuvan Raw Data saved: {bhuvan_raw_file.resolve()}")

    # WMS Layer URL display
    bhuvan_wms_url = bhuvan_client.build_wms_layer_url(
        layer_name=BhuvanGeospatialClient.LAYER_LULC_WATERBODY,
        bbox=args.bbox
    )
    print(f"   [+] Bhuvan WMS Visualization Layer URL: {bhuvan_wms_url[:80]}...")

    # -------------------------------------------------------------------------
    # 2. India-WRIS Data Acquisition
    # -------------------------------------------------------------------------
    print("\n[2/3] Querying India-WRIS (Ministry of Jal Shakti)...")
    wris_client = IndiaWRISClient()
    
    # Water Bodies Query
    wris_wb_raw = wris_client.query_water_bodies(bbox=args.bbox, state=args.state)
    wris_wb_file = wris_raw_dir / "wris_waterbodies.json"
    with open(wris_wb_file, "w", encoding="utf-8") as f:
        json.dump(wris_wb_raw, f, indent=2)
    print(f"   [+] India-WRIS Water Bodies Raw Data saved: {wris_wb_file.resolve()}")

    # Rivers & Basins Query
    wris_basin_raw = wris_client.query_basins(bbox=args.bbox)
    wris_basin_file = wris_raw_dir / "wris_basins.json"
    with open(wris_basin_file, "w", encoding="utf-8") as f:
        json.dump(wris_basin_raw, f, indent=2)
    print(f"   [+] India-WRIS Basins Raw Data saved: {wris_basin_file.resolve()}")

    # WMS Layer URL display
    wris_wms_url = wris_client.build_wms_layer_url(
        layer_name=IndiaWRISClient.LAYER_WATER_BODIES,
        bbox=args.bbox
    )
    print(f"   [+] India-WRIS WMS Visualization Layer URL: {wris_wms_url[:80]}...")

    # -------------------------------------------------------------------------
    # 3. Schema Normalization
    # -------------------------------------------------------------------------
    print("\n[3/3] Normalizing into Unified AquaGuard Water-Body Schema...")
    bhuvan_norm = normalize_feature_collection(bhuvan_raw, default_source="Bhuvan WFS")
    wris_norm = normalize_feature_collection(wris_wb_raw, default_source="India-WRIS WFS")

    all_normalized = bhuvan_norm + wris_norm

    processed_json = processed_dir / "indian_water_bodies.json"
    with open(processed_json, "w", encoding="utf-8") as f:
        json.dump({
            "status": "success",
            "total_records": len(all_normalized),
            "sources": ["Bhuvan (ISRO/NRSC)", "India-WRIS (Ministry of Jal Shakti)"],
            "data": all_normalized
        }, f, indent=2)

    print("\n------------------------------------------------------------------------")
    print(" AQUAGUARD INDIAN GEOSPATIAL NORMALIZED RESULTS")
    print("------------------------------------------------------------------------")
    print(f" Total Normalized Records : {len(all_normalized)}")
    
    for idx, rec in enumerate(all_normalized, 1):
        print(f"\n Record #{idx}:")
        print(f"   - Source              : {rec['source']}")
        print(f"   - Source ID           : {rec['source_id']}")
        print(f"   - Water Body ID       : {rec['water_body_id']}")
        print(f"   - Name                : {rec['name']}")
        print(f"   - Location            : {rec['district']}, {rec['state']}")
        print(f"   - CRS                 : {rec['CRS']}")
        print(f"   - Area                : {rec['area']} m²" if rec['area'] else "   - Area                : N/A")
        print(f"   - Retrieval Date      : {rec['retrieval_date']}")

    print("------------------------------------------------------------------------")
    print(f" Process Complete. Outputs Saved:")
    print(f"   1. Raw Bhuvan Data   : {bhuvan_raw_file.resolve()}")
    print(f"   2. Raw WRIS Data     : {wris_wb_file.resolve()}")
    print(f"   3. Normalized JSON   : {processed_json.resolve()}")
    print("========================================================================\n")


if __name__ == "__main__":
    main()
