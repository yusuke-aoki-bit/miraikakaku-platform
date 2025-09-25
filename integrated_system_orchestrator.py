#!/usr/bin/env python3
"""
統合システムオーケストレーター
Integrated System Orchestrator for Miraikakaku Platform

このモジュールは全システム コンポーネントを統合・管理します：
- システム統合とパフォーマンス最適化
- 分散システムの協調とメッセージング
- リソース管理と負荷分散
- ヘルスチェックと自動復旧
- メトリクス収集と監視
"""

import asyncio
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import uuid
import gc
import psutil
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our custom systems
try:
    from advanced_ml_engine import AdvancedMLEngine
    from realtime_streaming_engine import RealtimeStreamingEngine
    from ai_assistant_system import AIAssistantSystem
    from advanced_analytics_system import AdvancedAnalyticsSystem
    from enterprise_features_system import EnterpriseFeaturesSystem
    ML_SYSTEMS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some ML systems not available: {e}")
    ML_SYSTEMS_AVAILABLE = False

class ServiceStatus(Enum):
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    RECOVERING = "recovering"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ServiceConfig:
    name: str
    enabled: bool = True
    auto_restart: bool = True
    max_retries: int = 3
    retry_delay: int = 30
    health_check_interval: int = 60
    memory_limit_mb: int = 1024
    cpu_limit_percent: int = 80
    dependencies: List[str] = field(default_factory=list)
    priority: Priority = Priority.MEDIUM

@dataclass
class ServiceInstance:
    config: ServiceConfig
    status: ServiceStatus
    instance: Optional[Any] = None
    start_time: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    restart_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    active_services: int
    total_requests: int
    error_rate: float
    response_time_ms: float

@dataclass
class PerformanceProfile:
    name: str
    max_services: int
    memory_limit_mb: int
    cpu_threshold: float
    enable_caching: bool
    enable_compression: bool
    batch_size: int
    worker_threads: int

