"""
Production Error Handler and Fallback System - 恒久的エラーハンドリング
Comprehensive error handling with intelligent fallbacks and circuit breakers
"""
import asyncio
import logging
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories"""
    DATABASE = "database"
    NETWORK = "network"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    DATA_SOURCE = "data_source"
    PROCESSING = "processing"
    SYSTEM = "system"

@dataclass
class ErrorEvent:
    """Error event data structure"""
    timestamp: datetime
    error_type: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class CircuitBreakerState:
    """Circuit breaker state"""
    failures: int = 0
    last_failure: Optional[datetime] = None
    state: str = "closed"  # closed, open, half_open
    last_request: Optional[datetime] = None
    success_count: int = 0

class ErrorHandler:
    """Production-ready error handler with circuit breakers and fallbacks"""

    def __init__(self):
        self.error_history: List[ErrorEvent] = []
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.fallback_cache: Dict[str, Any] = {}
        self.metrics = {
            'total_errors': 0,
            'errors_by_category': {},
            'errors_by_severity': {},
            'circuit_breaker_trips': 0,
            'fallback_activations': 0
        }

        # Configuration
        self.max_error_history = 1000
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 300  # 5 minutes
        self.cache_ttl = 3600  # 1 hour

    def log_error(self, error: Exception, category: ErrorCategory, severity: ErrorSeverity, **kwargs):
        """Log error with context"""
        error_event = ErrorEvent(
            timestamp=datetime.now(),
            error_type=type(error).__name__,
            category=category,
            severity=severity,
            message=str(error),
            details={
                'traceback': traceback.format_exc(),
                'context': kwargs
            }
        )

        self.error_history.append(error_event)
        self._update_metrics(error_event)
        self._trim_error_history()

        # Log to system logger
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(severity, logging.ERROR)

        logger.log(log_level, f"[{category.value}] {error_event.message}", extra=error_event.details)

        return error_event

    def _update_metrics(self, error_event: ErrorEvent):
        """Update error metrics"""
        self.metrics['total_errors'] += 1

        category = error_event.category.value
        if category not in self.metrics['errors_by_category']:
            self.metrics['errors_by_category'][category] = 0
        self.metrics['errors_by_category'][category] += 1

        severity = error_event.severity.value
        if severity not in self.metrics['errors_by_severity']:
            self.metrics['errors_by_severity'][severity] = 0
        self.metrics['errors_by_severity'][severity] += 1

    def _trim_error_history(self):
        """Trim error history to prevent memory issues"""
        if len(self.error_history) > self.max_error_history:
            self.error_history = self.error_history[-self.max_error_history:]

    def circuit_breaker(self, service_name: str):
        """Circuit breaker decorator"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await self._execute_with_circuit_breaker(service_name, func, *args, **kwargs)
            return wrapper
        return decorator

    async def _execute_with_circuit_breaker(self, service_name: str, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        breaker = self._get_circuit_breaker(service_name)

        # Check circuit breaker state
        if breaker.state == "open":
            if self._should_attempt_reset(breaker):
                breaker.state = "half_open"
                logger.info(f"Circuit breaker for {service_name} moving to half-open")
            else:
                self.metrics['circuit_breaker_trips'] += 1
                raise Exception(f"Circuit breaker open for {service_name}")

        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

            # Success - reset circuit breaker
            if breaker.state == "half_open":
                breaker.success_count += 1
                if breaker.success_count >= 3:  # Require 3 successes to close
                    breaker.state = "closed"
                    breaker.failures = 0
                    breaker.success_count = 0
                    logger.info(f"Circuit breaker for {service_name} reset to closed")

            breaker.last_request = datetime.now()
            return result

        except Exception as e:
            breaker.failures += 1
            breaker.last_failure = datetime.now()
            breaker.last_request = datetime.now()

            if breaker.failures >= self.circuit_breaker_threshold:
                breaker.state = "open"
                logger.warning(f"Circuit breaker for {service_name} tripped open")

            raise e

    def _get_circuit_breaker(self, service_name: str) -> CircuitBreakerState:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreakerState()
        return self.circuit_breakers[service_name]

    def _should_attempt_reset(self, breaker: CircuitBreakerState) -> bool:
        """Check if circuit breaker should attempt reset"""
        if not breaker.last_failure:
            return True
        return (datetime.now() - breaker.last_failure).total_seconds() > self.circuit_breaker_timeout

    def with_fallback(self, fallback_key: str, fallback_func: Callable, cache_result: bool = True):
        """Fallback decorator"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

                    # Cache successful result
                    if cache_result:
                        self.fallback_cache[fallback_key] = {
                            'data': result,
                            'timestamp': time.time()
                        }

                    return result

                except Exception as e:
                    self.log_error(e, ErrorCategory.PROCESSING, ErrorSeverity.MEDIUM, fallback_key=fallback_key)
                    return await self._execute_fallback(fallback_key, fallback_func, *args, **kwargs)

            return wrapper
        return decorator

    async def _execute_fallback(self, fallback_key: str, fallback_func: Callable, *args, **kwargs):
        """Execute fallback with caching"""
        self.metrics['fallback_activations'] += 1

        # Try cache first
        if fallback_key in self.fallback_cache:
            cache_entry = self.fallback_cache[fallback_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                logger.info(f"Using cached fallback for {fallback_key}")
                return cache_entry['data']

        # Execute fallback function
        try:
            logger.info(f"Executing fallback for {fallback_key}")
            result = await fallback_func(*args, **kwargs) if asyncio.iscoroutinefunction(fallback_func) else fallback_func(*args, **kwargs)

            # Cache fallback result
            self.fallback_cache[fallback_key] = {
                'data': result,
                'timestamp': time.time()
            }

            return result

        except Exception as e:
            self.log_error(e, ErrorCategory.PROCESSING, ErrorSeverity.HIGH, fallback_key=fallback_key)
            raise Exception(f"Both primary and fallback failed for {fallback_key}")

    def get_error_stats(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        recent_errors = [
            e for e in self.error_history
            if (datetime.now() - e.timestamp).total_seconds() < 3600  # Last hour
        ]

        return {
            'summary': self.metrics.copy(),
            'recent_errors': len(recent_errors),
            'circuit_breakers': {
                name: {
                    'state': breaker.state,
                    'failures': breaker.failures,
                    'last_failure': breaker.last_failure.isoformat() if breaker.last_failure else None
                }
                for name, breaker in self.circuit_breakers.items()
            },
            'error_rate': {
                'last_hour': len(recent_errors),
                'last_24h': len([
                    e for e in self.error_history
                    if (datetime.now() - e.timestamp).total_seconds() < 86400
                ])
            },
            'top_error_categories': sorted(
                self.metrics['errors_by_category'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status based on errors"""
        recent_errors = len([
            e for e in self.error_history
            if (datetime.now() - e.timestamp).total_seconds() < 300  # Last 5 minutes
        ])

        critical_errors = len([
            e for e in self.error_history
            if e.severity == ErrorSeverity.CRITICAL and
            (datetime.now() - e.timestamp).total_seconds() < 3600
        ])

        open_circuits = len([
            b for b in self.circuit_breakers.values()
            if b.state == "open"
        ])

        # Determine health status
        if critical_errors > 0 or open_circuits > 2:
            status = "unhealthy"
        elif recent_errors > 10 or open_circuits > 0:
            status = "degraded"
        else:
            status = "healthy"

        return {
            'status': status,
            'recent_errors': recent_errors,
            'critical_errors': critical_errors,
            'open_circuits': open_circuits,
            'uptime_estimate': max(0, 100 - (recent_errors * 2) - (critical_errors * 10) - (open_circuits * 5)),
            'last_check': datetime.now().isoformat()
        }

    async def reset_circuit_breaker(self, service_name: str):
        """Manually reset circuit breaker"""
        if service_name in self.circuit_breakers:
            breaker = self.circuit_breakers[service_name]
            breaker.state = "closed"
            breaker.failures = 0
            breaker.success_count = 0
            logger.info(f"Circuit breaker for {service_name} manually reset")

    def clear_error_history(self):
        """Clear error history (for maintenance)"""
        self.error_history.clear()
        self.metrics = {
            'total_errors': 0,
            'errors_by_category': {},
            'errors_by_severity': {},
            'circuit_breaker_trips': 0,
            'fallback_activations': 0
        }
        logger.info("Error history cleared")

# Global error handler instance
error_handler = ErrorHandler()

# Convenience decorators
def with_error_handling(category: ErrorCategory, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
    """Decorator for automatic error handling"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            except Exception as e:
                error_handler.log_error(e, category, severity, function=func.__name__)
                raise
        return wrapper
    return decorator

def with_database_fallback(fallback_func: Callable):
    """Decorator for database operations with fallback"""
    return error_handler.with_fallback("database", fallback_func)

def with_api_circuit_breaker(service_name: str):
    """Decorator for API calls with circuit breaker"""
    return error_handler.circuit_breaker(service_name)