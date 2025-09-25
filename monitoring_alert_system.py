#!/usr/bin/env python3
"""
監視とアラートシステム
Monitoring and Alert System for Miraikakaku Platform

このモジュールは包括的な監視とアラート機能を提供します：
- リアルタイム システム監視
- カスタム メトリクス収集
- インテリジェント アラート処理
- パフォーマンス分析と異常検出
- SLA監視とレポート
"""

import time
import json
import logging
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import statistics
import uuid
import re
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"

class NotificationType(Enum):
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    DASHBOARD = "dashboard"

@dataclass
class Metric:
    name: str
    value: Union[float, int]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE

@dataclass
class AlertRule:
    rule_id: str
    name: str
    description: str
    metric_name: str
    condition: str  # e.g., "> 80", "< 0.5", "== 0"
    level: AlertLevel
    evaluation_interval: int = 60  # seconds
    for_duration: int = 300  # seconds (5 minutes)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True

@dataclass
class Alert:
    alert_id: str
    rule_id: str
    rule_name: str
    level: AlertLevel
    status: AlertStatus
    message: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    current_value: Optional[float] = None

@dataclass
class SLATarget:
    name: str
    description: str
    target_percentage: float  # e.g., 99.9 for 99.9% uptime
    measurement_window: int   # seconds
    metric_name: str
    success_condition: str    # condition for successful measurement
    notification_threshold: float = 0.1  # notify if within this % of breach

@dataclass
class SLAStatus:
    target: SLATarget
    current_percentage: float
    measurement_count: int
    success_count: int
    breach_count: int
    last_breach: Optional[datetime] = None
    status: str = "ok"  # ok, warning, breach

class MetricCollector:
    """Collect and store system metrics"""

    def __init__(self):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.metric_metadata: Dict[str, Dict[str, Any]] = {}
        self.collectors: List[Callable] = []
        self.is_collecting = False
        self.collection_thread = None

    def register_collector(self, collector: Callable):
        """Register a metric collector function"""
        self.collectors.append(collector)
        logger.info(f"Registered metric collector: {collector.__name__}")

    def add_metric(self, metric: Metric):
        """Add a metric value"""
        metric_key = self._get_metric_key(metric.name, metric.labels)
        self.metrics[metric_key].append(metric)

        # Update metadata
        self.metric_metadata[metric_key] = {
            'name': metric.name,
            'type': metric.metric_type,
            'labels': metric.labels,
            'last_updated': metric.timestamp
        }

    def _get_metric_key(self, name: str, labels: Dict[str, str]) -> str:
        """Generate unique key for metric with labels"""
        if not labels:
            return name

        label_parts = [f"{k}={v}" for k, v in sorted(labels.items())]
        return f"{name}{{{',' .join(label_parts)}}}"

    def get_metric_values(self, metric_name: str, labels: Dict[str, str] = None,
                         duration_minutes: int = 60) -> List[Metric]:
        """Get metric values for specified duration"""
        metric_key = self._get_metric_key(metric_name, labels or {})

        if metric_key not in self.metrics:
            return []

        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        return [m for m in self.metrics[metric_key] if m.timestamp > cutoff_time]

    def get_latest_value(self, metric_name: str, labels: Dict[str, str] = None) -> Optional[float]:
        """Get latest value for a metric"""
        values = self.get_metric_values(metric_name, labels, 5)  # Last 5 minutes
        return values[-1].value if values else None

    def start_collection(self, interval: int = 30):
        """Start automatic metric collection"""
        self.is_collecting = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            args=(interval,),
            daemon=True
        )
        self.collection_thread.start()
        logger.info("Metric collection started")

    def stop_collection(self):
        """Stop automatic metric collection"""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("Metric collection stopped")

    def _collection_loop(self, interval: int):
        """Main collection loop"""
        while self.is_collecting:
            try:
                # Run system metric collectors
                self._collect_system_metrics()

                # Run custom collectors
                for collector in self.collectors:
                    try:
                        metrics = collector()
                        if isinstance(metrics, list):
                            for metric in metrics:
                                self.add_metric(metric)
                        elif isinstance(metrics, Metric):
                            self.add_metric(metrics)
                    except Exception as e:
                        logger.error(f"Error in collector {collector.__name__}: {e}")

                time.sleep(interval)

            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                time.sleep(interval)

    def _collect_system_metrics(self):
        """Collect basic system metrics"""
        now = datetime.now()

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        self.add_metric(Metric("system_cpu_percent", cpu_percent, now))

        # Memory metrics
        memory = psutil.virtual_memory()
        self.add_metric(Metric("system_memory_percent", memory.percent, now))
        self.add_metric(Metric("system_memory_used_gb", memory.used / (1024**3), now))

        # Disk metrics
        disk = psutil.disk_usage('/')
        self.add_metric(Metric("system_disk_percent", disk.percent, now))
        self.add_metric(Metric("system_disk_used_gb", disk.used / (1024**3), now))

        # Network metrics (simplified)
        try:
            net_io = psutil.net_io_counters()
            self.add_metric(Metric("system_network_bytes_sent", net_io.bytes_sent, now, metric_type=MetricType.COUNTER))
            self.add_metric(Metric("system_network_bytes_recv", net_io.bytes_recv, now, metric_type=MetricType.COUNTER))
        except:
            pass  # Network metrics not available on all systems

    def get_metric_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {
            'total_metrics': len(self.metrics),
            'active_collectors': len(self.collectors),
            'is_collecting': self.is_collecting,
            'metrics': {}
        }

        for metric_key, metric_deque in self.metrics.items():
            if metric_deque:
                latest = metric_deque[-1]
                values = [m.value for m in metric_deque if isinstance(m.value, (int, float))]

                if values:
                    summary['metrics'][metric_key] = {
                        'latest_value': latest.value,
                        'count': len(values),
                        'avg': statistics.mean(values),
                        'min': min(values),
                        'max': max(values),
                        'last_updated': latest.timestamp.isoformat()
                    }

        return summary

