"""
Custom exceptions and error handling utilities for the Miraikakaku API.
"""
import logging
from typing import Optional, Dict, Any
from enum import Enum
from fastapi import HTTPException


logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Error categories for better error classification."""
    VALIDATION = "validation"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    CACHE = "cache"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"


class APIError(Exception):
    """Base API error class with enhanced error context."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None
    ):
        self.message = message
        self.category = category
        self.status_code = status_code
        self.error_code = error_code or f"{category.value}_error"
        self.details = details or {}
        self.suggestion = suggestion
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format for API responses."""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "category": self.category.value,
            "details": self.details,
            "suggestion": self.suggestion
        }

    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail=self.to_dict()
        )


class ValidationError(APIError):
    """Error for validation failures."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            status_code=400,
            details=details,
            **kwargs
        )


class DatabaseError(APIError):
    """Error for database operations."""

    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if operation:
            details["operation"] = operation
        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE,
            status_code=500,
            suggestion="Please try again later or contact support if the issue persists.",
            details=details,
            **kwargs
        )


class ExternalAPIError(APIError):
    """Error for external API failures."""

    def __init__(self, message: str, service: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if service:
            details["service"] = service
        super().__init__(
            message=message,
            category=ErrorCategory.EXTERNAL_API,
            status_code=502,
            suggestion="External service is temporarily unavailable. Please try again later.",
            details=details,
            **kwargs
        )


class CacheError(APIError):
    """Error for cache operations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.CACHE,
            status_code=500,
            suggestion="Cache is temporarily unavailable. Data will be fetched directly.",
            **kwargs
        )


class RateLimitError(APIError):
    """Error for rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.RATE_LIMIT,
            status_code=429,
            suggestion="Please wait before making another request.",
            **kwargs
        )


class AuthenticationError(APIError):
    """Error for authentication failures."""

    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            status_code=401,
            suggestion="Please provide valid authentication credentials.",
            **kwargs
        )


class AuthorizationError(APIError):
    """Error for authorization failures."""

    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHORIZATION,
            status_code=403,
            suggestion="Contact administrator for access permissions.",
            **kwargs
        )


class StockNotFoundError(APIError):
    """Error for when stock symbol is not found."""

    def __init__(self, symbol: str, **kwargs):
        super().__init__(
            message=f"Stock symbol '{symbol}' not found or not supported",
            category=ErrorCategory.BUSINESS_LOGIC,
            status_code=404,
            error_code="stock_not_found",
            details={"symbol": symbol},
            suggestion="Please check the stock symbol and try again.",
            **kwargs
        )


def handle_service_error(
    error: Exception,
    operation: str,
    context: Optional[Dict[str, Any]] = None,
    fallback_message: str = "Service operation failed"
) -> APIError:
    """
    Convert various exception types to appropriate APIError instances.

    Args:
        error: The original exception
        operation: Description of the operation that failed
        context: Additional context information
        fallback_message: Default message if error type is unknown

    Returns:
        APIError instance
    """
    context = context or {}

    # If it's already an APIError, return as-is
    if isinstance(error, APIError):
        return error

    # Log the original error
    logger.error(
        f"Error in {operation}: {type(error).__name__}: {str(error)}",
        extra={"context": context, "error_type": type(error).__name__},
        exc_info=True
    )

    # Convert common exception types
    if "database" in str(error).lower() or "connection" in str(error).lower():
        return DatabaseError(
            message=f"Database error during {operation}",
            operation=operation,
            details={"original_error": str(error), **context}
        )

    if "timeout" in str(error).lower() or "network" in str(error).lower():
        return ExternalAPIError(
            message=f"Network timeout during {operation}",
            details={"original_error": str(error), **context}
        )

    if "permission" in str(error).lower() or "forbidden" in str(error).lower():
        return AuthorizationError(
            message=f"Permission denied for {operation}",
            details={"original_error": str(error), **context}
        )

    # Default to system error
    return APIError(
        message=f"{fallback_message}: {str(error)}",
        category=ErrorCategory.SYSTEM,
        status_code=500,
        details={"original_error": str(error), "operation": operation, **context}
    )


def create_error_response(
    error: Exception,
    operation: str = "operation",
    include_traceback: bool = False
) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.

    Args:
        error: The exception to convert
        operation: Description of the failed operation
        include_traceback: Whether to include traceback (for debugging)

    Returns:
        Dictionary with error details
    """
    if isinstance(error, APIError):
        response = error.to_dict()
    else:
        api_error = handle_service_error(error, operation)
        response = api_error.to_dict()

    if include_traceback:
        import traceback
        response["traceback"] = traceback.format_exc()

    return response