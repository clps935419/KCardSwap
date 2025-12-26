"""API Exception classes.

This module provides custom exception classes for API error responses.
"""

from typing import Any, Dict, Optional


class APIException(Exception):  # noqa: N818
    """Base API exception class.

    All API exceptions should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize API exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}


class BadRequestException(APIException):
    """400 Bad Request - Invalid request data."""

    def __init__(
        self, message: str = "Bad request", details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code="400_VALIDATION_FAILED",
            details=details,
        )


class UnauthorizedException(APIException):
    """401 Unauthorized - Authentication required."""

    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=401,
            error_code="401_UNAUTHORIZED",
            details=details,
        )


class ForbiddenException(APIException):
    """403 Forbidden - Insufficient permissions."""

    def __init__(
        self, message: str = "Forbidden", details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code="403_FORBIDDEN",
            details=details,
        )


class NotFoundException(APIException):
    """404 Not Found - Resource not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=404,
            error_code="404_NOT_FOUND",
            details=details,
        )


class UnprocessableEntityException(APIException):
    """422 Unprocessable Entity - Request validation failed or limit exceeded."""

    def __init__(
        self,
        message: str = "Unprocessable entity",
        error_code: str = "422_LIMIT_EXCEEDED",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message, status_code=422, error_code=error_code, details=details
        )


class RateLimitException(APIException):
    """429 Too Many Requests - Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=429,
            error_code="429_RATE_LIMIT_EXCEEDED",
            details=details,
        )


class ConflictException(APIException):
    """409 Conflict - Resource conflict."""

    def __init__(
        self,
        error_code: str = "409_CONFLICT",
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message, status_code=409, error_code=error_code, details=details
        )


class InternalServerException(APIException):
    """500 Internal Server Error - Server error."""

    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=500,
            error_code="500_INTERNAL_ERROR",
            details=details,
        )


class ServiceUnavailableException(APIException):
    """503 Service Unavailable - External service unavailable."""

    def __init__(
        self,
        error_code: str = "503_SERVICE_UNAVAILABLE",
        message: str = "Service temporarily unavailable",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=503,
            error_code=error_code,
            details=details,
        )


# Alias for compatibility
ValidationException = BadRequestException
