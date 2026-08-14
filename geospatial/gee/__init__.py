"""
Google Earth Engine (GEE) integration package for AquaGuard.
Provides acquisition and processing pipelines for Sentinel-2 and Landsat.
"""

from .sentinel2_pipeline import Sentinel2AcquisitionPipeline
from .landsat_pipeline import LandsatAcquisitionPipeline

__all__ = [
    "Sentinel2AcquisitionPipeline",
    "LandsatAcquisitionPipeline"
]
