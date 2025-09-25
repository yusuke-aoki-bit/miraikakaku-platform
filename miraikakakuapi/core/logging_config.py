"""
Centralized logging configuration for the Miraikakaku API.
"""
import logging
import logging.config
import sys
from typing import Dict, Any
from datetime import datetime
import json
import os


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra"):
            log_entry["extra"] = record.extra

        # Add context fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", "pathname",
                          "filename", "module", "exc_info", "exc_text", "stack_info",
                          "lineno", "funcName", "created", "msecs", "relativeCreated",
                          "thread", "threadName", "processName", "process", "getMessage"]:
                if not key.startswith("_"):
                    log_entry[key] = value

        return json.dumps(log_entry, ensure_ascii=False)


class HealthCheckFilter(logging.Filter):
    """Filter to reduce noise from health check endpoints."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter out health check requests in production."""
        message = record.getMessage()
        if any(path in message.lower() for path in ["/health", "/api/system/health"]):
            return record.levelno >= logging.WARNING
        return True


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    include_health_checks: bool = False
) -> None:
    """
    Setup centralized logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type ("json" or "text")
        include_health_checks: Whether to include health check logs
    """
    log_level = getattr(logging, level.upper())

    # Configure formatters
    formatters = {
        "json": {
            "()": JSONFormatter,
        },
        "text": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(module)s:%(funcName)s:%(lineno)d]",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    }

    # Configure handlers
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": format_type,
            "stream": sys.stdout
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": logging.ERROR,
            "formatter": format_type,
            "filename": "logs/error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        }
    }

    # Add filters if needed
    if not include_health_checks:
        handlers["console"]["filters"] = ["health_check"]
        handlers["error_file"]["filters"] = ["health_check"]

    # Configure root logger
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "filters": {
            "health_check": {
                "()": HealthCheckFilter,
            }
        },
        "handlers": handlers,
        "root": {
            "level": log_level,
            "handlers": ["console"]
        },
        "loggers": {
            "miraikakaku": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": logging.INFO,
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": logging.WARNING if not include_health_checks else logging.INFO,
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": logging.WARNING,
                "handlers": ["console"],
                "propagate": False
            },
            "asyncpg": {
                "level": logging.WARNING,
                "handlers": ["console"],
                "propagate": False
            }
        }
    }

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Add error file handler in production
    if not os.getenv("DEBUG", "").lower() == "true":
        logging_config["root"]["handlers"].append("error_file")
        logging_config["loggers"]["miraikakaku"]["handlers"].append("error_file")

    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_performance(func_name: str, duration: float, **kwargs) -> None:
    """
    Log performance metrics for functions.

    Args:
        func_name: Name of the function being measured
        duration: Duration in seconds
        **kwargs: Additional context information
    """
    logger = get_logger("performance")

    log_data = {
        "function": func_name,
        "duration_ms": round(duration * 1000, 2),
        "performance_metric": True,
        **kwargs
    }

    if duration > 1.0:  # Log as warning if > 1 second
        logger.warning(f"Slow operation: {func_name}", extra=log_data)
    else:
        logger.info(f"Performance: {func_name}", extra=log_data)


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    user_id: str = None,
    **kwargs
) -> None:
    """
    Log API request information.

    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration: Request duration in seconds
        user_id: User identifier if authenticated
        **kwargs: Additional context
    """
    logger = get_logger("api.requests")

    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration * 1000, 2),
        "api_request": True,
        **kwargs
    }

    if user_id:
        log_data["user_id"] = user_id

    if status_code >= 500:
        logger.error(f"API Error: {method} {path}", extra=log_data)
    elif status_code >= 400:
        logger.warning(f"API Client Error: {method} {path}", extra=log_data)
    else:
        logger.info(f"API Request: {method} {path}", extra=log_data)


def log_business_event(
    event_type: str,
    details: Dict[str, Any],
    user_id: str = None,
    symbol: str = None
) -> None:
    """
    Log business events for analytics and monitoring.

    Args:
        event_type: Type of business event
        details: Event details
        user_id: User identifier if applicable
        symbol: Stock symbol if applicable
    """
    logger = get_logger("business.events")

    log_data = {
        "event_type": event_type,
        "details": details,
        "business_event": True
    }

    if user_id:
        log_data["user_id"] = user_id
    if symbol:
        log_data["symbol"] = symbol

    logger.info(f"Business Event: {event_type}", extra=log_data)


def log_external_api_call(
    service: str,
    endpoint: str,
    method: str,
    status_code: int,
    duration: float,
    **kwargs
) -> None:
    """
    Log external API calls for monitoring and debugging.

    Args:
        service: External service name
        endpoint: API endpoint called
        method: HTTP method
        status_code: Response status code
        duration: Call duration in seconds
        **kwargs: Additional context
    """
    logger = get_logger("external.api")

    log_data = {
        "service": service,
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "duration_ms": round(duration * 1000, 2),
        "external_api_call": True,
        **kwargs
    }

    if status_code >= 500:
        logger.error(f"External API Error: {service}", extra=log_data)
    elif status_code >= 400:
        logger.warning(f"External API Client Error: {service}", extra=log_data)
    else:
        logger.info(f"External API Call: {service}", extra=log_data)


# Performance decorator
import functools
import time
from typing import Callable, Any


def log_execution_time(
    include_args: bool = False,
    log_level: str = "INFO"
) -> Callable:
    """
    Decorator to log function execution time.

    Args:
        include_args: Whether to include function arguments in logs
        log_level: Logging level for performance logs

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                log_data = {"args": str(args), "kwargs": str(kwargs)} if include_args else {}
                log_performance(func.__name__, duration, **log_data)

                return result
            except Exception as e:
                duration = time.time() - start_time
                logger = get_logger("performance")
                logger.error(
                    f"Function {func.__name__} failed after {duration:.3f}s: {str(e)}",
                    extra={"function": func.__name__, "duration_ms": round(duration * 1000, 2), "error": str(e)}
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                log_data = {"args": str(args), "kwargs": str(kwargs)} if include_args else {}
                log_performance(func.__name__, duration, **log_data)

                return result
            except Exception as e:
                duration = time.time() - start_time
                logger = get_logger("performance")
                logger.error(
                    f"Function {func.__name__} failed after {duration:.3f}s: {str(e)}",
                    extra={"function": func.__name__, "duration_ms": round(duration * 1000, 2), "error": str(e)}
                )
                raise

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator