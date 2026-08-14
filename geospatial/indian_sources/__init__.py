"""
AquaGuard Indian Geospatial Data Integration Package
---------------------------------------------------
Provides official clients for Bhuvan (NRSC / ISRO) and India-WRIS (Ministry of Jal Shakti)
and schema normalization utilities.
"""

from .bhuvan import BhuvanGeospatialClient
from .india_wris import IndiaWRISClient
from .schema_normalizer import normalize_to_aquaguard_schema, normalize_feature_collection

__all__ = [
    "BhuvanGeospatialClient",
    "IndiaWRISClient",
    "normalize_to_aquaguard_schema",
    "normalize_feature_collection"
]
