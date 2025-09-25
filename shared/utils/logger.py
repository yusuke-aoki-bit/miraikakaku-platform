"""
Centralized logging configuration for MiraiKakaku system
"""
import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


class MiraiKakakuLogger:
    """Centralized logger for MiraiKakaku system"""

    _loggers: Dict[str, logging.Logger] = {}
    _configured = False

    @classmethod
    def configure_logging(
        cls,
        log_level: str = "INFO",
        log_format: str = "json",
        log_file: Optional[str] = None,
        service_name: str = "miraikakaku"
    ) -> None:
        """Configure centralized logging"""
        if cls._configured:
            return

        # Set log level
        level = getattr(logging, log_level.upper(), logging.INFO)

        # Create formatters
        if log_format.lower() == "json":
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)

        # File handler (if specified)
        if log_file:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            root_logger.addHandler(file_handler)

        # Set service name for all loggers
        logging.getLogger().name = service_name
        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get logger instance with centralized configuration"""
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger

        return cls._loggers[name]

    @classmethod
    def log_with_context(
        cls,
        logger: logging.Logger,
        level: int,
        message: str,
        **context: Any
    ) -> None:
        """Log message with additional context"""
        extra = {"extra_fields": context}
        logger.log(level, message, extra=extra)


# Convenience functions
def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return MiraiKakakuLogger.get_logger(name)


def configure_logging(**kwargs) -> None:
    """Configure logging with given parameters"""
    MiraiKakakuLogger.configure_logging(**kwargs)


def log_api_request(logger: logging.Logger, method: str, path: str, status: int, duration: float) -> None:
    """Log API request with structured data"""
    MiraiKakakuLogger.log_with_context(
        logger, logging.INFO, f"{method} {path} - {status}",
        method=method, path=path, status_code=status,
        duration_ms=round(duration * 1000, 2), request_type="api"
    )


def log_batch_job(logger: logging.Logger, job_name: str, status: str, **kwargs) -> None:
    """Log batch job execution"""
    MiraiKakakuLogger.log_with_context(
        logger, logging.INFO, f"Batch job {job_name}: {status}",
        job_name=job_name, status=status, job_type="batch", **kwargs
    )


def log_database_operation(logger: logging.Logger, operation: str, table: str, count: int, duration: float) -> None:
    """Log database operation"""
    MiraiKakakuLogger.log_with_context(
        logger, logging.INFO, f"Database {operation} on {table}: {count} records",
        operation=operation, table=table, record_count=count,
        duration_ms=round(duration * 1000, 2), operation_type="database"
    )