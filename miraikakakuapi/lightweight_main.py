from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import json
import asyncio
from datetime import datetime, timedelta
import random
from typing import List, Optional

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Miraikakaku Lightweight API",
    description="軽量版金融分析・株価予測API",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket接続管理
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
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

manager = ConnectionManager()

# モックデータ生成
def generate_mock_price_data(symbol: str, days: int = 30):
    """モック価格データ生成"""
    base_price = {
        'AAPL': 225.0,
        'GOOGL': 2800.0,
        'MSFT': 420.0,
        'AMZN': 185.0,
        'TSLA': 250.0
    }.get(symbol, 150.0)
    
    data = []
    current_date = datetime.now()
    
    for i in range(days):
        date = current_date - timedelta(days=days-i-1)
        price_variation = random.uniform(-0.05, 0.05)
        daily_price = base_price * (1 + price_variation)
        
        data.append({
            "symbol": symbol.upper(),
            "date": date.strftime("%Y-%m-%d"),
            "open_price": round(daily_price * 0.995, 2),
            "high_price": round(daily_price * 1.02, 2),
            "low_price": round(daily_price * 0.98, 2),
            "close_price": round(daily_price, 2),
            "volume": random.randint(50000000, 200000000),
            "data_source": "Mock Data"
        })
    
    return data

def generate_mock_predictions(symbol: str, days: int = 7):
    """モック予測データ生成"""
    base_price = {
        'AAPL': 225.0,
        'GOOGL': 2800.0,
        'MSFT': 420.0,
        'AMZN': 185.0,
        'TSLA': 250.0
    }.get(symbol, 150.0)
    
    predictions = []
    current_date = datetime.now()
    
    for i in range(1, days + 1):
        date = current_date + timedelta(days=i)
        trend_factor = random.uniform(-0.03, 0.05)
        predicted_price = base_price * (1 + trend_factor)
        confidence = max(0.6, 0.95 - (i * 0.03))
        
        predictions.append({
            "symbol": symbol.upper(),
            "prediction_date": date.strftime("%Y-%m-%d"),
            "predicted_price": round(predicted_price, 2),
            "confidence_score": round(confidence, 3),
            "model_type": "LSTM-Mock",
            "prediction_horizon": f"{i}d",
            "is_active": True
        })
    
    return predictions

def generate_mock_indicators(symbol: str):
    """モックテクニカル指標生成"""
    base_price = {
        'AAPL': 225.0,
        'GOOGL': 2800.0,
        'MSFT': 420.0,
        'AMZN': 185.0,
        'TSLA': 250.0
    }.get(symbol, 150.0)
    
    return {
        'symbol': symbol.upper(),
        'current_price': round(base_price, 2),
        'sma_5': round(base_price * 0.998, 2),
        'sma_20': round(base_price * 0.995, 2),
        'sma_50': round(base_price * 0.990, 2),
        'rsi': round(random.uniform(30, 80), 2),
        'macd': round(random.uniform(-2, 2), 4),
        'bollinger_upper': round(base_price * 1.04, 2),
        'bollinger_middle': round(base_price, 2),
        'bollinger_lower': round(base_price * 0.96, 2),
        'volume_avg': random.randint(40000000, 80000000),
        'volume_ratio': round(random.uniform(0.5, 2.0), 2),
        'daily_change_pct': round(random.uniform(-3, 3), 2),
        'weekly_change_pct': round(random.uniform(-8, 8), 2),
        'current_volume': random.randint(20000000, 60000000),
        'last_updated': datetime.now().isoformat(),
        'data_points': 30
    }

@app.get("/")
async def root():
    return {
        "message": "Universal Stock Market API",
        "version": "1.0.0",
        "description": "軽量版 - モックデータ対応",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "miraikakaku-lightweight-api",
        "websocket_connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/finance/stocks/search")
