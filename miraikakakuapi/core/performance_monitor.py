#!/usr/bin/env python3
"""
パフォーマンス監視システム
Performance Monitoring System

アプリケーション全体のパフォーマンスを継続的に監視
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import asyncio
from fastapi import Request
from contextlib import asynccontextmanager
import logging
from .logging_config import setup_logging

logger = setup_logging(__name__)

@dataclass
class PerformanceMetrics:
    """パフォーマンスメトリクス"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    api_response_time: float
    active_requests: int
    total_requests: int
    error_rate: float
    database_connections: int
    cache_hit_rate: float

@dataclass
class EndpointMetrics:
    """エンドポイントメトリクス"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    timestamp: datetime

class PerformanceMonitor:
    """パフォーマンス監視クラス"""

    def __init__(self, max_history: int = 1000):
        self.metrics_history: List[PerformanceMetrics] = []
        self.endpoint_metrics: List[EndpointMetrics] = []
        self.max_history = max_history
        self.active_requests = 0
        self.total_requests = 0
        self.total_errors = 0
        self.response_times: List[float] = []
        self.monitoring_active = False
        self.alerts_enabled = True

        # アラート閾値
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'avg_response_time': 2.0,
            'error_rate': 5.0,
            'database_connections': 50
        }

    def start_monitoring(self, interval: int = 30):
        """監視を開始"""
        if self.monitoring_active:
            return

        self.monitoring_active = True

        def monitor_loop():
            while self.monitoring_active:
                try:
                    self._collect_system_metrics()
                    self._check_alerts()
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(interval)

        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """監視を停止"""
        self.monitoring_active = False
        logger.info("Performance monitoring stopped")

    def _collect_system_metrics(self):
        """システムメトリクスを収集"""
        try:
            # システムリソース
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # API メトリクス
            avg_response_time = sum(self.response_times[-100:]) / len(self.response_times[-100:]) if self.response_times else 0
            error_rate = (self.total_errors / max(self.total_requests, 1)) * 100

            metrics = PerformanceMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                api_response_time=avg_response_time,
                active_requests=self.active_requests,
                total_requests=self.total_requests,
                error_rate=error_rate,
                database_connections=self._get_database_connections(),
                cache_hit_rate=self._get_cache_hit_rate()
            )

            self._store_metrics(metrics)

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")

    def _get_database_connections(self) -> int:
        """データベース接続数を取得（簡易実装）"""
        try:
            # 実際にはデータベースから取得
            return len([conn for conn in psutil.net_connections() if conn.laddr.port == 5432])
        except:
            return 0

    def _get_cache_hit_rate(self) -> float:
        """キャッシュヒット率を取得（プレースホルダー）"""
        # 実際のキャッシュシステムから取得
        return 85.0

    def _store_metrics(self, metrics: PerformanceMetrics):
        """メトリクスを保存"""
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]

    def _check_alerts(self):
        """アラートをチェック"""
        if not self.alerts_enabled or not self.metrics_history:
            return

        latest = self.metrics_history[-1]
        alerts = []

        # CPU使用率チェック
        if latest.cpu_usage > self.thresholds['cpu_usage']:
            alerts.append(f"High CPU usage: {latest.cpu_usage:.1f}%")

        # メモリ使用率チェック
        if latest.memory_usage > self.thresholds['memory_usage']:
            alerts.append(f"High memory usage: {latest.memory_usage:.1f}%")

        # ディスク使用率チェック
        if latest.disk_usage > self.thresholds['disk_usage']:
            alerts.append(f"High disk usage: {latest.disk_usage:.1f}%")

        # レスポンス時間チェック
        if latest.api_response_time > self.thresholds['avg_response_time']:
            alerts.append(f"Slow API response: {latest.api_response_time:.2f}s")

        # エラー率チェック
        if latest.error_rate > self.thresholds['error_rate']:
            alerts.append(f"High error rate: {latest.error_rate:.1f}%")

        # アラート送信
        if alerts:
            self._send_alerts(alerts)

    def _send_alerts(self, alerts: List[str]):
        """アラートを送信"""
        timestamp = datetime.utcnow().isoformat()
        for alert in alerts:
            logger.warning(f"PERFORMANCE ALERT [{timestamp}]: {alert}")

            # 通知システムにアラートを送信
            asyncio.create_task(self._send_notification_alert(alert))

    @asynccontextmanager
    async def track_request(self, request: Request):
        """リクエストを追跡"""
        start_time = time.time()
        self.active_requests += 1
        self.total_requests += 1

        try:
            yield
            status_code = 200
        except Exception as e:
            status_code = 500
            self.total_errors += 1
            raise
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            self.active_requests -= 1

            # レスポンス時間を記録
            self.response_times.append(response_time)
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]

            # エンドポイントメトリクスを記録
            endpoint_metric = EndpointMetrics(
                endpoint=str(request.url.path),
                method=request.method,
                response_time=response_time,
                status_code=status_code,
                timestamp=datetime.utcnow()
            )

            self._store_endpoint_metrics(endpoint_metric)

    def _store_endpoint_metrics(self, metric: EndpointMetrics):
        """エンドポイントメトリクスを保存"""
        self.endpoint_metrics.append(metric)
        if len(self.endpoint_metrics) > self.max_history:
            self.endpoint_metrics = self.endpoint_metrics[-self.max_history:]

    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """現在のメトリクスを取得"""
        if not self.metrics_history:
            return None

        latest = self.metrics_history[-1]
        return {
            "timestamp": latest.timestamp.isoformat(),
            "system": {
                "cpu_usage": latest.cpu_usage,
                "memory_usage": latest.memory_usage,
                "disk_usage": latest.disk_usage
            },
            "api": {
                "response_time": latest.api_response_time,
                "active_requests": latest.active_requests,
                "total_requests": latest.total_requests,
                "error_rate": latest.error_rate
            },
            "database": {
                "connections": latest.database_connections
            },
            "cache": {
                "hit_rate": latest.cache_hit_rate
            }
        }

    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """パフォーマンスサマリーを取得"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp > cutoff_time
        ]

        if not recent_metrics:
            return {"error": "No metrics available for the specified period"}

        # 統計計算
        cpu_values = [m.cpu_usage for m in recent_metrics]
        memory_values = [m.memory_usage for m in recent_metrics]
        response_times = [m.api_response_time for m in recent_metrics if m.api_response_time > 0]

        summary = {
            "period_hours": hours,
            "data_points": len(recent_metrics),
            "system": {
                "cpu": {
                    "avg": sum(cpu_values) / len(cpu_values),
                    "max": max(cpu_values),
                    "min": min(cpu_values)
                },
                "memory": {
                    "avg": sum(memory_values) / len(memory_values),
                    "max": max(memory_values),
                    "min": min(memory_values)
                }
            },
            "api": {
                "total_requests": self.total_requests,
                "total_errors": self.total_errors,
                "error_rate": (self.total_errors / max(self.total_requests, 1)) * 100,
                "response_time": {
                    "avg": sum(response_times) / len(response_times) if response_times else 0,
                    "max": max(response_times) if response_times else 0,
                    "min": min(response_times) if response_times else 0
                }
            },
            "period": {
                "start": min(m.timestamp for m in recent_metrics).isoformat(),
                "end": max(m.timestamp for m in recent_metrics).isoformat()
            }
        }

        return summary

    def get_endpoint_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """エンドポイント分析を取得"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_endpoints = [
            m for m in self.endpoint_metrics
            if m.timestamp > cutoff_time
        ]

        if not recent_endpoints:
            return {"error": "No endpoint metrics available"}

        # エンドポイント別集計
        endpoint_stats = {}
        for metric in recent_endpoints:
            key = f"{metric.method} {metric.endpoint}"
            if key not in endpoint_stats:
                endpoint_stats[key] = {
                    "requests": 0,
                    "response_times": [],
                    "errors": 0
                }

            endpoint_stats[key]["requests"] += 1
            endpoint_stats[key]["response_times"].append(metric.response_time)
            if metric.status_code >= 400:
                endpoint_stats[key]["errors"] += 1

        # 統計計算
        analytics = {}
        for endpoint, stats in endpoint_stats.items():
            response_times = stats["response_times"]
            analytics[endpoint] = {
                "requests": stats["requests"],
                "avg_response_time": sum(response_times) / len(response_times),
                "max_response_time": max(response_times),
                "error_rate": (stats["errors"] / stats["requests"]) * 100,
                "requests_per_hour": stats["requests"] / hours
            }

        # 上位10位までを返す
        sorted_analytics = dict(sorted(
            analytics.items(),
            key=lambda x: x[1]["requests"],
            reverse=True
        )[:10])

        return {
            "period_hours": hours,
            "total_endpoints": len(analytics),
            "endpoints": sorted_analytics
        }

    def export_metrics(self, filename: Optional[str] = None) -> str:
        """メトリクスをJSONでエクスポート"""
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.json"

        data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "metrics_count": len(self.metrics_history),
            "endpoint_metrics_count": len(self.endpoint_metrics),
            "metrics": [asdict(m) for m in self.metrics_history],
            "endpoint_metrics": [asdict(m) for m in self.endpoint_metrics]
        }

        # タイムスタンプをISO形式に変換
        for metric in data["metrics"]:
            metric["timestamp"] = metric["timestamp"].isoformat()

        for metric in data["endpoint_metrics"]:
            metric["timestamp"] = metric["timestamp"].isoformat()

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        return filename

    async def _send_notification_alert(self, alert_message: str):
        """通知システムにアラートを送信"""
        try:
            from .notification_system import send_performance_alert, AlertSeverity

            # アラートメッセージから数値と閾値を抽出（簡易実装）
            if "CPU usage" in alert_message:
                parts = alert_message.split(": ")
                if len(parts) > 1:
                    value = float(parts[1].replace("%", ""))
                    await send_performance_alert("cpu_usage", value, 80.0)
            elif "memory usage" in alert_message:
                parts = alert_message.split(": ")
                if len(parts) > 1:
                    value = float(parts[1].replace("%", ""))
                    await send_performance_alert("memory_usage", value, 85.0)
            elif "disk usage" in alert_message:
                parts = alert_message.split(": ")
                if len(parts) > 1:
                    value = float(parts[1].replace("%", ""))
                    await send_performance_alert("disk_usage", value, 90.0)
            elif "API response" in alert_message:
                parts = alert_message.split(": ")
                if len(parts) > 1:
                    value = float(parts[1].replace("s", ""))
                    await send_performance_alert("response_time", value, 2.0)
            elif "error rate" in alert_message:
                parts = alert_message.split(": ")
                if len(parts) > 1:
                    value = float(parts[1].replace("%", ""))
                    await send_performance_alert("error_rate", value, 5.0)
        except Exception as e:
            logger.error(f"Failed to send notification alert: {e}")

# グローバル監視インスタンス
performance_monitor = PerformanceMonitor()

def start_performance_monitoring():
    """パフォーマンス監視を開始"""
    performance_monitor.start_monitoring()

def stop_performance_monitoring():
    """パフォーマンス監視を停止"""
    performance_monitor.stop_monitoring()

def get_current_performance() -> Optional[Dict[str, Any]]:
    """現在のパフォーマンスを取得"""
    return performance_monitor.get_current_metrics()

def get_performance_analytics(hours: int = 24) -> Dict[str, Any]:
    """パフォーマンス分析を取得"""
    return performance_monitor.get_performance_summary(hours)

def get_endpoint_performance(hours: int = 24) -> Dict[str, Any]:
    """エンドポイント性能分析を取得"""
    return performance_monitor.get_endpoint_analytics(hours)