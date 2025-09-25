"""
Performance Monitoring and Optimization System
Monitors system performance and provides actionable insights
"""
import asyncio
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import redis
from prometheus_client import Gauge, Counter, Histogram, generate_latest

# Configure logging
from shared.utils.logger import get_logger, log_with_context

logger = get_logger("miraikakaku.performance_monitor")

# Prometheus metrics
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
REQUEST_COUNT = Counter('http_requests_total', 'HTTP requests count', ['method', 'endpoint', 'status'])
DB_QUERY_DURATION = Histogram('db_query_duration_seconds', 'Database query duration', ['operation', 'table'])
SYSTEM_CPU_USAGE = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')
SYSTEM_MEMORY_USAGE = Gauge('system_memory_usage_percent', 'System memory usage percentage')
ACTIVE_CONNECTIONS = Gauge('db_active_connections', 'Database active connections')

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
    database_connections: int
    response_times: Dict[str, float]
    error_rates: Dict[str, float]

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation data structure"""
    category: str  # 'database', 'api', 'frontend', 'infrastructure'
    priority: str  # 'high', 'medium', 'low'
    title: str
    description: str
    impact: str  # Expected performance impact
    implementation_effort: str  # 'low', 'medium', 'high'
    code_example: Optional[str] = None

class PerformanceMonitor:
    """Main performance monitoring class"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.monitoring_interval = 30  # seconds
        self.is_running = False
        self.metrics_history = []

    async def start_monitoring(self):
        """Start continuous performance monitoring"""
        self.is_running = True
        logger.info("Starting performance monitoring")

        while self.is_running:
            try:
                metrics = await self.collect_metrics()
                self.store_metrics(metrics)
                self.analyze_and_alert(metrics)
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)

    async def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        # System metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {}
        network_io = psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}

        # Update Prometheus metrics
        SYSTEM_CPU_USAGE.set(cpu_usage)
        SYSTEM_MEMORY_USAGE.set(memory.percent)

        # Database metrics (would need actual DB connection)
        db_connections = await self.get_database_connections()
        ACTIVE_CONNECTIONS.set(db_connections)

        # API response times (from cache or recent measurements)
        response_times = await self.get_response_times()
        error_rates = await self.get_error_rates()

        metrics = PerformanceMetrics(
            timestamp=datetime.utcnow(),
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_io=disk_io,
            network_io=network_io,
            database_connections=db_connections,
            response_times=response_times,
            error_rates=error_rates
        )

        logger.info(f"Collected metrics: CPU={cpu_usage:.1f}%, Memory={memory.percent:.1f}%")
        return metrics

    async def get_database_connections(self) -> int:
        """Get current database connection count"""
        try:
            # This would connect to your actual database
            # For now, return a mock value
            return 5  # Mock value
        except Exception as e:
            logger.error(f"Failed to get DB connections: {e}")
            return 0

    async def get_response_times(self) -> Dict[str, float]:
        """Get recent API response times"""
        try:
            # Get from Redis cache or calculate from recent requests
            cached_times = self.redis_client.hgetall("api_response_times")
            return {k.decode(): float(v) for k, v in cached_times.items()}
        except Exception:
            return {"health": 0.1, "stock": 0.5, "predictions": 1.2}  # Mock values

    async def get_error_rates(self) -> Dict[str, float]:
        """Get recent error rates by endpoint"""
        try:
            cached_rates = self.redis_client.hgetall("api_error_rates")
            return {k.decode(): float(v) for k, v in cached_rates.items()}
        except Exception:
            return {"health": 0.0, "stock": 0.02, "predictions": 0.05}  # Mock values

    def store_metrics(self, metrics: PerformanceMetrics):
        """Store metrics for historical analysis"""
        self.metrics_history.append(metrics)

        # Keep only last 24 hours of data
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.metrics_history = [
            m for m in self.metrics_history
            if m.timestamp > cutoff_time
        ]

        # Store in Redis for real-time access
        metrics_data = {
            'timestamp': metrics.timestamp.isoformat(),
            'cpu_usage': metrics.cpu_usage,
            'memory_usage': metrics.memory_usage,
            'db_connections': metrics.database_connections
        }
        self.redis_client.setex(
            "current_metrics",
            300,  # 5 minutes TTL
            json.dumps(metrics_data)
        )

    def analyze_and_alert(self, metrics: PerformanceMetrics):
        """Analyze metrics and generate alerts/recommendations"""
        recommendations = []

        # CPU usage analysis
        if metrics.cpu_usage > 80:
            recommendations.append(OptimizationRecommendation(
                category="infrastructure",
                priority="high",
                title="High CPU Usage Detected",
                description=f"CPU usage is at {metrics.cpu_usage:.1f}%, consider scaling up",
                impact="Significant performance degradation likely",
                implementation_effort="medium"
            ))

        # Memory usage analysis
        if metrics.memory_usage > 85:
            recommendations.append(OptimizationRecommendation(
                category="infrastructure",
                priority="high",
                title="High Memory Usage",
                description=f"Memory usage is at {metrics.memory_usage:.1f}%",
                impact="Risk of out-of-memory errors",
                implementation_effort="low",
                code_example="# Scale up Cloud Run memory\ngcloud run services update SERVICE --memory=1Gi"
            ))

        # Response time analysis
        for endpoint, time_ms in metrics.response_times.items():
            if time_ms > 2000:  # 2 seconds
                recommendations.append(OptimizationRecommendation(
                    category="api",
                    priority="medium",
                    title=f"Slow Response Time: {endpoint}",
                    description=f"Endpoint {endpoint} responding in {time_ms}ms",
                    impact="Poor user experience",
                    implementation_effort="medium",
                    code_example="# Add caching\n@lru_cache(maxsize=128)\ndef cached_function():\n    pass"
                ))

        # Database connections analysis
        if metrics.database_connections > 20:
            recommendations.append(OptimizationRecommendation(
                category="database",
                priority="medium",
                title="High Database Connection Count",
                description=f"Currently {metrics.database_connections} active connections",
                impact="Database performance degradation",
                implementation_effort="low",
                code_example="# Implement connection pooling\nfrom sqlalchemy.pool import QueuePool\nengine = create_engine('postgresql://...', poolclass=QueuePool, pool_size=5)"
            ))

        # Log and store recommendations
        if recommendations:
            logger.warning(f"Generated {len(recommendations)} performance recommendations")
            self.store_recommendations(recommendations)

    def store_recommendations(self, recommendations: List[OptimizationRecommendation]):
        """Store optimization recommendations"""
        recommendations_data = []
        for rec in recommendations:
            rec_dict = {
                'category': rec.category,
                'priority': rec.priority,
                'title': rec.title,
                'description': rec.description,
                'impact': rec.impact,
                'implementation_effort': rec.implementation_effort,
                'code_example': rec.code_example,
                'timestamp': datetime.utcnow().isoformat()
            }
            recommendations_data.append(rec_dict)

        # Store in Redis
        self.redis_client.setex(
            "performance_recommendations",
            3600,  # 1 hour TTL
            json.dumps(recommendations_data)
        )

    def get_current_recommendations(self) -> List[OptimizationRecommendation]:
        """Get current optimization recommendations"""
        try:
            stored_data = self.redis_client.get("performance_recommendations")
            if stored_data:
                recommendations_data = json.loads(stored_data)
                return [
                    OptimizationRecommendation(**rec)
                    for rec in recommendations_data
                ]
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")

        return []

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.metrics_history:
            return {"error": "No metrics data available"}

        recent_metrics = self.metrics_history[-60:]  # Last 60 measurements

        # Calculate averages and trends
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)

        # Response time trends
        response_time_trends = {}
        for endpoint in ["health", "stock", "predictions"]:
            times = [m.response_times.get(endpoint, 0) for m in recent_metrics]
            response_time_trends[endpoint] = {
                "average": sum(times) / len(times) if times else 0,
                "max": max(times) if times else 0,
                "min": min(times) if times else 0
            }

        # Performance score calculation
        performance_score = self.calculate_performance_score(recent_metrics)

        report = {
            "report_generated": datetime.utcnow().isoformat(),
            "metrics_period": f"Last {len(recent_metrics)} measurements",
            "system_performance": {
                "average_cpu_usage": round(avg_cpu, 2),
                "average_memory_usage": round(avg_memory, 2),
                "performance_score": performance_score
            },
            "response_time_analysis": response_time_trends,
            "recommendations": [
                {
                    "category": rec.category,
                    "priority": rec.priority,
                    "title": rec.title,
                    "description": rec.description,
                    "impact": rec.impact
                }
                for rec in self.get_current_recommendations()
            ],
            "optimization_priorities": self.get_optimization_priorities()
        }

        return report

    def calculate_performance_score(self, metrics: List[PerformanceMetrics]) -> float:
        """Calculate overall performance score (0-100)"""
        if not metrics:
            return 0

        cpu_score = max(0, 100 - (sum(m.cpu_usage for m in metrics) / len(metrics)))
        memory_score = max(0, 100 - (sum(m.memory_usage for m in metrics) / len(metrics)))

        # Response time score
        avg_response_times = []
        for m in metrics:
            avg_response_times.extend(m.response_times.values())

        if avg_response_times:
            avg_response_time = sum(avg_response_times) / len(avg_response_times)
            response_score = max(0, 100 - (avg_response_time / 10))  # 10ms = 99 score
        else:
            response_score = 50  # Neutral score if no data

        # Weighted average
        overall_score = (cpu_score * 0.3 + memory_score * 0.3 + response_score * 0.4)
        return round(overall_score, 1)

    def get_optimization_priorities(self) -> List[Dict[str, Any]]:
        """Get prioritized list of optimizations"""
        recommendations = self.get_current_recommendations()

        # Group by priority and category
        priorities = {
            "immediate_action": [],
            "short_term": [],
            "long_term": []
        }

        for rec in recommendations:
            if rec.priority == "high":
                priorities["immediate_action"].append({
                    "title": rec.title,
                    "category": rec.category,
                    "impact": rec.impact
                })
            elif rec.priority == "medium":
                priorities["short_term"].append({
                    "title": rec.title,
                    "category": rec.category,
                    "impact": rec.impact
                })
            else:
                priorities["long_term"].append({
                    "title": rec.title,
                    "category": rec.category,
                    "impact": rec.impact
                })

        return priorities

    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_running = False
        logger.info("Performance monitoring stopped")


# Performance middleware for FastAPI
class PerformanceMiddleware:
    """Middleware to track API performance"""

    def __init__(self, app):
        self.app = app
        self.monitor = PerformanceMonitor()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()

            # Process request
            await self.app(scope, receive, send)

            # Record metrics
            duration = time.time() - start_time
            method = scope["method"]
            path = scope["path"]

            # Update Prometheus metrics
            REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)

            # Store in Redis for real-time monitoring
            self.monitor.redis_client.hset(
                "api_response_times",
                path,
                duration * 1000  # Convert to milliseconds
            )
        else:
            await self.app(scope, receive, send)


# Usage example
if __name__ == "__main__":
    async def main():
        monitor = PerformanceMonitor()

        # Start monitoring
        monitoring_task = asyncio.create_task(monitor.start_monitoring())

        # Generate report after some time
        await asyncio.sleep(60)  # Wait 1 minute

        report = monitor.generate_performance_report()
        print(json.dumps(report, indent=2))

        monitor.stop_monitoring()
        await monitoring_task

    asyncio.run(main())