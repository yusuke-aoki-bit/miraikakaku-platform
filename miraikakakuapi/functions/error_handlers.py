"""
Centralized error handling for the MiraiKakaku API.
"""
import logging
import traceback
from typing import Union, Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
import asyncio


logger = logging.getLogger("miraikakaku.errors")


class MiraikakakuError(Exception):
    """Base exception class for MiraiKakaku specific errors."""

    def __init__(self, message: str, error_code: str = None, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "MIRAIKAKAKU_ERROR"
        self.status_code = status_code


class DataFetchError(MiraikakakuError):
    """Error when fetching external data fails."""

    def __init__(self, message: str = "Failed to fetch data from external source"):
        super().__init__(message, "DATA_FETCH_ERROR", 503)


class PredictionError(MiraikakakuError):
    """Error when prediction generation fails."""

    def __init__(self, message: str = "Failed to generate prediction"):
        super().__init__(message, "PREDICTION_ERROR", 500)


class ValidationError(MiraikakakuError):
    """Error when data validation fails."""

    def __init__(self, message: str = "Data validation failed"):
        super().__init__(message, "VALIDATION_ERROR", 422)


class DatabaseError(MiraikakakuError):
    """Error when database operations fail."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR", 503)


class RateLimitError(MiraikakakuError):
    """Error when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT_ERROR", 429)


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 500,
    details: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a standardized error response."""
    response = {
        "error": {
            "code": error_code,
            "message": message,
            "status_code": status_code
        }
    }

    if details:
        response["error"]["details"] = details

    return response


async def miraikakaku_exception_handler(request: Request, exc: MiraikakakuError) -> JSONResponse:
    """Handle MiraiKakaku specific exceptions."""
    logger.error(
        f"MiraiKakaku error: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc.error_code, exc.message, exc.status_code)
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(
        f"Validation error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "validation_errors": exc.errors() if hasattr(exc, 'errors') else str(exc)
        }
    )

    details = {"validation_errors": exc.errors()} if hasattr(exc, 'errors') else None

    return JSONResponse(
        status_code=422,
        content=create_error_response(
            "VALIDATION_ERROR",
            "Input validation failed",
            422,
            details
        )
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors."""
    error_message = "Database operation failed"
    status_code = 503

    # Specific handling for different database errors
    if isinstance(exc, IntegrityError):
        error_message = "Data integrity constraint violation"
        status_code = 409
    elif isinstance(exc, OperationalError):
        error_message = "Database connection or operation error"
        status_code = 503

    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "error_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )

    return JSONResponse(
        status_code=status_code,
        content=create_error_response(
            "DATABASE_ERROR",
            error_message,
            status_code
        )
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    logger.info(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            f"HTTP_{exc.status_code}",
            exc.detail,
            exc.status_code
        )
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any uncaught exceptions."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "error_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )

    # Don't expose internal error details in production
    import os
    if os.getenv("DEBUG", "").lower() != "true":
        message = "An internal server error occurred"
    else:
        message = str(exc)

    return JSONResponse(
        status_code=500,
        content=create_error_response(
            "INTERNAL_ERROR",
            message,
            500
        )
    )


async def timeout_exception_handler(request: Request, exc: asyncio.TimeoutError) -> JSONResponse:
    """Handle timeout errors."""
    logger.warning(
        f"Request timeout: {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )

    return JSONResponse(
        status_code=504,
        content=create_error_response(
            "TIMEOUT_ERROR",
            "Request timeout - the operation took too long to complete",
            504
        )
    )


def setup_error_handlers(app):
    """Setup all error handlers for the FastAPI app."""
    app.add_exception_handler(MiraikakakuError, miraikakaku_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(asyncio.TimeoutError, timeout_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Error handlers configured successfully")


# Utility functions for common error scenarios
def handle_external_api_error(service_name: str, error: Exception) -> DataFetchError:
    """Handle errors from external APIs."""
    logger.error(f"External API error from {service_name}: {str(error)}")
    return DataFetchError(f"Failed to fetch data from {service_name}")


def handle_prediction_error(model_name: str, error: Exception) -> PredictionError:
    """Handle prediction generation errors."""
    logger.error(f"Prediction error with {model_name}: {str(error)}")
    return PredictionError(f"Failed to generate prediction using {model_name}")


def validate_stock_symbol(symbol: str) -> None:
    """Validate stock symbol format."""
    if not symbol or len(symbol) > 10:
        raise ValidationError(f"Invalid stock symbol: {symbol}")

    if not symbol.isalnum():
        raise ValidationError(f"Stock symbol must contain only alphanumeric characters: {symbol}")


def validate_date_range(start_date: str, end_date: str) -> None:
    """Validate date range parameters."""
    try:
        from datetime import datetime
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        if start >= end:
            raise ValidationError("Start date must be before end date")

        # Check if date range is too large (more than 5 years)
        max_days = 5 * 365
        if (end - start).days > max_days:
            raise ValidationError("Date range cannot exceed 5 years")

    except ValueError as e:
        raise ValidationError(f"Invalid date format: {str(e)}")


def safe_execute(func, *args, **kwargs):
    """Safely execute a function with error handling."""
    try:
        return func(*args, **kwargs)
    except MiraikakakuError:
        raise  # Re-raise our custom errors
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {str(e)}")
        raise MiraikakakuError(f"Operation failed in {func.__name__}")


async def safe_execute_async(func, *args, **kwargs):
    """Safely execute an async function with error handling."""
    try:
        return await func(*args, **kwargs)
    except MiraikakakuError:
        raise  # Re-raise our custom errors
    except asyncio.TimeoutError:
        raise  # Let timeout handler deal with this
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {str(e)}")
        raise MiraikakakuError(f"Async operation failed in {func.__name__}")