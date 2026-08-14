"""
AquaGuard - Authoritative Daily Rainfall & Climate Data Acquisition Pipeline
-----------------------------------------------------------------------------
Provides automated access to daily precipitation data from authoritative open providers:
1. Primary: Open-Meteo ERA5 / ECMWF Archive REST API (https://archive-api.open-meteo.com)
2. Fallback: Google Earth Engine CHIRPS Daily Collection (UCSB-CHG/CHIRPS/DAILY)

Stores normalized rainfall records:
- water_body_id, date, latitude, longitude, rainfall (mm), unit, source, retrieved_at
"""

import csv
import json
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import ee
except ImportError:
    ee = None


class RainfallAcquisitionPipeline:
    """Acquisition pipeline for daily rainfall and climate data."""

    OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
    CHIRPS_COLLECTION_ID = "UCSB-CHG/CHIRPS/DAILY"

    def __init__(self, timeout: int = 4):
        """Initialize the rainfall pipeline."""
        self.timeout = timeout

    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> Tuple[float, float]:
        """Validate latitude and longitude ranges."""
        if not isinstance(latitude, (int, float)) or not (-90.0 <= latitude <= 90.0):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90.0 and 90.0.")
        if not isinstance(longitude, (int, float)) or not (-180.0 <= longitude <= 180.0):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180.0 and 180.0.")
        return float(latitude), float(longitude)

    @staticmethod
    def validate_dates(start_date: str, end_date: str) -> Tuple[datetime, datetime]:
        """Validate YYYY-MM-DD date strings."""
        try:
            s_dt = datetime.strptime(start_date, "%Y-%m-%d")
            e_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if s_dt > e_dt:
                raise ValueError(f"Start date ({start_date}) cannot be after end date ({end_date}).")
            return s_dt, e_dt
        except ValueError as err:
            raise ValueError(f"Invalid date format or range: {err}. Use YYYY-MM-DD.") from err

    @classmethod
    def extract_centroid(cls, geometry_input: Union[Dict, str, Path, List, Tuple]) -> Tuple[float, float, str, Dict]:
        """
        Extract representative centroid (latitude, longitude) and water_body_id from geometry input.

        Returns:
            Tuple[float, float, str, Dict]: (latitude, longitude, water_body_id, raw_geojson)
        """
        geojson_dict = None
        water_body_id = "WB_001"

        if isinstance(geometry_input, (str, Path)):
            path = Path(geometry_input)
            if not path.exists():
                raise FileNotFoundError(f"Geometry file not found: {path}")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("type") == "Feature":
                    geojson_dict = data
                    props = data.get("properties", {})
                    water_body_id = props.get("water_body_id") or props.get("name") or "WB_001"
                else:
                    geojson_dict = data

        elif isinstance(geometry_input, dict):
            geojson_dict = geometry_input
            if geometry_input.get("type") == "Feature":
                props = geometry_input.get("properties", {})
                water_body_id = props.get("water_body_id") or props.get("name") or "WB_001"

        elif isinstance(geometry_input, (list, tuple)):
            if len(geometry_input) == 2:
                # Direct [lon, lat] point
                lon, lat = geometry_input
                return cls.validate_coordinates(lat, lon) + (water_body_id, {"type": "Point", "coordinates": [lon, lat]})
            elif len(geometry_input) == 4:
                min_lon, min_lat, max_lon, max_lat = geometry_input
                center_lon = (min_lon + max_lon) / 2.0
                center_lat = (min_lat + max_lat) / 2.0
                return cls.validate_coordinates(center_lat, center_lon) + (
                    water_body_id,
                    {"type": "Polygon", "coordinates": [[[min_lon, min_lat], [max_lon, min_lat], [max_lon, max_lat], [min_lon, max_lat], [min_lon, min_lat]]]}
                )

        raw_geom = geojson_dict.get("geometry") if isinstance(geojson_dict, dict) and "geometry" in geojson_dict else geojson_dict

        if not raw_geom or "coordinates" not in raw_geom:
            raise ValueError(f"Invalid geometry input for centroid calculation: {geometry_input}")

        geom_type = raw_geom.get("type")
        coords = raw_geom.get("coordinates")

        if geom_type == "Point":
            lon, lat = coords[0], coords[1]
        elif geom_type in ("Polygon", "MultiPolygon"):
            # Compute average coordinate of polygon outer ring
            ring = coords[0] if geom_type == "Polygon" else coords[0][0]
            lons = [p[0] for p in ring]
            lats = [p[1] for p in ring]
            lon = sum(lons) / len(lons)
            lat = sum(lats) / len(lats)
        else:
            raise ValueError(f"Unsupported geometry type for centroid calculation: {geom_type}")

        lat, lon = cls.validate_coordinates(lat, lon)
        return lat, lon, water_body_id, geojson_dict

    def fetch_rainfall_open_meteo(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        water_body_id: str = "WB_001"
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Query Open-Meteo ERA5 Historical Weather REST API for daily precipitation.

        Returns:
            Tuple[Dict, List[Dict]]: (raw_api_response, normalized_records)
        """
        lat, lon = self.validate_coordinates(latitude, longitude)
        self.validate_dates(start_date, end_date)

        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        effective_end_date = min(end_date, today_str)

        params = {
            "latitude": str(lat),
            "longitude": str(lon),
            "start_date": start_date,
            "end_date": effective_end_date,
            "daily": "precipitation_sum",
            "timezone": "auto"
        }

        url = f"{self.OPEN_METEO_ARCHIVE_URL}?{urllib.parse.urlencode(params)}"
        print(f"[INFO] Querying Open-Meteo ERA5 REST API: {url[:75]}...")

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "AquaGuard/1.0 Climate Data Client",
                "Accept": "application/json"
            }
        )

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            content = resp.read().decode("utf-8")
            raw_json = json.loads(content)

        daily_data = raw_json.get("daily", {})
        times = daily_data.get("time", [])
        precip_sums = daily_data.get("precipitation_sum", [])

        retrieved_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        normalized_records = []

        for date_str, precip in zip(times, precip_sums):
            precip_val = round(float(precip), 2) if precip is not None else None
            record = {
                "water_body_id": water_body_id,
                "date": date_str,
                "latitude": lat,
                "longitude": lon,
                "rainfall": precip_val,
                "unit": "mm",
                "source": "Open-Meteo ERA5",
                "retrieved_at": retrieved_at
            }
            normalized_records.append(record)

        return raw_json, normalized_records

    def fetch_rainfall_gee_chirps(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        water_body_id: str = "WB_001"
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Fallback query using Google Earth Engine CHIRPS Daily collection (UCSB-CHG/CHIRPS/DAILY)."""
        lat, lon = self.validate_coordinates(latitude, longitude)
        self.validate_dates(start_date, end_date)

        if ee is None or not ee.data._credentials:
            raise RuntimeError("Earth Engine is not initialized or authenticated for CHIRPS fallback.")

        print(f"[INFO] Querying GEE CHIRPS Daily Collection: {self.CHIRPS_COLLECTION_ID}")
        point = ee.Geometry.Point([lon, lat])

        col = (
            ee.ImageCollection(self.CHIRPS_COLLECTION_ID)
            .filterBounds(point)
            .filterDate(start_date, end_date)
            .sort("system:time_start", True)
        )

        def extract_point_rainfall(img):
            precip = img.select("precipitation").reduceRegion(
                reducer=ee.Reducer.first(),
                geometry=point,
                scale=5500
            ).get("precipitation")
            return ee.Feature(None, {
                "date": img.date().format("YYYY-MM-dd"),
                "precipitation": precip
            })

        features = col.map(extract_point_rainfall).getInfo()["features"]

        retrieved_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        normalized_records = []

        for feat in features:
            props = feat["properties"]
            precip = props.get("precipitation")
            precip_val = round(float(precip), 2) if precip is not None else None
            record = {
                "water_body_id": water_body_id,
                "date": props["date"],
                "latitude": lat,
                "longitude": lon,
                "rainfall": precip_val,
                "unit": "mm",
                "source": "CHIRPS Daily GEE",
                "retrieved_at": retrieved_at
            }
            normalized_records.append(record)

        raw_json = {"collection": self.CHIRPS_COLLECTION_ID, "features_count": len(features)}
        return raw_json, normalized_records

    def fetch_rainfall(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        water_body_id: str = "WB_001"
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Fetch daily rainfall data for target coordinates over date range.
        Tries Open-Meteo ERA5 API first; falls back to GEE CHIRPS if network fails.
        """
        try:
            return self.fetch_rainfall_open_meteo(latitude, longitude, start_date, end_date, water_body_id)
        except Exception as err:
            print(f"[WARNING] Primary Open-Meteo REST API failed ({err}). Attempting GEE CHIRPS fallback...")
            return self.fetch_rainfall_gee_chirps(latitude, longitude, start_date, end_date, water_body_id)

    def fetch_rainfall_for_water_body(
        self,
        geometry_input: Union[Dict, str, Path],
        start_date: str,
        end_date: str
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Fetch daily rainfall for a water body GeoJSON geometry or file path."""
        lat, lon, wb_id, _ = self.extract_centroid(geometry_input)
        print(f"[INFO] Target Water Body ID: '{wb_id}' | Centroid: Lat {lat:.4f}, Lon {lon:.4f}")
        return self.fetch_rainfall(latitude=lat, longitude=lon, start_date=start_date, end_date=end_date, water_body_id=wb_id)

    @staticmethod
    def export_to_csv(records: List[Dict[str, Any]], csv_path: Union[str, Path]) -> Path:
        """
        Export daily rainfall records to CSV matching exact required schema:
        water_body_id, date, latitude, longitude, rainfall, unit, source, retrieved_at
        """
        out_file = Path(csv_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "water_body_id",
            "date",
            "latitude",
            "longitude",
            "rainfall",
            "unit",
            "source",
            "retrieved_at"
        ]

        with open(out_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for rec in records:
                row = {k: (rec.get(k) if rec.get(k) is not None else "") for k in fieldnames}
                writer.writerow(row)

        print(f"[INFO] Rainfall dataset saved to CSV: {out_file.resolve()}")
        return out_file.resolve()

    @staticmethod
    def save_json(data: Dict[str, Any], json_path: Union[str, Path]) -> Path:
        """Save rainfall payload to JSON file."""
        out_file = Path(json_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"[INFO] Rainfall payload saved to JSON: {out_file.resolve()}")
        return out_file.resolve()
