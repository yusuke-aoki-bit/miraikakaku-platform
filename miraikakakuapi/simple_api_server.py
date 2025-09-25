#!/usr/bin/env python3
"""
Simple API Server for Testing
Minimal FastAPI server without complex dependencies
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import threading
import time
from collections import deque, defaultdict

# Import connection pool and notification system
sys.path.append('/mnt/c/Users/yuuku/cursor/miraikakaku')
from shared.database.connection_pool import get_database_connection, get_pool_metrics, health_check as db_health_check

# Import notification system - Using minimal fallback due to import issues
class MinimalNotificationManager:
    def __init__(self):
        self.active_connections = set()
        logging.info("MinimalNotificationManager initialized")

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logging.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket):
        self.active_connections.discard(websocket)
        logging.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")

notification_manager = MinimalNotificationManager()

async def handle_websocket_notifications(websocket: WebSocket):
    await notification_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            # Keep connection alive
    except WebSocketDisconnect:
        notification_manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        notification_manager.disconnect(websocket)

# Enhanced logging configuration
import logging.config
from datetime import datetime
import uuid
import traceback

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s | %(levelname)s | %(name)s | [%(filename)s:%(lineno)d] | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "file": "%(filename)s", "line": %(lineno)d, "message": "%(message)s"}',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'json',
            'filename': 'miraikakaku_api.log',
            'mode': 'a'
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'miraikakaku_errors.log',
            'mode': 'a'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Error tracking storage
class ErrorTracker:
    def __init__(self):
        self.errors = deque(maxlen=1000)  # Store last 1000 errors
        self.error_counts = defaultdict(int)

    def record_error(self, error_type: str, error_message: str, endpoint: str, request_id: str, traceback_str: str = None):
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'error_message': error_message,
            'endpoint': endpoint,
            'request_id': request_id,
            'traceback': traceback_str
        }
        self.errors.append(error_entry)
        self.error_counts[error_type] += 1

        # Log the error
        logger.error(f"Error in {endpoint} (ID: {request_id}): {error_type} - {error_message}",
                    extra={'request_id': request_id, 'endpoint': endpoint})

    def get_error_summary(self):
        return {
            'total_errors': len(self.errors),
            'error_types': dict(self.error_counts),
            'recent_errors': list(self.errors)[-10:] if self.errors else []
        }

# Global error tracker
error_tracker = ErrorTracker()

# ML Engine import
try:
    from ml_engine import ml_engine, PredictionTimeframe
    ML_ENGINE_AVAILABLE = True
    logger.info("ML Engine loaded successfully")
except ImportError as e:
    ML_ENGINE_AVAILABLE = False
    logger.warning(f"ML Engine not available: {e}")

# Batch Job Monitor import
try:
    import sys
    sys.path.append('../')
    from batch_job_monitor import BatchJobMonitor
    BATCH_MONITOR_AVAILABLE = True
    batch_monitor = BatchJobMonitor()
    logger.info("Batch Job Monitor loaded successfully")
except ImportError as e:
    BATCH_MONITOR_AVAILABLE = False
    logger.warning(f"Batch Job Monitor not available: {e}")

# Auto Recovery System import
try:
    from auto_recovery import AutoRecoverySystem
    AUTO_RECOVERY_AVAILABLE = True
    recovery_system = AutoRecoverySystem()
    logger.info("Auto Recovery System loaded successfully")
except ImportError as e:
    AUTO_RECOVERY_AVAILABLE = False
    logger.warning(f"Auto Recovery System not available: {e}")

# Database configuration
DB_CONFIG = {
    'host': '34.173.9.214',
    'user': 'postgres',
    'password': 'os.getenv('DB_PASSWORD', '')',
    'database': 'miraikakaku'
}

# System metrics storage
class SystemMetrics:
    def __init__(self):
        self.request_count = 0
        self.response_times = deque(maxlen=1000)  # Store last 1000 response times
        self.error_count = 0
        self.endpoint_stats = defaultdict(lambda: {'count': 0, 'avg_time': 0, 'max_time': 0, 'min_time': float('inf')})
        self.db_query_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'avg_time': 0, 'max_time': 0})
        self.start_time = time.time()

    def record_request(self, endpoint: str, response_time: float, success: bool = True):
        self.request_count += 1
        self.response_times.append(response_time)

        if not success:
            self.error_count += 1

        # Update endpoint stats
        stats = self.endpoint_stats[endpoint]
        stats['count'] += 1
        # Calculate rolling average
        stats['avg_time'] = (stats['avg_time'] * (stats['count'] - 1) + response_time) / stats['count']
        stats['max_time'] = max(stats['max_time'], response_time)
        stats['min_time'] = min(stats['min_time'], response_time)

    def record_db_query(self, query_type: str, execution_time: float):
        stats = self.db_query_stats[query_type]
        stats['count'] += 1
        stats['total_time'] += execution_time
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['max_time'] = max(stats['max_time'], execution_time)

    def get_avg_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

    def get_response_percentiles(self) -> Dict[str, float]:
        if not self.response_times:
            return {}

        sorted_times = sorted(self.response_times)
        length = len(sorted_times)

        return {
            'p50': sorted_times[int(length * 0.5)],
            'p75': sorted_times[int(length * 0.75)],
            'p90': sorted_times[int(length * 0.9)],
            'p95': sorted_times[int(length * 0.95)],
            'p99': sorted_times[int(length * 0.99)]
        }

    def get_uptime(self) -> float:
        return time.time() - self.start_time

    def get_performance_summary(self) -> Dict[str, Any]:
        percentiles = self.get_response_percentiles()
        return {
            'uptime_seconds': self.get_uptime(),
            'total_requests': self.request_count,
            'error_count': self.error_count,
            'error_rate': (self.error_count / max(self.request_count, 1)) * 100,
            'avg_response_time': self.get_avg_response_time(),
            'response_percentiles': percentiles,
            'slowest_endpoints': sorted(
                [
                    {
                        'endpoint': endpoint,
                        'avg_time': stats['avg_time'],
                        'max_time': stats['max_time'],
                        'count': stats['count']
                    }
                    for endpoint, stats in self.endpoint_stats.items()
                    if stats['count'] > 5  # Only include endpoints with significant traffic
                ],
                key=lambda x: x['avg_time'],
                reverse=True
            )[:10],
            'database_performance': dict(self.db_query_stats)
        }

# Global metrics instance
metrics = SystemMetrics()

app = FastAPI(
    title="Miraikakaku API - Simple Test Server",
    description="Simplified API for E2E testing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TEMPORARILY DISABLED - Enhanced request tracking middleware
# @app.middleware("http")
async def request_tracking_middleware_disabled(request, call_next):
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()
    endpoint = request.url.path
    method = request.method

    # Log incoming request
    logger.info(f"Incoming {method} {endpoint}",
               extra={'request_id': request_id, 'endpoint': endpoint, 'method': method})

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Record metrics
        success = response.status_code < 400
        metrics.record_request(endpoint, process_time * 1000, success)

        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        # Log response
        logger.info(f"Response {response.status_code} for {method} {endpoint} in {process_time:.3f}s",
                   extra={'request_id': request_id, 'status_code': response.status_code, 'response_time': process_time})

        return response

    except Exception as e:
        process_time = time.time() - start_time
        error_type = type(e).__name__
        error_message = str(e)
        traceback_str = traceback.format_exc()

        # Record error
        error_tracker.record_error(error_type, error_message, endpoint, request_id, traceback_str)
        metrics.record_request(endpoint, process_time * 1000, False)

        # Log error
        logger.error(f"Unhandled exception in {method} {endpoint}",
                    extra={'request_id': request_id, 'error_type': error_type},
                    exc_info=True)

        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
            },
            headers={"X-Request-ID": request_id}
        )

def get_db_connection():
    """Get database connection with enhanced error handling"""
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        logger.debug("Database connection established successfully")
        return conn
    except psycopg2.OperationalError as e:
        error_msg = f"Database operational error: {e}"
        logger.error(error_msg)
        raise HTTPException(status_code=503, detail="Database service unavailable")
    except psycopg2.DatabaseError as e:
        error_msg = f"Database error: {e}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        error_msg = f"Unexpected database connection error: {e}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail="Database connection failed")

def safe_db_operation(operation_func, query_type: str = "unknown", *args, **kwargs):
    """Wrapper for safe database operations with connection pool and performance monitoring"""
    start_time = time.time()
    try:
        # Use connection pool context manager
        with get_database_connection() as conn:
            result = operation_func(conn, *args, **kwargs)

            # Record successful query performance
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            metrics.record_db_query(query_type, execution_time)

            return result
    except HTTPException:
        # Re-raise HTTP exceptions as they are already handled
        raise
    except psycopg2.Error as e:
        error_msg = f"Database operation failed: {e}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail="Database operation failed")
    except Exception as e:
        error_msg = f"Unexpected error during database operation: {e}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        conn.close()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "message": "All systems operational"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "database": "disconnected",
                "error": str(e)
            }
        )

@app.get("/api/system/status")
@app.get("/api/system/database/status")
async def database_status():
    """Database status endpoint for frontend monitoring"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get basic database statistics
        cur.execute("""
            SELECT
                (SELECT COUNT(*) FROM stock_master WHERE is_active = true) as total_symbols,
                (SELECT COUNT(DISTINCT symbol) FROM stock_prices) as symbols_with_data,
                (SELECT COUNT(*) FROM stock_predictions) as total_predictions,
                (SELECT MAX(created_at) FROM stock_prices) as latest_price_update,
                (SELECT MAX(created_at) FROM stock_predictions) as latest_prediction_update
        """)

        stats = cur.fetchone()
        conn.close()

        # Calculate data coverage
        total_symbols = stats.get("total_symbols", 0) if stats else 0
        symbols_with_data = stats.get("symbols_with_data", 0) if stats else 0
        data_coverage = round((symbols_with_data / max(total_symbols, 1)) * 100, 2) if total_symbols > 0 else 0

        return {
            "status": "connected",
            "total_symbols": total_symbols,
            "symbols_with_data": symbols_with_data,
            "total_predictions": stats.get("total_predictions", 0) if stats else 0,
            "latest_price_update": stats.get("latest_price_update").isoformat() if stats and stats.get("latest_price_update") else None,
            "latest_prediction_update": stats.get("latest_prediction_update").isoformat() if stats and stats.get("latest_prediction_update") else None,
            "data_coverage": data_coverage
        }
    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "disconnected",
                "error": str(e),
                "message": "Database connection failed"
            }
        )