class ResourceMonitor:
    """System resource monitoring"""

    def __init__(self):
        self.metrics_history: deque = deque(maxlen=1000)
        self.alert_thresholds = {
            'cpu': 85.0,
            'memory': 90.0,
            'disk': 95.0
        }
        self.is_monitoring = False
        self.monitor_thread = None

    def start_monitoring(self, interval: int = 30):
        """Start resource monitoring"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Resource monitoring started")

    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Resource monitoring stopped")

    def _monitor_loop(self, interval: int):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                self._check_alerts(metrics)
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                time.sleep(interval)

    def _collect_metrics(self) -> SystemMetrics:
        """Collect system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            disk_usage_percent=disk.percent,
            active_services=0,  # Will be updated by orchestrator
            total_requests=0,   # Will be updated by orchestrator
            error_rate=0.0,     # Will be updated by orchestrator
            response_time_ms=0.0  # Will be updated by orchestrator
        )

    def _check_alerts(self, metrics: SystemMetrics):
        """Check for resource alerts"""
        alerts = []

        if metrics.cpu_percent > self.alert_thresholds['cpu']:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")

        if metrics.memory_percent > self.alert_thresholds['memory']:
            alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")

        if metrics.disk_usage_percent > self.alert_thresholds['disk']:
            alerts.append(f"High disk usage: {metrics.disk_usage_percent:.1f}%")

        for alert in alerts:
            logger.warning(f"RESOURCE ALERT: {alert}")

    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get current system metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None

    def get_metrics_history(self, minutes: int = 60) -> List[SystemMetrics]:
        """Get metrics history for specified time period"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.metrics_history if m.timestamp > cutoff]

class LoadBalancer:
    """Simple load balancer for service instances"""

    def __init__(self):
        self.service_pools: Dict[str, List[Any]] = defaultdict(list)
        self.round_robin_counters: Dict[str, int] = defaultdict(int)
        self.request_counts: Dict[str, int] = defaultdict(int)

    def register_service(self, service_name: str, instance: Any):
        """Register service instance"""
        self.service_pools[service_name].append(instance)
        logger.info(f"Registered {service_name} instance: {len(self.service_pools[service_name])} total")

    def get_service_instance(self, service_name: str) -> Optional[Any]:
        """Get service instance using round-robin"""
        pool = self.service_pools.get(service_name, [])
        if not pool:
            return None

        # Round-robin selection
        counter = self.round_robin_counters[service_name]
        instance = pool[counter % len(pool)]
        self.round_robin_counters[service_name] = (counter + 1) % len(pool)
        self.request_counts[service_name] += 1

        return instance

    def remove_service_instance(self, service_name: str, instance: Any):
        """Remove service instance"""
        if service_name in self.service_pools:
            pool = self.service_pools[service_name]
            if instance in pool:
                pool.remove(instance)
                logger.info(f"Removed {service_name} instance: {len(pool)} remaining")

    def get_load_stats(self) -> Dict[str, Dict[str, int]]:
        """Get load balancing statistics"""
        return {
            service_name: {
                'instances': len(pool),
                'requests': self.request_counts[service_name]
            }
            for service_name, pool in self.service_pools.items()
        }

class ServiceOrchestrator:
    """Service lifecycle management and orchestration"""

    def __init__(self):
        self.services: Dict[str, ServiceInstance] = {}
        self.load_balancer = LoadBalancer()
        self.resource_monitor = ResourceMonitor()
        self.performance_profiles: Dict[str, PerformanceProfile] = {}
        self.current_profile = "default"
        self.is_running = False
        self.management_thread = None

        # Initialize performance profiles
        self._init_performance_profiles()

    def _init_performance_profiles(self):
        """Initialize performance profiles"""
        self.performance_profiles = {
            "minimal": PerformanceProfile(
                name="minimal",
                max_services=3,
                memory_limit_mb=512,
                cpu_threshold=70.0,
                enable_caching=False,
                enable_compression=False,
                batch_size=10,
                worker_threads=2
            ),
            "default": PerformanceProfile(
                name="default",
                max_services=5,
                memory_limit_mb=1024,
                cpu_threshold=80.0,
                enable_caching=True,
                enable_compression=True,
                batch_size=50,
                worker_threads=4
            ),
            "high_performance": PerformanceProfile(
                name="high_performance",
                max_services=10,
                memory_limit_mb=2048,
                cpu_threshold=90.0,
                enable_caching=True,
                enable_compression=True,
                batch_size=100,
                worker_threads=8
            )
        }

    def register_service(self, config: ServiceConfig) -> bool:
        """Register a service for management"""
        if config.name in self.services:
            logger.warning(f"Service {config.name} already registered")
            return False

        instance = ServiceInstance(
            config=config,
            status=ServiceStatus.STOPPED
        )

        self.services[config.name] = instance
        logger.info(f"Registered service: {config.name}")
        return True

    def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        service = self.services.get(service_name)
        if not service:
            logger.error(f"Service not found: {service_name}")
            return False

        if service.status == ServiceStatus.RUNNING:
            logger.info(f"Service already running: {service_name}")
            return True

        # Check dependencies
        for dep in service.config.dependencies:
            dep_service = self.services.get(dep)
            if not dep_service or dep_service.status != ServiceStatus.RUNNING:
                logger.error(f"Dependency {dep} not running for service {service_name}")
                return False

        try:
            logger.info(f"Starting service: {service_name}")
            service.status = ServiceStatus.STARTING

            # Create service instance based on service name
            service.instance = self._create_service_instance(service_name)

            if service.instance and hasattr(service.instance, 'start'):
                service.instance.start()

            service.status = ServiceStatus.RUNNING
            service.start_time = datetime.now()
            service.restart_count = 0

            # Register with load balancer
            self.load_balancer.register_service(service_name, service.instance)

            logger.info(f"Service started successfully: {service_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to start service {service_name}: {e}")
            service.status = ServiceStatus.ERROR
            service.last_error = str(e)
            service.error_count += 1
            return False

    def _create_service_instance(self, service_name: str) -> Optional[Any]:
        """Create service instance based on service name"""
        if not ML_SYSTEMS_AVAILABLE:
            logger.warning(f"ML systems not available, creating mock service for {service_name}")
            return MockService(service_name)

        try:
            if service_name == "ml_engine":
                return AdvancedMLEngine()
            elif service_name == "streaming_engine":
                return RealtimeStreamingEngine()
            elif service_name == "ai_assistant":
                return AIAssistantSystem()
            elif service_name == "analytics_system":
                return AdvancedAnalyticsSystem()
            elif service_name == "enterprise_features":
                return EnterpriseFeaturesSystem()
            else:
                logger.warning(f"Unknown service type: {service_name}")
                return MockService(service_name)

        except Exception as e:
            logger.error(f"Error creating service instance {service_name}: {e}")
            return MockService(service_name)

    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        service = self.services.get(service_name)
        if not service:
            logger.error(f"Service not found: {service_name}")
            return False

        if service.status == ServiceStatus.STOPPED:
            logger.info(f"Service already stopped: {service_name}")
            return True

        try:
            logger.info(f"Stopping service: {service_name}")
            service.status = ServiceStatus.STOPPING

            if service.instance and hasattr(service.instance, 'stop'):
                service.instance.stop()

            # Remove from load balancer
            self.load_balancer.remove_service_instance(service_name, service.instance)

            service.status = ServiceStatus.STOPPED
            service.instance = None
            service.start_time = None

            logger.info(f"Service stopped successfully: {service_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop service {service_name}: {e}")
            service.status = ServiceStatus.ERROR
            service.last_error = str(e)
            return False

    def restart_service(self, service_name: str) -> bool:
        """Restart a specific service"""
        logger.info(f"Restarting service: {service_name}")

        if self.stop_service(service_name):
            time.sleep(2)  # Brief pause
            return self.start_service(service_name)

        return False

    def start_all_services(self) -> bool:
        """Start all enabled services in dependency order"""
        logger.info("Starting all services...")

        # Sort services by priority and dependencies
        sorted_services = self._get_startup_order()

        success_count = 0
        for service_name in sorted_services:
            service = self.services[service_name]
            if service.config.enabled:
                if self.start_service(service_name):
                    success_count += 1
                    time.sleep(1)  # Brief pause between starts

        logger.info(f"Started {success_count}/{len(sorted_services)} services")
        return success_count == len([s for s in self.services.values() if s.config.enabled])

    def stop_all_services(self) -> bool:
        """Stop all services in reverse dependency order"""
        logger.info("Stopping all services...")

        # Stop in reverse order
        sorted_services = list(reversed(self._get_startup_order()))

        success_count = 0
        for service_name in sorted_services:
            if self.stop_service(service_name):
                success_count += 1

        logger.info(f"Stopped {success_count}/{len(sorted_services)} services")
        return success_count == len(sorted_services)

    def _get_startup_order(self) -> List[str]:
        """Get service startup order based on dependencies and priority"""
        # Simple topological sort with priority
        ordered = []
        remaining = set(self.services.keys())

        while remaining:
            # Find services with no unmet dependencies
            ready = []
            for service_name in remaining:
                service = self.services[service_name]
                deps_met = all(
                    dep in ordered or dep not in self.services
                    for dep in service.config.dependencies
                )
                if deps_met:
                    ready.append((service_name, service.config.priority.value))

            if not ready:
                # Circular dependency or invalid dependency
                logger.warning("Circular dependency detected, starting remaining services")
                ready = [(name, self.services[name].config.priority.value) for name in remaining]

            # Sort by priority (higher value = higher priority)
            ready.sort(key=lambda x: x[1], reverse=True)

            # Add first ready service
            next_service = ready[0][0]
            ordered.append(next_service)
            remaining.remove(next_service)

        return ordered

    def check_service_health(self, service_name: str) -> bool:
        """Check health of a specific service"""
        service = self.services.get(service_name)
        if not service:
            return False

        if service.status != ServiceStatus.RUNNING:
            return False

        try:
            # Basic health check - service has instance and start time
            if not service.instance or not service.start_time:
                return False

            # Check if service has health check method
            if hasattr(service.instance, 'get_health_status'):
                health_status = service.instance.get_health_status()
                if isinstance(health_status, dict):
                    return health_status.get('status') == 'healthy'
                return bool(health_status)

            # Default health check - service is running
            service.last_health_check = datetime.now()
            return True

        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            service.error_count += 1
            service.last_error = str(e)
            return False

    def start_orchestration(self):
        """Start orchestration management"""
        self.is_running = True
        self.resource_monitor.start_monitoring()

        self.management_thread = threading.Thread(
            target=self._management_loop,
            daemon=True
        )
        self.management_thread.start()

        logger.info("Service orchestration started")

    def stop_orchestration(self):
        """Stop orchestration management"""
        self.is_running = False
        self.resource_monitor.stop_monitoring()

        if self.management_thread:
            self.management_thread.join(timeout=10)

        logger.info("Service orchestration stopped")

    def _management_loop(self):
        """Main orchestration management loop"""
        while self.is_running:
            try:
                # Perform health checks
                self._perform_health_checks()

                # Handle auto-restart
                self._handle_auto_restart()

                # Optimize performance
                self._optimize_performance()

                # Update metrics
                self._update_service_metrics()

                time.sleep(30)  # Run every 30 seconds

            except Exception as e:
                logger.error(f"Error in orchestration management: {e}")
                time.sleep(60)

    def _perform_health_checks(self):
        """Perform health checks on all services"""
        for service_name, service in self.services.items():
            if service.status == ServiceStatus.RUNNING:
                if not self.check_service_health(service_name):
                    logger.warning(f"Health check failed for service: {service_name}")

                    if service.config.auto_restart and service.restart_count < service.config.max_retries:
                        logger.info(f"Scheduling restart for unhealthy service: {service_name}")
                        service.status = ServiceStatus.RECOVERING

    def _handle_auto_restart(self):
        """Handle automatic service restart"""
        for service_name, service in self.services.items():
            if service.status == ServiceStatus.RECOVERING:
                if service.restart_count < service.config.max_retries:
                    logger.info(f"Auto-restarting service: {service_name} (attempt {service.restart_count + 1})")

                    if self.restart_service(service_name):
                        service.restart_count += 1
                        logger.info(f"Successfully restarted service: {service_name}")
                    else:
                        service.restart_count += 1
                        if service.restart_count >= service.config.max_retries:
                            logger.error(f"Max restart attempts reached for service: {service_name}")
                            service.status = ServiceStatus.ERROR
                        else:
                            time.sleep(service.config.retry_delay)

    def _optimize_performance(self):
        """Optimize system performance based on current load"""
        current_metrics = self.resource_monitor.get_current_metrics()
        if not current_metrics:
            return

        profile = self.performance_profiles[self.current_profile]

        # Auto-scale based on resource usage
        if current_metrics.cpu_percent > profile.cpu_threshold:
            logger.info(f"High CPU usage detected: {current_metrics.cpu_percent:.1f}%")
            self._scale_down_non_critical_services()
        elif current_metrics.memory_percent > 85:
            logger.info(f"High memory usage detected: {current_metrics.memory_percent:.1f}%")
            self._perform_memory_cleanup()

    def _scale_down_non_critical_services(self):
        """Scale down non-critical services to reduce load"""
        for service_name, service in self.services.items():
            if (service.config.priority == Priority.LOW and
                service.status == ServiceStatus.RUNNING and
                service.config.name not in ['ml_engine', 'streaming_engine']):

                logger.info(f"Temporarily stopping low-priority service: {service_name}")
                self.stop_service(service_name)
                break  # Stop one service at a time

    def _perform_memory_cleanup(self):
        """Perform memory cleanup"""
        logger.info("Performing memory cleanup...")
        gc.collect()

        # Clear service metrics older than 1 hour
        cutoff = datetime.now() - timedelta(hours=1)
        for service in self.services.values():
            if 'history' in service.metrics:
                service.metrics['history'] = [
                    m for m in service.metrics['history']
                    if m.get('timestamp', datetime.now()) > cutoff
                ]

    def _update_service_metrics(self):
        """Update service metrics"""
        current_metrics = self.resource_monitor.get_current_metrics()
        if current_metrics:
            # Update active services count
            active_count = len([s for s in self.services.values() if s.status == ServiceStatus.RUNNING])
            current_metrics.active_services = active_count

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        current_metrics = self.resource_monitor.get_current_metrics()
        load_stats = self.load_balancer.get_load_stats()

        service_statuses = {}
        for name, service in self.services.items():
            service_statuses[name] = {
                'status': service.status.value,
                'uptime': (datetime.now() - service.start_time).total_seconds() if service.start_time else 0,
                'restart_count': service.restart_count,
                'error_count': service.error_count,
                'last_error': service.last_error,
                'last_health_check': service.last_health_check.isoformat() if service.last_health_check else None
            }

        return {
            'system_metrics': {
                'cpu_percent': current_metrics.cpu_percent if current_metrics else 0,
                'memory_percent': current_metrics.memory_percent if current_metrics else 0,
                'memory_used_mb': current_metrics.memory_used_mb if current_metrics else 0,
                'disk_usage_percent': current_metrics.disk_usage_percent if current_metrics else 0
            },
            'services': service_statuses,
            'load_balancer': load_stats,
            'performance_profile': self.current_profile,
            'orchestration_running': self.is_running,
            'timestamp': datetime.now().isoformat()
        }

class MockService:
    """Mock service for testing when real services aren't available"""

    def __init__(self, name: str):
        self.name = name
        self.is_running = False

    def start(self):
        self.is_running = True
        logger.info(f"Mock service {self.name} started")

    def stop(self):
        self.is_running = False
        logger.info(f"Mock service {self.name} stopped")

    def get_health_status(self):
        return {'status': 'healthy' if self.is_running else 'stopped'}

