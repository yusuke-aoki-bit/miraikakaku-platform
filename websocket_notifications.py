"""
WebSocket Notification System for Real-time Alerts
Phase 11: Real-time notification implementation
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set, List
import json
import asyncio
from datetime import datetime
from auth_utils import get_current_user_from_token
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'dbname': os.getenv('POSTGRES_DB', 'miraikakaku'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
}


class ConnectionManager:
    """
    WebSocket Connection Manager
    管理各ユーザーのWebSocket接続
    """
    def __init__(self):
        # user_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """新しいWebSocket接続を追加"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        print(f"✅ WebSocket connected: user_id={user_id}, total={len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """WebSocket接続を削除"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"❌ WebSocket disconnected: user_id={user_id}")

    async def send_personal_message(self, message: dict, user_id: str):
        """特定のユーザーにメッセージを送信"""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"⚠️  Failed to send message: {e}")
                    disconnected.add(connection)

            # 切断されたconnectionを削除
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)

    async def broadcast(self, message: dict):
        """全ユーザーにブロードキャスト"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)


# Global connection manager instance
manager = ConnectionManager()


def get_db_connection():
    """データベース接続を取得"""
    return psycopg2.connect(**DB_CONFIG)


async def check_price_alerts(user_id: str) -> List[dict]:
    """
    価格アラートをチェックして、トリガーされたアラートを返す
    """
    conn = None
    triggered_alerts = []

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # アクティブなアラートを取得
        cur.execute("""
            SELECT
                pa.id,
                pa.symbol,
                pa.alert_type,
                pa.target_price,
                pa.threshold_pct,
                sp.close_price as current_price,
                sm.company_name
            FROM price_alerts pa
            JOIN stock_master sm ON pa.symbol = sm.symbol
            LEFT JOIN (
                SELECT DISTINCT ON (symbol)
                    symbol, close_price, date
                FROM stock_prices
                ORDER BY symbol, date DESC
            ) sp ON pa.symbol = sp.symbol
            WHERE pa.user_id = %s
              AND pa.is_active = TRUE
              AND pa.triggered_at IS NULL
        """, (user_id,))

        alerts = cur.fetchall()

        for alert in alerts:
            triggered = False
            message = ""

            if alert['current_price'] is None:
                continue

            current_price = float(alert['current_price'])

            # アラートタイプごとの判定
            if alert['alert_type'] == 'price_above' and alert['target_price']:
                if current_price >= float(alert['target_price']):
                    triggered = True
                    message = f"{alert['company_name']} ({alert['symbol']}) が目標価格 ¥{alert['target_price']:,.0f} を上回りました（現在: ¥{current_price:,.0f}）"

            elif alert['alert_type'] == 'price_below' and alert['target_price']:
                if current_price <= float(alert['target_price']):
                    triggered = True
                    message = f"{alert['company_name']} ({alert['symbol']}) が目標価格 ¥{alert['target_price']:,.0f} を下回りました（現在: ¥{current_price:,.0f}）"

            elif alert['alert_type'] == 'price_change' and alert['threshold_pct']:
                # 前日比の変動率チェック（簡易実装）
                cur.execute("""
                    SELECT close_price
                    FROM stock_prices
                    WHERE symbol = %s
                    ORDER BY date DESC
                    OFFSET 1 LIMIT 1
                """, (alert['symbol'],))
                prev = cur.fetchone()

                if prev and prev['close_price']:
                    prev_price = float(prev['close_price'])
                    change_pct = ((current_price - prev_price) / prev_price) * 100

                    if abs(change_pct) >= float(alert['threshold_pct']):
                        triggered = True
                        direction = "上昇" if change_pct > 0 else "下落"
                        message = f"{alert['company_name']} ({alert['symbol']}) が{abs(change_pct):.1f}% {direction}しました（閾値: {alert['threshold_pct']}%）"

            if triggered:
                # アラートをトリガー済みとしてマーク
                cur.execute("""
                    UPDATE price_alerts
                    SET triggered_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (alert['id'],))
                conn.commit()

                triggered_alerts.append({
                    'id': alert['id'],
                    'symbol': alert['symbol'],
                    'company_name': alert['company_name'],
                    'alert_type': alert['alert_type'],
                    'current_price': current_price,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                })

        cur.close()

    except Exception as e:
        print(f"❌ Error checking alerts: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

    return triggered_alerts


async def monitor_alerts_task():
    """
    定期的にアラートをチェックするバックグラウンドタスク
    全アクティブユーザーのアラートを監視
    """
    while True:
        try:
            # 接続中のユーザーのアラートをチェック
            for user_id in list(manager.active_connections.keys()):
                triggered = await check_price_alerts(user_id)

                for alert in triggered:
                    # WebSocket経由で通知
                    await manager.send_personal_message({
                        'type': 'alert_triggered',
                        'data': alert
                    }, user_id)

            # 30秒ごとにチェック
            await asyncio.sleep(30)

        except Exception as e:
            print(f"❌ Error in monitor task: {e}")
            await asyncio.sleep(30)


# FastAPI router integration
from fastapi import APIRouter

router = APIRouter(prefix="/api/ws", tags=["websocket"])


@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """
    WebSocket通知エンドポイント

    接続方法:
    ws://localhost:8080/api/ws/notifications?token=<access_token>
    """
    # トークン検証
    if not token:
        await websocket.close(code=1008, reason="Token required")
        return

    try:
        # JWTトークンからユーザーを取得
        from jose import jwt, JWTError

        SECRET_KEY = os.getenv("JWT_SECRET_KEY", "miraikakaku-secret-key-change-in-production")
        ALGORITHM = "HS256"

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return

    except JWTError:
        await websocket.close(code=1008, reason="Invalid token")
        return

    # 接続を追加
    await manager.connect(websocket, str(user_id))

    # 接続成功メッセージ
    await websocket.send_json({
        'type': 'connected',
        'message': 'WebSocket connection established',
        'user_id': user_id,
        'timestamp': datetime.now().isoformat()
    })

    try:
        while True:
            # クライアントからのメッセージを受信（pingなど）
            data = await websocket.receive_text()

            if data == "ping":
                await websocket.send_json({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
            elif data == "check_alerts":
                # 手動でアラートチェックを実行
                triggered = await check_price_alerts(str(user_id))
                await websocket.send_json({
                    'type': 'alert_check_result',
                    'alerts': triggered,
                    'count': len(triggered),
                    'timestamp': datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, str(user_id))
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket, str(user_id))


@router.get("/connections/count")
async def get_connection_count():
    """現在のWebSocket接続数を取得（デバッグ用）"""
    total = sum(len(conns) for conns in manager.active_connections.values())
    return {
        'total_connections': total,
        'active_users': len(manager.active_connections),
        'users': list(manager.active_connections.keys())
    }


# アプリケーション起動時にバックグラウンドタスクを開始
async def start_monitoring():
    """監視タスクを開始"""
    asyncio.create_task(monitor_alerts_task())
    print("✅ Alert monitoring task started")
