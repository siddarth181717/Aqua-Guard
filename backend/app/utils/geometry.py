"""
AquaGuard Geometry Utilities
----------------------------
Converts between GeoJSON, WKT, Shapely geometries, and calculates geodesic distances.
"""

import json
import math
from typing import Any, Dict, List, Tuple, Union
from shapely.geometry import shape, mapping, Point, Polygon


def geojson_to_shapely(geojson_dict: Dict[str, Any]):
    """Convert GeoJSON dictionary to Shapely geometry."""
    return shape(geojson_dict)


def shapely_to_geojson(geom) -> Dict[str, Any]:
    """Convert Shapely geometry to GeoJSON dictionary."""
    return mapping(geom)


def extract_centroid(geojson_dict: Dict[str, Any]) -> Tuple[float, float]:
    """
    Extract centroid (latitude, longitude) from GeoJSON geometry.

    Returns:
        Tuple[float, float]: (latitude, longitude)
    """
    sh_geom = shape(geojson_dict)
    c = sh_geom.centroid
    return float(c.y), float(c.x)


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate geodesic Haversine distance in km between two lat/lon points.

    Returns:
        float: Distance in kilometers.
    """
    r = 6371.0  # Earth's radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return round(r * c, 3)
