#!/usr/bin/env python3
"""
リアルタイム通知システム
Real-time Notification System

WebSocketを使用してリアルタイム通知を配信
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from websockets.server import WebSocketServerProtocol
from fastapi import WebSocket, WebSocketDisconnect
import threading
from .logging_config import setup_logging

logger = setup_logging(__name__)

class NotificationType(Enum):
    """通知タイプ"""
    SYSTEM_ALERT = "system_alert"
    PERFORMANCE_WARNING = "performance_warning"
    PRICE_ALERT = "price_alert"
    PREDICTION_UPDATE = "prediction_update"
    DATABASE_ISSUE = "database_issue"
    SERVER_STATUS = "server_status"

class AlertSeverity(Enum):
    """アラート重要度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Notification:
    """通知データ"""
    id: str
    type: NotificationType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        result = asdict(self)
        result['type'] = self.type.value
        result['severity'] = self.severity.value
        result['timestamp'] = self.timestamp.isoformat()
        if self.expires_at:
            result['expires_at'] = self.expires_at.isoformat()
        return result

class NotificationManager:
    """通知管理クラス"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.notification_history: List[Notification] = []
        self.max_history = 1000
        self.alert_rules: Dict[str, Dict[str, Any]] = {
            'cpu_usage': {'threshold': 80.0, 'severity': AlertSeverity.WARNING},
            'memory_usage': {'threshold': 85.0, 'severity': AlertSeverity.WARNING},
            'disk_usage': {'threshold': 90.0, 'severity': AlertSeverity.ERROR},
            'error_rate': {'threshold': 5.0, 'severity': AlertSeverity.WARNING},
            'response_time': {'threshold': 3.0, 'severity': AlertSeverity.WARNING},
            'database_connections': {'threshold': 50, 'severity': AlertSeverity.WARNING}
        }

    async def connect(self, websocket: WebSocket):
        """WebSocket接続を追加"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")

        # 接続時に最近の通知を送信
        await self._send_recent_notifications(websocket)

    def disconnect(self, websocket: WebSocket):
        """WebSocket接続を削除"""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")

    async def _send_recent_notifications(self, websocket: WebSocket):
        """最近の通知を送信"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            recent_notifications = [
                n for n in self.notification_history
                if n.timestamp > cutoff_time and (not n.expires_at or n.expires_at > datetime.utcnow())
            ]

            if recent_notifications:
                await websocket.send_text(json.dumps({
                    'type': 'notification_history',
                    'notifications': [n.to_dict() for n in recent_notifications[-10:]]  # 最新10件
                }))
        except Exception as e:
            logger.error(f"Failed to send recent notifications: {e}")

    async def broadcast_notification(self, notification: Notification):
        """通知をブロードキャスト"""
        # 履歴に追加
        self.notification_history.append(notification)
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]

        # アクティブな接続に通知を送信
        if self.active_connections:
            message = json.dumps({
                'type': 'notification',
                'notification': notification.to_dict()
            })

            disconnected = set()
            for websocket in self.active_connections:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.warning(f"Failed to send notification to websocket: {e}")
                    disconnected.add(websocket)

            # 切断された接続を削除
            for websocket in disconnected:
                self.disconnect(websocket)

        logger.info(f"Broadcasted notification: {notification.title} to {len(self.active_connections)} connections")

    def create_notification(
        self,
        notification_type: NotificationType,
        severity: AlertSeverity,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        expires_hours: Optional[int] = None
    ) -> Notification:
        """通知を作成"""
        notification_id = f"{notification_type.value}_{int(datetime.utcnow().timestamp())}"
        expires_at = None
        if expires_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_hours)

        return Notification(
            id=notification_id,
            type=notification_type,
            severity=severity,
            title=title,
            message=message,
            timestamp=datetime.utcnow(),
            data=data,
            expires_at=expires_at
        )

    async def send_system_alert(self, title: str, message: str, severity: AlertSeverity = AlertSeverity.WARNING, data: Optional[Dict[str, Any]] = None):
        """システムアラートを送信"""
        notification = self.create_notification(
            NotificationType.SYSTEM_ALERT,
            severity,
            title,
            message,
            data,
            expires_hours=24
        )
        await self.broadcast_notification(notification)

    async def send_performance_alert(self, metric: str, value: float, threshold: float, data: Optional[Dict[str, Any]] = None):
        """パフォーマンスアラートを送信"""
        severity = AlertSeverity.WARNING
        if metric in ['cpu_usage', 'memory_usage'] and value > 90:
            severity = AlertSeverity.ERROR
        elif metric == 'disk_usage' and value > 95:
            severity = AlertSeverity.CRITICAL

        title = f"パフォーマンス警告: {metric}"
        message = f"{metric} が閾値を超過しました: {value:.1f} (閾値: {threshold})"

        notification = self.create_notification(
            NotificationType.PERFORMANCE_WARNING,
            severity,
            title,
            message,
            data,
            expires_hours=1
        )
        await self.broadcast_notification(notification)

    async def send_database_alert(self, issue: str, recommendations: List[str] = None):
        """データベースアラートを送信"""
        notification = self.create_notification(
            NotificationType.DATABASE_ISSUE,
            AlertSeverity.ERROR,
            "データベース問題",
            issue,
            {'recommendations': recommendations or []},
            expires_hours=12
        )
        await self.broadcast_notification(notification)

    async def send_price_alert(self, symbol: str, current_price: float, alert_price: float, direction: str):
        """価格アラートを送信"""
        title = f"価格アラート: {symbol}"
        message = f"{symbol} の価格が {alert_price} を{direction}ました (現在価格: {current_price})"

        notification = self.create_notification(
            NotificationType.PRICE_ALERT,
            AlertSeverity.INFO,
            title,
            message,
            {
                'symbol': symbol,
                'current_price': current_price,
                'alert_price': alert_price,
                'direction': direction
            },
            expires_hours=6
        )
        await self.broadcast_notification(notification)

    async def send_server_status(self, status: str, message: str):
        """サーバー状態通知を送信"""
        severity = AlertSeverity.INFO
        if status.lower() in ['error', 'critical', 'down']:
            severity = AlertSeverity.CRITICAL
        elif status.lower() in ['warning', 'degraded']:
            severity = AlertSeverity.WARNING

        notification = self.create_notification(
            NotificationType.SERVER_STATUS,
            severity,
            f"サーバー状態: {status}",
            message,
            {'status': status},
            expires_hours=2
        )
        await self.broadcast_notification(notification)

    def get_active_notifications(self) -> List[Dict[str, Any]]:
        """アクティブな通知を取得"""
        now = datetime.utcnow()
        active = [
            n.to_dict() for n in self.notification_history
            if not n.expires_at or n.expires_at > now
        ]
        return active[-50:]  # 最新50件

    def get_notification_statistics(self) -> Dict[str, Any]:
        """通知統計を取得"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)

        recent_notifications = [
            n for n in self.notification_history
            if n.timestamp > last_24h
        ]

        stats = {
            'total_notifications_24h': len(recent_notifications),
            'active_connections': len(self.active_connections),
            'notification_types_24h': {},
            'severity_distribution_24h': {},
            'total_history': len(self.notification_history)
        }

        for notification in recent_notifications:
            # タイプ別統計
            type_key = notification.type.value
            stats['notification_types_24h'][type_key] = stats['notification_types_24h'].get(type_key, 0) + 1

            # 重要度別統計
            severity_key = notification.severity.value
            stats['severity_distribution_24h'][severity_key] = stats['severity_distribution_24h'].get(severity_key, 0) + 1

        return stats

    async def cleanup_expired_notifications(self):
        """期限切れ通知をクリーンアップ"""
        now = datetime.utcnow()
        original_count = len(self.notification_history)

        self.notification_history = [
            n for n in self.notification_history
            if not n.expires_at or n.expires_at > now
        ]

        cleaned_count = original_count - len(self.notification_history)
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired notifications")

# グローバル通知マネージャー
notification_manager = NotificationManager()

async def handle_websocket_notifications(websocket: WebSocket):
    """WebSocket通知ハンドラー"""
    await notification_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Handle ping/pong or other client messages if needed
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        notification_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        notification_manager.disconnect(websocket)

# 便利関数
async def send_system_alert(title: str, message: str, severity: AlertSeverity = AlertSeverity.WARNING, data: Optional[Dict[str, Any]] = None):
    """システムアラートを送信（便利関数）"""
    await notification_manager.send_system_alert(title, message, severity, data)

async def send_performance_alert(metric: str, value: float, threshold: float, data: Optional[Dict[str, Any]] = None):
    """パフォーマンスアラートを送信（便利関数）"""
    await notification_manager.send_performance_alert(metric, value, threshold, data)

def get_notification_stats() -> Dict[str, Any]:
    """通知統計を取得（便利関数）"""
    return notification_manager.get_notification_statistics()