@app.get("/api/system/metrics")
async def get_system_metrics():
    """Get system performance metrics"""
    try:
        uptime_seconds = metrics.get_uptime()
        uptime_hours = uptime_seconds / 3600

        # Calculate error rate
        error_rate = (metrics.error_count / max(metrics.request_count, 1)) * 100

        # Get top endpoints by usage
        top_endpoints = sorted(
            metrics.endpoint_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]

        return {
            "uptime_seconds": round(uptime_seconds, 2),
            "uptime_hours": round(uptime_hours, 2),
            "total_requests": metrics.request_count,
            "error_count": metrics.error_count,
            "error_rate": round(error_rate, 2),
            "avg_response_time": round(metrics.get_avg_response_time(), 2),
            "top_endpoints": [
                {
                    "endpoint": endpoint,
                    "count": stats['count'],
                    "avg_time": round(stats['avg_time'], 2)
                } for endpoint, stats in top_endpoints
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system metrics")

@app.get("/api/system/errors")
async def get_error_report():
    """Get error tracking report"""
    try:
        error_summary = error_tracker.get_error_summary()

        return {
            "success": True,
            "error_tracking": {
                "total_errors": error_summary['total_errors'],
                "error_types": error_summary['error_types'],
                "recent_errors": error_summary['recent_errors']
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching error report: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch error report")

@app.get("/api/system/logs")
async def get_recent_logs(lines: int = Query(100, ge=1, le=1000)):
    """Get recent log entries"""
    try:
        log_entries = []
        try:
            with open('miraikakaku_api.log', 'r') as f:
                lines_list = f.readlines()
                recent_lines = lines_list[-lines:] if len(lines_list) > lines else lines_list

                for line in recent_lines:
                    try:
                        log_entry = json.loads(line.strip())
                        log_entries.append(log_entry)
                    except json.JSONDecodeError:
                        # Handle non-JSON log lines
                        log_entries.append({"message": line.strip(), "timestamp": datetime.now().isoformat()})

        except FileNotFoundError:
            logger.warning("Log file not found")

        return {
            "success": True,
            "logs": log_entries,
            "count": len(log_entries),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch logs")

@app.get("/api/system/batch/status")
async def get_batch_job_status():
    """Get GCP batch job status"""
    try:
        if not BATCH_MONITOR_AVAILABLE:
            return {
                "success": False,
                "message": "Batch monitoring not available",
                "status": "unknown"
            }

        health = batch_monitor.check_job_health()
        return {
            "success": True,
            "batch_health": health,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching batch job status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch batch job status")

@app.get("/api/system/batch/jobs")
async def get_batch_jobs(limit: int = Query(20, ge=1, le=100)):
    """Get list of batch jobs"""
    try:
        if not BATCH_MONITOR_AVAILABLE:
            return {
                "success": False,
                "message": "Batch monitoring not available",
                "jobs": []
            }

        jobs = batch_monitor.get_batch_jobs(limit)
        return {
            "success": True,
            "jobs": [
                {
                    "job_name": job.job_name,
                    "status": job.status,
                    "create_time": job.create_time,
                    "start_time": job.start_time,
                    "end_time": job.end_time,
                    "duration": job.duration
                } for job in jobs
            ],
            "count": len(jobs),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching batch jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch batch jobs")

@app.get("/api/system/batch/jobs/{job_name}")
async def get_batch_job_details(job_name: str):
    """Get detailed information about a specific batch job"""
    try:
        if not BATCH_MONITOR_AVAILABLE:
            return {
                "success": False,
                "message": "Batch monitoring not available"
            }

        details = batch_monitor.get_job_details(job_name)
        if not details:
            raise HTTPException(status_code=404, detail="Job not found")

        return {
            "success": True,
            "job_details": details,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job details for {job_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch job details")

@app.get("/api/system/batch/jobs/{job_name}/logs")
async def get_batch_job_logs(job_name: str, lines: int = Query(100, ge=1, le=1000)):
    """Get logs for a specific batch job"""
    try:
        if not BATCH_MONITOR_AVAILABLE:
            return {
                "success": False,
                "message": "Batch monitoring not available",
                "logs": []
            }

        logs = batch_monitor.get_job_logs(job_name, lines)
        return {
            "success": True,
            "job_name": job_name,
            "logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching logs for job {job_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch job logs")

@app.get("/api/system/performance")
async def get_performance_metrics():
    """Get detailed performance metrics"""
    try:
        performance_data = metrics.get_performance_summary()
        return {
            "success": True,
            "performance": performance_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch performance metrics")

@app.get("/api/system/health/comprehensive")
async def comprehensive_health_check():
    """Comprehensive system health check including performance metrics"""
    try:
        # Basic health check
        health_status = "healthy"
        issues = []

        # Check database connection
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1")
            result = cur.fetchone()
            conn.close()
            db_status = "connected"
        except Exception as e:
            db_status = "disconnected"
            health_status = "degraded"
            issues.append(f"Database connection failed: {str(e)}")

        # Get performance metrics
        performance = metrics.get_performance_summary()

        # Check performance thresholds
        avg_response_time = performance.get('avg_response_time', 0)
        error_rate = performance.get('error_rate', 0)

        if avg_response_time > 1000:  # More than 1 second
            health_status = "degraded" if health_status == "healthy" else health_status
            issues.append(f"High average response time: {avg_response_time:.2f}ms")

        if error_rate > 5:  # More than 5% error rate
            health_status = "degraded"
            issues.append(f"High error rate: {error_rate:.2f}%")

        # Check batch jobs if available
        batch_status = "unknown"
        if BATCH_MONITOR_AVAILABLE:
            try:
                batch_health = batch_monitor.check_job_health()
                batch_status = batch_health.get('status', 'unknown')
                if batch_status in ['degraded', 'warning']:
                    if health_status == "healthy":
                        health_status = "warning"
                    issues.append(f"Batch jobs issue: {batch_health.get('message', '')}")
            except Exception as e:
                logger.warning(f"Could not check batch job health: {e}")

        return {
            "status": health_status,
            "timestamp": datetime.now().isoformat(),
            "components": {
                "api": "healthy",
                "database": db_status,
                "batch_jobs": batch_status
            },
            "performance": {
                "uptime_hours": performance.get('uptime_seconds', 0) / 3600,
                "total_requests": performance.get('total_requests', 0),
                "error_rate": error_rate,
                "avg_response_time": avg_response_time,
                "response_percentiles": performance.get('response_percentiles', {})
            },
            "issues": issues,
            "message": "; ".join(issues) if issues else "All systems operational"
        }

    except Exception as e:
        logger.error(f"Error in comprehensive health check: {e}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "message": f"Health check failed: {str(e)}"
        }

@app.post("/api/system/recovery/run")
async def run_auto_recovery():
    """Trigger automatic recovery procedures"""
    try:
        if not AUTO_RECOVERY_AVAILABLE:
            return {
                "success": False,
                "message": "Auto recovery system not available"
            }

        # Run recovery check
        recovery_report = recovery_system.check_and_recover()

        return {
            "success": True,
            "recovery_report": recovery_report,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error running auto recovery: {e}")
        raise HTTPException(status_code=500, detail="Auto recovery failed")

@app.get("/api/system/recovery/status")
async def get_recovery_status():
    """Get current recovery system status"""
    try:
        if not AUTO_RECOVERY_AVAILABLE:
            return {
                "success": False,
                "message": "Auto recovery system not available",
                "status": "unavailable"
            }

        # Test all components
        status = {
            "database": recovery_system.test_database_connection(),
            "api_server": recovery_system.test_api_health(),
            "frontend_server": recovery_system.test_frontend_health()
        }

        # Determine overall health
        all_healthy = all(status.values())
        overall_status = "healthy" if all_healthy else "degraded"

        return {
            "success": True,
            "overall_status": overall_status,
            "components": status,
            "recovery_attempts": recovery_system.recovery_attempts,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting recovery status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recovery status")

@app.post("/api/system/recovery/clear-attempts")
async def clear_recovery_attempts():
    """Clear recovery attempt counters"""
    try:
        if not AUTO_RECOVERY_AVAILABLE:
            return {
                "success": False,
                "message": "Auto recovery system not available"
            }

        recovery_system.recovery_attempts.clear()

        return {
            "success": True,
            "message": "Recovery attempt counters cleared",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error clearing recovery attempts: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear recovery attempts")

@app.get("/api/symbols")
async def get_symbols(limit: int = Query(100, ge=1, le=1000)):
    """Get available stock symbols"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT symbol, company_name, exchange, is_active
            FROM stock_master
            WHERE is_active = true
            ORDER BY symbol
            LIMIT %s
        """, (limit,))

        symbols = cur.fetchall()
        conn.close()

        return {
            "symbols": [dict(row) for row in symbols],
            "count": len(symbols),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch symbols")

@app.get("/api/stocks/search")
async def search_stocks(query: str = Query(..., min_length=1)):
    """Search stocks by symbol or company name"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        search_term = f"%{query.upper()}%"
        cur.execute("""
            SELECT symbol, company_name, exchange
            FROM stock_master
            WHERE is_active = true
            AND (
                UPPER(symbol) LIKE %s
                OR UPPER(company_name) LIKE %s
            )
            ORDER BY
                CASE WHEN UPPER(symbol) = UPPER(%s) THEN 1 ELSE 2 END,
                symbol
            LIMIT 20
        """, (search_term, search_term, query.upper()))

        results = cur.fetchall()
        conn.close()

        return {
            "query": query,
            "results": [dict(row) for row in results],
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error searching stocks with query '{query}': {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.get("/api/stocks/{symbol}")
async def get_stock_info(symbol: str):
    """Get stock information and latest price"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get basic stock info
        cur.execute("""
            SELECT symbol, company_name, exchange, is_active
            FROM stock_master
            WHERE symbol = %s
        """, (symbol,))

        stock_info = cur.fetchone()
        if not stock_info:
            raise HTTPException(status_code=404, detail="Symbol not found")

        # Get latest price
        cur.execute("""
            SELECT date, open_price, high_price, low_price, close_price, volume
            FROM stock_prices
            WHERE symbol = %s
            ORDER BY date DESC
            LIMIT 1
        """, (symbol,))

        latest_price = cur.fetchone()

        # Get recent price history (30 days)
        cur.execute("""
            SELECT date, close_price
            FROM stock_prices
            WHERE symbol = %s
            AND date >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY date DESC
            LIMIT 30
        """, (symbol,))

        price_history = cur.fetchall()
        conn.close()

        result = {
            "symbol": stock_info['symbol'],
            "company_name": stock_info['company_name'],
            "exchange": stock_info['exchange'],
            "is_active": stock_info['is_active'],
            "current_price": float(latest_price['close_price']) if latest_price and latest_price['close_price'] else None,
            "latest_date": latest_price['date'].isoformat() if latest_price else None,
            "price_history": [
                {
                    "date": row['date'].isoformat(),
                    "price": float(row['close_price'])
                } for row in price_history if row['close_price']
            ],
            "timestamp": datetime.now().isoformat()
        }

        if latest_price:
            result.update({
                "open_price": float(latest_price['open_price']) if latest_price['open_price'] else None,
                "high_price": float(latest_price['high_price']) if latest_price['high_price'] else None,
                "low_price": float(latest_price['low_price']) if latest_price['low_price'] else None,
                "volume": int(latest_price['volume']) if latest_price['volume'] else None
            })

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock information")


@app.get("/api/finance/stocks/search/popular")
async def get_popular_stocks():
    """Get popular stocks for search suggestions"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get popular stocks with current prices (high volume, recent activity)
        cur.execute("""
            SELECT DISTINCT
                sm.symbol,
                sm.company_name,
                sm.exchange,
                COUNT(sp.date) as trading_days,
                AVG(sp.volume) as avg_volume,
                (SELECT close_price
                 FROM stock_prices latest_sp
                 WHERE latest_sp.symbol = sm.symbol
                 AND latest_sp.close_price IS NOT NULL
                 ORDER BY latest_sp.date DESC
                 LIMIT 1) as current_price
            FROM stock_master sm
            JOIN stock_prices sp ON sm.symbol = sp.symbol
            WHERE sm.is_active = true
            AND sp.date >= CURRENT_DATE - INTERVAL '30 days'
            AND sp.volume IS NOT NULL
            AND sp.volume > 0
            GROUP BY sm.symbol, sm.company_name, sm.exchange
            HAVING COUNT(sp.date) >= 5
            ORDER BY avg_volume DESC
            LIMIT 10
        """)

        popular_stocks = cur.fetchall()
        conn.close()

        return {
            "popular_stocks": [
                {
                    "symbol": row['symbol'],
                    "display": f"{row['company_name']} ({row['symbol']})" if row['company_name'] else row['symbol'],
                    "type": "stock",
                    "currentPrice": float(row['current_price']) if row['current_price'] else 0.0
                } for row in popular_stocks
            ],
            "count": len(popular_stocks),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching popular stocks: {e}")
        # Return fallback popular stocks with mock current prices
        fallback_stocks = [
            {"symbol": "AAPL", "display": "Apple Inc. (AAPL)", "type": "stock", "currentPrice": 175.50},
            {"symbol": "MSFT", "display": "Microsoft Corp. (MSFT)", "type": "stock", "currentPrice": 380.25},
            {"symbol": "GOOGL", "display": "Alphabet Inc. (GOOGL)", "type": "stock", "currentPrice": 142.80},
            {"symbol": "AMZN", "display": "Amazon.com Inc. (AMZN)", "type": "stock", "currentPrice": 155.30},
            {"symbol": "TSLA", "display": "Tesla Inc. (TSLA)", "type": "stock", "currentPrice": 245.60}
        ]
        return {
            "popular_stocks": fallback_stocks,
            "count": len(fallback_stocks),
            "timestamp": datetime.now().isoformat(),
            "fallback": True
        }

@app.get("/api/rankings/top-performers")
async def get_top_performers(days: int = Query(7, ge=1, le=30), limit: int = Query(10, ge=1, le=50)):
    """Get top performing stocks"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Simplified query for top performers
        cur.execute("""
            SELECT
                sm.symbol,
                sm.company_name,
                COUNT(sp.date) as trading_days,
                AVG(sp.close_price) as avg_price,
                MAX(sp.close_price) as max_price,
                MIN(sp.close_price) as min_price
            FROM stock_master sm
            JOIN stock_prices sp ON sm.symbol = sp.symbol
            WHERE sm.is_active = true
            AND sp.date >= CURRENT_DATE - INTERVAL %s
            AND sp.close_price IS NOT NULL
            GROUP BY sm.symbol, sm.company_name
            HAVING COUNT(sp.date) >= 3
            ORDER BY avg_price DESC
            LIMIT %s
        """, (f"{days} days", limit))

        performers = cur.fetchall()
        conn.close()

        return {
            "top_performers": [
                {
                    "symbol": row['symbol'],
                    "company_name": row['company_name'],
                    "trading_days": row['trading_days'],
                    "avg_price": float(row['avg_price']) if row['avg_price'] else 0,
                    "max_price": float(row['max_price']) if row['max_price'] else None,
                    "min_price": float(row['min_price']) if row['min_price'] else None,
                    "price_range_percent": round(((float(row['max_price']) - float(row['min_price'])) / float(row['min_price']) * 100), 2) if row['max_price'] and row['min_price'] and row['min_price'] > 0 else 0
                } for row in performers
            ],
            "period_days": days,
            "count": len(performers),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching top performers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch top performers")

# Additional endpoints to match frontend API expectations

@app.get("/api/finance/stocks/{symbol}/price")
async def get_stock_price_history(symbol: str, days: int = Query(30, ge=1, le=730)):
    """Get stock price history for frontend"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT date, open_price, high_price, low_price, close_price, volume
            FROM stock_prices
            WHERE symbol = %s
            AND date >= CURRENT_DATE - INTERVAL %s
            ORDER BY date ASC
        """, (symbol, f"{days} days"))

        prices = cur.fetchall()
        conn.close()

        if not prices:
            raise HTTPException(status_code=404, detail=f"No price data found for symbol {symbol}")

        return [
            {
                "date": row['date'].isoformat(),
                "open_price": float(row['open_price']) if row['open_price'] else None,
                "high_price": float(row['high_price']) if row['high_price'] else None,
                "low_price": float(row['low_price']) if row['low_price'] else None,
                "close_price": float(row['close_price']) if row['close_price'] else None,
                "volume": int(row['volume']) if row['volume'] else None
            } for row in prices
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch price history")



@app.get("/api/finance/stocks/{symbol}/analysis/ai")
async def get_ai_analysis(symbol: str):
    """Get AI analysis factors for frontend"""
    try:
        # Return mock AI analysis for now
        return {
            "decision_factors": [
                {
                    "factor": "Technical Analysis",
                    "reason": f"Stock {symbol} shows positive technical indicators",
                    "impact": "positive",
                    "weight": 0.7
                },
                {
                    "factor": "Market Sentiment",
                    "reason": f"General market sentiment for {symbol} is bullish",
                    "impact": "positive",
                    "weight": 0.6
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching AI analysis for {symbol}: {e}")
        return {"decision_factors": []}

@app.get("/api/finance/stocks/{symbol}/analysis/financial")
async def get_financial_analysis(symbol: str):
    """Get financial analysis for frontend"""
    try:
        # Return mock financial analysis for now
        return {
            "analysis": "Financial metrics indicate stable performance",
            "metrics": {}
        }
    except Exception as e:
        logger.error(f"Error fetching financial analysis for {symbol}: {e}")
        return {"analysis": "No analysis available", "metrics": {}}

@app.get("/api/finance/stocks/{symbol}/analysis/risk")
async def get_risk_analysis(symbol: str):
    """Get risk analysis for frontend"""
    try:
        # Return mock risk analysis for now
        return {
            "risk_level": "moderate",
            "risk_factors": []
        }
    except Exception as e:
        logger.error(f"Error fetching risk analysis for {symbol}: {e}")
        return {"risk_level": "unknown", "risk_factors": []}

@app.get("/api/finance/stocks/search")
async def search_stocks_frontend(q: str = Query(...), limit: int = Query(10, ge=1, le=50)):
    """Search stocks for frontend (matches existing search functionality)"""
    return await search_stocks(query=q)


@app.get("/api/finance/rankings/accuracy")
async def get_prediction_accuracy_rankings(
    timeframe: str = Query("7d", description="Time period for accuracy rankings"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return")
):
    """Get prediction accuracy rankings based on MSE for historical predictions"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Convert timeframe to days
        days_map = {"7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(timeframe, 7)

        # Calculate MSE for historical predictions (1+ months old)
        cur.execute("""
            WITH historical_accuracy AS (
                SELECT
                    sp.symbol,
                    sm.company_name,
                    sp.model_type,
                    COUNT(*) as prediction_count,
                    AVG(POWER(sp.predicted_price - sph.close_price, 2)) as mse,
                    AVG(sp.confidence_score) as avg_confidence,
                    AVG(ABS((sp.predicted_price - sph.close_price) / sph.close_price * 100)) as avg_error_pct,
                    MIN(sp.prediction_date) as earliest_prediction,
                    MAX(sp.prediction_date) as latest_prediction
                FROM stock_predictions sp
                LEFT JOIN stock_master sm ON sp.symbol = sm.symbol
                JOIN stock_prices sph ON sp.symbol = sph.symbol
                    AND sp.prediction_date = sph.date
                WHERE sp.prediction_date < CURRENT_DATE - INTERVAL '30 days'
                AND sp.prediction_date >= CURRENT_DATE - INTERVAL %s
                AND sp.current_price IS NOT NULL
                AND sp.predicted_price IS NOT NULL
                AND sph.close_price IS NOT NULL
                AND sph.close_price > 0
                GROUP BY sp.symbol, sm.company_name, sp.model_type
                HAVING COUNT(*) >= 5
                AND MIN(sp.prediction_date) <= CURRENT_DATE - INTERVAL '30 days'
            )
            SELECT
                symbol,
                company_name,
                model_type,
                prediction_count,
                mse,
                avg_confidence,
                avg_error_pct,
                earliest_prediction,
                latest_prediction,
                (1.0 / (1.0 + mse)) * 100 as accuracy_score
            FROM historical_accuracy
            ORDER BY mse ASC, avg_error_pct ASC
            LIMIT %s
        """, (f"{days} days", limit))

        accuracy_results = cur.fetchall()
        conn.close()

        # Format response
        accuracy_ranking = []
        for result in accuracy_results:
            accuracy_ranking.append({
                "symbol": result['symbol'],
                "companyName": result['company_name'],
                "modelType": result['model_type'],
                "predictionCount": int(result['prediction_count']),
                "mse": float(result['mse']),
                "averageConfidence": float(result['avg_confidence']) if result['avg_confidence'] else 0,
                "averageErrorPercent": float(result['avg_error_pct']) if result['avg_error_pct'] else 0,
                "accuracyScore": float(result['accuracy_score']),
                "earliestPrediction": result['earliest_prediction'].isoformat() if result['earliest_prediction'] else None,
                "latestPrediction": result['latest_prediction'].isoformat() if result['latest_prediction'] else None,
                "dataSource": "database",
                "isRealData": True
            })

        return {
            "success": True,
            "accuracy_ranking": accuracy_ranking,
            "timeframe": timeframe,
            "total_count": len(accuracy_ranking),
            "data_source_info": {
                "real_data_count": len(accuracy_ranking),
                "fallback_data_count": 0,
                "total_count": len(accuracy_ranking),
                "has_real_data": len(accuracy_ranking) > 0,
                "has_fallback_data": False,
                "error": False
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching prediction accuracy rankings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch prediction accuracy rankings")

@app.get("/api/finance/rankings/predictions")
async def get_prediction_rankings(
    timeframe: str = Query("7d", description="Time period for prediction rankings"),
    limit: int = Query(10, description="Number of results to return"),
    type: str = Query("top", description="Ranking type: top, bottom, accurate, best_predictions")
):
    """Get stock prediction rankings by predicted performance"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Calculate date range based on timeframe
        if timeframe == "1d":
            days = 1
        elif timeframe == "7d":
            days = 7
        elif timeframe == "30d":
            days = 30
        elif timeframe == "90d":
            days = 90
        else:
            days = 7

        # Get prediction rankings based on type
        if type == "accurate" or type == "best_predictions":
            # Return accuracy rankings with confidence scores and current prices
            query = """
                WITH latest_prices AS (
                    SELECT DISTINCT ON (symbol)
                        symbol,
                        close_price as current_price,
                        date as price_date
                    FROM stock_prices
                    WHERE close_price IS NOT NULL
                    ORDER BY symbol, date DESC
                ),
                accuracy_stats AS (
                    SELECT
                        sp.symbol,
                        sm.company_name,
                        sp.predicted_price,
                        sp.confidence_score,
                        sph.close_price as actual_price,
                        ABS(sp.predicted_price - sph.close_price) as absolute_error,
                        POWER(sp.predicted_price - sph.close_price, 2) as squared_error,
                        sp.prediction_date,
                        (sp.prediction_date + INTERVAL '1 day' * sp.prediction_days) as target_date
                    FROM stock_predictions sp
                    JOIN stock_master sm ON sp.symbol = sm.symbol
                    JOIN stock_prices sph ON sp.symbol = sph.symbol
                        AND sph.date = (sp.prediction_date + INTERVAL '1 day' * sp.prediction_days)
                    WHERE (sp.prediction_date + INTERVAL '1 day' * sp.prediction_days) >= CURRENT_DATE - INTERVAL '%s days'
                    AND sp.predicted_price IS NOT NULL
                    AND sp.confidence_score IS NOT NULL
                    AND sph.close_price IS NOT NULL
                )
                SELECT
                    a.symbol,
                    a.company_name,
                    AVG(a.predicted_price) as avg_predicted_price,
                    AVG(a.confidence_score) as avg_confidence_score,
                    lp.current_price as avg_current_price,
                    AVG(a.actual_price) as avg_actual_price,
                    SQRT(AVG(a.squared_error)) as rmse,
                    AVG(ABS(a.absolute_error / NULLIF(a.actual_price, 0)) * 100) as mape,
                    COUNT(*) as prediction_count
                FROM accuracy_stats a
                JOIN latest_prices lp ON a.symbol = lp.symbol
                GROUP BY a.symbol, a.company_name, lp.current_price
                HAVING COUNT(*) >= 3
                ORDER BY rmse ASC
                LIMIT %s
            """
        elif type == "bottom":
            # Worst predicted performers
            query = """
                WITH latest_prices AS (
                    SELECT DISTINCT ON (symbol)
                        symbol,
                        close_price as current_price,
                        date as price_date
                    FROM stock_prices
                    WHERE close_price IS NOT NULL
                    ORDER BY symbol, date DESC
                )
                SELECT
                    sp.symbol,
                    sm.company_name,
                    AVG(sp.predicted_price) as avg_predicted_price,
                    AVG(sp.confidence_score) as avg_confidence_score,
                    lp.current_price as avg_current_price,
                    ((AVG(sp.predicted_price) - lp.current_price) / NULLIF(lp.current_price, 0)) * 100 as predicted_change_percent,
                    COUNT(*) as prediction_count,
                    MAX(sp.prediction_date) as latest_prediction_date
                FROM stock_predictions sp
                JOIN stock_master sm ON sp.symbol = sm.symbol
                JOIN latest_prices lp ON sp.symbol = lp.symbol
                WHERE sp.prediction_date >= CURRENT_DATE - INTERVAL '%s days'
                AND sp.predicted_price IS NOT NULL
                AND sp.confidence_score IS NOT NULL
                GROUP BY sp.symbol, sm.company_name, lp.current_price
                HAVING COUNT(*) >= 1
                ORDER BY predicted_change_percent ASC
                LIMIT %s
            """
        else:
            # Top predicted performers (default)
            query = """
                WITH latest_prices AS (
                    SELECT DISTINCT ON (symbol)
                        symbol,
                        close_price as current_price,
                        date as price_date
                    FROM stock_prices
                    WHERE close_price IS NOT NULL
                    ORDER BY symbol, date DESC
                )
                SELECT
                    sp.symbol,
                    sm.company_name,
                    AVG(sp.predicted_price) as avg_predicted_price,
                    AVG(sp.confidence_score) as avg_confidence_score,
                    lp.current_price as avg_current_price,
                    ((AVG(sp.predicted_price) - lp.current_price) / NULLIF(lp.current_price, 0)) * 100 as predicted_change_percent,
                    COUNT(*) as prediction_count,
                    MAX(sp.prediction_date) as latest_prediction_date
                FROM stock_predictions sp
                JOIN stock_master sm ON sp.symbol = sm.symbol
                JOIN latest_prices lp ON sp.symbol = lp.symbol
                WHERE sp.prediction_date >= CURRENT_DATE - INTERVAL '%s days'
                AND sp.predicted_price IS NOT NULL
                AND sp.confidence_score IS NOT NULL
                GROUP BY sp.symbol, sm.company_name, lp.current_price
                HAVING COUNT(*) >= 1
                ORDER BY predicted_change_percent DESC
                LIMIT %s
            """

        cur.execute(query, (days, limit))
        results = cur.fetchall()
        conn.close()

        rankings = []
        for i, row in enumerate(results, 1):
            # Use confidence score from database
            confidence_score = float(row.get('avg_confidence_score', 0)) if row.get('avg_confidence_score') else 0

            # Get current price and predicted price
            current_price = float(row.get('avg_current_price', 0))
            predicted_price = float(row.get('avg_predicted_price', 0))

            # Calculate change percent
            if current_price > 0:
                change_percent = ((predicted_price - current_price) / current_price) * 100
            else:
                change_percent = 0

            ranking_data = {
                "rank": i,
                "symbol": row['symbol'],
                "company_name": row['company_name'],
                "predicted_price": predicted_price,
                "current_price": current_price,
                "avg_predicted_price": predicted_price,
                "prediction_count": row['prediction_count'],
                "confidence_score": confidence_score,
                "prediction_change_percent": change_percent,
                "prediction_date": datetime.now().isoformat()
            }

            if type == "accurate" or type == "best_predictions":
                ranking_data.update({
                    "avg_actual_price": float(row['avg_actual_price']) if row['avg_actual_price'] else 0,
                    "rmse": float(row['rmse']) if row['rmse'] else 0,
                    "mape": float(row['mape']) if row['mape'] else 0
                })
            else:
                ranking_data.update({
                    "predicted_change_percent": float(row.get('predicted_change_percent', change_percent)),
                    "latest_prediction_date": row.get('latest_prediction_date', datetime.now()).isoformat() if row.get('latest_prediction_date') else datetime.now().isoformat()
                })

            rankings.append(ranking_data)

        return {
            "success": True,
            "predictions_ranking": rankings,
            "data_source_info": {
                "timeframe": timeframe,
                "type": type,
                "limit": limit,
                "total_results": len(rankings),
                "last_updated": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error fetching prediction rankings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch prediction rankings")

@app.get("/api/market/summary")
async def get_market_summary():
    """Get market summary statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get basic statistics
        cur.execute("""
            SELECT
                COUNT(DISTINCT sm.symbol) as total_symbols,
                COUNT(DISTINCT sp.symbol) as symbols_with_prices,
                COUNT(DISTINCT spr.symbol) as symbols_with_predictions,
                MAX(sp.date) as latest_price_date,
                MAX(spr.prediction_date) as latest_prediction_date
            FROM stock_master sm
            LEFT JOIN stock_prices sp ON sm.symbol = sp.symbol
            LEFT JOIN stock_predictions spr ON sm.symbol = spr.symbol
            WHERE sm.is_active = true
        """)

        stats = cur.fetchone()

        # Get recent activity
        cur.execute("""
            SELECT COUNT(*) as recent_prices
            FROM stock_prices
            WHERE date >= CURRENT_DATE - INTERVAL '1 day'
        """)

        recent_activity = cur.fetchone()
        conn.close()

        return {
            "market_summary": {
                "total_active_symbols": stats['total_symbols'],
                "symbols_with_price_data": stats['symbols_with_prices'],
                "symbols_with_predictions": stats['symbols_with_predictions'],
                "price_coverage_percent": round((stats['symbols_with_prices'] / stats['total_symbols']) * 100, 1) if stats['total_symbols'] > 0 else 0,
                "prediction_coverage_percent": round((stats['symbols_with_predictions'] / stats['total_symbols']) * 100, 1) if stats['total_symbols'] > 0 else 0,
                "latest_price_date": stats['latest_price_date'].isoformat() if stats['latest_price_date'] else None,
                "latest_prediction_date": stats['latest_prediction_date'].isoformat() if stats['latest_prediction_date'] else None,
                "recent_price_updates": recent_activity['recent_prices']
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching market summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market summary")

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An internal server error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# LSTM/VertexAI Enhanced Endpoints
@app.get("/api/finance/stocks/{symbol}/lstm-predictions")
async def get_lstm_predictions(
    symbol: str,
    timeframe: str = Query("1d", description="Prediction timeframe: 1d, 7d, 30d, 90d")
):
    """Get LSTM-powered stock predictions"""
    if not ML_ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML Engine not available")

    try:
        # Map timeframe string to PredictionTimeframe enum
        timeframe_map = {
            "1d": PredictionTimeframe.ONE_DAY,
            "7d": PredictionTimeframe.ONE_WEEK,
            "30d": PredictionTimeframe.ONE_MONTH,
            "90d": PredictionTimeframe.THREE_MONTHS
        }

        tf = timeframe_map.get(timeframe, PredictionTimeframe.ONE_DAY)

        # Get LSTM prediction
        prediction = await ml_engine.predict_with_lstm(symbol.upper(), tf)

        if not prediction:
            raise HTTPException(status_code=404, detail="Unable to generate LSTM prediction")

        return {
            "symbol": prediction.symbol,
            "predicted_price": prediction.predicted_price,
            "confidence_score": prediction.confidence_score,
            "model_type": prediction.model_type,
            "timeframe_days": prediction.timeframe_days,
            "prediction_date": prediction.prediction_date.isoformat(),
            "features_used": prediction.features_used,
            "market_conditions": prediction.market_conditions,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"LSTM prediction error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/api/finance/stocks/{symbol}/vertexai-predictions")
async def get_vertexai_predictions(
    symbol: str,
    timeframe: str = Query("1d", description="Prediction timeframe: 1d, 7d, 30d, 90d")
):
    """Get VertexAI-powered stock predictions (独立システム)"""
    if not ML_ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML Engine not available")

    try:
        # Map timeframe string to PredictionTimeframe enum
        timeframe_map = {
            "1d": PredictionTimeframe.ONE_DAY,
            "7d": PredictionTimeframe.ONE_WEEK,
            "30d": PredictionTimeframe.ONE_MONTH,
            "90d": PredictionTimeframe.THREE_MONTHS
        }

        tf = timeframe_map.get(timeframe, PredictionTimeframe.ONE_DAY)

        # Get VertexAI prediction
        prediction = await ml_engine.predict_with_vertex_ai(symbol.upper(), tf)

        if not prediction:
            raise HTTPException(status_code=404, detail="VertexAI service temporarily unavailable")

        return {
            "symbol": prediction.symbol,
            "predicted_price": prediction.predicted_price,
            "confidence_score": prediction.confidence_score,
            "model_type": prediction.model_type,
            "timeframe_days": prediction.timeframe_days,
            "prediction_date": prediction.prediction_date.isoformat(),
            "features_used": prediction.features_used,
            "market_conditions": prediction.market_conditions,
            "vertex_ai_status": "enabled",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"VertexAI prediction error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/api/finance/stocks/{symbol}/dual-predictions")
async def get_dual_predictions(
    symbol: str,
    timeframe: str = Query("1d", description="Prediction timeframe: 1d, 7d, 30d, 90d")
):
    """Get both LSTM and VertexAI predictions for comparison (2系統の独立予測)"""
    if not ML_ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML Engine not available")

    try:
        # Map timeframe string to PredictionTimeframe enum
        timeframe_map = {
            "1d": PredictionTimeframe.ONE_DAY,
            "7d": PredictionTimeframe.ONE_WEEK,
            "30d": PredictionTimeframe.ONE_MONTH,
            "90d": PredictionTimeframe.THREE_MONTHS
        }

        tf = timeframe_map.get(timeframe, PredictionTimeframe.ONE_DAY)

        # Get dual predictions
        predictions = await ml_engine.get_dual_predictions(symbol.upper(), tf)

        lstm_pred = predictions.get("lstm")
        vertex_pred = predictions.get("vertex_ai")

        result = {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat(),
            "predictions": {
                "lstm": None,
                "vertex_ai": None
            },
            "comparison": {}
        }

        # Process LSTM prediction
        if lstm_pred:
            result["predictions"]["lstm"] = {
                "predicted_price": lstm_pred.predicted_price,
                "confidence_score": lstm_pred.confidence_score,
                "model_type": lstm_pred.model_type,
                "prediction_date": lstm_pred.prediction_date.isoformat(),
                "market_conditions": lstm_pred.market_conditions
            }

        # Process VertexAI prediction
        if vertex_pred:
            result["predictions"]["vertex_ai"] = {
                "predicted_price": vertex_pred.predicted_price,
                "confidence_score": vertex_pred.confidence_score,
                "model_type": vertex_pred.model_type,
                "prediction_date": vertex_pred.prediction_date.isoformat(),
                "market_conditions": vertex_pred.market_conditions
            }

        # Add comparison if both predictions are available
        if lstm_pred and vertex_pred:
            price_diff = abs(lstm_pred.predicted_price - vertex_pred.predicted_price)
            avg_price = (lstm_pred.predicted_price + vertex_pred.predicted_price) / 2
            diff_percentage = (price_diff / avg_price) * 100 if avg_price > 0 else 0

            result["comparison"] = {
                "price_difference": price_diff,
                "difference_percentage": diff_percentage,
                "average_predicted_price": avg_price,
                "higher_prediction": "lstm" if lstm_pred.predicted_price > vertex_pred.predicted_price else "vertex_ai",
                "confidence_winner": "lstm" if lstm_pred.confidence_score > vertex_pred.confidence_score else "vertex_ai",
                "consensus": diff_percentage < 2.0  # 2%未満の差なら合意
            }

        return result

    except Exception as e:
        logger.error(f"Dual prediction error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/api/ml/train/{symbol}")
async def train_ml_models(symbol: str):
    """Train ML models for a specific symbol"""
    if not ML_ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML Engine not available")

    try:
        logger.info(f"Starting ML training for {symbol}")

        # Train models for the symbol
        performances = await ml_engine.train_models_for_symbol(symbol.upper())

        if not performances:
            raise HTTPException(status_code=400, detail="Unable to train models - insufficient data")

        return {
            "symbol": symbol.upper(),
            "training_completed": True,
            "model_performances": performances,
            "trained_models": list(performances.keys()),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Training error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

@app.get("/api/ml/status")
async def get_ml_status():
    """Get ML Engine status and capabilities"""
    try:
        from ml_engine import TENSORFLOW_AVAILABLE, VERTEXAI_AVAILABLE

        status = {
            "ml_engine_available": ML_ENGINE_AVAILABLE,
            "tensorflow_available": TENSORFLOW_AVAILABLE,
            "vertexai_available": VERTEXAI_AVAILABLE,
            "trained_symbols": list(ml_engine.trained_symbols) if ML_ENGINE_AVAILABLE else [],
            "capabilities": {
                "lstm_models": TENSORFLOW_AVAILABLE,
                "traditional_ml": True,
                "vertex_ai_integration": VERTEXAI_AVAILABLE,
                "real_time_predictions": True,
                "batch_training": True
            },
            "timestamp": datetime.now().isoformat()
        }

        if ML_ENGINE_AVAILABLE:
            # Get performance summary
            performance_summary = ml_engine.get_model_performance_summary()
            status["performance_summary"] = performance_summary

            # VertexAI status
            if hasattr(ml_engine, 'vertex_ai'):
                status["vertex_ai_status"] = {
                    "initialized": ml_engine.vertex_ai.is_available(),
                    "project_id": ml_engine.vertex_ai.project_id,
                    "location": ml_engine.vertex_ai.location
                }

        return status

    except Exception as e:
        logger.error(f"ML status error: {e}")
        return {
            "ml_engine_available": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/finance/stocks/{symbol}/details")
async def get_stock_details(symbol: str):
    """Get detailed stock information including price history and predictions"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get basic stock info
        cur.execute("""
            SELECT symbol, company_name
            FROM stock_master
            WHERE symbol = %s
        """, (symbol,))

        stock_info = cur.fetchone()
        if not stock_info:
            raise HTTPException(status_code=404, detail="Stock not found")

        # Get recent price history (last 30 days)
        cur.execute("""
            SELECT date, open_price, high_price, low_price, close_price, volume
            FROM stock_prices
            WHERE symbol = %s
            AND date >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY date DESC
            LIMIT 30
        """, (symbol,))

        price_history = cur.fetchall()

        # Get predictions
        cur.execute("""
            SELECT
                prediction_date,
                predicted_price,
                confidence_score,
                prediction_days,
                current_price,
                model_type,
                created_at
            FROM stock_predictions
            WHERE symbol = %s
            AND prediction_date >= CURRENT_DATE
            ORDER BY prediction_date ASC
            LIMIT 10
        """, (symbol,))

        predictions = cur.fetchall()

        # Calculate statistics
        if price_history:
            latest_price = float(price_history[0]['close_price']) if price_history[0]['close_price'] else 0
            prices = [float(p['close_price']) for p in price_history if p['close_price']]

            if len(prices) >= 2:
                price_change = prices[0] - prices[1]
                price_change_percent = (price_change / prices[1]) * 100 if prices[1] != 0 else 0
            else:
                price_change = 0
                price_change_percent = 0

            high_52w = max(prices) if prices else 0
            low_52w = min(prices) if prices else 0
        else:
            latest_price = 0
            price_change = 0
            price_change_percent = 0
            high_52w = 0
            low_52w = 0

        conn.close()

        return {
            "success": True,
            "stock_info": {
                "symbol": stock_info['symbol'],
                "company_name": stock_info['company_name'],
                "latest_price": latest_price,
                "price_change": price_change,
                "price_change_percent": round(price_change_percent, 2),
                "high_52w": high_52w,
                "low_52w": low_52w
            },
            "price_history": [
                {
                    "date": p['date'].isoformat() if p['date'] else None,
                    "open": float(p['open_price']) if p['open_price'] else None,
                    "high": float(p['high_price']) if p['high_price'] else None,
                    "low": float(p['low_price']) if p['low_price'] else None,
                    "close": float(p['close_price']) if p['close_price'] else None,
                    "volume": int(p['volume']) if p['volume'] else None
                } for p in price_history
            ],
            "predictions": [
                {
                    "prediction_date": p['prediction_date'].isoformat() if p['prediction_date'] else None,
                    "predicted_price": float(p['predicted_price']) if p['predicted_price'] else None,
                    "confidence_score": float(p['confidence_score']) if p['confidence_score'] else 0,
                    "prediction_days": p['prediction_days'],
                    "current_price": float(p['current_price']) if p['current_price'] else None,
                    "model_type": p['model_type'],
                    "created_at": p['created_at'].isoformat() if p['created_at'] else None
                } for p in predictions
            ],
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/finance/stocks/{symbol}/predictions/history")
async def get_historical_predictions(
    symbol: str,
    days: int = Query(30, description="Number of days of historical predictions to fetch")
):
    """Get historical prediction accuracy data for a stock symbol"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get historical predictions with actual outcomes
        cur.execute("""
            SELECT
                sp.prediction_date,
                sp.predicted_price,
                sp.confidence_score,
                sp.prediction_days,
                sp.current_price,
                sp.model_type,
                sp.created_at,
                sph.close_price as actual_price,
                (sp.prediction_date + INTERVAL '1 day' * sp.prediction_days) as target_date,
                CASE
                    WHEN sph.close_price IS NOT NULL AND sph.close_price > 0 THEN
                        ABS((sp.predicted_price - sph.close_price) / sph.close_price * 100)
                    ELSE NULL
                END as accuracy_percentage
            FROM stock_predictions sp
            LEFT JOIN stock_prices sph ON sp.symbol = sph.symbol
                AND sph.date = (sp.prediction_date + INTERVAL '1 day' * sp.prediction_days)
            WHERE sp.symbol = %s
            AND sp.prediction_date >= CURRENT_DATE - INTERVAL '%s days'
            AND sp.prediction_date < CURRENT_DATE - INTERVAL '1 day'
            ORDER BY sp.prediction_date DESC
            LIMIT 50
        """, (symbol, days))

        historical_predictions = cur.fetchall()
        conn.close()

        # Format response
        predictions_data = []
        for pred in historical_predictions:
            predictions_data.append({
                "prediction_date": pred['prediction_date'].isoformat() if pred['prediction_date'] else None,
                "target_date": pred['target_date'].isoformat() if pred['target_date'] else None,
                "predicted_price": float(pred['predicted_price']) if pred['predicted_price'] else None,
                "actual_price": float(pred['actual_price']) if pred['actual_price'] else None,
                "accuracy_percentage": float(pred['accuracy_percentage']) if pred['accuracy_percentage'] else None,
                "confidence_score": float(pred['confidence_score']) if pred['confidence_score'] else 0,
                "prediction_days": pred['prediction_days'],
                "current_price": float(pred['current_price']) if pred['current_price'] else None,
                "model_type": pred['model_type'],
                "created_at": pred['created_at'].isoformat() if pred['created_at'] else None
            })

        return {
            "success": True,
            "symbol": symbol,
            "days_requested": days,
            "historical_predictions": predictions_data,
            "total_records": len(predictions_data),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching historical predictions for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch historical predictions: {str(e)}")


@app.get("/api/finance/stocks/{symbol}/historical-predictions")
async def get_historical_predictions_alt(
    symbol: str,
    days: int = Query(30, description="Number of days of historical predictions to fetch")
):
    """Alternative endpoint for historical predictions (compatibility)"""
    return await get_historical_predictions(symbol, days)

@app.get("/api/system/connection-pool")
async def get_connection_pool_status():
    """Get connection pool status and metrics - TEST ENDPOINT"""
    try:
        # Test the pool with current environment
        from shared.database.connection_pool import get_connection_pool
        pool = get_connection_pool()

        # Get pool status (this will show why connection fails)
        pool_status = pool.get_pool_status()

        # Attempt database health check using existing DB_CONFIG
        db_test_result = "not_tested"
        try:
            conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            cursor.execute("SELECT version(), current_timestamp")
            result = cursor.fetchone()
            db_test_result = {
                "status": "success",
                "version": result[0][:50] + "...",
                "timestamp": str(result[1])
            }
            cursor.close()
            conn.close()
        except Exception as db_e:
            db_test_result = {"status": "failed", "error": str(db_e)}

        return {
            "status": "diagnostic",
            "connection_pool_status": pool_status,
            "direct_db_test": db_test_result,
            "current_db_config": {
                "host": DB_CONFIG.get("host", "not_set"),
                "port": DB_CONFIG.get("port", "not_set"),
                "database": DB_CONFIG.get("dbname", "not_set"),
                "user": DB_CONFIG.get("user", "not_set")
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in connection pool diagnostic: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============= WEBSOCKET ENDPOINTS =============

@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """WebSocket通知エンドポイント - FIXED"""
    try:
        await handle_websocket_notifications(websocket)
    except Exception as e:
        logger.error(f"WebSocket error in /ws/notifications: {e}")
        try:
            await websocket.close()
        except:
            pass

# ============= MISSING API ENDPOINTS =============

@app.get("/api/rankings")
async def get_rankings():
    """Top performing stocks rankings"""
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()

            # Get top performers based on recent price changes
            cursor.execute("""
                SELECT
                    sp.symbol,
                    sm.company_name,
                    sp.close_price as current_price,
                    sp.date as last_updated,
                    LAG(sp.close_price, 1) OVER (PARTITION BY sp.symbol ORDER BY sp.date DESC) as previous_price
                FROM stock_prices sp
                LEFT JOIN stock_master sm ON sp.symbol = sm.symbol
                WHERE sp.date >= CURRENT_DATE - INTERVAL '7 days'
                  AND sp.close_price IS NOT NULL
                ORDER BY sp.symbol, sp.date DESC
                LIMIT 50
            """)

            results = cursor.fetchall()
            rankings = []

            for row in results:
                symbol = row['symbol']
                current_price = float(row['current_price']) if row['current_price'] else 0
                previous_price = float(row['previous_price']) if row['previous_price'] else current_price

                change_percent = 0
                if previous_price and previous_price != 0:
                    change_percent = ((current_price - previous_price) / previous_price) * 100

                rankings.append({
                    'symbol': symbol,
                    'company_name': row['company_name'] or symbol,
                    'current_price': current_price,
                    'change_percent': round(change_percent, 2),
                    'last_updated': row['last_updated'].isoformat() if row['last_updated'] else None
                })

            # Sort by change_percent descending
            rankings.sort(key=lambda x: x['change_percent'], reverse=True)

            return {
                "status": "success",
                "rankings": rankings[:20],  # Top 20
                "total_count": len(rankings),
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"Error getting rankings: {e}")
        return {
            "status": "error",
            "rankings": [],
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/system/health")
async def get_system_health():
    """System health check endpoint - FIXED"""
    try:
        # Test database connectivity
        db_status = "unknown"
        db_response_time = 0

        try:
            start_time = time.time()
            with get_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                db_response_time = (time.time() - start_time) * 1000
                db_status = "healthy"
        except Exception as db_e:
            logger.error(f"Database health check failed: {db_e}")
            db_status = "unhealthy"

        # Check connection pool
        try:
            pool_metrics = get_pool_metrics()
            pool_status = "healthy" if pool_metrics['connection_errors'] == 0 else "degraded"
        except Exception as pool_e:
            logger.error(f"Pool health check failed: {pool_e}")
            pool_status = "unhealthy"
            pool_metrics = {}

        overall_status = "healthy"
        if db_status != "healthy" or pool_status != "healthy":
            overall_status = "degraded"

        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": {
                    "status": db_status,
                    "response_time_ms": round(db_response_time, 2)
                },
                "connection_pool": {
                    "status": pool_status,
                    "metrics": pool_metrics
                }
            },
            "message": f"System is {overall_status}"
        }

    except Exception as e:
        logger.error(f"System health check error: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "message": "System health check failed"
        }

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))

    print("🚀 Starting Simple Miraikakaku API Server")
    print("=========================================")
    print(f"API Documentation: http://localhost:{port}/docs")
    print(f"Health Check: http://localhost:{port}/health")

    uvicorn.run(
        "simple_api_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False
    )

