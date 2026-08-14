"""
AquaGuard Common Pydantic Schemas
---------------------------------
Standard response envelopes, pagination, and error structures.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class APIError(BaseModel):
    """Structured error payload."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class APIResponse(BaseModel, Generic[T]):
    """Consistent API response envelope."""
    success: bool = True
    data: Optional[T] = None
    message: str = "Operation completed successfully"
    error: Optional[APIError] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Consistent paginated response envelope."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
