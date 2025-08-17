from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket接続: {len(self.active_connections)}件")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket切断: {len(self.active_connections)}件")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"WebSocket送信エラー: {e}")
                disconnected.append(connection)
        
        # 切断されたコネクションを削除
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # 接続時にウェルカムメッセージを送信
        welcome_message = {
            "type": "connection",
            "data": {
                "message": "Miraikakaku WebSocketに接続しました",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await manager.send_personal_message(json.dumps(welcome_message), websocket)
        
        # 定期的に価格更新をシミュレート
        while True:
            # 実際の実装では、ここで最新の株価データを取得
            price_update = {
                "type": "price_update",
                "data": {
                    "symbol": "AAPL",
                    "price": 150.25 + (hash(str(datetime.utcnow())) % 100 - 50) / 100,
                    "change": 1.25,
                    "change_percent": 0.84,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            await manager.send_personal_message(json.dumps(price_update), websocket)
            await asyncio.sleep(5)  # 5秒間隔で更新
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.websocket("/ws/{symbol}")
async def websocket_symbol_endpoint(websocket: WebSocket, symbol: str):
    """特定銘柄のWebSocket接続"""
    await manager.connect(websocket)
    try:
        # 銘柄固有の価格更新を送信
        while True:
            price_update = {
                "type": "price_update",
                "data": {
                    "symbol": symbol.upper(),
                    "price": 100 + (hash(str(datetime.utcnow()) + symbol) % 200),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            await manager.send_personal_message(json.dumps(price_update), websocket)
            await asyncio.sleep(3)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ブロードキャスト用のヘルパー関数
async def broadcast_price_update(symbol: str, price_data: dict):
    """価格更新をすべてのクライアントにブロードキャスト"""
    message = {
        "type": "price_update",
        "data": {
            "symbol": symbol,
            **price_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    await manager.broadcast(json.dumps(message))

async def broadcast_prediction_update(symbol: str, prediction_data: dict):
    """予測更新をすべてのクライアントにブロードキャスト"""
    message = {
        "type": "prediction_update",
        "data": {
            "symbol": symbol,
            **prediction_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    await manager.broadcast(json.dumps(message))