async def search_stocks(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100)
):
    """株式検索API"""
    major_stocks = {
        'AAPL': {'name': 'Apple Inc.', 'exchange': 'NASDAQ', 'sector': 'Technology'},
        'GOOGL': {'name': 'Alphabet Inc.', 'exchange': 'NASDAQ', 'sector': 'Technology'},
        'MSFT': {'name': 'Microsoft Corporation', 'exchange': 'NASDAQ', 'sector': 'Technology'},
        'AMZN': {'name': 'Amazon.com Inc.', 'exchange': 'NASDAQ', 'sector': 'Consumer Discretionary'},
        'TSLA': {'name': 'Tesla, Inc.', 'exchange': 'NASDAQ', 'sector': 'Consumer Discretionary'},
        'META': {'name': 'Meta Platforms Inc.', 'exchange': 'NASDAQ', 'sector': 'Technology'},
        'NVDA': {'name': 'NVIDIA Corporation', 'exchange': 'NASDAQ', 'sector': 'Technology'},
        'JPM': {'name': 'JPMorgan Chase & Co.', 'exchange': 'NYSE', 'sector': 'Financial Services'},
    }
    
    results = []
    for symbol, info in major_stocks.items():
        if query.upper() in symbol or query.lower() in info['name'].lower():
            results.append({
                "symbol": symbol,
                "company_name": info['name'],
                "exchange": info['exchange'],
                "sector": info['sector'],
                "industry": None
            })
    
    return results[:limit]

@app.get("/api/finance/stocks/{symbol}/price")
async def get_stock_price(
    symbol: str,
    days: int = Query(30, ge=1, le=365)
):
    """株価履歴取得API"""
    logger.info(f"Price data mock: {symbol}, {days} days")
    return generate_mock_price_data(symbol, days)

@app.get("/api/finance/stocks/{symbol}/predictions")
async def get_stock_predictions(
    symbol: str,
    days: int = Query(7, ge=1, le=30)
):
    """株価予測取得API"""
    logger.info(f"Predictions mock: {symbol}, {days} days")
    return generate_mock_predictions(symbol, days)

@app.get("/api/finance/stocks/{symbol}/indicators")
async def get_technical_indicators(symbol: str):
    """テクニカル指標取得API"""
    logger.info(f"Indicators mock: {symbol}")
    return generate_mock_indicators(symbol)

@app.get("/api/finance/rankings/universal")
async def get_universal_rankings(limit: int = Query(20, ge=1, le=50)):
    """ユニバーサルランキング"""
    rankings = [
        {"symbol": "AAPL", "company_name": "Apple Inc.", "growth_potential": 15.2, "accuracy_score": 0.885, "composite_score": 0.82},
        {"symbol": "GOOGL", "company_name": "Alphabet Inc.", "growth_potential": 12.8, "accuracy_score": 0.790, "composite_score": 0.78},
        {"symbol": "MSFT", "company_name": "Microsoft Corporation", "growth_potential": 18.5, "accuracy_score": 0.825, "composite_score": 0.85},
        {"symbol": "TSLA", "company_name": "Tesla, Inc.", "growth_potential": 25.3, "accuracy_score": 0.720, "composite_score": 0.75},
        {"symbol": "NVDA", "company_name": "NVIDIA Corporation", "growth_potential": 35.2, "accuracy_score": 0.890, "composite_score": 0.92}
    ]
    
    return rankings[:limit]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket接続エンドポイント"""
    await manager.connect(websocket)
    try:
        welcome = {
            "type": "connection",
            "data": {
                "message": "Lightweight API WebSocketに接続しました",
                "timestamp": datetime.now().isoformat(),
                "active_connections": len(manager.active_connections)
            }
        }
        await manager.send_personal_message(json.dumps(welcome), websocket)
        
        # 定期的な価格更新（模擬）
        while True:
            symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
            for symbol in symbols:
                base_price = {
                    'AAPL': 225.0,
                    'GOOGL': 2800.0,
                    'MSFT': 420.0,
                    'TSLA': 250.0,
                    'NVDA': 950.0
                }.get(symbol, 150.0)
                
                price_update = {
                    "type": "price_update",
                    "data": {
                        "symbol": symbol,
                        "price": round(base_price * (1 + random.uniform(-0.02, 0.02)), 2),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                await manager.send_personal_message(json.dumps(price_update), websocket)
                await asyncio.sleep(1)
            
            await asyncio.sleep(10)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("lightweight_main:app", host="0.0.0.0", port=port, log_level="info")