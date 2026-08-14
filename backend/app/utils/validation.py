"""
AquaGuard Validation Utilities
------------------------------
Input parameter validation for dates, coordinates, and query ranges.
"""

from datetime import datetime
from typing import Tuple
from fastapi import HTTPException, status


def validate_coordinates(latitude: float, longitude: float) -> Tuple[float, float]:
    """Validate latitude and longitude values."""
    if not (-90.0 <= latitude <= 90.0):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid latitude '{latitude}'. Must be between -90.0 and 90.0."
        )
    if not (-180.0 <= longitude <= 180.0):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid longitude '{longitude}'. Must be between -180.0 and 180.0."
        )
    return latitude, longitude


def validate_date_range(start_date: str, end_date: str) -> Tuple[datetime, datetime]:
    """Validate YYYY-MM-DD date range strings."""
    try:
        s_dt = datetime.strptime(start_date, "%Y-%m-%d")
        e_dt = datetime.strptime(end_date, "%Y-%m-%d")
        if s_dt > e_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Start date ({start_date}) cannot be after end date ({end_date})."
            )
        return s_dt, e_dt
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: {err}. Use YYYY-MM-DD."
        ) from err
