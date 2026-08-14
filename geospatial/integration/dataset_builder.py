"""
AquaGuard - Unified Feature Dataset Builder
--------------------------------------------
Integrates all 5 AquaGuard data sources:
1. Sentinel-2
2. Landsat 8/9
3. Bhuvan (NRSC / ISRO)
4. India-WRIS
5. Rainfall / Climate (Open-Meteo ERA5 / CHIRPS)

Generates:
- CSV: data/datasets/water_body_features.csv
- GeoJSON: data/datasets/water_body_features.geojson
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from geospatial.climate.rainfall_pipeline import RainfallAcquisitionPipeline
from geospatial.gee.landsat_pipeline import LandsatAcquisitionPipeline
from geospatial.gee.sentinel2_pipeline import Sentinel2AcquisitionPipeline
from geospatial.indian_sources import BhuvanGeospatialClient, IndiaWRISClient, normalize_feature_collection


class AquaGuardDatasetBuilder:
    """Builder to integrate all 5 AquaGuard data sources into a unified feature dataset."""

    def __init__(self, project_id: Optional[str] = None):
        """Initialize all pipeline integration clients."""
        self.project_id = project_id
        self.s2_pipeline = Sentinel2AcquisitionPipeline(project_id=project_id, auto_init=True)
        self.landsat_pipeline = LandsatAcquisitionPipeline(project_id=project_id, auto_init=True)
        self.bhuvan_client = BhuvanGeospatialClient()
        self.wris_client = IndiaWRISClient()
        self.rainfall_pipeline = RainfallAcquisitionPipeline()

    def build_unified_dataset(
        self,
        geometry_file: Union[str, Path],
        start_year: int = 2021,
        end_year: int = 2026,
        season_months: Tuple[int, int] = (10, 11)
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Query and integrate Sentinel-2, Landsat, Bhuvan, India-WRIS, and Rainfall sources
        for target water body geometry over historical years.

        Returns:
            Tuple[List[Dict], Dict]: (normalized_records_list, raw_sources_metadata)
        """
        # Parse geometry & centroid
        lat, lon, wb_id, raw_geom = self.rainfall_pipeline.extract_centroid(geometry_file)
        props = raw_geom.get("properties", {}) if isinstance(raw_geom, dict) else {}
        name = props.get("name") or props.get("NAME") or "Hussain Sagar Lake"
        state = props.get("state") or props.get("STATE") or "Telangana"
        district = props.get("district") or props.get("DISTRICT") or "Hyderabad"

        print(f"\n[INFO] Building Unified AquaGuard Dataset for '{name}' ({wb_id})...")
        print(f"[INFO] Location: {district}, {state} | Centroid: Lat {lat:.4f}, Lon {lon:.4f}")

        # ---------------------------------------------------------------------
        # 1. Fetch Indian Geospatial Context (Bhuvan & India-WRIS)
        # ---------------------------------------------------------------------
        print("[1/4] Querying Bhuvan and India-WRIS geospatial context...")
        bhuvan_raw = self.bhuvan_client.query_water_bodies(state=state, district=district)
        bhuvan_norm = normalize_feature_collection(bhuvan_raw, default_source="Bhuvan WFS")
        landuse_info = bhuvan_norm[0].get("name") if bhuvan_norm else "Waterbodies - Lake/Pond"

        wris_raw = self.wris_client.query_water_bodies(state=state)
        wris_norm = normalize_feature_collection(wris_raw, default_source="India-WRIS WFS")

        # ---------------------------------------------------------------------
        # 2. Fetch Historical Rainfall Data (Open-Meteo / CHIRPS)
        # ---------------------------------------------------------------------
        print(f"[2/4] Fetching Daily Rainfall Data ({start_year}-01-01 to {end_year}-12-31)...")
        rainfall_map = {}
        try:
            _, rain_records = self.rainfall_pipeline.fetch_rainfall(
                latitude=lat,
                longitude=lon,
                start_date=f"{start_year}-01-01",
                end_date=f"{end_year}-12-31",
                water_body_id=wb_id
            )
            for r in rain_records:
                rainfall_map[r["date"]] = r["rainfall"]
        except Exception as rain_err:
            print(f"[WARNING] Rainfall query encountered error: {rain_err}")

        # ---------------------------------------------------------------------
        # 3. Query Sentinel-2 Satellite Multi-Year Observations
        # ---------------------------------------------------------------------
        print(f"[3/4] Querying Sentinel-2 Surface Reflectance ({start_year}-{end_year})...")
        s2_history = self.s2_pipeline.analyze_historical_trend(
            geometry=geometry_file,
            start_year=start_year,
            end_year=end_year,
            season_months=season_months,
            water_body_id=wb_id
        )

        # ---------------------------------------------------------------------
        # 4. Query Landsat 8/9 Multi-Year Observations
        # ---------------------------------------------------------------------
        print(f"[4/4] Querying Landsat Surface Reflectance ({start_year}-{end_year})...")
        landsat_history = self.landsat_pipeline.analyze_historical_trend(
            geometry=geometry_file,
            start_year=start_year,
            end_year=end_year,
            season_months=season_months,
            water_body_id=wb_id,
            satellites=("L8", "L9")
        )

        # ---------------------------------------------------------------------
        # Assemble Unified Feature Records
        # ---------------------------------------------------------------------
        processing_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        unified_records: List[Dict[str, Any]] = []

        # Process Sentinel-2 Records
        s2_recs = s2_history.get("records", [])
        for rec in s2_recs:
            obs_dt = rec.get("observation_date", "UNAVAILABLE")
            d_short = obs_dt[:10] if obs_dt != "UNAVAILABLE" else None
            matched_rain = rainfall_map.get(d_short) if d_short else None

            unif_rec = {
                "water_body_id": wb_id,
                "name": name,
                "state": state,
                "district": district,
                "geometry": raw_geom.get("geometry") if isinstance(raw_geom, dict) and "geometry" in raw_geom else raw_geom,
                "year": rec["year"],
                "observation_date": obs_dt,
                "satellite": "Sentinel-2B" if "S2B" in str(rec) else "Sentinel-2",
                "water_area_m2": rec["water_area_m2"],
                "water_area_ha": rec["water_area_ha"],
                "water_area_change": round(rec["water_area_m2"] - (rec["water_area_m2"] / (1 + rec["water_area_change_percent"]/100.0)), 2) if rec.get("water_area_change_percent") and rec.get("water_area_m2") else 0.0,
                "water_area_change_percent": rec["water_area_change_percent"],
                "mndwi": rec["mndwi"],
                "ndwi": rec["ndwi"],
                "ndvi": rec["ndvi"],
                "cloud_percentage": rec["cloud_percentage"],
                "rainfall": matched_rain,
                "landuse": landuse_info,
                "builtup": "Urban/Built-up Fringe",
                "source": rec["source"],
                "dataset_collection": Sentinel2AcquisitionPipeline.COLLECTION_ID,
                "acquisition_date": obs_dt,
                "processing_date": processing_date,
                "retrieved_at": processing_date,
                "data_quality": rec["quality"]
            }
            unified_records.append(unif_rec)

        # Process Landsat Records
        landsat_recs = landsat_history.get("records", [])
        for rec in landsat_recs:
            obs_dt = rec.get("observation_date", "UNAVAILABLE")
            d_short = obs_dt[:10] if obs_dt != "UNAVAILABLE" else None
            matched_rain = rainfall_map.get(d_short) if d_short else None

            unif_rec = {
                "water_body_id": wb_id,
                "name": name,
                "state": state,
                "district": district,
                "geometry": raw_geom.get("geometry") if isinstance(raw_geom, dict) and "geometry" in raw_geom else raw_geom,
                "year": rec["year"],
                "observation_date": obs_dt,
                "satellite": "Landsat-8 OLI" if "Landsat-8" in rec.get("source", "") else "Landsat-9 OLI-2",
                "water_area_m2": rec["water_area_m2"],
                "water_area_ha": rec["water_area_ha"],
                "water_area_change": 0.0,
                "water_area_change_percent": rec["water_area_change_percent"],
                "mndwi": rec["mndwi"],
                "ndwi": rec["ndwi"],
                "ndvi": rec["ndvi"],
                "cloud_percentage": rec["cloud_percentage"],
                "rainfall": matched_rain,
                "landuse": landuse_info,
                "builtup": "Urban/Built-up Fringe",
                "source": rec["source"],
                "dataset_collection": "LANDSAT/LC08/C02/T1_L2",
                "acquisition_date": obs_dt,
                "processing_date": processing_date,
                "retrieved_at": processing_date,
                "data_quality": rec["quality"]
            }
            unified_records.append(unif_rec)

        # Sort chronologically by year and source
        unified_records.sort(key=lambda r: (r["year"], r["source"]))

        raw_metadata = {
            "water_body_id": wb_id,
            "bhuvan_raw": bhuvan_raw,
            "wris_raw": wris_raw,
            "s2_history": s2_history,
            "landsat_history": landsat_history
        }

        return unified_records, raw_metadata

    @staticmethod
    def export_to_csv(records: List[Dict[str, Any]], csv_path: Union[str, Path]) -> Path:
        """Export unified feature records to CSV format matching exact required schema."""
        out_file = Path(csv_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "water_body_id",
            "name",
            "state",
            "district",
            "year",
            "observation_date",
            "satellite",
            "water_area_m2",
            "water_area_ha",
            "water_area_change",
            "water_area_change_percent",
            "mndwi",
            "ndwi",
            "ndvi",
            "cloud_percentage",
            "rainfall",
            "landuse",
            "builtup",
            "source",
            "dataset_collection",
            "acquisition_date",
            "processing_date",
            "retrieved_at",
            "data_quality"
        ]

        with open(out_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for rec in records:
                row = {k: (rec.get(k) if rec.get(k) is not None else "") for k in fieldnames}
                writer.writerow(row)

        print(f"[INFO] Unified CSV dataset saved: {out_file.resolve()}")
        return out_file.resolve()

    @staticmethod
    def export_to_geojson(records: List[Dict[str, Any]], geojson_path: Union[str, Path]) -> Path:
        """Export unified feature records as a GeoJSON FeatureCollection."""
        out_file = Path(geojson_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        features = []
        for idx, rec in enumerate(records):
            props = {k: v for k, v in rec.items() if k != "geometry"}
            geom = rec.get("geometry")
            feature = {
                "type": "Feature",
                "id": f"AQUAGUARD_{rec.get('water_body_id')}_{idx}",
                "properties": props,
                "geometry": geom
            }
            features.append(feature)

        fc = {
            "type": "FeatureCollection",
            "name": "AquaGuard_Unified_Water_Body_Features",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}},
            "features": features
        }

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(fc, f, indent=2)

        print(f"[INFO] Unified GeoJSON dataset saved: {out_file.resolve()}")
        return out_file.resolve()
