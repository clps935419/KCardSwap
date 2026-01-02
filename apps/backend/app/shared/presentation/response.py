"""
Response helper functions for creating standardized API responses.

These helpers ensure all API responses follow the envelope format:
{
    "data": <response_data> | null,
    "meta": <metadata> | null,
    "error": <error_object> | null
}
"""

from math import ceil
from typing import Any, Dict, List, Optional, TypeVar

from .schemas.response_envelope import (
    ErrorDetail,
    PaginationMeta,
    PaginatedResponse,
    ResponseEnvelope,
    SuccessResponse,
)

T = TypeVar("T")


def success(data: T) -> Dict[str, Any]:
    """
    Create a successful response with data.

    Args:
        data: Response data

    Returns:
        Dictionary with data, meta=None, error=None

    Example:
        >>> success({"id": "123", "name": "John"})
        {"data": {"id": "123", "name": "John"}, "meta": None, "error": None}
    """
    return SuccessResponse[type(data)](data=data, meta=None, error=None).model_dump()


def paginated(
    data: List[T],
    total: int,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """
    Create a paginated response with data and metadata.

    Args:
        data: List of items for current page
        total: Total number of items across all pages
        page: Current page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Dictionary with data, meta (pagination info), error=None

    Example:
        >>> paginated([{"id": "1"}, {"id": "2"}], total=100, page=1, page_size=20)
        {
            "data": [{"id": "1"}, {"id": "2"}],
            "meta": {"total": 100, "page": 1, "page_size": 20, "total_pages": 5},
            "error": None
        }
    """
    total_pages = ceil(total / page_size) if page_size > 0 else 0

    meta = PaginationMeta(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

    return PaginatedResponse[type(data[0]) if data else Any](
        data=data, meta=meta, error=None
    ).model_dump()


def error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create an error response.

    Note: This is typically used by error handlers/middleware.
    In application code, raise APIException instead.

    Args:
        code: Error code (e.g., "404_NOT_FOUND")
        message: Human-readable error message
        details: Optional additional error details

    Returns:
        Dictionary with data=None, meta=None, error

    Example:
        >>> error_response("404_NOT_FOUND", "Resource not found", {"resource_id": "123"})
        {
            "data": None,
            "meta": None,
            "error": {
                "code": "404_NOT_FOUND",
                "message": "Resource not found",
                "details": {"resource_id": "123"}
            }
        }
    """
    error = ErrorDetail(
        code=code,
        message=message,
        details=details or {},
    )

    return {"data": None, "meta": None, "error": error.model_dump()}
