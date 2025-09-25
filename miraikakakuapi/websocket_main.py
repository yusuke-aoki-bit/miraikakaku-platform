"""
WebSocket Integration with FastAPI
Phase 3.1 - リアルタイムAPI統合

FastAPI WebSocket endpoint integration for real-time AI inference
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from services.realtime_inference import realtime_server, RealtimeWebSocketServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    logger.info("🚀 Starting Realtime AI WebSocket server...")

    # サーバー初期化・開始
    await realtime_server.initialize()
    await realtime_server.start()

    logger.info("✅ Realtime AI WebSocket server started successfully")

    yield

    # サーバー停止
    logger.info("⏹ Stopping Realtime AI WebSocket server...")
    await realtime_server.stop()
    logger.info("✅ Realtime AI WebSocket server stopped")

# FastAPI アプリケーション作成
app = FastAPI(
    title="MiraiKakaku Realtime AI API",
    description="High-performance real-time AI stock prediction WebSocket API",
    version="3.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    try:
        server_stats = realtime_server.get_server_stats()

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "realtime-ai-websocket",
                "version": "3.1.0",
                "stats": server_stats,
                "capabilities": [
                    "websocket_realtime_predictions",
                    "market_data_streaming",
                    "alert_system",
                    "system_health_monitoring"
                ]
            }
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

@app.get("/stats")
async def get_server_stats():
    """サーバー統計取得"""
    try:
        stats = realtime_server.get_server_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"❌ Stats retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get server stats: {str(e)}"
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket エンドポイント

    リアルタイムAI予測、市場データ、アラートの配信

    接続例:
    ```javascript
    const ws = new WebSocket('ws://localhost:8080/ws');

    // 接続確立後
    ws.send(JSON.stringify({
        type: 'subscribe',
        channel: 'predictions',
        symbol: 'AAPL'
    }));

    // 予測リクエスト
    ws.send(JSON.stringify({
        type: 'request_prediction',
        symbol: 'AAPL',
        options: {
            horizon: '1d',
            confidence: 0.95,
            model: 'ensemble'
        }
    }));
    ```
    """
    await realtime_server.handle_websocket(websocket)

@app.get("/")
async def root():
    """API ルート"""
    return {
        "message": "MiraiKakaku Realtime AI WebSocket API",
        "version": "3.1.0",
        "endpoints": {
            "websocket": "/ws",
            "health": "/health",
            "stats": "/stats",
            "docs": "/docs"
        },
        "features": [
            "Real-time stock predictions (< 100ms)",
            "Live market data streaming",
            "Instant alert notifications",
            "System health monitoring",
            "Auto-reconnection support",
            "High-concurrency (10,000+ connections)"
        ]
    }

# WebSocket 接続管理用のRESTエンドポイント

@app.get("/connections")
async def get_connection_info():
    """アクティブな接続情報を取得"""
    try:
        connection_stats = realtime_server.connection_manager.get_stats()
        return JSONResponse(content=connection_stats)
    except Exception as e:
        logger.error(f"❌ Connection info retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get connection info: {str(e)}"
        )

@app.get("/inference-stats")
async def get_inference_stats():
    """推論エンジンの統計情報を取得"""
    try:
        inference_stats = realtime_server.inference_engine.get_stats()
        return JSONResponse(content=inference_stats)
    except Exception as e:
        logger.error(f"❌ Inference stats retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get inference stats: {str(e)}"
        )

@app.post("/broadcast")
async def broadcast_message(message: Dict[str, Any]):
    """
    管理者用：全接続にメッセージ配信

    例:
    ```json
    {
        "channel": "system_health",
        "message": {
            "type": "maintenance_notice",
            "message": "System maintenance in 5 minutes",
            "severity": "medium"
        }
    }
    ```
    """
    try:
        channel = message.get("channel", "system_health")
        msg_data = message.get("message", {})

        sent_count = await realtime_server.connection_manager.broadcast_to_channel(
            channel, msg_data
        )

        return JSONResponse(content={
            "status": "success",
            "sent_to_connections": sent_count,
            "channel": channel
        })
    except Exception as e:
        logger.error(f"❌ Broadcast failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to broadcast message: {str(e)}"
        )

# 開発用エンドポイント

@app.post("/dev/simulate-prediction")
async def simulate_prediction_broadcast(symbol: str, count: int = 1):
    """
    開発用：模擬予測を配信
    """
    try:
        sent_total = 0

        for i in range(count):
            prediction = await realtime_server.inference_engine.generate_prediction(
                symbol=symbol,
                model="ensemble"
            )

            sent_count = await realtime_server.connection_manager.broadcast_to_channel(
                "predictions",
                {
                    "type": "prediction",
                    "data": prediction.__dict__
                },
                symbol=symbol
            )

            sent_total += sent_count

            if count > 1:
                await asyncio.sleep(0.1)  # 100ms間隔

        return JSONResponse(content={
            "status": "success",
            "predictions_sent": count,
            "total_deliveries": sent_total,
            "symbol": symbol
        })
    except Exception as e:
        logger.error(f"❌ Prediction simulation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to simulate prediction: {str(e)}"
        )

if __name__ == "__main__":
    # サーバー起動
    uvicorn.run(
        "websocket_main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
        ws_max_size=16777216,  # 16MB
        ws_ping_interval=20,   # 20秒間隔でping
        ws_ping_timeout=10,    # 10秒でpingタイムアウト
    )