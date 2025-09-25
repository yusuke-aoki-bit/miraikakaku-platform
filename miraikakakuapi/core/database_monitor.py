#!/usr/bin/env python3
"""
データベース接続監視システム
Database Connection Monitoring System

PostgreSQL接続の健全性を監視し、問題を早期に検出する
"""
import time
import logging
import psutil
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy import text
from sqlalchemy.orm import Session
from .database import get_db
from .logging_config import setup_logging

logger = setup_logging(__name__)

@dataclass
class ConnectionMetrics:
    """接続メトリクス"""
    timestamp: datetime
    active_connections: int
    idle_connections: int
    total_connections: int
    query_duration_avg: float
    query_duration_max: float
    failed_connections: int
    cpu_usage: float
    memory_usage: float

@dataclass
class DatabaseHealth:
    """データベース健全性"""
    status: str  # 'healthy', 'warning', 'critical'
    connection_status: bool
    metrics: Optional[ConnectionMetrics]
    issues: List[str]
    recommendations: List[str]

class DatabaseMonitor:
    """データベース監視クラス"""

    def __init__(self):
        self.metrics_history: List[ConnectionMetrics] = []
        self.alert_thresholds = {
            'max_connections': 80,  # 最大接続数の警告閾値(%)
            'avg_query_duration': 5.0,  # 平均クエリ時間の警告閾値(秒)
            'max_query_duration': 30.0,  # 最大クエリ時間の警告閾値(秒)
            'cpu_usage': 80.0,  # CPU使用率の警告閾値(%)
            'memory_usage': 85.0,  # メモリ使用率の警告閾値(%)
        }

    def get_connection_metrics(self, db: Session) -> Optional[ConnectionMetrics]:
        """接続メトリクスを取得"""
        try:
            # PostgreSQL接続統計を取得
            connection_stats = db.execute(text("""
                SELECT
                    count(*) as total_connections,
                    count(*) FILTER (WHERE state = 'active') as active_connections,
                    count(*) FILTER (WHERE state = 'idle') as idle_connections
                FROM pg_stat_activity
                WHERE datname = current_database()
            """)).fetchone()

            # クエリ実行時間統計を取得
            query_stats = db.execute(text("""
                SELECT
                    COALESCE(AVG(mean_exec_time), 0) as avg_duration,
                    COALESCE(MAX(max_exec_time), 0) as max_duration
                FROM pg_stat_statements
                WHERE calls > 0
                LIMIT 1
            """)).fetchone()

            # システムリソース使用量を取得
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent

            return ConnectionMetrics(
                timestamp=datetime.utcnow(),
                active_connections=connection_stats.active_connections or 0,
                idle_connections=connection_stats.idle_connections or 0,
                total_connections=connection_stats.total_connections or 0,
                query_duration_avg=float(query_stats.avg_duration or 0) if query_stats else 0.0,
                query_duration_max=float(query_stats.max_duration or 0) if query_stats else 0.0,
                failed_connections=0,  # PostgreSQLから取得が困難なため0に設定
                cpu_usage=cpu_usage,
                memory_usage=memory_usage
            )

        except Exception as e:
            logger.error(f"Failed to get connection metrics: {e}")
            return None

    def check_database_health(self, db: Session) -> DatabaseHealth:
        """データベース健全性をチェック"""
        issues = []
        recommendations = []

        # 接続テスト
        try:
            db.execute(text("SELECT 1"))
            connection_status = True
        except Exception as e:
            connection_status = False
            issues.append(f"Database connection failed: {e}")

        # メトリクス取得
        metrics = self.get_connection_metrics(db)

        if metrics:
            # 接続数チェック
            if metrics.total_connections > self.alert_thresholds['max_connections']:
                issues.append(f"High connection count: {metrics.total_connections}")
                recommendations.append("Consider connection pooling optimization")

            # クエリ実行時間チェック
            if metrics.query_duration_avg > self.alert_thresholds['avg_query_duration']:
                issues.append(f"Slow average query time: {metrics.query_duration_avg:.2f}s")
                recommendations.append("Review and optimize slow queries")

            if metrics.query_duration_max > self.alert_thresholds['max_query_duration']:
                issues.append(f"Very slow maximum query time: {metrics.query_duration_max:.2f}s")
                recommendations.append("Identify and fix the slowest queries")

            # システムリソースチェック
            if metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
                issues.append(f"High CPU usage: {metrics.cpu_usage:.1f}%")
                recommendations.append("Monitor CPU-intensive queries")

            if metrics.memory_usage > self.alert_thresholds['memory_usage']:
                issues.append(f"High memory usage: {metrics.memory_usage:.1f}%")
                recommendations.append("Check for memory leaks or optimize memory usage")

        # 健全性ステータス決定
        if not connection_status:
            status = 'critical'
        elif len(issues) >= 3:
            status = 'critical'
        elif len(issues) >= 1:
            status = 'warning'
        else:
            status = 'healthy'

        return DatabaseHealth(
            status=status,
            connection_status=connection_status,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations
        )

    def store_metrics(self, metrics: ConnectionMetrics):
        """メトリクスを履歴に保存（メモリ内、最大1000件）"""
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]

    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """指定時間内のメトリクスサマリーを取得"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp > cutoff_time
        ]

        if not recent_metrics:
            return {
                'period_hours': hours,
                'data_points': 0,
                'message': 'No metrics available for the specified period'
            }

        return {
            'period_hours': hours,
            'data_points': len(recent_metrics),
            'avg_connections': sum(m.total_connections for m in recent_metrics) / len(recent_metrics),
            'max_connections': max(m.total_connections for m in recent_metrics),
            'avg_query_duration': sum(m.query_duration_avg for m in recent_metrics) / len(recent_metrics),
            'max_query_duration': max(m.query_duration_max for m in recent_metrics),
            'avg_cpu_usage': sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
            'avg_memory_usage': sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
            'first_timestamp': min(m.timestamp for m in recent_metrics).isoformat(),
            'last_timestamp': max(m.timestamp for m in recent_metrics).isoformat()
        }

    def run_continuous_monitoring(self, interval_seconds: int = 60):
        """継続的監視を実行"""
        logger.info(f"Starting continuous database monitoring (interval: {interval_seconds}s)")

        while True:
            try:
                with next(get_db()) as db:
                    health = self.check_database_health(db)

                    if health.metrics:
                        self.store_metrics(health.metrics)

                    # ログ出力
                    if health.status == 'healthy':
                        logger.info(f"Database health: {health.status}")
                    elif health.status == 'warning':
                        logger.warning(f"Database health: {health.status} - Issues: {health.issues}")
                    else:  # critical
                        logger.error(f"Database health: {health.status} - Issues: {health.issues}")

                    # 推奨事項があれば出力
                    if health.recommendations:
                        logger.info(f"Recommendations: {health.recommendations}")

            except Exception as e:
                logger.error(f"Error during monitoring cycle: {e}")

            time.sleep(interval_seconds)

# グローバル監視インスタンス
db_monitor = DatabaseMonitor()

def get_database_health() -> DatabaseHealth:
    """データベース健全性を取得"""
    try:
        with next(get_db()) as db:
            return db_monitor.check_database_health(db)
    except Exception as e:
        logger.error(f"Failed to get database health: {e}")
        return DatabaseHealth(
            status='critical',
            connection_status=False,
            metrics=None,
            issues=[f"Failed to check database health: {e}"],
            recommendations=['Check database connectivity and configuration']
        )

def get_monitoring_summary(hours: int = 24) -> Dict[str, Any]:
    """監視サマリーを取得"""
    return db_monitor.get_metrics_summary(hours)