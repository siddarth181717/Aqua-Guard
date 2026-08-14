"""
AquaGuard Climate & Hydrometeorological Integration Package
----------------------------------------------------------
Provides daily precipitation and climate data acquisition via Open-Meteo ERA5 API and GEE CHIRPS.
"""

from .rainfall_pipeline import RainfallAcquisitionPipeline

__all__ = ["RainfallAcquisitionPipeline"]
