"""
Real-time AI Inference Engine
Phase 3.1 - リアルタイム推論システム

High-performance WebSocket server for real-time stock predictions
Target: < 100ms response time, 10,000+ concurrent connections
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Any
import weakref
from dataclasses import dataclass, asdict
from enum import Enum

import redis.asyncio as redis
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException
import numpy as np
from fastapi import WebSocket, WebSocketDisconnect
import tensorflow as tf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    REQUEST_PREDICTION = "request_prediction"
    PING = "ping"
    PONG = "pong"

class ChannelType(Enum):
    PREDICTIONS = "predictions"
    MARKET_DATA = "market_data"
    ALERTS = "alerts"
    SYSTEM_HEALTH = "system_health"

@dataclass
class RealtimePrediction:
    symbol: str
    prediction: float
    confidence: float
    timestamp: str
    model_version: str
    factors: List[Dict[str, Any]]
    latency_ms: int

@dataclass
class MarketData:
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: str

@dataclass
class SystemHealth:
    status: str
    latency_ms: float
    active_connections: int
    predictions_per_second: float
    timestamp: str

class ConnectionManager:
    """管理 WebSocket 接続とサブスクリプション"""

    def __init__(self):
        # 接続管理
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_subscriptions: Dict[str, Set[str]] = {}
        self.channel_subscribers: Dict[str, Set[str]] = {}

        # パフォーマンス統計
        self.connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
            'start_time': time.time()
        }

    async def connect(self, websocket: WebSocket) -> str:
        """新しい WebSocket 接続を登録"""
        connection_id = str(uuid.uuid4())

        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.connection_subscriptions[connection_id] = set()

        self.connection_stats['total_connections'] += 1
        self.connection_stats['active_connections'] = len(self.active_connections)

        # 接続確立メッセージ送信
        await self.send_to_connection(connection_id, {
            'type': 'connection_established',
            'connection_id': connection_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'server_info': {
                'version': '3.1.0',
                'capabilities': ['predictions', 'market_data', 'alerts', 'system_health']
            }
        })

        logger.info(f"✅ Connection established: {connection_id}")
        return connection_id

    async def disconnect(self, connection_id: str):
        """WebSocket 接続を切断"""
        if connection_id in self.active_connections:
            # サブスクリプション解除
            await self.unsubscribe_all(connection_id)

            # 接続削除
            del self.active_connections[connection_id]
            del self.connection_subscriptions[connection_id]

            self.connection_stats['active_connections'] = len(self.active_connections)
            logger.info(f"❌ Connection disconnected: {connection_id}")

    async def subscribe(self, connection_id: str, channel: str, **kwargs):
        """チャンネルにサブスクライブ"""
        if connection_id not in self.active_connections:
            return False

        subscription_key = f"{channel}:{kwargs.get('symbol', kwargs.get('user_id', 'global'))}"

        # 接続のサブスクリプションに追加
        self.connection_subscriptions[connection_id].add(subscription_key)

        # チャンネルの購読者に追加
        if subscription_key not in self.channel_subscribers:
            self.channel_subscribers[subscription_key] = set()
        self.channel_subscribers[subscription_key].add(connection_id)

        logger.info(f"📡 Subscription added: {connection_id} -> {subscription_key}")
        return True

    async def unsubscribe(self, connection_id: str, channel: str, **kwargs):
        """チャンネルから登録解除"""
        subscription_key = f"{channel}:{kwargs.get('symbol', kwargs.get('user_id', 'global'))}"

        # 接続のサブスクリプションから削除
        if connection_id in self.connection_subscriptions:
            self.connection_subscriptions[connection_id].discard(subscription_key)

        # チャンネルの購読者から削除
        if subscription_key in self.channel_subscribers:
            self.channel_subscribers[subscription_key].discard(connection_id)
            if not self.channel_subscribers[subscription_key]:
                del self.channel_subscribers[subscription_key]

        logger.info(f"📡 Subscription removed: {connection_id} -> {subscription_key}")

    async def unsubscribe_all(self, connection_id: str):
        """接続のすべてのサブスクリプションを解除"""
        if connection_id not in self.connection_subscriptions:
            return

        subscriptions = self.connection_subscriptions[connection_id].copy()
        for subscription in subscriptions:
            channel_parts = subscription.split(':', 1)
            channel = channel_parts[0]
            identifier = channel_parts[1] if len(channel_parts) > 1 else 'global'

            if channel == 'predictions':
                await self.unsubscribe(connection_id, channel, symbol=identifier)
            elif channel == 'alerts':
                await self.unsubscribe(connection_id, channel, user_id=identifier)
            else:
                await self.unsubscribe(connection_id, channel)

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any], **kwargs):
        """チャンネルの全購読者にメッセージ配信"""
        subscription_key = f"{channel}:{kwargs.get('symbol', kwargs.get('user_id', 'global'))}"

        if subscription_key not in self.channel_subscribers:
            return 0

        subscribers = self.channel_subscribers[subscription_key].copy()
        sent_count = 0

        for connection_id in subscribers:
            try:
                await self.send_to_connection(connection_id, message)
                sent_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to send to {connection_id}: {e}")
                # 失敗した接続は自動的に切断される

        return sent_count

    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """特定の接続にメッセージ送信"""
        if connection_id not in self.active_connections:
            return False

        websocket = self.active_connections[connection_id]
        try:
            await websocket.send_text(json.dumps(message))
            self.connection_stats['messages_sent'] += 1
            return True
        except (ConnectionClosed, WebSocketDisconnect):
            # 接続が閉じられている場合は自動切断
            await self.disconnect(connection_id)
            return False
        except Exception as e:
            logger.error(f"❌ Send error to {connection_id}: {e}")
            self.connection_stats['errors'] += 1
            return False

    def get_stats(self) -> Dict[str, Any]:
        """接続統計を取得"""
        uptime = time.time() - self.connection_stats['start_time']
        return {
            **self.connection_stats,
            'uptime_seconds': uptime,
            'messages_per_second': self.connection_stats['messages_sent'] / max(uptime, 1),
            'channel_count': len(self.channel_subscribers),
            'subscription_count': sum(len(subs) for subs in self.connection_subscriptions.values())
        }

class RealtimeInferenceEngine:
    """リアルタイム推論エンジン"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client: Optional[redis.Redis] = None
        self.redis_url = redis_url

        # 推論モデル (簡易実装、実際はより高度なモデルを使用)
        self.model_cache: Dict[str, Any] = {}
        self.prediction_cache: Dict[str, Dict] = {}
        self.cache_ttl = 60  # 1分間キャッシュ

        # パフォーマンス統計
        self.inference_stats = {
            'predictions_generated': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_latency_ms': 0,
            'total_latency_ms': 0,
            'start_time': time.time()
        }

    async def initialize(self):
        """推論エンジンを初期化"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            # Redis なしでも動作するようにフォールバック

        # モデルのウォームアップ (模擬)
        await self.warmup_models()
        logger.info("🤖 Inference engine initialized")

    async def warmup_models(self):
        """モデルのウォームアップ"""
        # 実際の実装では、TensorFlow/PyTorch モデルをロード
        # 現在は模擬実装
        logger.info("🔥 Warming up inference models...")

        # 模擬的なウォームアップ
        await asyncio.sleep(0.1)

        self.model_cache['lstm'] = {'version': '1.0', 'loaded': True}
        self.model_cache['transformer'] = {'version': '1.1', 'loaded': True}
        self.model_cache['ensemble'] = {'version': '2.0', 'loaded': True}

        logger.info("✅ Models warmed up successfully")

    async def generate_prediction(self, symbol: str, model: str = 'ensemble', **options) -> RealtimePrediction:
        """リアルタイム予測生成"""
        start_time = time.time()

        # キャッシュチェック
        cache_key = f"{symbol}:{model}:{hash(str(options))}"
        cached_result = self.prediction_cache.get(cache_key)

        if cached_result and time.time() - cached_result['timestamp'] < self.cache_ttl:
            self.inference_stats['cache_hits'] += 1
            cached_result['from_cache'] = True
            latency_ms = int((time.time() - start_time) * 1000)
            cached_result['latency_ms'] = latency_ms
            return RealtimePrediction(**cached_result)

        self.inference_stats['cache_misses'] += 1

        try:
            # 実際の推論処理 (現在は模擬実装)
            prediction_result = await self._run_inference(symbol, model, **options)

            # 推論結果をキャッシュ
            prediction_data = {
                'symbol': symbol,
                'prediction': prediction_result['prediction'],
                'confidence': prediction_result['confidence'],
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'model_version': f"{model}_v1.0",
                'factors': prediction_result['factors'],
                'latency_ms': int((time.time() - start_time) * 1000),
                'from_cache': False
            }

            self.prediction_cache[cache_key] = {
                **prediction_data,
                'timestamp': time.time()
            }

            # 統計更新
            latency_ms = prediction_data['latency_ms']
            self.inference_stats['predictions_generated'] += 1
            self.inference_stats['total_latency_ms'] += latency_ms
            self.inference_stats['average_latency_ms'] = (
                self.inference_stats['total_latency_ms'] /
                self.inference_stats['predictions_generated']
            )

            return RealtimePrediction(**prediction_data)

        except Exception as e:
            logger.error(f"❌ Inference error for {symbol}: {e}")
            # エラー時はフォールバック予測を返す
            return await self._fallback_prediction(symbol, start_time)

    async def _run_inference(self, symbol: str, model: str, **options) -> Dict[str, Any]:
        """実際の推論処理 (模擬実装)"""
        # 実際の実装では、ここでTensorFlow/PyTorchモデルを実行
        await asyncio.sleep(0.05)  # 50ms の推論時間をシミュレート

        # 模擬予測結果
        base_price = hash(symbol) % 1000 + 50  # 50-1050の範囲
        prediction = base_price * (1 + np.random.normal(0.02, 0.05))  # ±5%の変動
        confidence = np.random.uniform(0.7, 0.95)

        factors = [
            {
                'name': 'Technical Analysis',
                'impact': np.random.uniform(-0.3, 0.3),
                'confidence': np.random.uniform(0.6, 0.9)
            },
            {
                'name': 'Market Sentiment',
                'impact': np.random.uniform(-0.2, 0.2),
                'confidence': np.random.uniform(0.7, 0.95)
            },
            {
                'name': 'Volume Analysis',
                'impact': np.random.uniform(-0.1, 0.1),
                'confidence': np.random.uniform(0.8, 0.95)
            }
        ]

        return {
            'prediction': float(prediction),
            'confidence': float(confidence),
            'factors': factors
        }

    async def _fallback_prediction(self, symbol: str, start_time: float) -> RealtimePrediction:
        """フォールバック予測"""
        return RealtimePrediction(
            symbol=symbol,
            prediction=100.0,  # デフォルト価格
            confidence=0.5,    # 低信頼度
            timestamp=datetime.now(timezone.utc).isoformat(),
            model_version="fallback_v1.0",
            factors=[{
                'name': 'Fallback',
                'impact': 0.0,
                'confidence': 0.5
            }],
            latency_ms=int((time.time() - start_time) * 1000)
        )

    def get_stats(self) -> Dict[str, Any]:
        """推論統計を取得"""
        uptime = time.time() - self.inference_stats['start_time']
        return {
            **self.inference_stats,
            'uptime_seconds': uptime,
            'predictions_per_second': self.inference_stats['predictions_generated'] / max(uptime, 1),
            'cache_hit_rate': (
                self.inference_stats['cache_hits'] /
                max(self.inference_stats['cache_hits'] + self.inference_stats['cache_misses'], 1)
            ),
            'cached_predictions': len(self.prediction_cache)
        }

class RealtimeWebSocketServer:
    """リアルタイム WebSocket サーバー"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.connection_manager = ConnectionManager()
        self.inference_engine = RealtimeInferenceEngine(redis_url)
        self.is_running = False
        self.health_check_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """サーバーを初期化"""
        await self.inference_engine.initialize()
        logger.info("🚀 Realtime WebSocket server initialized")

    async def start(self):
        """サーバー開始"""
        self.is_running = True

        # ヘルスチェックタスクを開始
        self.health_check_task = asyncio.create_task(self.health_check_loop())

        logger.info("✅ Realtime WebSocket server started")

    async def stop(self):
        """サーバー停止"""
        self.is_running = False

        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        logger.info("⏹ Realtime WebSocket server stopped")

    async def handle_websocket(self, websocket: WebSocket):
        """WebSocket 接続処理"""
        connection_id = await self.connection_manager.connect(websocket)

        try:
            while self.is_running:
                try:
                    # メッセージ受信 (タイムアウト30秒)
                    message_text = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=30.0
                    )

                    # メッセージ処理
                    await self.handle_message(connection_id, message_text)

                except asyncio.TimeoutError:
                    # タイムアウト - ping送信
                    await self.connection_manager.send_to_connection(connection_id, {
                        'type': 'ping',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

                except WebSocketDisconnect:
                    logger.info(f"🔌 Client disconnected: {connection_id}")
                    break

                except Exception as e:
                    logger.error(f"❌ WebSocket error for {connection_id}: {e}")
                    await self.connection_manager.send_to_connection(connection_id, {
                        'type': 'error',
                        'error': str(e),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

        finally:
            await self.connection_manager.disconnect(connection_id)

    async def handle_message(self, connection_id: str, message_text: str):
        """メッセージ処理"""
        try:
            message = json.loads(message_text)
            message_type = message.get('type')

            if message_type == MessageType.SUBSCRIBE.value:
                await self.handle_subscribe(connection_id, message)

            elif message_type == MessageType.UNSUBSCRIBE.value:
                await self.handle_unsubscribe(connection_id, message)

            elif message_type == MessageType.REQUEST_PREDICTION.value:
                await self.handle_prediction_request(connection_id, message)

            elif message_type == MessageType.PING.value:
                await self.connection_manager.send_to_connection(connection_id, {
                    'type': 'pong',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })

            else:
                logger.warning(f"🤔 Unknown message type: {message_type}")

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {e}")
            await self.connection_manager.send_to_connection(connection_id, {
                'type': 'error',
                'error': 'Invalid JSON format',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

    async def handle_subscribe(self, connection_id: str, message: Dict[str, Any]):
        """サブスクリプション処理"""
        channel = message.get('channel')

        if channel == ChannelType.PREDICTIONS.value:
            symbol = message.get('symbol')
            if symbol:
                await self.connection_manager.subscribe(connection_id, channel, symbol=symbol)

        elif channel == ChannelType.ALERTS.value:
            user_id = message.get('user_id')
            if user_id:
                await self.connection_manager.subscribe(connection_id, channel, user_id=user_id)

        elif channel == ChannelType.SYSTEM_HEALTH.value:
            await self.connection_manager.subscribe(connection_id, channel)

        else:
            await self.connection_manager.send_to_connection(connection_id, {
                'type': 'error',
                'error': f'Unknown channel: {channel}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

    async def handle_unsubscribe(self, connection_id: str, message: Dict[str, Any]):
        """登録解除処理"""
        channel = message.get('channel')

        if channel == ChannelType.PREDICTIONS.value:
            symbol = message.get('symbol')
            if symbol:
                await self.connection_manager.unsubscribe(connection_id, channel, symbol=symbol)

        elif channel == ChannelType.ALERTS.value:
            user_id = message.get('user_id')
            if user_id:
                await self.connection_manager.unsubscribe(connection_id, channel, user_id=user_id)

        elif channel == ChannelType.SYSTEM_HEALTH.value:
            await self.connection_manager.unsubscribe(connection_id, channel)

    async def handle_prediction_request(self, connection_id: str, message: Dict[str, Any]):
        """予測リクエスト処理"""
        symbol = message.get('symbol')
        options = message.get('options', {})

        if not symbol:
            await self.connection_manager.send_to_connection(connection_id, {
                'type': 'error',
                'error': 'Symbol required for prediction request',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            return

        try:
            # 予測生成
            prediction = await self.inference_engine.generate_prediction(symbol, **options)

            # 結果送信
            await self.connection_manager.send_to_connection(connection_id, {
                'type': 'prediction',
                'data': asdict(prediction),
                'request_id': message.get('request_id'),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

        except Exception as e:
            logger.error(f"❌ Prediction request error: {e}")
            await self.connection_manager.send_to_connection(connection_id, {
                'type': 'error',
                'error': f'Prediction failed: {str(e)}',
                'request_id': message.get('request_id'),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

    async def health_check_loop(self):
        """ヘルスチェック配信ループ"""
        while self.is_running:
            try:
                # システムヘルス情報作成
                connection_stats = self.connection_manager.get_stats()
                inference_stats = self.inference_engine.get_stats()

                health_data = SystemHealth(
                    status='healthy' if self.is_running else 'down',
                    latency_ms=inference_stats['average_latency_ms'],
                    active_connections=connection_stats['active_connections'],
                    predictions_per_second=inference_stats['predictions_per_second'],
                    timestamp=datetime.now(timezone.utc).isoformat()
                )

                # システムヘルス配信
                await self.connection_manager.broadcast_to_channel(
                    ChannelType.SYSTEM_HEALTH.value,
                    {
                        'type': 'system_health',
                        'data': asdict(health_data),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                )

                # 30秒間隔
                await asyncio.sleep(30)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                await asyncio.sleep(10)

    def get_server_stats(self) -> Dict[str, Any]:
        """サーバー統計取得"""
        return {
            'connection_stats': self.connection_manager.get_stats(),
            'inference_stats': self.inference_engine.get_stats(),
            'server_status': {
                'running': self.is_running,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }

# グローバルサーバーインスタンス
realtime_server = RealtimeWebSocketServer()

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket エンドポイント"""
    await realtime_server.handle_websocket(websocket)