class IntegratedSystemOrchestrator:
    """Main integrated system orchestrator"""

    def __init__(self):
        self.orchestrator = ServiceOrchestrator()
        self.is_initialized = False

        logger.info("Integrated System Orchestrator initialized")

    def initialize_services(self):
        """Initialize all service configurations"""

        # ML Engine Service
        ml_config = ServiceConfig(
            name="ml_engine",
            enabled=True,
            auto_restart=True,
            max_retries=3,
            health_check_interval=120,
            memory_limit_mb=512,
            priority=Priority.HIGH,
            dependencies=[]
        )
        self.orchestrator.register_service(ml_config)

        # Streaming Engine Service
        streaming_config = ServiceConfig(
            name="streaming_engine",
            enabled=True,
            auto_restart=True,
            max_retries=3,
            health_check_interval=60,
            memory_limit_mb=256,
            priority=Priority.HIGH,
            dependencies=[]
        )
        self.orchestrator.register_service(streaming_config)

        # AI Assistant Service
        ai_config = ServiceConfig(
            name="ai_assistant",
            enabled=True,
            auto_restart=True,
            max_retries=2,
            health_check_interval=90,
            memory_limit_mb=384,
            priority=Priority.MEDIUM,
            dependencies=["ml_engine"]
        )
        self.orchestrator.register_service(ai_config)

        # Analytics System Service
        analytics_config = ServiceConfig(
            name="analytics_system",
            enabled=True,
            auto_restart=True,
            max_retries=3,
            health_check_interval=180,
            memory_limit_mb=256,
            priority=Priority.MEDIUM,
            dependencies=["ml_engine"]
        )
        self.orchestrator.register_service(analytics_config)

        # Enterprise Features Service
        enterprise_config = ServiceConfig(
            name="enterprise_features",
            enabled=True,
            auto_restart=True,
            max_retries=2,
            health_check_interval=120,
            memory_limit_mb=256,
            priority=Priority.LOW,
            dependencies=["analytics_system"]
        )
        self.orchestrator.register_service(enterprise_config)

        self.is_initialized = True
        logger.info("All services configured successfully")

    def start_system(self):
        """Start the complete integrated system"""
        if not self.is_initialized:
            self.initialize_services()

        logger.info("🚀 Starting Integrated Miraikakaku System...")

        # Start orchestration
        self.orchestrator.start_orchestration()

        # Start all services
        if self.orchestrator.start_all_services():
            logger.info("✅ All services started successfully")
            return True
        else:
            logger.error("❌ Some services failed to start")
            return False

    def stop_system(self):
        """Stop the complete integrated system"""
        logger.info("🛑 Stopping Integrated Miraikakaku System...")

        # Stop all services
        self.orchestrator.stop_all_services()

        # Stop orchestration
        self.orchestrator.stop_orchestration()

        logger.info("✅ System stopped successfully")

    def get_system_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive system dashboard"""
        status = self.orchestrator.get_system_status()

        # Calculate uptime
        running_services = [
            s for s in status['services'].values()
            if s['status'] == 'running'
        ]

        total_uptime = sum(s['uptime'] for s in running_services)
        avg_uptime = total_uptime / len(running_services) if running_services else 0

        # Calculate health score
        total_services = len(status['services'])
        healthy_services = len([
            s for s in status['services'].values()
            if s['status'] == 'running' and s['error_count'] == 0
        ])

        health_score = (healthy_services / total_services * 100) if total_services > 0 else 0

        dashboard = {
            'overview': {
                'system_status': 'healthy' if health_score > 80 else 'degraded' if health_score > 50 else 'critical',
                'health_score': round(health_score, 1),
                'total_services': total_services,
                'running_services': len(running_services),
                'average_uptime_seconds': round(avg_uptime, 1)
            },
            'performance': {
                'cpu_usage': status['system_metrics']['cpu_percent'],
                'memory_usage': status['system_metrics']['memory_percent'],
                'memory_used_mb': round(status['system_metrics']['memory_used_mb'], 1),
                'disk_usage': status['system_metrics']['disk_usage_percent']
            },
            'services': status['services'],
            'load_balancer': status['load_balancer'],
            'alerts': self._generate_system_alerts(status),
            'timestamp': status['timestamp']
        }

        return dashboard

    def _generate_system_alerts(self, status: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate system alerts based on current status"""
        alerts = []

        # Check system resources
        metrics = status['system_metrics']
        if metrics['cpu_percent'] > 80:
            alerts.append({
                'level': 'warning',
                'message': f"High CPU usage: {metrics['cpu_percent']:.1f}%"
            })

        if metrics['memory_percent'] > 85:
            alerts.append({
                'level': 'warning',
                'message': f"High memory usage: {metrics['memory_percent']:.1f}%"
            })

        # Check service status
        for service_name, service_info in status['services'].items():
            if service_info['status'] == 'error':
                alerts.append({
                    'level': 'error',
                    'message': f"Service {service_name} is in error state"
                })
            elif service_info['error_count'] > 5:
                alerts.append({
                    'level': 'warning',
                    'message': f"Service {service_name} has {service_info['error_count']} errors"
                })

        return alerts

