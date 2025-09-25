"""
Auto-Scaling System for MiraiKakaku
Implements intelligent scaling based on metrics, load patterns, and business logic
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import google.auth
from google.cloud import monitoring_v3
from google.cloud import run_v2
import redis.asyncio as aioredis

from shared.utils.logger import get_logger

logger = get_logger("miraikakaku.scaling")

class ScalingDirection(Enum):
    UP = "up"
    DOWN = "down"
    MAINTAIN = "maintain"

class ScalingTrigger(Enum):
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_DEPTH = "queue_depth"
    CUSTOM_METRIC = "custom_metric"

@dataclass
class ScalingMetric:
    """Scaling metric definition"""
    name: str
    current_value: float
    threshold_up: float
    threshold_down: float
    weight: float = 1.0
    trend_factor: float = 0.0  # Positive = increasing, Negative = decreasing

@dataclass
class ScalingDecision:
    """Scaling decision result"""
    service_name: str
    direction: ScalingDirection
    target_instances: int
    current_instances: int
    confidence: float
    reasoning: str
    metrics_used: List[ScalingMetric]
    timestamp: datetime

@dataclass
class ServiceConfig:
    """Service scaling configuration"""
    name: str
    min_instances: int
    max_instances: int
    target_cpu_utilization: float = 70.0
    target_memory_utilization: float = 80.0
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 600  # seconds
    custom_metrics: Dict[str, Dict[str, Any]] = None

class MetricsCollector:
    """Collects metrics from various sources"""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"

    async def collect_cloud_run_metrics(self, service_name: str, minutes: int = 5) -> Dict[str, float]:
        """Collect Cloud Run service metrics"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes)

        try:
            # CPU utilization
            cpu_filter = f'resource.type="cloud_run_revision" AND resource.labels.service_name="{service_name}"'
            cpu_query = monitoring_v3.ListTimeSeriesRequest(
                name=self.project_name,
                filter=f'metric.type="run.googleapis.com/container/cpu/utilizations" AND {cpu_filter}',
                interval=monitoring_v3.TimeInterval({
                    "end_time": {"seconds": int(end_time.timestamp())},
                    "start_time": {"seconds": int(start_time.timestamp())},
                }),
            )

            cpu_series = self.monitoring_client.list_time_series(request=cpu_query)
            cpu_values = []
            for series in cpu_series:
                for point in series.points:
                    cpu_values.append(point.value.double_value * 100)  # Convert to percentage

            # Memory utilization
            memory_filter = f'resource.type="cloud_run_revision" AND resource.labels.service_name="{service_name}"'
            memory_query = monitoring_v3.ListTimeSeriesRequest(
                name=self.project_name,
                filter=f'metric.type="run.googleapis.com/container/memory/utilizations" AND {memory_filter}',
                interval=monitoring_v3.TimeInterval({
                    "end_time": {"seconds": int(end_time.timestamp())},
                    "start_time": {"seconds": int(start_time.timestamp())},
                }),
            )

            memory_series = self.monitoring_client.list_time_series(request=memory_query)
            memory_values = []
            for series in memory_series:
                for point in series.points:
                    memory_values.append(point.value.double_value * 100)  # Convert to percentage

            # Request count/rate
            request_query = monitoring_v3.ListTimeSeriesRequest(
                name=self.project_name,
                filter=f'metric.type="run.googleapis.com/request_count" AND {cpu_filter}',
                interval=monitoring_v3.TimeInterval({
                    "end_time": {"seconds": int(end_time.timestamp())},
                    "start_time": {"seconds": int(start_time.timestamp())},
                }),
            )

            request_series = self.monitoring_client.list_time_series(request=request_query)
            request_counts = []
            for series in request_series:
                for point in series.points:
                    request_counts.append(point.value.int64_value)

            return {
                "cpu_utilization": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "memory_utilization": sum(memory_values) / len(memory_values) if memory_values else 0,
                "request_rate": sum(request_counts) / (minutes * 60) if request_counts else 0,  # requests per second
                "avg_cpu_trend": self._calculate_trend(cpu_values),
                "avg_memory_trend": self._calculate_trend(memory_values)
            }

        except Exception as e:
            logger.error(f"Failed to collect metrics for {service_name}: {e}")
            return {}

    async def collect_custom_metrics(self, service_name: str, redis_client) -> Dict[str, float]:
        """Collect custom business metrics from Redis"""
        try:
            # API response times
            response_times = await redis_client.hgetall(f"{service_name}:response_times")
            avg_response_time = 0
            if response_times:
                times = [float(v) for v in response_times.values()]
                avg_response_time = sum(times) / len(times)

            # Error rates
            error_rates = await redis_client.hgetall(f"{service_name}:error_rates")
            avg_error_rate = 0
            if error_rates:
                rates = [float(v) for v in error_rates.values()]
                avg_error_rate = sum(rates) / len(rates)

            # Queue depths (for batch services)
            queue_depth = await redis_client.get(f"{service_name}:queue_depth")
            queue_depth = int(queue_depth) if queue_depth else 0

            # Active connections
            active_connections = await redis_client.get(f"{service_name}:active_connections")
            active_connections = int(active_connections) if active_connections else 0

            return {
                "avg_response_time": avg_response_time,
                "error_rate": avg_error_rate,
                "queue_depth": queue_depth,
                "active_connections": active_connections
            }

        except Exception as e:
            logger.error(f"Failed to collect custom metrics for {service_name}: {e}")
            return {}

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend factor from time series values"""
        if len(values) < 2:
            return 0.0

        # Simple linear regression slope
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n

        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return slope / y_mean if y_mean != 0 else 0.0  # Normalize by mean

class ScalingEngine:
    """Core scaling decision engine"""

    def __init__(self, project_id: str, redis_url: str = "redis://localhost:6379"):
        self.project_id = project_id
        self.metrics_collector = MetricsCollector(project_id)
        self.redis_client = None
        self.scaling_history = []
        self.cooldown_tracker = {}

    async def _get_redis_client(self):
        if self.redis_client is None:
            self.redis_client = aioredis.from_url(redis_url)
        return self.redis_client

    async def analyze_scaling_need(self, service_config: ServiceConfig) -> ScalingDecision:
        """Analyze if scaling is needed for a service"""
        service_name = service_config.name

        # Collect metrics
        cloud_metrics = await self.metrics_collector.collect_cloud_run_metrics(service_name)
        redis_client = await self._get_redis_client()
        custom_metrics = await self.metrics_collector.collect_custom_metrics(service_name, redis_client)

        # Get current instance count
        current_instances = await self._get_current_instances(service_name)

        # Create scaling metrics
        metrics = []

        # CPU metric
        if "cpu_utilization" in cloud_metrics:
            metrics.append(ScalingMetric(
                name="cpu_utilization",
                current_value=cloud_metrics["cpu_utilization"],
                threshold_up=service_config.target_cpu_utilization,
                threshold_down=service_config.target_cpu_utilization * 0.5,
                weight=1.0,
                trend_factor=cloud_metrics.get("avg_cpu_trend", 0.0)
            ))

        # Memory metric
        if "memory_utilization" in cloud_metrics:
            metrics.append(ScalingMetric(
                name="memory_utilization",
                current_value=cloud_metrics["memory_utilization"],
                threshold_up=service_config.target_memory_utilization,
                threshold_down=service_config.target_memory_utilization * 0.5,
                weight=1.0,
                trend_factor=cloud_metrics.get("avg_memory_trend", 0.0)
            ))

        # Request rate metric
        if "request_rate" in cloud_metrics:
            # Dynamic threshold based on current capacity
            base_capacity = current_instances * 10  # Assume 10 RPS per instance
            metrics.append(ScalingMetric(
                name="request_rate",
                current_value=cloud_metrics["request_rate"],
                threshold_up=base_capacity * 0.8,
                threshold_down=base_capacity * 0.3,
                weight=0.8
            ))

        # Response time metric
        if "avg_response_time" in custom_metrics:
            metrics.append(ScalingMetric(
                name="response_time",
                current_value=custom_metrics["avg_response_time"],
                threshold_up=2000,  # 2 seconds
                threshold_down=500,  # 0.5 seconds
                weight=0.6
            ))

        # Queue depth metric (for batch services)
        if "queue_depth" in custom_metrics and custom_metrics["queue_depth"] > 0:
            metrics.append(ScalingMetric(
                name="queue_depth",
                current_value=custom_metrics["queue_depth"],
                threshold_up=100,
                threshold_down=10,
                weight=1.2
            ))

        # Make scaling decision
        decision = self._make_scaling_decision(service_config, current_instances, metrics)

        # Apply cooldown logic
        decision = self._apply_cooldown(decision, service_config)

        # Store decision history
        self.scaling_history.append(decision)

        # Keep only last 100 decisions
        self.scaling_history = self.scaling_history[-100:]

        return decision

    def _make_scaling_decision(
        self,
        service_config: ServiceConfig,
        current_instances: int,
        metrics: List[ScalingMetric]
    ) -> ScalingDecision:
        """Make scaling decision based on metrics"""
        if not metrics:
            return ScalingDecision(
                service_name=service_config.name,
                direction=ScalingDirection.MAINTAIN,
                target_instances=current_instances,
                current_instances=current_instances,
                confidence=0.0,
                reasoning="No metrics available",
                metrics_used=metrics,
                timestamp=datetime.utcnow()
            )

        # Calculate weighted scores
        scale_up_score = 0.0
        scale_down_score = 0.0
        total_weight = 0.0

        reasoning_parts = []

        for metric in metrics:
            weight = metric.weight
            total_weight += weight

            # Scale up conditions
            if metric.current_value > metric.threshold_up:
                excess_ratio = (metric.current_value - metric.threshold_up) / metric.threshold_up
                metric_score = min(excess_ratio * weight, weight)  # Cap at weight

                # Apply trend factor (positive trend increases urgency)
                if metric.trend_factor > 0:
                    metric_score *= (1 + metric.trend_factor)

                scale_up_score += metric_score
                reasoning_parts.append(f"{metric.name}: {metric.current_value:.1f} > {metric.threshold_up}")

            # Scale down conditions
            elif metric.current_value < metric.threshold_down:
                under_ratio = (metric.threshold_down - metric.current_value) / metric.threshold_down
                metric_score = min(under_ratio * weight, weight)

                # Apply trend factor (negative trend increases scale-down urgency)
                if metric.trend_factor < 0:
                    metric_score *= (1 - metric.trend_factor)

                scale_down_score += metric_score
                reasoning_parts.append(f"{metric.name}: {metric.current_value:.1f} < {metric.threshold_down}")

        # Normalize scores
        if total_weight > 0:
            scale_up_score /= total_weight
            scale_down_score /= total_weight

        # Decision logic
        confidence_threshold = 0.3
        target_instances = current_instances
        direction = ScalingDirection.MAINTAIN
        confidence = 0.0

        if scale_up_score > confidence_threshold and scale_up_score > scale_down_score:
            direction = ScalingDirection.UP
            confidence = scale_up_score
            # Calculate target instances (conservative scaling)
            scale_factor = min(1 + scale_up_score, 2.0)  # Max 2x scaling
            target_instances = min(
                int(current_instances * scale_factor),
                service_config.max_instances
            )

        elif scale_down_score > confidence_threshold and scale_down_score > scale_up_score:
            direction = ScalingDirection.DOWN
            confidence = scale_down_score
            # Calculate target instances (conservative scaling)
            scale_factor = max(1 - scale_down_score * 0.5, 0.5)  # Max 50% reduction
            target_instances = max(
                int(current_instances * scale_factor),
                service_config.min_instances
            )

        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "All metrics within normal range"

        return ScalingDecision(
            service_name=service_config.name,
            direction=direction,
            target_instances=target_instances,
            current_instances=current_instances,
            confidence=confidence,
            reasoning=reasoning,
            metrics_used=metrics,
            timestamp=datetime.utcnow()
        )

    def _apply_cooldown(self, decision: ScalingDecision, service_config: ServiceConfig) -> ScalingDecision:
        """Apply cooldown logic to prevent flapping"""
        service_name = service_config.name
        current_time = datetime.utcnow()

        # Check if we're in cooldown period
        if service_name in self.cooldown_tracker:
            last_scaling = self.cooldown_tracker[service_name]

            if decision.direction == ScalingDirection.UP:
                cooldown_period = service_config.scale_up_cooldown
            else:
                cooldown_period = service_config.scale_down_cooldown

            if (current_time - last_scaling['timestamp']).total_seconds() < cooldown_period:
                # Still in cooldown, maintain current state
                decision.direction = ScalingDirection.MAINTAIN
                decision.target_instances = decision.current_instances
                decision.reasoning += f" | COOLDOWN: {cooldown_period}s remaining"
                decision.confidence *= 0.1  # Reduce confidence during cooldown

        # Update cooldown tracker if action is taken
        if decision.direction != ScalingDirection.MAINTAIN:
            self.cooldown_tracker[service_name] = {
                'timestamp': current_time,
                'direction': decision.direction
            }

        return decision

    async def _get_current_instances(self, service_name: str) -> int:
        """Get current number of instances for a Cloud Run service"""
        try:
            # This would use the Cloud Run API to get current instance count
            # For now, return a mock value
            return 2  # Mock value
        except Exception as e:
            logger.error(f"Failed to get current instances for {service_name}: {e}")
            return 1

class AutoScaler:
    """Main auto-scaling orchestrator"""

    def __init__(self, project_id: str, redis_url: str = "redis://localhost:6379"):
        self.project_id = project_id
        self.scaling_engine = ScalingEngine(project_id, redis_url)
        self.service_configs = {}
        self.is_running = False

    def add_service(self, config: ServiceConfig):
        """Add a service to auto-scaling management"""
        self.service_configs[config.name] = config
        logger.info(f"Added service to auto-scaling: {config.name}")

    async def start_auto_scaling(self, check_interval: int = 60):
        """Start the auto-scaling loop"""
        self.is_running = True
        logger.info(f"Starting auto-scaling with {check_interval}s interval")

        while self.is_running:
            try:
                # Process all services
                for service_name, config in self.service_configs.items():
                    decision = await self.scaling_engine.analyze_scaling_need(config)

                    logger.info(f"Scaling decision for {service_name}: "
                               f"{decision.direction.value} to {decision.target_instances} instances "
                               f"(confidence: {decision.confidence:.2f})")

                    # Execute scaling action
                    if decision.direction != ScalingDirection.MAINTAIN:
                        await self._execute_scaling(decision)

                await asyncio.sleep(check_interval)

            except Exception as e:
                logger.error(f"Error in auto-scaling loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying

    async def _execute_scaling(self, decision: ScalingDecision) -> bool:
        """Execute the scaling decision"""
        try:
            # This would use the Cloud Run API to scale the service
            # For now, just log the action
            logger.info(f"SCALING ACTION: {decision.service_name} "
                       f"{decision.direction.value} from {decision.current_instances} "
                       f"to {decision.target_instances} instances")

            # Store scaling action in Redis for monitoring
            redis_client = await self.scaling_engine._get_redis_client()
            scaling_record = {
                'service': decision.service_name,
                'direction': decision.direction.value,
                'from_instances': decision.current_instances,
                'to_instances': decision.target_instances,
                'confidence': decision.confidence,
                'reasoning': decision.reasoning,
                'timestamp': decision.timestamp.isoformat()
            }

            await redis_client.lpush(
                "scaling_history",
                json.dumps(scaling_record)
            )

            # Keep only last 1000 scaling events
            await redis_client.ltrim("scaling_history", 0, 999)

            return True

        except Exception as e:
            logger.error(f"Failed to execute scaling for {decision.service_name}: {e}")
            return False

    def stop_auto_scaling(self):
        """Stop the auto-scaling loop"""
        self.is_running = False
        logger.info("Auto-scaling stopped")

    async def get_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling status and metrics"""
        status = {
            "is_running": self.is_running,
            "managed_services": list(self.service_configs.keys()),
            "last_decisions": [asdict(d) for d in self.scaling_engine.scaling_history[-10:]],
            "cooldown_status": {}
        }

        # Add cooldown status
        current_time = datetime.utcnow()
        for service_name, cooldown_info in self.scaling_engine.cooldown_tracker.items():
            if service_name in self.service_configs:
                config = self.service_configs[service_name]
                if cooldown_info['direction'] == ScalingDirection.UP:
                    cooldown_period = config.scale_up_cooldown
                else:
                    cooldown_period = config.scale_down_cooldown

                elapsed = (current_time - cooldown_info['timestamp']).total_seconds()
                remaining = max(0, cooldown_period - elapsed)

                status["cooldown_status"][service_name] = {
                    "in_cooldown": remaining > 0,
                    "remaining_seconds": remaining,
                    "last_direction": cooldown_info['direction'].value
                }

        return status


# Usage example
if __name__ == "__main__":
    async def main():
        # Initialize auto-scaler
        auto_scaler = AutoScaler("your-project-id")

        # Configure services
        api_config = ServiceConfig(
            name="miraikakaku-api-prod",
            min_instances=1,
            max_instances=20,
            target_cpu_utilization=70.0,
            target_memory_utilization=80.0,
            scale_up_cooldown=300,
            scale_down_cooldown=600
        )

        batch_config = ServiceConfig(
            name="miraikakaku-batch-prod",
            min_instances=0,
            max_instances=10,
            target_cpu_utilization=80.0,
            target_memory_utilization=85.0,
            scale_up_cooldown=180,
            scale_down_cooldown=900
        )

        auto_scaler.add_service(api_config)
        auto_scaler.add_service(batch_config)

        # Start auto-scaling (this would run indefinitely)
        # await auto_scaler.start_auto_scaling(check_interval=60)

        # For testing, just check one service
        decision = await auto_scaler.scaling_engine.analyze_scaling_need(api_config)
        print(f"Scaling decision: {asdict(decision)}")

        # Get status
        status = await auto_scaler.get_scaling_status()
        print(f"Auto-scaling status: {json.dumps(status, indent=2, default=str)}")

    # asyncio.run(main())