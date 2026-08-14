"""
AquaGuard - Indian Geospatial Data Schema Normalizer
---------------------------------------------------
Normalizes raw vector features from Bhuvan (NRSC/ISRO) and India-WRIS (Ministry of Jal Shakti)
into the unified AquaGuard water-body schema.
"""

from datetime import datetime
from typing import Any, Dict, List


def normalize_to_aquaguard_schema(
    raw_feature: Dict[str, Any],
    default_source: str = "Indian Geospatial Source",
    default_crs: str = "EPSG:4326"
) -> Dict[str, Any]:
    """
    Transform a raw Bhuvan or India-WRIS GeoJSON Feature into the AquaGuard standard schema.

    Schema:
    - source
    - source_id
    - water_body_id
    - name
    - state
    - district
    - geometry
    - CRS
    - area
    - retrieval_date
    """
    props = raw_feature.get("properties", {})
    feature_id = raw_feature.get("id") or props.get("SOURCE_ID") or props.get("id") or "IND_WB_000"

    source_name = props.get("SOURCE") or default_source
    source_id = str(props.get("SOURCE_ID") or feature_id)
    name = (
        props.get("NAME")
        or props.get("name")
        or props.get("WB_NAME")
        or props.get("RESERVOIR_NAME")
        or props.get("LU_CATEGORY")
        or "Unnamed Water Body"
    )
    state = props.get("STATE") or props.get("state") or "India"
    district = props.get("DISTRICT") or props.get("district") or "Unknown"

    # Area resolution: convert to m² if provided in hectares or acres
    area_sq_m = None
    if "AREA_SQ_M" in props and props["AREA_SQ_M"] is not None:
        area_sq_m = float(props["AREA_SQ_M"])
    elif "AREA_HA" in props and props["AREA_HA"] is not None:
        area_sq_m = float(props["AREA_HA"]) * 10000.0
    elif "area_ha" in props and props["area_ha"] is not None:
        area_sq_m = float(props["area_ha"]) * 10000.0

    retrieval_date = (
        props.get("RETRIEVAL_DATE")
        or props.get("retrieval_date")
        or datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    geometry = raw_feature.get("geometry")

    return {
        "source": source_name,
        "source_id": source_id,
        "water_body_id": f"WB_IND_{source_id}",
        "name": name,
        "state": state,
        "district": district,
        "geometry": geometry,
        "CRS": default_crs,
        "area": round(area_sq_m, 2) if area_sq_m is not None else None,
        "retrieval_date": retrieval_date
    }


def normalize_feature_collection(
    raw_collection: Dict[str, Any],
    default_source: str = "Indian Geospatial Source"
) -> List[Dict[str, Any]]:
    """Normalize an entire GeoJSON FeatureCollection into a list of AquaGuard water body records."""
    features = raw_collection.get("features", [])
    normalized_records = []
    for feat in features:
        normalized_records.append(normalize_to_aquaguard_schema(feat, default_source=default_source))
    return normalized_records