def main():
    """Main function for testing the integrated system"""

    print("🚀 Initializing Integrated System Orchestrator...")

    orchestrator = IntegratedSystemOrchestrator()

    try:
        # Start the system
        if orchestrator.start_system():
            print("✅ Integrated system started successfully")

            # Wait a bit for services to stabilize
            time.sleep(5)

            # Get system dashboard
            print("\n📊 System Dashboard:")
            dashboard = orchestrator.get_system_dashboard()

            print(f"System Status: {dashboard['overview']['system_status']}")
            print(f"Health Score: {dashboard['overview']['health_score']}%")
            print(f"Running Services: {dashboard['overview']['running_services']}/{dashboard['overview']['total_services']}")
            print(f"CPU Usage: {dashboard['performance']['cpu_usage']:.1f}%")
            print(f"Memory Usage: {dashboard['performance']['memory_usage']:.1f}%")

            print("\n🔧 Service Status:")
            for service_name, service_info in dashboard['services'].items():
                status_emoji = "✅" if service_info['status'] == 'running' else "❌"
                uptime_min = service_info['uptime'] / 60
                print(f"  {status_emoji} {service_name}: {service_info['status']} ({uptime_min:.1f}m uptime)")

            print("\n📈 Load Balancer Stats:")
            for service_name, stats in dashboard['load_balancer'].items():
                print(f"  {service_name}: {stats['instances']} instances, {stats['requests']} requests")

            if dashboard['alerts']:
                print("\n⚠️ System Alerts:")
                for alert in dashboard['alerts']:
                    emoji = "🚨" if alert['level'] == 'error' else "⚠️"
                    print(f"  {emoji} {alert['message']}")
            else:
                print("\n✅ No system alerts")

            # Run for a bit to show monitoring
            print("\n⏳ Running system for 30 seconds to demonstrate monitoring...")
            time.sleep(30)

            # Show updated dashboard
            dashboard = orchestrator.get_system_dashboard()
            print(f"\n📊 Updated Health Score: {dashboard['overview']['health_score']}%")

        else:
            print("❌ Failed to start integrated system")

    except KeyboardInterrupt:
        print("\n⏹️ Shutdown requested by user")
    except Exception as e:
        print(f"❌ Error during system operation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop the system
        orchestrator.stop_system()
        print("🛑 Integrated system stopped")

if __name__ == "__main__":
    main()