class AlertManager:
    """Manage alert rules and active alerts"""

    def __init__(self, metric_collector: MetricCollector):
        self.metric_collector = metric_collector
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_handlers: Dict[NotificationType, Callable] = {}
        self.is_monitoring = False
        self.monitoring_thread = None

    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name}")

    def remove_rule(self, rule_id: str):
        """Remove an alert rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")

    def register_notification_handler(self, notification_type: NotificationType, handler: Callable):
        """Register notification handler"""
        self.notification_handlers[notification_type] = handler
        logger.info(f"Registered notification handler: {notification_type.value}")

    def start_monitoring(self):
        """Start alert monitoring"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("Alert monitoring started")

    def stop_monitoring(self):
        """Stop alert monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Alert monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                for rule_id, rule in self.rules.items():
                    if rule.enabled:
                        self._evaluate_rule(rule)

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)

    def _evaluate_rule(self, rule: AlertRule):
        """Evaluate a single alert rule"""
        try:
            # Get metric values
            current_value = self.metric_collector.get_latest_value(rule.metric_name)

            if current_value is None:
                return

            # Evaluate condition
            condition_met = self._evaluate_condition(current_value, rule.condition)

            alert_key = f"{rule.rule_id}_{rule.metric_name}"

            if condition_met:
                # Check if alert already exists
                if alert_key not in self.active_alerts:
                    # Create new alert
                    alert = Alert(
                        alert_id=str(uuid.uuid4()),
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        level=rule.level,
                        status=AlertStatus.ACTIVE,
                        message=f"{rule.description} (current: {current_value})",
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        labels=rule.labels.copy(),
                        annotations=rule.annotations.copy(),
                        current_value=current_value
                    )

                    self.active_alerts[alert_key] = alert
                    self.alert_history.append(alert)

                    logger.warning(f"Alert triggered: {rule.name} - {alert.message}")
                    self._send_notifications(alert)

                else:
                    # Update existing alert
                    alert = self.active_alerts[alert_key]
                    alert.updated_at = datetime.now()
                    alert.current_value = current_value

            else:
                # Condition not met, resolve alert if it exists
                if alert_key in self.active_alerts:
                    alert = self.active_alerts[alert_key]
                    alert.status = AlertStatus.RESOLVED
                    alert.resolved_at = datetime.now()
                    alert.updated_at = datetime.now()

                    logger.info(f"Alert resolved: {rule.name}")
                    del self.active_alerts[alert_key]

        except Exception as e:
            logger.error(f"Error evaluating rule {rule.name}: {e}")

    def _evaluate_condition(self, value: float, condition: str) -> bool:
        """Evaluate alert condition"""
        try:
            # Parse condition like "> 80", "< 0.5", "== 0"
            condition = condition.strip()

            if condition.startswith('>='):
                threshold = float(condition[2:].strip())
                return value >= threshold
            elif condition.startswith('<='):
                threshold = float(condition[2:].strip())
                return value <= threshold
            elif condition.startswith('>'):
                threshold = float(condition[1:].strip())
                return value > threshold
            elif condition.startswith('<'):
                threshold = float(condition[1:].strip())
                return value < threshold
            elif condition.startswith('=='):
                threshold = float(condition[2:].strip())
                return abs(value - threshold) < 0.0001  # Float comparison
            elif condition.startswith('!='):
                threshold = float(condition[2:].strip())
                return abs(value - threshold) >= 0.0001
            else:
                logger.error(f"Invalid condition format: {condition}")
                return False

        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False

    def _send_notifications(self, alert: Alert):
        """Send notifications for alert"""
        for notification_type, handler in self.notification_handlers.items():
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error sending {notification_type.value} notification: {e}")

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.active_alerts.values():
            if alert.alert_id == alert_id:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now()
                alert.acknowledged_by = acknowledged_by
                alert.updated_at = datetime.now()

                logger.info(f"Alert acknowledged by {acknowledged_by}: {alert.rule_name}")
                return True

        return False

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())

    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.created_at > cutoff_time]

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        active_alerts = self.get_active_alerts()
        recent_alerts = self.get_alert_history(24)

        by_level = defaultdict(int)
        for alert in active_alerts:
            by_level[alert.level.value] += 1

        return {
            'active_count': len(active_alerts),
            'total_rules': len(self.rules),
            'enabled_rules': len([r for r in self.rules.values() if r.enabled]),
            'recent_24h': len(recent_alerts),
            'by_level': dict(by_level),
            'is_monitoring': self.is_monitoring
        }

class SLAMonitor:
    """Monitor Service Level Agreements"""

    def __init__(self, metric_collector: MetricCollector):
        self.metric_collector = metric_collector
        self.targets: Dict[str, SLATarget] = {}
        self.status: Dict[str, SLAStatus] = {}
        self.is_monitoring = False
        self.monitoring_thread = None

    def add_sla_target(self, target: SLATarget):
        """Add SLA target"""
        self.targets[target.name] = target
        self.status[target.name] = SLAStatus(
            target=target,
            current_percentage=100.0,
            measurement_count=0,
            success_count=0,
            breach_count=0
        )
        logger.info(f"Added SLA target: {target.name} ({target.target_percentage}%)")

    def start_monitoring(self):
        """Start SLA monitoring"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("SLA monitoring started")

    def stop_monitoring(self):
        """Stop SLA monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("SLA monitoring stopped")

    def _monitoring_loop(self):
        """Main SLA monitoring loop"""
        while self.is_monitoring:
            try:
                for target_name, target in self.targets.items():
                    self._evaluate_sla(target_name, target)

                time.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in SLA monitoring loop: {e}")
                time.sleep(60)

    def _evaluate_sla(self, target_name: str, target: SLATarget):
        """Evaluate SLA target"""
        try:
            # Get metric values for the measurement window
            window_minutes = target.measurement_window // 60
            values = self.metric_collector.get_metric_values(
                target.metric_name,
                duration_minutes=window_minutes
            )

            if not values:
                return

            status = self.status[target_name]

            # Count successful measurements
            success_count = 0
            total_count = len(values)

            for metric in values:
                if self._evaluate_condition(metric.value, target.success_condition):
                    success_count += 1

            # Calculate current percentage
            current_percentage = (success_count / total_count * 100) if total_count > 0 else 100.0

            # Update status
            status.current_percentage = current_percentage
            status.measurement_count = total_count
            status.success_count = success_count

            # Check for breach
            if current_percentage < target.target_percentage:
                if status.status != "breach":
                    status.last_breach = datetime.now()
                    status.breach_count += 1
                    logger.error(f"SLA breach: {target_name} ({current_percentage:.2f}% < {target.target_percentage}%)")

                status.status = "breach"
            elif current_percentage < (target.target_percentage + target.notification_threshold):
                status.status = "warning"
                logger.warning(f"SLA warning: {target_name} ({current_percentage:.2f}% near breach)")
            else:
                status.status = "ok"

        except Exception as e:
            logger.error(f"Error evaluating SLA {target_name}: {e}")

    def _evaluate_condition(self, value: float, condition: str) -> bool:
        """Evaluate SLA success condition"""
        try:
            condition = condition.strip()

            if condition.startswith('>='):
                threshold = float(condition[2:].strip())
                return value >= threshold
            elif condition.startswith('<='):
                threshold = float(condition[2:].strip())
                return value <= threshold
            elif condition.startswith('>'):
                threshold = float(condition[1:].strip())
                return value > threshold
            elif condition.startswith('<'):
                threshold = float(condition[1:].strip())
                return value < threshold
            elif condition.startswith('=='):
                threshold = float(condition[2:].strip())
                return abs(value - threshold) < 0.0001
            else:
                return True  # Default to success if condition unclear

        except Exception as e:
            logger.error(f"Error evaluating SLA condition '{condition}': {e}")
            return False

    def get_sla_status(self, target_name: str) -> Optional[SLAStatus]:
        """Get SLA status for target"""
        return self.status.get(target_name)

    def get_all_sla_status(self) -> Dict[str, SLAStatus]:
        """Get all SLA statuses"""
        return self.status.copy()

    def get_sla_report(self) -> Dict[str, Any]:
        """Generate SLA report"""
        report = {
            'targets': len(self.targets),
            'overall_status': 'ok',
            'sla_details': {},
            'generated_at': datetime.now().isoformat()
        }

        breach_count = 0
        warning_count = 0

        for target_name, status in self.status.items():
            target = self.targets[target_name]

            report['sla_details'][target_name] = {
                'target_percentage': target.target_percentage,
                'current_percentage': status.current_percentage,
                'status': status.status,
                'measurement_count': status.measurement_count,
                'success_count': status.success_count,
                'breach_count': status.breach_count,
                'last_breach': status.last_breach.isoformat() if status.last_breach else None
            }

            if status.status == 'breach':
                breach_count += 1
            elif status.status == 'warning':
                warning_count += 1

        # Overall status
        if breach_count > 0:
            report['overall_status'] = 'breach'
        elif warning_count > 0:
            report['overall_status'] = 'warning'

        report['breach_count'] = breach_count
        report['warning_count'] = warning_count

        return report

class MonitoringAlertSystem:
    """Main monitoring and alert system"""

    def __init__(self):
        self.metric_collector = MetricCollector()
        self.alert_manager = AlertManager(self.metric_collector)
        self.sla_monitor = SLAMonitor(self.metric_collector)
        self.is_running = False

        # Setup default notification handlers
        self._setup_notification_handlers()

        # Setup default metrics and rules
        self._setup_default_monitoring()

        logger.info("Monitoring and Alert System initialized")

    def _setup_notification_handlers(self):
        """Setup notification handlers"""

        def email_handler(alert: Alert):
            logger.info(f"EMAIL ALERT: {alert.level.value.upper()} - {alert.message}")

        def slack_handler(alert: Alert):
            logger.info(f"SLACK ALERT: {alert.level.value.upper()} - {alert.message}")

        def webhook_handler(alert: Alert):
            logger.info(f"WEBHOOK ALERT: {alert.level.value.upper()} - {alert.message}")

        def dashboard_handler(alert: Alert):
            logger.info(f"DASHBOARD ALERT: {alert.level.value.upper()} - {alert.message}")

        self.alert_manager.register_notification_handler(NotificationType.EMAIL, email_handler)
        self.alert_manager.register_notification_handler(NotificationType.SLACK, slack_handler)
        self.alert_manager.register_notification_handler(NotificationType.WEBHOOK, webhook_handler)
        self.alert_manager.register_notification_handler(NotificationType.DASHBOARD, dashboard_handler)

    def _setup_default_monitoring(self):
        """Setup default monitoring rules and SLAs"""

        # System monitoring rules
        cpu_rule = AlertRule(
            rule_id="high_cpu",
            name="High CPU Usage",
            description="CPU usage is above 80%",
            metric_name="system_cpu_percent",
            condition="> 80",
            level=AlertLevel.WARNING,
            evaluation_interval=60,
            for_duration=300
        )
        self.alert_manager.add_rule(cpu_rule)

        memory_rule = AlertRule(
            rule_id="high_memory",
            name="High Memory Usage",
            description="Memory usage is above 85%",
            metric_name="system_memory_percent",
            condition="> 85",
            level=AlertLevel.ERROR,
            evaluation_interval=60,
            for_duration=180
        )
        self.alert_manager.add_rule(memory_rule)

        disk_rule = AlertRule(
            rule_id="high_disk",
            name="High Disk Usage",
            description="Disk usage is above 90%",
            metric_name="system_disk_percent",
            condition="> 90",
            level=AlertLevel.CRITICAL,
            evaluation_interval=300,
            for_duration=600
        )
        self.alert_manager.add_rule(disk_rule)

        # Application SLA targets
        uptime_sla = SLATarget(
            name="system_uptime",
            description="System uptime SLA",
            target_percentage=99.9,
            measurement_window=3600,  # 1 hour
            metric_name="system_cpu_percent",  # Proxy for system availability
            success_condition=">= 0"  # System is up if CPU metrics are available
        )
        self.sla_monitor.add_sla_target(uptime_sla)

        response_time_sla = SLATarget(
            name="response_time",
            description="Response time SLA",
            target_percentage=95.0,
            measurement_window=1800,  # 30 minutes
            metric_name="http_response_time",
            success_condition="< 500"  # Response time under 500ms
        )
        self.sla_monitor.add_sla_target(response_time_sla)

    def add_custom_metric_collector(self, collector: Callable):
        """Add custom metric collector"""
        self.metric_collector.register_collector(collector)

    def add_custom_alert_rule(self, rule: AlertRule):
        """Add custom alert rule"""
        self.alert_manager.add_rule(rule)

    def add_sla_target(self, target: SLATarget):
        """Add SLA target"""
        self.sla_monitor.add_sla_target(target)

    def start_monitoring(self):
        """Start all monitoring components"""
        self.is_running = True

        self.metric_collector.start_collection(30)
        self.alert_manager.start_monitoring()
        self.sla_monitor.start_monitoring()

        logger.info("Monitoring and Alert System started")

    def stop_monitoring(self):
        """Stop all monitoring components"""
        self.is_running = False

        self.metric_collector.stop_collection()
        self.alert_manager.stop_monitoring()
        self.sla_monitor.stop_monitoring()

        logger.info("Monitoring and Alert System stopped")

    def get_system_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard"""

        # Get metric summary
        metric_summary = self.metric_collector.get_metric_summary()

        # Get alert summary
        alert_summary = self.alert_manager.get_alert_summary()

        # Get SLA report
        sla_report = self.sla_monitor.get_sla_report()

        # Get active alerts
        active_alerts = []
        for alert in self.alert_manager.get_active_alerts():
            active_alerts.append({
                'id': alert.alert_id,
                'rule_name': alert.rule_name,
                'level': alert.level.value,
                'status': alert.status.value,
                'message': alert.message,
                'created_at': alert.created_at.isoformat(),
                'current_value': alert.current_value
            })

        # System health score
        health_factors = []

        # CPU health (0-100)
        cpu_value = self.metric_collector.get_latest_value("system_cpu_percent")
        if cpu_value is not None:
            cpu_health = max(0, 100 - cpu_value)
            health_factors.append(cpu_health)

        # Memory health (0-100)
        memory_value = self.metric_collector.get_latest_value("system_memory_percent")
        if memory_value is not None:
            memory_health = max(0, 100 - memory_value)
            health_factors.append(memory_health)

        # Alert health (fewer alerts = better health)
        alert_health = max(0, 100 - (len(active_alerts) * 10))
        health_factors.append(alert_health)

        # SLA health
        sla_health = 100
        if sla_report['breach_count'] > 0:
            sla_health -= 30
        if sla_report['warning_count'] > 0:
            sla_health -= 10
        health_factors.append(sla_health)

        overall_health = statistics.mean(health_factors) if health_factors else 100

        return {
            'overview': {
                'system_health': round(overall_health, 1),
                'status': 'healthy' if overall_health > 80 else 'degraded' if overall_health > 50 else 'critical',
                'monitoring_active': self.is_running,
                'last_updated': datetime.now().isoformat()
            },
            'metrics': {
                'total_metrics': metric_summary.get('total_metrics', 0),
                'active_collectors': metric_summary.get('active_collectors', 0),
                'is_collecting': metric_summary.get('is_collecting', False),
                'latest_values': {
                    'cpu_percent': self.metric_collector.get_latest_value("system_cpu_percent"),
                    'memory_percent': self.metric_collector.get_latest_value("system_memory_percent"),
                    'disk_percent': self.metric_collector.get_latest_value("system_disk_percent")
                }
            },
            'alerts': {
                'active_count': alert_summary['active_count'],
                'total_rules': alert_summary['total_rules'],
                'recent_24h': alert_summary['recent_24h'],
                'by_level': alert_summary['by_level'],
                'active_alerts': active_alerts[:10]  # Top 10 active alerts
            },
            'sla': {
                'targets': sla_report['targets'],
                'overall_status': sla_report['overall_status'],
                'breach_count': sla_report['breach_count'],
                'warning_count': sla_report['warning_count'],
                'details': sla_report['sla_details']
            }
        }

