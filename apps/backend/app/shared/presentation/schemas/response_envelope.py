"""
Response envelope schemas for standardized API responses.

All API endpoints should return responses in the following format:
{
    "data": <response_data> | null,
    "meta": <metadata> | null,
    "error": <error_object> | null
}
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

# Type variable for generic response data
T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Error detail schema."""

    code: str = Field(..., description="Error code (e.g., '400_VALIDATION_FAILED')")
    message: str = Field(..., description="Human-readable error message")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional error details"
    )


class PaginationMeta(BaseModel):
    """Pagination metadata schema."""

    total: int = Field(..., description="Total number of items", ge=0)
    page: int = Field(..., description="Current page number (1-indexed)", ge=1)
    page_size: int = Field(..., description="Number of items per page", ge=1)
    total_pages: int = Field(..., description="Total number of pages", ge=0)


class ResponseEnvelope(BaseModel, Generic[T]):
    """
    Generic response envelope for all API responses.

    Success responses have data and error=None.
    Error responses have data=None and error with details.
    Paginated responses have data, meta with pagination, and error=None.
    """

    data: Optional[T] = Field(None, description="Response data (null on error)")
    meta: Optional[PaginationMeta] = Field(
        None, description="Metadata (e.g., pagination info)"
    )
    error: Optional[ErrorDetail] = Field(None, description="Error details (null on success)")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "examples": [
                {
                    "data": {"id": "123", "name": "Example"},
                    "meta": None,
                    "error": None,
                },
                {
                    "data": None,
                    "meta": None,
                    "error": {
                        "code": "404_NOT_FOUND",
                        "message": "Resource not found",
                        "details": {},
                    },
                },
            ]
        }


class SuccessResponse(ResponseEnvelope[T], Generic[T]):
    """Success response with data."""

    data: T
    error: None = None


class PaginatedResponse(ResponseEnvelope[List[T]], Generic[T]):
    """Paginated response with data and metadata."""

    data: List[T]
    meta: PaginationMeta
    error: None = None


class ErrorResponse(ResponseEnvelope[None]):
    """Error response with error details."""

    data: None = None
    meta: None = None
    error: ErrorDetail
