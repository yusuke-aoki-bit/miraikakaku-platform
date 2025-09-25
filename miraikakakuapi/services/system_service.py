import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
from ..core.cache import cache
from ..core.database import db
from ..core.exceptions import (
    APIError, DatabaseError, CacheError,
    handle_service_error, create_error_response
)
from ..core.logging_config import (
    get_logger, log_execution_time, log_performance
)

logger = get_logger(__name__)


class SystemService:
    """Service for system monitoring and health checks."""

    @log_execution_time()
    async def get_system_health(self) -> Dict:
        """Get comprehensive system health status."""
        operation = "get_system_health"

        try:
            health_data = {}
            health_checks = []

            # Database health
            try:
                health_data["database"] = await self._check_database_health()
                health_checks.append(("database", health_data["database"].get("status") == "healthy"))
            except Exception as e:
                logger.error(f"Database health check failed: {e}")
                health_data["database"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                health_checks.append(("database", False))

            # Cache health
            try:
                health_data["cache"] = await self._check_cache_health()
                health_checks.append(("cache", health_data["cache"].get("status") == "healthy"))
            except Exception as e:
                logger.error(f"Cache health check failed: {e}")
                health_data["cache"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                health_checks.append(("cache", False))

            # System resources
            try:
                health_data["system"] = await self._get_system_metrics()
                health_checks.append(("system", health_data["system"].get("status") == "healthy"))
            except Exception as e:
                logger.error(f"System metrics check failed: {e}")
                health_data["system"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                health_checks.append(("system", False))

            # API status
            health_data["api"] = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": self._get_uptime()
            }
            health_checks.append(("api", True))

            # Overall health status
            passed_checks = sum(1 for _, healthy in health_checks if healthy)
            total_checks = len(health_checks)
            all_healthy = passed_checks == total_checks

            health_data["overall"] = {
                "status": "healthy" if all_healthy else "degraded",
                "checks_passed": passed_checks,
                "total_checks": total_checks,
                "failed_checks": [name for name, healthy in health_checks if not healthy],
                "timestamp": datetime.utcnow().isoformat()
            }

            # Log health status
            if not all_healthy:
                logger.warning(
                    f"System health degraded: {passed_checks}/{total_checks} checks passed",
                    extra={"failed_checks": health_data["overall"]["failed_checks"]}
                )

            return health_data

        except Exception as e:
            error_response = {
                "overall": {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            logger.error(f"Critical error in {operation}: {e}", exc_info=True)
            return error_response

    async def get_system_metrics(self) -> Dict:
        """Get detailed system metrics."""
        try:
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "system": self._get_system_info(),
                "resources": self._get_resource_usage(),
                "database": await self._get_database_metrics(),
                "cache": await self._get_cache_metrics(),
                "api": await self._get_api_metrics()
            }

            return metrics

        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    async def get_system_jobs(self) -> List[Dict]:
        """Get information about background jobs and processes."""
        try:
            jobs = []

            # Check for running background processes
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if 'python' in proc_info['name'].lower():
                        jobs.append({
                            "job_id": f"proc_{proc_info['pid']}",
                            "name": proc_info['name'],
                            "status": proc_info['status'],
                            "cpu_percent": proc_info['cpu_percent'],
                            "memory_percent": proc_info['memory_percent'],
                            "type": "system_process"
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Get database job information if available
            database_jobs = await self._get_database_jobs()
            jobs.extend(database_jobs)

            return jobs

        except Exception as e:
            logger.error(f"Error getting system jobs: {e}")
            return []

    async def _check_database_health(self) -> Dict:
        """Check database connectivity and performance."""
        start_time = datetime.utcnow()

        try:
            # Test basic connectivity with timeout
            health_status = await asyncio.wait_for(
                db.health_check(),
                timeout=5.0  # 5 second timeout
            )

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            if not health_status:
                return {
                    "status": "unhealthy",
                    "error": "Database health check failed",
                    "response_time_ms": response_time,
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Get additional database metrics with error handling
            try:
                async with db.get_connection() as conn:
                    # Check database size
                    db_size = await asyncio.wait_for(
                        conn.fetchval("SELECT pg_size_pretty(pg_database_size(current_database()))"),
                        timeout=2.0
                    )

                    # Check active connections
                    active_connections = await asyncio.wait_for(
                        conn.fetchval("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"),
                        timeout=2.0
                    )

                    # Check for long-running queries
                    long_queries = await asyncio.wait_for(
                        conn.fetchval(
                            "SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '30 seconds'"
                        ),
                        timeout=2.0
                    )

                    health_result = {
                        "status": "healthy",
                        "response_time_ms": response_time,
                        "database_size": db_size,
                        "active_connections": active_connections,
                        "long_running_queries": long_queries,
                        "timestamp": datetime.utcnow().isoformat()
                    }

                    # Warn if response time is high or too many long queries
                    if response_time > 1000:  # > 1 second
                        health_result["warnings"] = health_result.get("warnings", [])
                        health_result["warnings"].append("High response time")

                    if long_queries > 5:
                        health_result["warnings"] = health_result.get("warnings", [])
                        health_result["warnings"].append("Multiple long-running queries detected")

                    return health_result

            except asyncio.TimeoutError:
                return {
                    "status": "degraded",
                    "error": "Database queries timed out",
                    "response_time_ms": response_time,
                    "timestamp": datetime.utcnow().isoformat()
                }

        except asyncio.TimeoutError:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return {
                "status": "unhealthy",
                "error": "Database connection timeout",
                "response_time_ms": response_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.error(f"Database health check error: {e}", exc_info=True)

            error_details = {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": response_time,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Add specific error categorization
            error_str = str(e).lower()
            if "connection" in error_str:
                error_details["error_type"] = "connection_error"
            elif "timeout" in error_str:
                error_details["error_type"] = "timeout_error"
            elif "permission" in error_str:
                error_details["error_type"] = "permission_error"
            else:
                error_details["error_type"] = "unknown_error"

            return error_details

    async def _check_cache_health(self) -> Dict:
        """Check cache connectivity and performance."""
        try:
            start_time = datetime.utcnow()

            # Test basic cache operations
            test_key = "health_check"
            test_value = {"timestamp": datetime.utcnow().isoformat()}

            # Set test value
            set_success = await cache.set(test_key, test_value, ttl=60)

            # Get test value
            retrieved_value = await cache.get(test_key)

            # Clean up
            await cache.delete(test_key)

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            if set_success and retrieved_value:
                return {
                    "status": "healthy",
                    "response_time_ms": response_time,
                    "operations": ["set", "get", "delete"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "degraded",
                    "warning": "Cache operations partially failed",
                    "response_time_ms": response_time,
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Cache health check error: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _get_system_metrics(self) -> Dict:
        """Get basic system resource metrics."""
        try:
            return {
                "status": "healthy",
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _get_system_info(self) -> Dict:
        """Get basic system information."""
        try:
            import platform
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "hostname": platform.node()
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}

    def _get_resource_usage(self) -> Dict:
        """Get detailed resource usage information."""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "count_logical": psutil.cpu_count(logical=True)
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_gb": round((disk.total - disk.free) / (1024**3), 2),
                    "percent": round((disk.total - disk.free) / disk.total * 100, 2)
                }
            }
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return {"error": str(e)}

    async def _get_database_metrics(self) -> Dict:
        """Get database-specific metrics."""
        try:
            async with db.get_connection() as conn:
                # Get table sizes
                table_sizes = await conn.fetch(
                    """
                    SELECT
                        tablename,
                        pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY pg_total_relation_size(tablename::regclass) DESC
                    LIMIT 10
                    """
                )

                # Get connection stats
                connection_stats = await conn.fetchrow(
                    """
                    SELECT
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity
                    """
                )

                return {
                    "table_sizes": [dict(row) for row in table_sizes],
                    "connections": dict(connection_stats) if connection_stats else {},
                    "status": "healthy"
                }

        except Exception as e:
            logger.error(f"Error getting database metrics: {e}")
            return {"error": str(e), "status": "error"}

    async def _get_cache_metrics(self) -> Dict:
        """Get cache-specific metrics."""
        try:
            # Basic cache health check
            health_status = await cache.health_check()

            return {
                "status": "healthy" if health_status else "unhealthy",
                "connected": health_status
            }

        except Exception as e:
            logger.error(f"Error getting cache metrics: {e}")
            return {"error": str(e), "status": "error"}

    async def _get_api_metrics(self) -> Dict:
        """Get API-specific metrics."""
        try:
            # This would typically include request counts, response times, etc.
            # For now, return basic status
            return {
                "status": "healthy",
                "endpoints": ["stocks", "predictions", "auth", "system"],
                "version": "7.0.0"
            }

        except Exception as e:
            logger.error(f"Error getting API metrics: {e}")
            return {"error": str(e), "status": "error"}

    async def _get_database_jobs(self) -> List[Dict]:
        """Get database background job information."""
        try:
            async with db.get_connection() as conn:
                # Get long-running queries
                long_queries = await conn.fetch(
                    """
                    SELECT
                        pid,
                        state,
                        query,
                        query_start,
                        now() - query_start as duration
                    FROM pg_stat_activity
                    WHERE state = 'active'
                    AND query NOT LIKE '%pg_stat_activity%'
                    AND now() - query_start > interval '5 seconds'
                    """
                )

                jobs = []
                for query in long_queries:
                    jobs.append({
                        "job_id": f"db_query_{query['pid']}",
                        "name": "Database Query",
                        "status": query["state"],
                        "duration": str(query["duration"]),
                        "type": "database_query",
                        "details": query["query"][:100] + "..." if len(query["query"]) > 100 else query["query"]
                    })

                return jobs

        except Exception as e:
            logger.error(f"Error getting database jobs: {e}")
            return []

    def _get_uptime(self) -> str:
        """Get API uptime (simplified implementation)."""
        try:
            import time
            # This is a simplified implementation
            # In production, you'd want to track actual startup time
            uptime_seconds = time.time() % (24 * 3600)  # Reset daily for demo
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        except Exception:
            return "unknown"