def main():
    """Main function for testing monitoring and alert system"""

    print("🚀 Initializing Monitoring and Alert System...")

    monitoring_system = MonitoringAlertSystem()

    try:
        # Start monitoring
        monitoring_system.start_monitoring()
        print("✅ Monitoring system started")

        # Wait a bit for initial metrics collection
        time.sleep(5)

        # Get initial dashboard
        print("\n📊 Initial System Dashboard:")
        dashboard = monitoring_system.get_system_dashboard()

        overview = dashboard['overview']
        metrics = dashboard['metrics']
        alerts = dashboard['alerts']
        sla = dashboard['sla']

        print(f"System Health: {overview['system_health']}% ({overview['status']})")
        print(f"Monitoring Active: {overview['monitoring_active']}")

        print(f"\nMetrics:")
        print(f"  Total Metrics: {metrics['total_metrics']}")
        print(f"  Active Collectors: {metrics['active_collectors']}")
        print(f"  Latest CPU: {metrics['latest_values']['cpu_percent']}%")
        print(f"  Latest Memory: {metrics['latest_values']['memory_percent']}%")
        print(f"  Latest Disk: {metrics['latest_values']['disk_percent']}%")

        print(f"\nAlerts:")
        print(f"  Active: {alerts['active_count']}")
        print(f"  Total Rules: {alerts['total_rules']}")
        print(f"  Recent (24h): {alerts['recent_24h']}")

        print(f"\nSLA:")
        print(f"  Targets: {sla['targets']}")
        print(f"  Overall Status: {sla['overall_status']}")
        print(f"  Breaches: {sla['breach_count']}")
        print(f"  Warnings: {sla['warning_count']}")

        # Simulate high load to trigger alerts
        print("\n⚡ Simulating high system load...")

        # Add mock high CPU metric
        from datetime import datetime
        high_cpu_metric = Metric(
            name="system_cpu_percent",
            value=85.0,  # Above 80% threshold
            timestamp=datetime.now()
        )
        monitoring_system.metric_collector.add_metric(high_cpu_metric)

        # Add mock high memory metric
        high_memory_metric = Metric(
            name="system_memory_percent",
            value=90.0,  # Above 85% threshold
            timestamp=datetime.now()
        )
        monitoring_system.metric_collector.add_metric(high_memory_metric)

        # Wait for alert evaluation
        print("⏳ Waiting for alert evaluation...")
        time.sleep(35)  # Wait longer than alert evaluation interval

        # Check for alerts
        dashboard = monitoring_system.get_system_dashboard()
        active_alerts = dashboard['alerts']['active_alerts']

        if active_alerts:
            print(f"\n🚨 Triggered {len(active_alerts)} alerts:")
            for alert in active_alerts:
                level_emoji = "🔴" if alert['level'] == 'critical' else "🟡" if alert['level'] == 'warning' else "🟢"
                print(f"  {level_emoji} {alert['rule_name']}: {alert['message']}")
                print(f"     Level: {alert['level']}, Status: {alert['status']}")
                print(f"     Current Value: {alert['current_value']}")
        else:
            print("ℹ️ No alerts triggered yet (evaluation in progress)")

        # Test alert acknowledgment
        if active_alerts:
            first_alert = active_alerts[0]
            print(f"\n✅ Acknowledging alert: {first_alert['rule_name']}")
            monitoring_system.alert_manager.acknowledge_alert(first_alert['id'], "test_user")

        # Show final dashboard
        print("\n📊 Final System Dashboard:")
        dashboard = monitoring_system.get_system_dashboard()
        print(f"System Health: {dashboard['overview']['system_health']}%")
        print(f"Active Alerts: {dashboard['alerts']['active_count']}")
        print(f"SLA Status: {dashboard['sla']['overall_status']}")

        print("\n🎯 Monitoring and Alert System Test Completed!")

    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop monitoring
        monitoring_system.stop_monitoring()
        print("🛑 Monitoring system stopped")

if __name__ == "__main__":
    main()