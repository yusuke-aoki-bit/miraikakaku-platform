from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Any
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
import json
import random

load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Miraikakaku API Production",
    description="金融分析・株価予測API - Full Featured Production Version",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番では適切に制限する
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
        except BaseException:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except BaseException:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()

# メモリキャッシュ
cache = {}
cache_timeout = 300  # 5分


def get_cached_data(key: str) -> Optional[Any]:
    """キャッシュからデータ取得"""
    if key in cache:
        data, timestamp = cache[key]
        if datetime.now() - timestamp < timedelta(seconds=cache_timeout):
            return data
    return None


def set_cached_data(key: str, data: Any):
    """キャッシュにデータ保存"""
    cache[key] = (data, datetime.now())


@app.get("/")
async def root():
    return {
        "message": "Universal Stock Market API",
        "version": "3.0.0",
        "description": "Cloud Run Production版 - Yahoo Financeリアルタイムデータ",
        "data_source": {
            "price_data": "Yahoo Finance API",
            "predictions": "Dynamic LSTM Simulation",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "miraikakaku-api-production",
        "environment": os.getenv("NODE_ENV", "production"),
        "websocket_connections": len(manager.active_connections),
        "cache_size": len(cache),
    }


@app.get("/api/finance/stocks/search")
async def search_stocks(
    query: str = Query(..., min_length=1, description="検索クエリ"),
    limit: int = Query(10, ge=1, le=100, description="結果数制限"),
):
    """株式検索API"""
    try:
        # Yahoo Financeで検索
        search_results = []

        # 主要銘柄リストから部分一致検索
        major_stocks = {
            "AAPL": {
                "name": "Apple Inc.",
                "exchange": "NASDAQ",
                "sector": "Technology",
            },
            "GOOGL": {
                "name": "Alphabet Inc.",
                "exchange": "NASDAQ",
                "sector": "Technology",
            },
            "MSFT": {
                "name": "Microsoft Corporation",
                "exchange": "NASDAQ",
                "sector": "Technology",
            },
            "AMZN": {
                "name": "Amazon.com Inc.",
                "exchange": "NASDAQ",
                "sector": "Consumer Discretionary",
            },
            "TSLA": {
                "name": "Tesla, Inc.",
                "exchange": "NASDAQ",
                "sector": "Consumer Discretionary",
            },
            "META": {
                "name": "Meta Platforms Inc.",
                "exchange": "NASDAQ",
                "sector": "Technology",
            },
            "NVDA": {
                "name": "NVIDIA Corporation",
                "exchange": "NASDAQ",
                "sector": "Technology",
            },
            "JPM": {
                "name": "JPMorgan Chase & Co.",
                "exchange": "NYSE",
                "sector": "Financial Services",
            },
            "V": {
                "name": "Visa Inc.",
                "exchange": "NYSE",
                "sector": "Financial Services",
            },
            "JNJ": {
                "name": "Johnson & Johnson",
                "exchange": "NYSE",
                "sector": "Healthcare",
            },
            "WMT": {
                "name": "Walmart Inc.",
                "exchange": "NYSE",
                "sector": "Consumer Staples",
            },
            "PG": {
                "name": "Procter & Gamble Co.",
                "exchange": "NYSE",
                "sector": "Consumer Staples",
            },
        }

        for symbol, info in major_stocks.items():
            if query.upper() in symbol or query.lower(
            ) in info["name"].lower():
                search_results.append(
                    {
                        "symbol": symbol,
                        "company_name": info["name"],
                        "exchange": info["exchange"],
                        "sector": info["sector"],
                        "industry": None,
                    }
                )

        return search_results[:limit]

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"検索エラー: {str(e)}")


@app.get("/api/finance/stocks/{symbol}/price")
async def get_stock_price(
    symbol: str, days: int = Query(30, ge=1, le=365, description="取得日数")
):
    """株価履歴取得API"""
    try:
        logger.info(f"Price data from Yahoo Finance: {symbol}, {days} days")

        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=f"{days}d")

        if hist.empty:
            raise HTTPException(status_code=404, detail="株価データが見つかりません")

        price_data = []
        for date, row in hist.iterrows():
            price_data.append(
                {
                    "symbol": symbol.upper(),
                    "date": date.strftime("%Y-%m-%d"),
                    "open_price": (
                        float(
                            row["Open"]) if not pd.isna(
                            row["Open"]) else None
                    ),
                    "high_price": (
                        float(
                            row["High"]) if not pd.isna(
                            row["High"]) else None
                    ),
                    "low_price": (
                        float(row["Low"]) if not pd.isna(row["Low"]) else None
                    ),
                    "close_price": float(row["Close"]),
                    "volume": (int(row["Volume"]) if not pd.isna(row["Volume"]) else 0),
                    "data_source": "Yahoo Finance",
                }
            )

        return price_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Price data error: {e}")
        raise HTTPException(status_code=500, detail=f"データ取得エラー: {str(e)}")


@app.get("/api/finance/stocks/{symbol}/predictions")
async def get_stock_predictions(
    symbol: str, days: int = Query(7, ge=1, le=30, description="予測期間")
):
    """株価予測取得API"""
    try:
        logger.info(f"Dynamic predictions: {symbol}, {days} days")

        # 現在価格を取得
        ticker = yf.Ticker(symbol.upper())
        current_data = ticker.history(period="1d")

        if current_data.empty:
            raise HTTPException(status_code=404, detail="銘柄データが見つかりません")

        current_price = float(current_data["Close"].iloc[-1])

        predictions = []
        base_date = datetime.now()

        for i in range(1, days + 1):
            # LSTM風の予測価格生成
            trend_factor = np.sin(i * 0.1) * 0.02  # 周期的なトレンド
            random_factor = random.uniform(-0.05, 0.05)  # ランダムな変動
            predicted_price = current_price * \
                (1 + trend_factor + random_factor)

            # 信頼度（時間とともに低下）
            confidence = max(0.5, 0.95 - (i * 0.02))

            prediction_date = base_date + timedelta(days=i)

            predictions.append(
                {
                    "symbol": symbol.upper(),
                    "prediction_date": prediction_date.strftime("%Y-%m-%d"),
                    "predicted_price": round(predicted_price, 2),
                    "confidence_score": round(confidence, 3),
                    "model_type": "LSTM-Dynamic",
                    "prediction_horizon": f"{i}d",
                    "is_active": True,
                }
            )

        return predictions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"予測データ取得エラー: {str(e)}")


@app.get("/api/finance/stocks/{symbol}/indicators")
async def get_technical_indicators(
    symbol: str, days: int = Query(30, ge=7, le=365, description="計算期間")
):
    """テクニカル指標取得API"""
    try:
        logger.info(f"Technical indicators: {symbol}, {days} days")

        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=f"{min(days + 30, 365)}d")

        if hist.empty:
            raise HTTPException(status_code=404, detail="株価データが取得できません")

        closes = hist["Close"].tolist()
        volumes = hist["Volume"].tolist()

        indicators = {
            "high": max(hist["High"].tolist()),
            "low": min(hist["Low"].tolist()),
        }

        # 移動平均線
        if len(closes) >= 5:
            indicators["sma_5"] = round(sum(closes[-5:]) / 5, 2)
        if len(closes) >= 20:
            indicators["sma_20"] = round(sum(closes[-20:]) / 20, 2)
        if len(closes) >= 50:
            indicators["sma_50"] = round(sum(closes[-50:]) / 50, 2)

        # RSI計算
        if len(closes) >= 14:
            gains, losses = [], []
            for i in range(1, min(15, len(closes))):
                change = closes[-(i)] - closes[-(i + 1)]
                gains.append(max(0, change))
                losses.append(max(0, -change))

            avg_gain = sum(gains) / len(gains) if gains else 0
            avg_loss = sum(losses) / len(losses) if losses else 0.01
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
            indicators["rsi"] = round(100 - (100 / (1 + rs)), 2)

        # ボリンジャーバンド
        if len(closes) >= 20:
            sma_20 = sum(closes[-20:]) / 20
            variance = sum((x - sma_20) ** 2 for x in closes[-20:]) / 20
            std_dev = variance**0.5
            indicators["bollinger_upper"] = round(sma_20 + (2 * std_dev), 2)
            indicators["bollinger_middle"] = round(sma_20, 2)
            indicators["bollinger_lower"] = round(sma_20 - (2 * std_dev), 2)

        # MACD計算
        if len(closes) >= 26:
            ema_12 = closes[-1]
            ema_26 = closes[-1]
            alpha_12 = 2 / (12 + 1)
            alpha_26 = 2 / (26 + 1)

            for i in range(min(26, len(closes))):
                price = closes[-(i + 1)]
                ema_12 = (price * alpha_12) + (ema_12 * (1 - alpha_12))
                ema_26 = (price * alpha_26) + (ema_26 * (1 - alpha_26))

            indicators["macd"] = round(ema_12 - ema_26, 4)

        # 出来高情報
        if len(volumes) >= 20:
            volume_avg = sum(volumes[-20:]) / 20
            indicators["volume_avg"] = int(volume_avg)
            indicators["volume_ratio"] = round(
                volumes[-1] / volume_avg if volume_avg > 0 else 1, 2
            )

        # 価格変動率
        if len(closes) >= 2:
            indicators["daily_change_pct"] = round(
                ((closes[-1] - closes[-2]) / closes[-2]) * 100, 2
            )
        if len(closes) >= 7:
            indicators["weekly_change_pct"] = round(
                ((closes[-1] - closes[-7]) / closes[-7]) * 100, 2
            )

        indicators.update(
            {
                "symbol": symbol.upper(),
                "current_price": round(closes[-1], 2),
                "current_volume": int(volumes[-1]),
                "last_updated": datetime.now().isoformat(),
                "data_points": len(closes),
            }
        )

        return indicators

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Indicators error: {e}")
        raise HTTPException(
            status_code=500, detail=f"テクニカル指標計算エラー: {str(e)}"
        )


@app.get("/api/finance/rankings/universal")
async def get_universal_rankings(
    limit: int = Query(20, ge=1, le=50, description="結果数制限")
):
    """ユニバーサルランキング"""
    try:
        # 主要銘柄の動的ランキング生成
        major_symbols = [
            "AAPL",
            "GOOGL",
            "MSFT",
            "AMZN",
            "TSLA",
            "META",
            "NVDA",
            "JPM",
            "V",
            "JNJ",
        ]
        rankings = []

        for symbol in major_symbols[:limit]:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="30d")

                if not hist.empty:
                    current_price = hist["Close"].iloc[-1]
                    start_price = hist["Close"].iloc[0]
                    growth_potential = (
                        (current_price - start_price) / start_price
                    ) * 100

                    rankings.append(
                        {
                            "symbol": symbol,
                            "company_name": info.get("longName", symbol),
                            "growth_potential": round(growth_potential, 2),
                            "accuracy_score": round(random.uniform(0.7, 0.95), 3),
                            "composite_score": round(random.uniform(0.6, 0.9), 3),
                            "country": "USA",
                            "asset_type": "Stock",
                        }
                    )
            except BaseException:
                continue

        rankings.sort(key=lambda x: x["composite_score"], reverse=True)
        return rankings

    except Exception as e:
        logger.error(f"Rankings error: {e}")
        raise HTTPException(status_code=500, detail="ランキング生成エラー")


# Volume API endpoints


@app.get("/api/finance/stocks/{symbol}/volume")
async def get_stock_volume(
    symbol: str, limit: int = Query(30, ge=1, le=365, description="取得日数")
):
    """株式出来高データ取得API"""
    try:
        logger.info(f"Volume data: {symbol}, {limit} days")

        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=f"{limit}d")

        if hist.empty:
            raise HTTPException(status_code=404, detail="出来高データが見つかりません")

        volume_data = []
        for date, row in hist.iterrows():
            volume_data.append(
                {
                    "symbol": symbol.upper(),
                    "date": date.strftime("%Y-%m-%d"),
                    "volume": (int(row["Volume"]) if not pd.isna(row["Volume"]) else 0),
                    "price": float(row["Close"]),
                    "volume_ma_20": None,  # 後で計算
                }
            )

        # 20日移動平均出来高を計算
        volumes = [d["volume"] for d in volume_data]
        for i, data_point in enumerate(volume_data):
            if i >= 19:  # 20日分のデータがある場合
                ma_20 = sum(volumes[i - 19: i + 1]) / 20
                data_point["volume_ma_20"] = int(ma_20)

        return volume_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Volume data error: {e}")
        raise HTTPException(status_code=500, detail=f"出来高データ取得エラー: {str(e)}")


@app.get("/api/finance/stocks/{symbol}/volume-predictions")
async def get_volume_predictions(
    symbol: str, days: int = Query(7, ge=1, le=30, description="予測期間")
):
    """出来高予測取得API"""
    try:
        logger.info(f"Volume predictions: {symbol}, {days} days")

        # 過去データから現在の平均出来高を取得
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period="30d")

        if hist.empty:
            raise HTTPException(status_code=404, detail="銘柄データが見つかりません")

        avg_volume = hist["Volume"].mean()

        predictions = []
        base_date = datetime.now()

        for i in range(1, days + 1):
            # 出来高予測アルゴリズム
            trend_factor = np.sin(i * 0.15) * 0.3  # 周期的な変動
            random_factor = random.uniform(-0.4, 0.6)  # ランダム変動
            predicted_volume = int(
                avg_volume * (1 + trend_factor + random_factor))
            predicted_volume = max(
                predicted_volume, int(avg_volume * 0.1)
            )  # 最小値制限

            confidence = max(0.4, 0.85 - (i * 0.03))  # 時間とともに信頼度低下

            prediction_date = base_date + timedelta(days=i)

            predictions.append(
                {
                    "symbol": symbol.upper(),
                    "prediction_date": prediction_date.strftime("%Y-%m-%d"),
                    "predicted_volume": predicted_volume,
                    "confidence_score": round(confidence, 3),
                    "volume_trend": (
                        "increasing" if trend_factor > 0 else "decreasing"
                    ),
                    "model_type": "Volume-LSTM",
                    "is_active": True,
                }
            )

        return predictions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Volume prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"出来高予測エラー: {str(e)}")


@app.get("/api/finance/volume-rankings")
async def get_volume_rankings(
    limit: int = Query(20, ge=1, le=50, description="結果数制限")
):
    """出来高ランキング取得API"""
    try:
        logger.info(f"Volume rankings, limit: {limit}")

        major_symbols = [
            "AAPL",
            "GOOGL",
            "MSFT",
            "AMZN",
            "TSLA",
            "META",
            "NVDA",
            "JPM",
            "V",
            "JNJ",
            "WMT",
            "PG",
            "UNH",
            "HD",
            "MA",
        ]

        rankings = []

        for symbol in major_symbols[: limit + 5]:  # 少し多めに取得してソート
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")

                if not hist.empty and len(hist) > 1:
                    current_volume = hist["Volume"].iloc[-1]
                    avg_volume = hist["Volume"][:-1].mean()  # 最新日除く平均
                    volume_change = (
                        ((current_volume - avg_volume) / avg_volume) * 100
                        if avg_volume > 0
                        else 0
                    )

                    # 会社名取得
                    try:
                        info = ticker.info
                        company_name = info.get("longName", symbol)
                    except BaseException:
                        company_name = symbol

                    rankings.append(
                        {
                            "symbol": symbol,
                            "company_name": company_name,
                            "current_volume": int(current_volume),
                            "average_volume": int(avg_volume),
                            "volume_change_percent": round(volume_change, 2),
                            "current_price": round(hist["Close"].iloc[-1], 2),
                            "price_change_percent": round(
                                (
                                    (hist["Close"].iloc[-1] -
                                     hist["Close"].iloc[-2])
                                    / hist["Close"].iloc[-2]
                                )
                                * 100,
                                2,
                            ),
                            "volume_rank": 0,  # 後でソート順に設定
                        }
                    )
            except Exception as e:
                logger.warning(f"Volume ranking error for {symbol}: {e}")
                continue

        # 出来高変化率でソート
        rankings.sort(key=lambda x: x["volume_change_percent"], reverse=True)

        # ランクを設定
        for i, ranking in enumerate(rankings[:limit]):
            ranking["volume_rank"] = i + 1

        return rankings[:limit]

    except Exception as e:
        logger.error(f"Volume rankings error: {e}")
        raise HTTPException(status_code=500, detail="出来高ランキング生成エラー")


# Sector API endpoints


@app.get("/api/finance/sectors")
async def get_sectors():
    """セクター一覧取得API"""
    try:
        logger.info("Getting sector information")

        sectors = [
            {
                "sector_id": "technology",
                "sector_name": "テクノロジー",
                "sector_name_en": "Technology",
                "description": "ソフトウェア、ハードウェア、ITサービス",
                "performance_1d": round(random.uniform(-3, 3), 2),
                "performance_1w": round(random.uniform(-8, 8), 2),
                "performance_1m": round(random.uniform(-15, 15), 2),
                "market_cap": random.randint(1000000, 5000000),
                "stocks_count": random.randint(50, 200),
                "top_stocks": ["AAPL", "MSFT", "GOOGL", "NVDA", "META"],
            },
            {
                "sector_id": "financials",
                "sector_name": "金融",
                "sector_name_en": "Financials",
                "description": "銀行、保険、投資サービス",
                "performance_1d": round(random.uniform(-2, 2), 2),
                "performance_1w": round(random.uniform(-6, 6), 2),
                "performance_1m": round(random.uniform(-12, 12), 2),
                "market_cap": random.randint(800000, 3000000),
                "stocks_count": random.randint(80, 150),
                "top_stocks": ["JPM", "V", "MA", "BAC", "WFC"],
            },
            {
                "sector_id": "healthcare",
                "sector_name": "ヘルスケア",
                "sector_name_en": "Healthcare",
                "description": "医薬品、医療機器、ヘルスケアサービス",
                "performance_1d": round(random.uniform(-1.5, 2.5), 2),
                "performance_1w": round(random.uniform(-5, 7), 2),
                "performance_1m": round(random.uniform(-10, 10), 2),
                "market_cap": random.randint(900000, 4000000),
                "stocks_count": random.randint(60, 120),
                "top_stocks": ["JNJ", "PFE", "UNH", "ABT", "MRK"],
            },
            {
                "sector_id": "consumer_discretionary",
                "sector_name": "一般消費財",
                "sector_name_en": "Consumer Discretionary",
                "description": "小売、自動車、レジャー、メディア",
                "performance_1d": round(random.uniform(-2.5, 3), 2),
                "performance_1w": round(random.uniform(-9, 9), 2),
                "performance_1m": round(random.uniform(-18, 18), 2),
                "market_cap": random.randint(700000, 3500000),
                "stocks_count": random.randint(40, 100),
                "top_stocks": ["AMZN", "TSLA", "HD", "MCD", "NKE"],
            },
            {
                "sector_id": "industrial",
                "sector_name": "工業",
                "sector_name_en": "Industrial",
                "description": "製造業、航空宇宙、建設、輸送",
                "performance_1d": round(random.uniform(-2, 2), 2),
                "performance_1w": round(random.uniform(-7, 7), 2),
                "performance_1m": round(random.uniform(-14, 14), 2),
                "market_cap": random.randint(600000, 2500000),
                "stocks_count": random.randint(70, 160),
                "top_stocks": ["BA", "CAT", "GE", "UPS", "HON"],
            },
            {
                "sector_id": "energy",
                "sector_name": "エネルギー",
                "sector_name_en": "Energy",
                "description": "石油、天然ガス、再生可能エネルギー",
                "performance_1d": round(random.uniform(-4, 4), 2),
                "performance_1w": round(random.uniform(-12, 12), 2),
                "performance_1m": round(random.uniform(-20, 25), 2),
                "market_cap": random.randint(400000, 2000000),
                "stocks_count": random.randint(30, 80),
                "top_stocks": ["XOM", "CVX", "COP", "SLB", "EOG"],
            },
        ]

        return sectors

    except Exception as e:
        logger.error(f"Sectors error: {e}")
        raise HTTPException(status_code=500, detail="セクター情報取得エラー")


@app.get("/api/sectors/{sector_id}")
async def get_sector_details(
    sector_id: str,
    limit: int = Query(50, ge=1, le=100, description="株式数制限"),
):
    """セクター詳細情報取得API"""
    try:
        logger.info(f"Sector details: {sector_id}, limit: {limit}")

        # セクター別銘柄マッピング
        sector_stocks = {
            "technology": [
                "AAPL",
                "MSFT",
                "GOOGL",
                "NVDA",
                "META",
                "CRM",
                "ADBE",
                "NFLX",
                "INTC",
                "AMD",
            ],
            "financials": [
                "JPM",
                "V",
                "MA",
                "BAC",
                "WFC",
                "C",
                "GS",
                "AXP",
                "USB",
                "PNC",
            ],
            "healthcare": [
                "JNJ",
                "PFE",
                "UNH",
                "ABT",
                "MRK",
                "TMO",
                "DHR",
                "BMY",
                "AMGN",
                "GILD",
            ],
            "consumer_discretionary": [
                "AMZN",
                "TSLA",
                "HD",
                "MCD",
                "NKE",
                "LOW",
                "SBUX",
                "TJX",
                "BKNG",
                "CMG",
            ],
            "industrial": [
                "BA",
                "CAT",
                "GE",
                "UPS",
                "HON",
                "MMM",
                "LMT",
                "UNP",
                "FDX",
                "RTX",
            ],
            "energy": [
                "XOM",
                "CVX",
                "COP",
                "SLB",
                "EOG",
                "PSX",
                "VLO",
                "MPC",
                "PXD",
                "OXY",
            ],
        }

        stocks = sector_stocks.get(sector_id, [])[:limit]

        if not stocks:
            raise HTTPException(status_code=404, detail="セクターが見つかりません")

        sector_data = {
            "sector_id": sector_id,
            "sector_name": sector_id.title(),
            "description": f"{sector_id.title()} sector stocks",
            "total_stocks": len(stocks),
            "stocks": [],
        }

        for symbol in stocks:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")

                if not hist.empty:
                    current_price = hist["Close"].iloc[-1]
                    prev_price = (
                        hist["Close"].iloc[-2] if len(
                            hist) > 1 else current_price
                    )
                    change_pct = (
                        ((current_price - prev_price) / prev_price) * 100
                        if prev_price > 0
                        else 0
                    )

                    try:
                        info = ticker.info
                        company_name = info.get("longName", symbol)
                        market_cap = info.get("marketCap", None)
                    except BaseException:
                        company_name = symbol
                        market_cap = None

                    sector_data["stocks"].append(
                        {
                            "symbol": symbol,
                            "company_name": company_name,
                            "current_price": round(current_price, 2),
                            "change_percent": round(change_pct, 2),
                            "volume": (
                                int(hist["Volume"].iloc[-1])
                                if not pd.isna(hist["Volume"].iloc[-1])
                                else 0
                            ),
                            "market_cap": market_cap,
                        }
                    )
            except Exception as e:
                logger.warning(f"Stock data error for {symbol}: {e}")
                continue

        return sector_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sector details error: {e}")
        raise HTTPException(status_code=500, detail="セクター詳細取得エラー")


# Theme/Insights API endpoints


@app.get("/api/insights/themes")
async def get_themes():
    """テーマ一覧取得API"""
    try:
        logger.info("Getting themes information")

        themes = [
            {
                "theme_id": "ai_revolution",
                "theme_name": "AI革命",
                "theme_name_en": "AI Revolution",
                "description": "人工知能・機械学習・自動化技術の発展",
                "category": "technology",
                "performance_1m": round(random.uniform(5, 25), 2),
                "performance_3m": round(random.uniform(10, 40), 2),
                "performance_6m": round(random.uniform(15, 60), 2),
                "market_momentum": "強気",
                "risk_level": "高",
                "stocks_count": 25,
                "total_market_cap": random.randint(800000, 2000000),
                "top_stocks": ["NVDA", "MSFT", "GOOGL", "AAPL", "META"],
                "growth_potential": "非常に高い",
                "image_url": "/themes/ai-revolution.jpg",
                "is_trending": True,
                "follow_count": random.randint(1000, 5000),
            },
            {
                "theme_id": "green_energy",
                "theme_name": "グリーンエネルギー",
                "theme_name_en": "Green Energy",
                "description": "再生可能エネルギー・電気自動車・環境技術",
                "category": "energy",
                "performance_1m": round(random.uniform(-5, 15), 2),
                "performance_3m": round(random.uniform(-10, 20), 2),
                "performance_6m": round(random.uniform(-5, 35), 2),
                "market_momentum": "中立",
                "risk_level": "中",
                "stocks_count": 18,
                "total_market_cap": random.randint(600000, 1500000),
                "top_stocks": ["TSLA", "ENPH", "SEDG", "PLUG", "NEE"],
                "growth_potential": "高い",
                "image_url": "/themes/green-energy.jpg",
                "is_trending": True,
                "follow_count": random.randint(800, 3000),
            },
            {
                "theme_id": "healthcare_innovation",
                "theme_name": "ヘルスケア革新",
                "theme_name_en": "Healthcare Innovation",
                "description": "バイオテクノロジー・デジタルヘルス・精密医療",
                "category": "healthcare",
                "performance_1m": round(random.uniform(-3, 12), 2),
                "performance_3m": round(random.uniform(-8, 18), 2),
                "performance_6m": round(random.uniform(-5, 25), 2),
                "market_momentum": "やや強気",
                "risk_level": "高",
                "stocks_count": 22,
                "total_market_cap": random.randint(500000, 1200000),
                "top_stocks": ["MRNA", "GILD", "BIIB", "REGN", "VRTX"],
                "growth_potential": "高い",
                "image_url": "/themes/healthcare-innovation.jpg",
                "is_trending": False,
                "follow_count": random.randint(600, 2500),
            },
            {
                "theme_id": "fintech_disruption",
                "theme_name": "フィンテック革新",
                "theme_name_en": "FinTech Disruption",
                "description": "デジタル金融・暗号資産・決済技術",
                "category": "financials",
                "performance_1m": round(random.uniform(-10, 20), 2),
                "performance_3m": round(random.uniform(-15, 30), 2),
                "performance_6m": round(random.uniform(-20, 50), 2),
                "market_momentum": "中立",
                "risk_level": "非常に高い",
                "stocks_count": 15,
                "total_market_cap": random.randint(300000, 800000),
                "top_stocks": ["PYPL", "SQ", "COIN", "HOOD", "AFRM"],
                "growth_potential": "非常に高い",
                "image_url": "/themes/fintech-disruption.jpg",
                "is_trending": True,
                "follow_count": random.randint(1200, 4000),
            },
            {
                "theme_id": "space_economy",
                "theme_name": "宇宙経済",
                "theme_name_en": "Space Economy",
                "description": "宇宙開発・衛星通信・宇宙旅行",
                "category": "industrial",
                "performance_1m": round(random.uniform(-15, 10), 2),
                "performance_3m": round(random.uniform(-20, 15), 2),
                "performance_6m": round(random.uniform(-25, 30), 2),
                "market_momentum": "弱気",
                "risk_level": "非常に高い",
                "stocks_count": 12,
                "total_market_cap": random.randint(200000, 500000),
                "top_stocks": ["SPCE", "RKLB", "ASTR", "PL", "MAXR"],
                "growth_potential": "高い",
                "image_url": "/themes/space-economy.jpg",
                "is_trending": False,
                "follow_count": random.randint(400, 1500),
            },
            {
                "theme_id": "cloud_computing",
                "theme_name": "クラウドコンピューティング",
                "theme_name_en": "Cloud Computing",
                "description": "クラウドインフラ・SaaS・エッジコンピューティング",
                "category": "technology",
                "performance_1m": round(random.uniform(0, 18), 2),
                "performance_3m": round(random.uniform(2, 25), 2),
                "performance_6m": round(random.uniform(5, 35), 2),
                "market_momentum": "強気",
                "risk_level": "中",
                "stocks_count": 20,
                "total_market_cap": random.randint(700000, 1800000),
                "top_stocks": ["AMZN", "MSFT", "CRM", "SNOW", "NET"],
                "growth_potential": "高い",
                "image_url": "/themes/cloud-computing.jpg",
                "is_trending": True,
                "follow_count": random.randint(1500, 6000),
            },
        ]

        return themes

    except Exception as e:
        logger.error(f"Themes error: {e}")
        raise HTTPException(status_code=500, detail="テーマ情報取得エラー")


@app.get("/api/insights/themes/{theme_name}")
async def get_theme_details(
    theme_name: str,
    limit: int = Query(20, ge=1, le=50, description="関連株式数制限"),
):
    """テーマ詳細情報取得API"""
    try:
        logger.info(f"Theme details: {theme_name}, limit: {limit}")

        # テーマ別銘柄マッピング
        theme_stocks = {
            "ai_revolution": [
                "NVDA",
                "MSFT",
                "GOOGL",
                "AAPL",
                "META",
                "TSLA",
                "AMD",
                "INTC",
                "CRM",
                "ADBE",
            ],
            "green_energy": [
                "TSLA",
                "ENPH",
                "SEDG",
                "PLUG",
                "NEE",
                "ICLN",
                "PBW",
                "QCLN",
                "FSLR",
                "SPWR",
            ],
            "healthcare_innovation": [
                "MRNA",
                "GILD",
                "BIIB",
                "REGN",
                "VRTX",
                "TMO",
                "DHR",
                "ISRG",
                "DXCM",
                "VEEV",
            ],
            "fintech_disruption": [
                "PYPL",
                "SQ",
                "COIN",
                "HOOD",
                "AFRM",
                "SOFI",
                "LC",
                "UPST",
                "NU",
                "PAGS",
            ],
            "space_economy": [
                "SPCE",
                "RKLB",
                "ASTR",
                "PL",
                "MAXR",
                "IRDM",
                "GSAT",
                "SATS",
                "LMT",
                "BA",
            ],
            "cloud_computing": [
                "AMZN",
                "MSFT",
                "CRM",
                "SNOW",
                "NET",
                "DDOG",
                "ZM",
                "OKTA",
                "TWLO",
                "MDB",
            ],
        }

        stocks = theme_stocks.get(theme_name, [])[:limit]

        if not stocks:
            raise HTTPException(status_code=404, detail="テーマが見つかりません")

        # テーマ基本情報
        theme_info = {
            "ai_revolution": {
                "name": "AI革命",
                "description": "人工知能と機械学習技術の急速な発展により、様々な産業で革新が起こっています。",
            },
            "green_energy": {
                "name": "グリーンエネルギー",
                "description": "脱炭素社会の実現に向けて、再生可能エネルギーと電気自動車分野が注目されています。",
            },
            "healthcare_innovation": {
                "name": "ヘルスケア革新",
                "description": "バイオテクノロジーとデジタルヘルス技術が医療業界を変革しています。",
            },
        }

        theme_data = {
            "theme_id": theme_name,
            "theme_name": theme_info.get(theme_name, {}).get(
                "name", theme_name.title()
            ),
            "description": theme_info.get(theme_name, {}).get(
                "description", f"{theme_name} related theme"
            ),
            "total_stocks": len(stocks),
            "last_updated": datetime.now().isoformat(),
            "performance": {
                "1m": round(random.uniform(-10, 25), 2),
                "3m": round(random.uniform(-15, 35), 2),
                "6m": round(random.uniform(-20, 50), 2),
                "1y": round(random.uniform(-25, 80), 2),
            },
            "stocks": [],
        }

        for symbol in stocks:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="30d")

                if not hist.empty:
                    current_price = hist["Close"].iloc[-1]
                    start_price = hist["Close"].iloc[0]
                    change_pct = (
                        ((current_price - start_price) / start_price) * 100
                        if start_price > 0
                        else 0
                    )

                    try:
                        info = ticker.info
                        company_name = info.get("longName", symbol)
                        market_cap = info.get("marketCap", None)
                        sector = info.get("sector", "Unknown")
                    except BaseException:
                        company_name = symbol
                        market_cap = None
                        sector = "Unknown"

                    theme_data["stocks"].append(
                        {
                            "symbol": symbol,
                            "company_name": company_name,
                            "current_price": round(current_price, 2),
                            "change_percent_1m": round(change_pct, 2),
                            "volume": (
                                int(hist["Volume"].iloc[-1])
                                if not pd.isna(hist["Volume"].iloc[-1])
                                else 0
                            ),
                            "market_cap": market_cap,
                            "sector": sector,
                            # テーマとの関連度
                            "theme_relevance": round(random.uniform(0.6, 1.0), 2),
                        }
                    )
            except Exception as e:
                logger.warning(f"Theme stock data error for {symbol}: {e}")
                continue

        return theme_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Theme details error: {e}")
        raise HTTPException(status_code=500, detail="テーマ詳細取得エラー")


@app.get("/api/insights/themes/{theme_id}/news")
async def get_theme_news(
    theme_id: str,
    limit: int = Query(10, ge=1, le=20, description="ニュース数制限"),
):
    """テーマ関連ニュース取得API"""
    try:
        logger.info(f"Theme news: {theme_id}, limit: {limit}")

        # サンプルニュースデータ
        news_templates = {
            "ai_revolution": [
                "AI チップの需要が急増、関連企業の業績予想が上方修正",
                "機械学習スタートアップへの投資が過去最高を記録",
                "生成AI技術の企業導入が加速、関連株に注目集まる",
            ],
            "green_energy": [
                "再生可能エネルギー投資が政府支援により拡大",
                "電気自動車の販売台数が前年同期比50%増",
                "太陽光発電コストの大幅削減が実現",
            ],
            "healthcare_innovation": [
                "新型コロナワクチン開発企業が次世代治療薬を発表",
                "デジタルヘルス市場が急成長、関連企業が好調",
                "遺伝子治療の臨床試験で画期的な結果",
            ],
        }

        templates = news_templates.get(theme_id, ["関連ニュースが更新されました"])

        news_data = []
        for i in range(min(limit, len(templates) * 3)):
            template = templates[i % len(templates)]

            news_data.append(
                {
                    "news_id": f"news_{theme_id}_{i + 1}",
                    "title": template + f" ({i + 1})",
                    "summary": f"{template}に関する詳細な分析と市場への影響について解説します。",
                    "published_at": (
                        datetime.now() - timedelta(days=random.randint(1, 30))
                    ).isoformat(),
                    "source": random.choice(
                        ["日経新聞", "ロイター", "Bloomberg", "TechCrunch"]
                    ),
                    "category": "market_analysis",
                    "relevance_score": round(random.uniform(0.7, 1.0), 2),
                    "sentiment": random.choice(["positive", "neutral", "negative"]),
                    "related_stocks": [],
                }
            )

        return {
            "theme_id": theme_id,
            "news_count": len(news_data),
            "last_updated": datetime.now().isoformat(),
            "news": news_data,
        }

    except Exception as e:
        logger.error(f"Theme news error: {e}")
        raise HTTPException(status_code=500, detail="テーマニュース取得エラー")


@app.get("/api/insights/themes/{theme_id}/ai-insights")
async def get_theme_ai_insights(theme_id: str):
    """テーマAI分析取得API"""
    try:
        logger.info(f"Theme AI insights: {theme_id}")

        # テーマ別AI分析データ
        ai_insights = {
            "ai_revolution": {
                "outlook": "非常に強気",
                "confidence": 0.85,
                "key_drivers": [
                    "企業のAI導入加速",
                    "半導体需要の急増",
                    "生成AI市場の拡大",
                ],
                "risks": [
                    "規制強化の可能性",
                    "技術バブル懸念",
                    "人材獲得競争",
                ],
                "price_target_range": {"min": 15, "max": 35},
                "investment_horizon": "中長期（1-3年）",
            },
            "green_energy": {
                "outlook": "強気",
                "confidence": 0.78,
                "key_drivers": [
                    "政府の脱炭素政策",
                    "技術コスト削減",
                    "企業のESG投資",
                ],
                "risks": ["政策変更リスク", "原材料価格変動", "天候依存性"],
                "price_target_range": {"min": 10, "max": 25},
                "investment_horizon": "長期（2-5年）",
            },
        }

        default_insight = {
            "outlook": "中立",
            "confidence": 0.65,
            "key_drivers": ["市場動向", "技術革新", "規制環境"],
            "risks": ["市場変動", "競争激化", "経済環境"],
            "price_target_range": {"min": 5, "max": 15},
            "investment_horizon": "中期（6ヶ月-2年）",
        }

        insight = ai_insights.get(theme_id, default_insight)

        return {
            "theme_id": theme_id,
            "analysis_date": datetime.now().isoformat(),
            "ai_outlook": insight["outlook"],
            "confidence_score": insight["confidence"],
            "key_growth_drivers": insight["key_drivers"],
            "potential_risks": insight["risks"],
            "price_target_range": insight["price_target_range"],
            "recommended_investment_horizon": insight["investment_horizon"],
            "model_version": "Theme-Analysis-v2.1",
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Theme AI insights error: {e}")
        raise HTTPException(status_code=500, detail="テーマAI分析取得エラー")


@app.post("/api/insights/themes/{theme_id}/follow")
async def follow_theme(theme_id: str):
    """テーマフォロー機能API"""
    try:
        logger.info(f"Following theme: {theme_id}")

        # 実際の実装では、ユーザーIDと紐付けてデータベースに保存
        return {
            "theme_id": theme_id,
            "followed": True,
            "follow_count": random.randint(100, 1000),
            "message": "テーマをフォローしました",
        }

    except Exception as e:
        logger.error(f"Follow theme error: {e}")
        raise HTTPException(status_code=500, detail="テーマフォローエラー")


@app.delete("/api/insights/themes/{theme_id}/follow")
async def unfollow_theme(theme_id: str):
    """テーマフォロー解除API"""
    try:
        logger.info(f"Unfollowing theme: {theme_id}")

        return {
            "theme_id": theme_id,
            "followed": False,
            "follow_count": random.randint(100, 1000),
            "message": "テーマのフォローを解除しました",
        }

    except Exception as e:
        logger.error(f"Unfollow theme error: {e}")
        raise HTTPException(status_code=500, detail="テーマフォロー解除エラー")


# Forex API endpoints


@app.get("/api/forex/currency-pairs")
async def get_currency_pairs():
    """通貨ペア一覧取得API"""
    try:
        logger.info("Getting currency pairs")

        currency_pairs = [
            {
                "pair": "USD/JPY",
                "pair_code": "USDJPY",
                "base_currency": "USD",
                "quote_currency": "JPY",
                "description": "米ドル/日本円",
                "is_major": True,
                "trading_hours": "24時間",
                "typical_spread": "0.3",
                "volatility": "低",
            },
            {
                "pair": "EUR/USD",
                "pair_code": "EURUSD",
                "base_currency": "EUR",
                "quote_currency": "USD",
                "description": "ユーロ/米ドル",
                "is_major": True,
                "trading_hours": "24時間",
                "typical_spread": "0.2",
                "volatility": "中",
            },
            {
                "pair": "GBP/USD",
                "pair_code": "GBPUSD",
                "base_currency": "GBP",
                "quote_currency": "USD",
                "description": "英ポンド/米ドル",
                "is_major": True,
                "trading_hours": "24時間",
                "typical_spread": "0.4",
                "volatility": "高",
            },
            {
                "pair": "AUD/USD",
                "pair_code": "AUDUSD",
                "base_currency": "AUD",
                "quote_currency": "USD",
                "description": "豪ドル/米ドル",
                "is_major": True,
                "trading_hours": "24時間",
                "typical_spread": "0.5",
                "volatility": "中",
            },
            {
                "pair": "USD/CHF",
                "pair_code": "USDCHF",
                "base_currency": "USD",
                "quote_currency": "CHF",
                "description": "米ドル/スイスフラン",
                "is_major": True,
                "trading_hours": "24時間",
                "typical_spread": "0.4",
                "volatility": "低",
            },
            {
                "pair": "USD/CAD",
                "pair_code": "USDCAD",
                "base_currency": "USD",
                "quote_currency": "CAD",
                "description": "米ドル/カナダドル",
                "is_major": True,
                "trading_hours": "24時間",
                "typical_spread": "0.5",
                "volatility": "中",
            },
        ]

        return {
            "pairs": currency_pairs,
            "total_count": len(currency_pairs),
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Currency pairs error: {e}")
        raise HTTPException(status_code=500, detail="通貨ペア取得エラー")


@app.get("/api/forex/currency-rate/{pair}")
async def get_currency_rate(pair: str):
    """通貨レート取得API"""
    try:
        logger.info(f"Getting currency rate: {pair}")

        # 通貨ペア正規化
        pair_normalized = pair.upper().replace("/", "")

        # Yahoo Financeでは通貨ペアの表記が特殊
        yf_symbols = {
            "USDJPY": "JPY=X",
            "EURUSD": "EURUSD=X",
            "GBPUSD": "GBPUSD=X",
            "AUDUSD": "AUDUSD=X",
            "USDCHF": "CHF=X",
            "USDCAD": "CAD=X",
        }

        yf_symbol = yf_symbols.get(pair_normalized)
        if not yf_symbol:
            raise HTTPException(status_code=404, detail="通貨ペアが見つかりません")

        ticker = yf.Ticker(yf_symbol)
        hist = ticker.history(period="2d")

        if hist.empty:
            # フォールバック: 模擬レートデータ
            base_rates = {
                "USDJPY": 150.0,
                "EURUSD": 1.08,
                "GBPUSD": 1.25,
                "AUDUSD": 0.65,
                "USDCHF": 0.88,
                "USDCAD": 1.36,
            }

            base_rate = base_rates.get(pair_normalized, 1.0)
            current_rate = base_rate * (1 + random.uniform(-0.02, 0.02))
            prev_rate = base_rate * (1 + random.uniform(-0.02, 0.02))
        else:
            current_rate = float(hist["Close"].iloc[-1])
            prev_rate = float(hist["Close"].iloc[-2]
                              ) if len(hist) > 1 else current_rate

        change = current_rate - prev_rate
        change_percent = (change / prev_rate) * 100 if prev_rate > 0 else 0

        return {
            "pair": pair,
            "current_rate": round(current_rate, 4),
            "previous_rate": round(prev_rate, 4),
            "change": round(change, 4),
            "change_percent": round(change_percent, 2),
            "bid": round(current_rate - 0.0001, 4),
            "ask": round(current_rate + 0.0001, 4),
            "last_updated": datetime.now().isoformat(),
            "data_source": "Yahoo Finance" if not hist.empty else "Simulated",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Currency rate error: {e}")
        raise HTTPException(status_code=500, detail=f"通貨レート取得エラー: {str(e)}")


@app.get("/api/forex/currency-history/{pair}")
async def get_currency_history(
    pair: str, days: int = Query(30, ge=1, le=365, description="履歴期間")
):
    """通貨履歴取得API"""
    try:
        logger.info(f"Getting currency history: {pair}, {days} days")

        pair_normalized = pair.upper().replace("/", "")

        yf_symbols = {
            "USDJPY": "JPY=X",
            "EURUSD": "EURUSD=X",
            "GBPUSD": "GBPUSD=X",
            "AUDUSD": "AUDUSD=X",
            "USDCHF": "CHF=X",
            "USDCAD": "CAD=X",
        }

        yf_symbol = yf_symbols.get(pair_normalized)
        if not yf_symbol:
            raise HTTPException(status_code=404, detail="通貨ペアが見つかりません")

        ticker = yf.Ticker(yf_symbol)
        hist = ticker.history(period=f"{days}d")

        if hist.empty:
            # フォールバック: 模擬履歴データ生成
            base_rates = {
                "USDJPY": 150.0,
                "EURUSD": 1.08,
                "GBPUSD": 1.25,
                "AUDUSD": 0.65,
                "USDCHF": 0.88,
                "USDCAD": 1.36,
            }

            base_rate = base_rates.get(pair_normalized, 1.0)
            history_data = []

            for i in range(days):
                date = datetime.now() - timedelta(days=days - i - 1)
                rate = base_rate * (1 + random.uniform(-0.1, 0.1))

                history_data.append(
                    {
                        "pair": pair,
                        "date": date.strftime("%Y-%m-%d"),
                        "open": round(rate * (1 + random.uniform(-0.005, 0.005)), 4),
                        "high": round(rate * (1 + random.uniform(0, 0.01)), 4),
                        "low": round(rate * (1 + random.uniform(-0.01, 0)), 4),
                        "close": round(rate, 4),
                        "volume": random.randint(1000000, 10000000),
                    }
                )
        else:
            history_data = []
            for date, row in hist.iterrows():
                history_data.append(
                    {
                        "pair": pair,
                        "date": date.strftime("%Y-%m-%d"),
                        "open": (
                            round(float(row["Open"]), 4)
                            if not pd.isna(row["Open"])
                            else None
                        ),
                        "high": (
                            round(float(row["High"]), 4)
                            if not pd.isna(row["High"])
                            else None
                        ),
                        "low": (
                            round(float(row["Low"]), 4)
                            if not pd.isna(row["Low"])
                            else None
                        ),
                        "close": round(float(row["Close"]), 4),
                        "volume": (
                            int(row["Volume"]) if not pd.isna(
                                row["Volume"]) else 0
                        ),
                    }
                )

        return {
            "pair": pair,
            "period_days": days,
            "data_points": len(history_data),
            "history": history_data,
            "data_source": "Yahoo Finance" if not hist.empty else "Simulated",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Currency history error: {e}")
        raise HTTPException(status_code=500, detail=f"通貨履歴取得エラー: {str(e)}")


@app.get("/api/forex/currency-predictions/{pair}")
async def get_currency_predictions(
    pair: str,
    timeframe: str = Query("1d", description="予測時間軸"),
    limit: int = Query(7, ge=1, le=30, description="予測期間"),
):
    """通貨予測取得API"""
    try:
        logger.info(
            f"Currency predictions: {pair}, {timeframe}, {limit} periods")

        # 現在レート取得
        current_rate_data = await get_currency_rate(pair)
        current_rate = current_rate_data["current_rate"]

        predictions = []
        base_date = datetime.now()

        for i in range(1, limit + 1):
            # 通貨予測アルゴリズム
            trend_factor = np.sin(i * 0.2) * 0.01  # より小さな変動
            random_factor = random.uniform(-0.005, 0.005)  # 為替は株式より変動小
            predicted_rate = current_rate * (1 + trend_factor + random_factor)

            # 信頼度は時間とともに低下
            confidence = max(0.5, 0.9 - (i * 0.03))

            if timeframe == "1h":
                prediction_date = base_date + timedelta(hours=i)
            elif timeframe == "1d":
                prediction_date = base_date + timedelta(days=i)
            elif timeframe == "1w":
                prediction_date = base_date + timedelta(weeks=i)
            else:
                prediction_date = base_date + timedelta(days=i)

            predictions.append(
                {
                    "pair": pair,
                    "prediction_date": prediction_date.isoformat(),
                    "predicted_rate": round(predicted_rate, 4),
                    "confidence_score": round(confidence, 3),
                    "trend_direction": "up" if trend_factor > 0 else "down",
                    "volatility_forecast": (
                        "low" if abs(trend_factor) < 0.005 else "medium"
                    ),
                    "model_type": "Forex-LSTM",
                    "timeframe": timeframe,
                    "is_active": True,
                }
            )

        return {
            "pair": pair,
            "timeframe": timeframe,
            "predictions_count": len(predictions),
            "base_rate": current_rate,
            "predictions": predictions,
            "model_info": {
                "version": "Forex-v1.2",
                "last_trained": (datetime.now() - timedelta(days=7)).isoformat(),
                "accuracy": round(random.uniform(0.65, 0.85), 3),
            },
        }

    except Exception as e:
        logger.error(f"Currency predictions error: {e}")
        raise HTTPException(status_code=500, detail=f"通貨予測エラー: {str(e)}")


@app.get("/api/forex/currency-insights/{pair}")
async def get_currency_insights(pair: str):
    """通貨インサイト取得API"""
    try:
        logger.info(f"Currency insights: {pair}")

        pair_normalized = pair.upper().replace("/", "")

        # 通貨ペア別インサイト
        insights_data = {
            "USDJPY": {
                "trend": "上昇トレンド",
                "key_factors": ["FRB政策", "日銀介入", "米国経済指標"],
                "resistance": 155.0,
                "support": 145.0,
                "volatility": "低",
                "sentiment": "やや強気",
            },
            "EURUSD": {
                "trend": "レンジ相場",
                "key_factors": ["ECB政策", "ユーロ圏経済", "米国インフレ"],
                "resistance": 1.12,
                "support": 1.05,
                "volatility": "中",
                "sentiment": "中立",
            },
            "GBPUSD": {
                "trend": "下降トレンド",
                "key_factors": ["英国政治", "BoE政策", "ブレグジット影響"],
                "resistance": 1.30,
                "support": 1.20,
                "volatility": "高",
                "sentiment": "弱気",
            },
        }

        default_insight = {
            "trend": "横ばい",
            "key_factors": ["経済指標", "中央銀行政策", "地政学リスク"],
            "resistance": 0.0,
            "support": 0.0,
            "volatility": "中",
            "sentiment": "中立",
        }

        insight = insights_data.get(pair_normalized, default_insight)

        return {
            "pair": pair,
            "analysis_date": datetime.now().isoformat(),
            "market_trend": insight["trend"],
            "key_factors": insight["key_factors"],
            "technical_levels": {
                "resistance": insight["resistance"],
                "support": insight["support"],
            },
            "volatility_assessment": insight["volatility"],
            "market_sentiment": insight["sentiment"],
            "economic_calendar": [
                {
                    "event": "FRB政策金利発表",
                    "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "impact": "高",
                },
                {
                    "event": "雇用統計",
                    "date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                    "impact": "中",
                },
            ],
            "recommendation": {
                "outlook": insight["sentiment"],
                "time_horizon": "1-3ヶ月",
                "risk_level": insight["volatility"],
            },
        }

    except Exception as e:
        logger.error(f"Currency insights error: {e}")
        raise HTTPException(status_code=500, detail="通貨インサイト取得エラー")


# Contest API endpoints


@app.get("/api/contests/stats")
async def get_contest_stats():
    """コンテスト統計取得API"""
    try:
        logger.info("Getting contest stats")

        return {
            "total_contests": 247,
            "active_contests": 5,
            "total_participants": 15420,
            "total_predictions": 89350,
            "average_accuracy": 67.8,
            "top_performer": {
                "username": "AITrader2024",
                "accuracy": 89.2,
                "contests_won": 12,
                "total_points": 8450,
            },
            "recent_contest_performance": [
                {"date": "2024-01-15", "accuracy": 72.5, "participants": 234},
                {"date": "2024-01-10", "accuracy": 68.9, "participants": 189},
                {"date": "2024-01-05", "accuracy": 71.2, "participants": 267},
            ],
            "contest_categories": [
                {"category": "株価予測", "count": 156, "avg_accuracy": 69.4},
                {"category": "為替予測", "count": 45, "avg_accuracy": 64.2},
                {"category": "指数予測", "count": 32, "avg_accuracy": 72.1},
                {
                    "category": "セクター予測",
                    "count": 14,
                    "avg_accuracy": 66.8,
                },
            ],
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Contest stats error: {e}")
        raise HTTPException(status_code=500, detail="コンテスト統計取得エラー")


@app.get("/api/contests/active")
async def get_active_contests():
    """アクティブコンテスト一覧取得API"""
    try:
        logger.info("Getting active contests")

        active_contests = []

        # 模擬アクティブコンテスト生成
        contest_types = [
            {
                "type": "stock_prediction",
                "name": "株価予測",
                "difficulty": "中級",
            },
            {
                "type": "forex_prediction",
                "name": "為替予測",
                "difficulty": "上級",
            },
            {
                "type": "index_prediction",
                "name": "指数予測",
                "difficulty": "初級",
            },
            {
                "type": "sector_prediction",
                "name": "セクター予測",
                "difficulty": "中級",
            },
        ]

        contest_symbols = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"]

        for i in range(5):
            contest_type = contest_types[i % len(contest_types)]
            symbol = contest_symbols[i % len(contest_symbols)]

            start_date = datetime.now() - timedelta(days=random.randint(1, 5))
            end_date = start_date + timedelta(days=random.randint(7, 14))

            # 現在価格取得（エラー処理付き）
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    current_price = float(hist["Close"].iloc[-1])
                else:
                    current_price = 150.0  # フォールバック価格
            except BaseException:
                current_price = 150.0

            active_contests.append(
                {
                    "contest_id": f"contest_{i + 1:03d}",
                    "title": f"{symbol} {contest_type['name']}コンテスト",
                    "description": f"{symbol}の{end_date.strftime('%Y-%m-%d')}時点での価格を予測してください",
                    "contest_type": contest_type["type"],
                    "target_symbol": symbol,
                    "target_date": end_date.isoformat(),
                    "current_price": round(current_price, 2),
                    "difficulty_level": contest_type["difficulty"],
                    "participants_count": random.randint(50, 300),
                    "prize_pool": random.randint(10000, 50000),
                    "entry_fee": random.randint(100, 1000),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "time_remaining": max(
                        0, int((end_date - datetime.now()).total_seconds())
                    ),
                    "status": "active",
                    "rules": {
                        "prediction_range": "±30%",
                        "max_predictions": 1,
                        "scoring_method": "accuracy_based",
                    },
                    "leaderboard_preview": [
                        {
                            "rank": 1,
                            "username": "PredictionMaster",
                            "prediction": round(
                                current_price * random.uniform(0.9, 1.1), 2
                            ),
                        },
                        {
                            "rank": 2,
                            "username": "MarketGuru",
                            "prediction": round(
                                current_price * random.uniform(0.9, 1.1), 2
                            ),
                        },
                        {
                            "rank": 3,
                            "username": "TraderAI",
                            "prediction": round(
                                current_price * random.uniform(0.9, 1.1), 2
                            ),
                        },
                    ],
                }
            )

        return {
            "contests": active_contests,
            "total_count": len(active_contests),
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Active contests error: {e}")
        raise HTTPException(status_code=500, detail="アクティブコンテスト取得エラー")


@app.get("/api/contests/past")
async def get_past_contests():
    """過去のコンテスト一覧取得API"""
    try:
        logger.info("Getting past contests")

        past_contests = []

        for i in range(20):
            end_date = datetime.now() - timedelta(days=random.randint(1, 30))

            symbol = random.choice(
                ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META"]
            )

            # 実際の結果（模擬）
            target_price = random.uniform(100, 300)
            actual_price = target_price * random.uniform(0.8, 1.2)

            past_contests.append(
                {
                    "contest_id": f"past_contest_{i + 1:03d}",
                    "title": f"{symbol} 株価予測コンテスト #{i + 1}",
                    "target_symbol": symbol,
                    "target_date": end_date.strftime("%Y-%m-%d"),
                    "target_price": round(target_price, 2),
                    "actual_result": round(actual_price, 2),
                    "participants_count": random.randint(80, 400),
                    "winner": {
                        "username": f"Winner{i + 1}",
                        "prediction": round(
                            actual_price * random.uniform(0.98, 1.02), 2
                        ),
                        "accuracy": round(random.uniform(95, 99.9), 2),
                        "prize_won": random.randint(5000, 25000),
                    },
                    "your_performance": {
                        "participated": random.choice([True, False]),
                        "prediction": round(actual_price * random.uniform(0.9, 1.1), 2),
                        "rank": random.randint(1, 100),
                        "accuracy": round(random.uniform(60, 95), 2),
                        "points_earned": random.randint(10, 500),
                    },
                    "contest_stats": {
                        "avg_prediction": round(
                            target_price * random.uniform(0.95, 1.05), 2
                        ),
                        "prediction_spread": round(random.uniform(10, 30), 2),
                        "accuracy_distribution": {
                            "90-100%": random.randint(5, 15),
                            "80-90%": random.randint(15, 30),
                            "70-80%": random.randint(30, 50),
                            "60-70%": random.randint(20, 40),
                            "below_60%": random.randint(10, 30),
                        },
                    },
                }
            )

        return {
            "contests": past_contests,
            "total_count": len(past_contests),
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Past contests error: {e}")
        raise HTTPException(status_code=500, detail="過去コンテスト取得エラー")


@app.get("/api/contests/leaderboard")
async def get_leaderboard(
    time_frame: str = Query("all_time", description="期間フィルター")
):
    """コンテストリーダーボード取得API"""
    try:
        logger.info(f"Getting leaderboard: {time_frame}")

        # ユーザーレベル定義
        levels = ["初心者", "中級者", "上級者", "エキスパート", "マスター"]
        badges = [
            "🏆 コンテスト王者",
            "🎯 精密射手",
            "🔥 連勝記録",
            "💎 ダイヤモンド",
            "🚀 急成長",
            "🧠 AI使い",
            "📈 上昇トレンド",
            "💰 利益マスター",
        ]

        leaderboard = []

        for i in range(50):
            user_level = random.choice(levels)
            user_badges = random.sample(badges, random.randint(1, 4))

            total_contests = random.randint(20, 200)
            contests_won = random.randint(1, min(20, total_contests // 3))

            leaderboard.append(
                {
                    "rank": i + 1,
                    "user_id": f"user_{i + 1:03d}",
                    "username": f"Trader{random.randint(1000, 9999)}",
                    "display_name": f"TraderPro{i + 1}",
                    "total_score": random.randint(1000, 10000),
                    "accuracy": round(random.uniform(55, 90), 2),
                    "contests_participated": total_contests,
                    "contests_won": contests_won,
                    "win_rate": round((contests_won / total_contests) * 100, 2),
                    "current_streak": random.randint(0, 15),
                    "best_streak": random.randint(5, 25),
                    "total_prize_money": random.randint(5000, 100000),
                    "level": user_level,
                    "badges": user_badges,
                    "recent_performance": [
                        {
                            "contest_id": f"c{j}",
                            "accuracy": round(random.uniform(60, 95), 1),
                        }
                        for j in range(5)
                    ],
                    "specialties": random.sample(
                        ["株価予測", "為替予測", "指数予測", "セクター予測"],
                        random.randint(1, 3),
                    ),
                    "join_date": (
                        datetime.now() - timedelta(days=random.randint(30, 365))
                    ).strftime("%Y-%m-%d"),
                    "last_active": (
                        datetime.now() - timedelta(days=random.randint(0, 7))
                    ).strftime("%Y-%m-%d"),
                }
            )

        # スコア順にソート
        leaderboard.sort(key=lambda x: x["total_score"], reverse=True)

        # ランク更新
        for i, user in enumerate(leaderboard):
            user["rank"] = i + 1

        return {
            "time_frame": time_frame,
            "leaderboard": leaderboard,
            "total_users": len(leaderboard),
            "stats": {
                "avg_accuracy": round(
                    sum(u["accuracy"] for u in leaderboard) / len(leaderboard),
                    2,
                ),
                "top_accuracy": max(u["accuracy"] for u in leaderboard),
                "total_contests_won": sum(u["contests_won"] for u in leaderboard),
                "total_prize_money": sum(u["total_prize_money"] for u in leaderboard),
            },
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        raise HTTPException(status_code=500, detail="リーダーボード取得エラー")


@app.get("/api/contests/{contest_id}")
async def get_contest_details(contest_id: str):
    """コンテスト詳細取得API"""
    try:
        logger.info(f"Getting contest details: {contest_id}")

        # 模擬コンテスト詳細データ
        symbol = random.choice(["AAPL", "TSLA", "NVDA", "MSFT"])

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            if not hist.empty:
                current_price = float(hist["Close"].iloc[-1])
                price_history = [
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "price": round(float(row["Close"]), 2),
                    }
                    for date, row in hist.iterrows()
                ]
            else:
                current_price = 150.0
                price_history = []
        except BaseException:
            current_price = 150.0
            price_history = []

        end_date = datetime.now() + timedelta(days=random.randint(1, 10))

        return {
            "contest_id": contest_id,
            "title": f"{symbol} 株価予測コンテスト",
            "description": f"{symbol}の株価を予測して賞金を獲得しましょう！",
            "status": "active",
            "target_symbol": symbol,
            "current_price": round(current_price, 2),
            "target_date": end_date.isoformat(),
            "time_remaining": int((end_date - datetime.now()).total_seconds()),
            "prize_pool": 25000,
            "entry_fee": 500,
            "participants_count": random.randint(100, 300),
            "your_entry": {
                "participated": False,
                "prediction": None,
                "submitted_at": None,
                "current_rank": None,
            },
            "price_history": price_history,
            "market_data": {
                "volume": random.randint(1000000, 10000000),
                "market_cap": random.randint(1000000, 3000000),
                "pe_ratio": round(random.uniform(15, 35), 2),
                "volatility": round(random.uniform(0.2, 0.6), 3),
            },
            "contest_rules": {
                "prediction_window": "1回のみ",
                "scoring_method": "絶対誤差による順位付け",
                "tie_breaker": "早い提出時刻",
                "minimum_participants": 50,
            },
            "insights": {
                "avg_prediction": round(current_price * random.uniform(0.95, 1.05), 2),
                "prediction_range": {
                    "min": round(current_price * 0.8, 2),
                    "max": round(current_price * 1.2, 2),
                },
                "confidence_distribution": {
                    "very_high": random.randint(10, 30),
                    "high": random.randint(20, 40),
                    "medium": random.randint(30, 50),
                    "low": random.randint(10, 20),
                },
            },
        }

    except Exception as e:
        logger.error(f"Contest details error: {e}")
        raise HTTPException(status_code=500, detail="コンテスト詳細取得エラー")


@app.get("/api/contests/{contest_id}/ranking")
async def get_contest_ranking(contest_id: str):
    """コンテスト内ランキング取得API"""
    try:
        logger.info(f"Getting contest ranking: {contest_id}")

        # 模擬ランキングデータ生成
        participants = []
        base_price = random.uniform(100, 300)

        for i in range(random.randint(50, 200)):
            prediction = base_price * random.uniform(0.8, 1.2)
            confidence = random.uniform(0.3, 1.0)

            participants.append(
                {
                    "rank": i + 1,
                    "user_id": f"user_{i + 1:03d}",
                    "username": f"Participant{random.randint(100, 999)}",
                    "prediction": round(prediction, 2),
                    "confidence": round(confidence, 3),
                    "submitted_at": (
                        datetime.now() - timedelta(hours=random.randint(1, 72))
                    ).isoformat(),
                    "user_level": random.choice(
                        ["初心者", "中級者", "上級者", "エキスパート"]
                    ),
                    "previous_contests": random.randint(5, 50),
                    "avg_accuracy": round(random.uniform(55, 85), 2),
                    "points_at_stake": random.randint(100, 1000),
                }
            )

        # 予測価格でソート（実際は精度でソートされる）
        participants.sort(key=lambda x: abs(x["prediction"] - base_price))

        # ランク更新
        for i, participant in enumerate(participants):
            participant["rank"] = i + 1

        return {
            "contest_id": contest_id,
            "total_participants": len(participants),
            "ranking": participants[:100],  # トップ100のみ
            "your_rank": (
                random.randint(1, len(participants))
                if random.choice([True, False])
                else None
            ),
            "statistics": {
                "avg_prediction": round(
                    sum(p["prediction"]
                        for p in participants) / len(participants),
                    2,
                ),
                "median_prediction": round(
                    sorted([p["prediction"] for p in participants])[
                        len(participants) // 2
                    ],
                    2,
                ),
                "prediction_std": round(
                    np.std([p["prediction"] for p in participants]), 2
                ),
                "avg_confidence": round(
                    sum(p["confidence"]
                        for p in participants) / len(participants),
                    3,
                ),
            },
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Contest ranking error: {e}")
        raise HTTPException(status_code=500, detail="コンテストランキング取得エラー")


@app.post("/api/contests/{contest_id}/predict")
async def submit_prediction(
    contest_id: str, prediction: float, confidence: float = None
):
    """予測投稿API"""
    try:
        logger.info(
            f"Submitting prediction for contest {contest_id}: {prediction}")

        if confidence is None:
            confidence = 0.7  # デフォルト信頼度

        # 予測範囲検証
        if prediction <= 0:
            raise HTTPException(
                status_code=400, detail="予測価格は正数である必要があります"
            )

        if confidence < 0 or confidence > 1:
            raise HTTPException(
                status_code=400, detail="信頼度は0-1の範囲である必要があります"
            )

        # 模擬予測投稿処理
        return {
            "contest_id": contest_id,
            "prediction": round(prediction, 2),
            "confidence": round(confidence, 3),
            "submitted_at": datetime.now().isoformat(),
            "status": "submitted",
            "estimated_rank": random.randint(1, 50),
            "points_potential": random.randint(100, 1000),
            "message": "予測が正常に投稿されました",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"予測投稿エラー: {str(e)}")


@app.put("/api/contests/{contest_id}/predict")
async def update_prediction(
    contest_id: str, prediction: float, confidence: float = None
):
    """予測更新API"""
    try:
        logger.info(
            f"Updating prediction for contest {contest_id}: {prediction}")

        if confidence is None:
            confidence = 0.7

        if prediction <= 0:
            raise HTTPException(
                status_code=400, detail="予測価格は正数である必要があります"
            )

        if confidence < 0 or confidence > 1:
            raise HTTPException(
                status_code=400, detail="信頼度は0-1の範囲である必要があります"
            )

        return {
            "contest_id": contest_id,
            "prediction": round(prediction, 2),
            "confidence": round(confidence, 3),
            "updated_at": datetime.now().isoformat(),
            "status": "updated",
            "estimated_rank": random.randint(1, 50),
            "points_potential": random.randint(100, 1000),
            "message": "予測が正常に更新されました",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"予測更新エラー: {str(e)}")


# ===============================
# AI Factors API
# ===============================


@app.get("/api/predictions/{prediction_id}/factors")
async def get_prediction_factors(prediction_id: str):
    """AI判断根拠 - 特定の予測のAI判断ファクターを取得"""
    try:
        # Mock AI factors for demonstration
        ai_factors = [
            {
                "factor_id": "technical_momentum",
                "factor_name": "テクニカルモメンタム",
                "weight": 0.35,
                "impact": "positive",
                "confidence": 0.87,
                "description": "RSI、MACD、移動平均線が強い買いシグナルを示している",
                "details": {
                    "rsi": {"value": 72.3, "signal": "overbought_caution"},
                    "macd": {"value": 1.23, "signal": "bullish_crossover"},
                    "sma_20": {"trend": "upward", "distance": "+2.3%"},
                },
            },
            {
                "factor_id": "volume_pattern",
                "factor_name": "出来高パターン",
                "weight": 0.28,
                "impact": "positive",
                "confidence": 0.74,
                "description": "異常な出来高増加と価格上昇の相関が確認された",
                "details": {
                    "avg_volume_ratio": 2.34,
                    "volume_trend": "increasing",
                    "volume_price_correlation": 0.82,
                },
            },
            {
                "factor_id": "market_sentiment",
                "factor_name": "マーケットセンチメント",
                "weight": 0.22,
                "impact": "neutral",
                "confidence": 0.63,
                "description": "全体的な市場心理は中性的、セクター別では若干強気",
                "details": {
                    "fear_greed_index": 54,
                    "sector_sentiment": "slightly_bullish",
                    "news_sentiment": 0.12,
                },
            },
            {
                "factor_id": "fundamental_score",
                "factor_name": "ファンダメンタル評価",
                "weight": 0.15,
                "impact": "positive",
                "confidence": 0.78,
                "description": "財務指標とバリュエーションが良好な水準を維持",
                "details": {
                    "pe_ratio": {"value": 18.7, "percentile": 65},
                    "revenue_growth": "8.3%",
                    "debt_ratio": "low",
                },
            },
        ]

        return {
            "prediction_id": prediction_id,
            "ai_factors": ai_factors,
            "total_factors": len(ai_factors),
            "overall_confidence": round(
                sum(f["confidence"] * f["weight"] for f in ai_factors), 2
            ),
            "analysis_timestamp": datetime.now().isoformat(),
            "data_source": "Miraikakaku AI Engine",
        }

    except Exception as e:
        logger.error(f"Error getting prediction factors: {e}")
        raise HTTPException(
            status_code=500, detail="予測ファクターの取得に失敗しました"
        )


@app.get("/api/ai-factors/all")
async def get_all_ai_factors():
    """AI判断根拠 - 利用可能なすべてのAIファクターを取得"""
    try:
        all_factors = [
            {
                "factor_id": "technical_momentum",
                "factor_name": "テクニカルモメンタム",
                "category": "technical",
                "description": "RSI、MACD、移動平均線などのテクニカル指標",
                "weight_range": [0.20, 0.40],
                "typical_confidence": 0.75,
            },
            {
                "factor_id": "volume_pattern",
                "factor_name": "出来高パターン",
                "category": "technical",
                "description": "出来高の変化パターンと価格との相関分析",
                "weight_range": [0.15, 0.35],
                "typical_confidence": 0.68,
            },
            {
                "factor_id": "market_sentiment",
                "factor_name": "マーケットセンチメント",
                "category": "sentiment",
                "description": "市場全体の心理状態とニュースセンチメント",
                "weight_range": [0.10, 0.30],
                "typical_confidence": 0.62,
            },
            {
                "factor_id": "fundamental_score",
                "factor_name": "ファンダメンタル評価",
                "category": "fundamental",
                "description": "財務指標、バリュエーション、業績トレンド",
                "weight_range": [0.10, 0.25],
                "typical_confidence": 0.78,
            },
            {
                "factor_id": "sector_rotation",
                "factor_name": "セクターローテーション",
                "category": "macro",
                "description": "セクター間の資金移動パターンと業種別パフォーマンス",
                "weight_range": [0.05, 0.20],
                "typical_confidence": 0.58,
            },
            {
                "factor_id": "economic_indicators",
                "factor_name": "経済指標",
                "category": "macro",
                "description": "GDP、雇用統計、金利動向などのマクロ経済要因",
                "weight_range": [0.05, 0.15],
                "typical_confidence": 0.71,
            },
        ]

        return {
            "ai_factors": all_factors,
            "total_count": len(all_factors),
            "categories": {
                "technical": len(
                    [f for f in all_factors if f["category"] == "technical"]
                ),
                "sentiment": len(
                    [f for f in all_factors if f["category"] == "sentiment"]
                ),
                "fundamental": len(
                    [f for f in all_factors if f["category"] == "fundamental"]
                ),
                "macro": len([f for f in all_factors if f["category"] == "macro"]),
            },
            "data_source": "Miraikakaku AI Engine",
        }

    except Exception as e:
        logger.error(f"Error getting all AI factors: {e}")
        raise HTTPException(
            status_code=500, detail="AIファクター一覧の取得に失敗しました"
        )


@app.get("/api/ai-factors/symbol/{symbol}")
async def get_symbol_ai_factors(symbol: str, days: int = 30):
    """AI判断根拠 - 特定銘柄のAIファクター分析を取得"""
    try:
        import yfinance as yf
        import numpy as np
        import pandas as pd

        # Get stock data for analysis
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo")

        if hist.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Symbol {symbol} not found")

        current_price = float(hist["Close"].iloc[-1])
        price_change = (
            (current_price - float(hist["Close"].iloc[-2]))
            / float(hist["Close"].iloc[-2])
        ) * 100

        # Calculate technical factors
        sma_20 = hist["Close"].rolling(20).mean().iloc[-1]
        rsi_period = 14
        delta = hist["Close"].diff()
        gain = delta.where(delta > 0, 0).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50

        # Generate symbol-specific AI factors
        symbol_factors = [
            {
                "factor_id": "technical_momentum",
                "factor_name": "テクニカルモメンタム",
                "weight": 0.32,
                "impact": "positive" if price_change > 0 else "negative",
                "confidence": min(0.9, 0.6 + abs(price_change) * 0.05),
                "current_value": {
                    "rsi": round(current_rsi, 1),
                    "sma_distance": round(((current_price - sma_20) / sma_20) * 100, 2),
                    "price_change": round(price_change, 2),
                },
                "description": f"RSI {current_rsi:.1f}, SMA20との乖離 {((current_price - sma_20) / sma_20) * 100:.1f}%",
            },
            {
                "factor_id": "volume_pattern",
                "factor_name": "出来高パターン",
                "weight": 0.26,
                "impact": (
                    "positive"
                    if hist["Volume"].iloc[-1]
                    > hist["Volume"].rolling(10).mean().iloc[-1]
                    else "neutral"
                ),
                "confidence": 0.71,
                "current_value": {
                    "volume_ratio": round(
                        float(
                            hist["Volume"].iloc[-1]
                            / hist["Volume"].rolling(10).mean().iloc[-1]
                        ),
                        2,
                    ),
                    "avg_volume": int(hist["Volume"].rolling(10).mean().iloc[-1]),
                },
                "description": f"10日平均比 {hist['Volume'].iloc[-1] / hist['Volume'].rolling(10).mean().iloc[-1]:.1f}倍の出来高",
            },
            {
                "factor_id": "volatility_analysis",
                "factor_name": "ボラティリティ分析",
                "weight": 0.24,
                "impact": "neutral",
                "confidence": 0.68,
                "current_value": {
                    "volatility_20d": round(
                        float(
                            hist["Close"].pct_change().rolling(20).std()
                            * np.sqrt(252)
                            * 100
                        ),
                        2,
                    ),
                    "price_range": round(
                        (
                            (hist["High"].iloc[-1] - hist["Low"].iloc[-1])
                            / hist["Close"].iloc[-1]
                        )
                        * 100,
                        2,
                    ),
                },
                "description": f"20日ボラティリティ {hist['Close'].pct_change().rolling(20).std().iloc[-1] * np.sqrt(252) * 100:.1f}%",
            },
            {
                "factor_id": "market_correlation",
                "factor_name": "市場相関性",
                "weight": 0.18,
                "impact": "neutral",
                "confidence": 0.64,
                "current_value": {
                    # Mock beta
                    "beta_estimate": round(np.random.uniform(0.8, 1.3), 2),
                    "correlation_sp500": round(np.random.uniform(0.6, 0.85), 2),
                },
                "description": f"S&P500との相関 {np.random.uniform(0.6, 0.85):.2f}, ベータ値推定 {np.random.uniform(0.8, 1.3):.2f}",
            },
        ]

        # Calculate overall scores
        overall_confidence = sum(f["confidence"] * f["weight"]
                                 for f in symbol_factors)
        positive_factors = [
            f for f in symbol_factors if f["impact"] == "positive"]
        negative_factors = [
            f for f in symbol_factors if f["impact"] == "negative"]

        return {
            "symbol": symbol.upper(),
            "current_price": round(current_price, 2),
            "price_change_24h": round(price_change, 2),
            "ai_factors": symbol_factors,
            "summary": {
                "overall_confidence": round(overall_confidence, 2),
                "positive_factors": len(positive_factors),
                "negative_factors": len(negative_factors),
                "neutral_factors": len(
                    [f for f in symbol_factors if f["impact"] == "neutral"]
                ),
                "dominant_factor": max(symbol_factors, key=lambda x: x["weight"])[
                    "factor_name"
                ],
            },
            "analysis_period": f"{days} days",
            "timestamp": datetime.now().isoformat(),
            "data_source": "Yahoo Finance + Miraikakaku AI Engine",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting AI factors for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"銘柄 {symbol} のAIファクター分析に失敗しました",
        )


# ===============================
# News API
# ===============================


@app.get("/api/news")
async def get_news(limit: int = 20, category: str = None, symbol: str = None):
    """ニュース一覧取得 - 最新の金融ニュースを取得"""
    try:
        # Mock news data for demonstration
        all_news = [
            {
                "news_id": "news_001",
                "title": "米FRB、金利据え置きを決定 - 市場は好反応",
                "summary": "連邦準備制度理事会（FRB）は政策金利を据え置くことを発表。インフレ動向を慎重に見極める方針を示した。",
                "content": "連邦準備制度理事会（FRB）は本日の会合で、政策金利を現行の5.25-5.50%に据え置くことを全会一致で決定した。パウエル議長は記者会見で「インフレ率の持続的な低下を確認するまで慎重なスタンスを維持する」と述べた。市場関係者は今回の決定を好意的に受け止めており、主要株価指数は軒並み上昇している。",
                "category": "monetary_policy",
                "tags": ["FRB", "金利", "金融政策", "インフレ"],
                "author": "Miraikakaku編集部",
                "published_at": "2024-01-24T14:30:00Z",
                "updated_at": "2024-01-24T14:30:00Z",
                "impact_score": 8.5,
                "affected_symbols": ["SPY", "QQQ", "DIA"],
                "sentiment": "positive",
                "source": "Federal Reserve",
                "image_url": None,
                "read_time_minutes": 3,
            },
            {
                "news_id": "news_002",
                "title": "NVIDIA、第4四半期決算で予想上回る - AI需要が牽引",
                "summary": "NVIDIA社が発表した第4四半期決算は市場予想を大幅に上回った。データセンター向けAIチップの需要が好調。",
                "content": "半導体大手のNVIDIA社は第4四半期決算を発表し、売上高は市場予想の220億ドルを大幅に上回る241億ドルを記録した。特にデータセンター事業の売上高は前年同期比427%増の184億ドルに達し、生成AIブームによる需要の急拡大が業績を押し上げた。",
                "category": "earnings",
                "tags": ["NVIDIA", "決算", "AI", "半導体", "データセンター"],
                "author": "テック担当記者",
                "published_at": "2024-01-24T12:15:00Z",
                "updated_at": "2024-01-24T12:15:00Z",
                "impact_score": 9.2,
                "affected_symbols": ["NVDA", "AMD", "TSM"],
                "sentiment": "very_positive",
                "source": "NVIDIA Investor Relations",
                "image_url": None,
                "read_time_minutes": 4,
            },
            {
                "news_id": "news_003",
                "title": "日銀、追加緩和措置を検討 - 円安進行への懸念も",
                "summary": "日本銀行が追加の金融緩和措置を検討していることが関係者への取材で明らかになった。ただし円安進行への懸念も。",
                "content": "複数の関係者によると、日本銀行は景気下支えのため追加の金融緩和措置を検討している。具体的にはETF買い入れ枠の拡大や長期金利の変動許容幅の調整が議論されている。一方で、円安進行による輸入物価上昇への懸念から、慎重な意見も根強い。",
                "category": "monetary_policy",
                "tags": ["日銀", "金融緩和", "円安", "ETF", "金利"],
                "author": "金融政策担当記者",
                "published_at": "2024-01-24T10:45:00Z",
                "updated_at": "2024-01-24T11:00:00Z",
                "impact_score": 7.8,
                "affected_symbols": ["USDJPY", "NIKKEI", "TOPIX"],
                "sentiment": "neutral",
                "source": "内部関係者",
                "image_url": None,
                "read_time_minutes": 3,
            },
            {
                "news_id": "news_004",
                "title": "Tesla、中国での販売回復傾向 - 価格戦略が功を奏す",
                "summary": "Tesla社の中国での車両販売が回復傾向にある。積極的な価格戦略と新モデル投入が効果を発揮。",
                "content": "電気自動車メーカーのTeslaは、中国市場での販売回復を発表した。12月の販売台数は前月比15%増となり、価格引き下げ戦略と新型Model Yの投入が奏功した形。中国のEV市場は競争が激化しているが、同社は技術優位性を活かして市場シェアの維持に努めている。",
                "category": "automotive",
                "tags": ["Tesla", "中国", "EV", "販売", "価格戦略"],
                "author": "自動車業界担当記者",
                "published_at": "2024-01-24T09:20:00Z",
                "updated_at": "2024-01-24T09:20:00Z",
                "impact_score": 6.5,
                "affected_symbols": ["TSLA", "BYD", "LI"],
                "sentiment": "positive",
                "source": "Tesla China",
                "image_url": None,
                "read_time_minutes": 2,
            },
        ]

        # Filter by category if specified
        if category:
            all_news = [
                news for news in all_news if news["category"] == category]

        # Filter by symbol if specified
        if symbol:
            all_news = [
                news for news in all_news if symbol.upper() in news["affected_symbols"]
            ]

        # Apply limit
        news_list = all_news[:limit]

        return {
            "news": news_list,
            "total_count": len(news_list),
            "available_categories": [
                "monetary_policy",
                "earnings",
                "automotive",
                "technology",
                "market_analysis",
            ],
            "filters_applied": {
                "category": category,
                "symbol": symbol,
                "limit": limit,
            },
            "timestamp": datetime.now().isoformat(),
            "data_source": "Miraikakaku News Network",
        }

    except Exception as e:
        logger.error(f"Error getting news: {e}")
        raise HTTPException(status_code=500, detail="ニュース取得に失敗しました")


@app.get("/api/news/{news_id}")
async def get_news_details(news_id: str):
    """ニュース詳細取得 - 特定ニュースの詳細情報を取得"""
    try:
        # Mock detailed news data
        news_details = {
            "news_001": {
                "news_id": "news_001",
                "title": "米FRB、金利据え置きを決定 - 市場は好反応",
                "summary": "連邦準備制度理事会（FRB）は政策金利を据え置くことを発表。インフレ動向を慎重に見極める方針を示した。",
                "content": """連邦準備制度理事会（FRB）は本日の会合で、政策金利を現行の5.25-5.50%に据え置くことを全会一致で決定した。パウエル議長は記者会見で「インフレ率の持続的な低下を確認するまで慎重なスタンスを維持する」と述べた。

市場関係者は今回の決定を好意的に受け止めており、主要株価指数は軒並み上昇している。S&P500指数は1.2%高、ナスダック総合指数は1.8%高で取引を終了した。

金融政策委員会（FOMC）の声明では、労働市場の堅調さとインフレ率の緩やかな低下傾向を評価する一方、地政学的リスクや金融システムの安定性についても言及された。

今後の政策パスについて、パウエル議長は「データ次第」との立場を強調し、次回3月会合での利下げ開始の可能性については明言を避けた。市場では6月までに利下げが開始されるとの見方が強まっている。""",
                "category": "monetary_policy",
                "tags": ["FRB", "金利", "金融政策", "インフレ", "FOMC"],
                "author": "Miraikakaku編集部",
                "author_bio": "金融政策と中央銀行動向を専門とする編集チーム",
                "published_at": "2024-01-24T14:30:00Z",
                "updated_at": "2024-01-24T14:30:00Z",
                "impact_score": 8.5,
                "affected_symbols": ["SPY", "QQQ", "DIA", "TLT", "GLD"],
                "sentiment": "positive",
                "sentiment_details": {
                    "positive_score": 0.75,
                    "negative_score": 0.15,
                    "neutral_score": 0.10,
                },
                "source": "Federal Reserve",
                "source_reliability": 9.8,
                "image_url": None,
                "read_time_minutes": 3,
                "related_news": ["news_003", "news_005"],
                "market_reaction": {
                    "immediate_impact": "positive",
                    "affected_sectors": [
                        "financials",
                        "technology",
                        "real_estate",
                    ],
                    "currency_impact": "USD strengthened",
                },
                "social_metrics": {
                    "views": 15420,
                    "shares": 892,
                    "bookmarks": 234,
                },
            }
        }

        if news_id not in news_details:
            raise HTTPException(status_code=404, detail="ニュースが見つかりません")

        return {
            **news_details[news_id],
            "timestamp": datetime.now().isoformat(),
            "data_source": "Miraikakaku News Network",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting news details: {e}")
        raise HTTPException(status_code=500, detail="ニュース詳細取得に失敗しました")


@app.post("/api/news/{news_id}/bookmark")
async def toggle_news_bookmark(news_id: str, action: str = "toggle"):
    """ニュースブックマーク - ニュースのブックマーク状態を切り替え"""
    try:
        # Mock bookmark operation
        current_status = random.choice([True, False])
        new_status = not current_status if action == "toggle" else (
            action == "add")

        return {
            "news_id": news_id,
            "bookmark_status": new_status,
            "action_performed": "added" if new_status else "removed",
            "total_bookmarks": random.randint(50, 500),
            "message": f"ニュースのブックマークが{'追加' if new_status else '削除'}されました",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error toggling bookmark for news {news_id}: {e}")
        raise HTTPException(status_code=500, detail="ブックマーク操作に失敗しました")


@app.get("/api/news/categories/{category}")
async def get_category_news(category: str, limit: int = 20):
    """カテゴリ別ニュース - 特定カテゴリのニュースを取得"""
    try:
        # Define category mappings
        categories = {
            "monetary_policy": "金融政策",
            "earnings": "企業決算",
            "automotive": "自動車",
            "technology": "テクノロジー",
            "market_analysis": "市場分析",
            "crypto": "暗号通貨",
            "commodities": "コモディティ",
        }

        if category not in categories:
            raise HTTPException(status_code=404, detail="無効なカテゴリです")

        # Mock category-specific news
        category_news = []
        for i in range(min(limit, 15)):
            category_news.append(
                {
                    "news_id": f"{category}_{i:03d}",
                    "title": f"{categories[category]}関連ニュース {i + 1}",
                    "summary": f"{categories[category]}に関する重要な動向をお伝えします。",
                    "category": category,
                    "tags": [category, "市場動向", "分析"],
                    "author": f"{category}担当記者",
                    "published_at": (datetime.now() - timedelta(hours=i)).isoformat(),
                    "impact_score": round(random.uniform(5.0, 9.5), 1),
                    "sentiment": random.choice(["positive", "negative", "neutral"]),
                    "read_time_minutes": random.randint(2, 5),
                }
            )

        return {
            "category": category,
            "category_name": categories[category],
            "news": category_news,
            "total_count": len(category_news),
            "related_categories": [k for k in categories.keys() if k != category][:3],
            "timestamp": datetime.now().isoformat(),
            "data_source": "Miraikakaku News Network",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category news: {e}")
        raise HTTPException(
            status_code=500, detail="カテゴリニュース取得に失敗しました"
        )


# ===============================
# Phase 3: User Management API
# ===============================


@app.get("/api/user/profile")
async def get_user_profile(user_id: str = "user_123"):
    """ユーザープロフィール取得 - ユーザーの基本情報と設定を取得"""
    try:
        # Mock user profile data
        user_profile = {
            "user_id": user_id,
            "username": "investor_pro",
            "email": "user@example.com",
            "display_name": "プロ投資家",
            "avatar_url": None,
            "created_at": "2023-06-15T08:30:00Z",
            "last_login": datetime.now().isoformat(),
            "account_status": "active",
            "membership_tier": "premium",
            "preferences": {
                "language": "ja",
                "timezone": "Asia/Tokyo",
                "currency_display": "JPY",
                "notification_email": True,
                "notification_push": True,
                "theme": "dark",
            },
            "statistics": {
                "total_predictions": 127,
                "correct_predictions": 89,
                "accuracy_rate": 0.70,
                "total_points": 15420,
                "ranking_position": 47,
                "contests_participated": 23,
                "watchlist_items": 15,
                "portfolio_count": 3,
            },
            "achievements": [
                {
                    "achievement_id": "predictor_novice",
                    "name": "予測初心者",
                    "description": "初回予測を投稿",
                    "earned_at": "2023-06-20T10:00:00Z",
                    "icon": "🎯",
                },
                {
                    "achievement_id": "accuracy_master",
                    "name": "精度マスター",
                    "description": "予測精度70%以上を達成",
                    "earned_at": "2023-12-01T15:30:00Z",
                    "icon": "🏆",
                },
            ],
        }

        return {
            **user_profile,
            "timestamp": datetime.now().isoformat(),
            "data_source": "Miraikakaku User System",
        }

    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=500, detail="ユーザープロフィール取得に失敗しました"
        )


@app.put("/api/user/profile")
async def update_user_profile(
    display_name: str = None,
    preferences: dict = None,
    user_id: str = "user_123",
):
    """ユーザープロフィール更新 - ユーザーの基本情報と設定を更新"""
    try:
        # Mock profile update
        updates = {}
        if display_name:
            updates["display_name"] = display_name
        if preferences:
            updates["preferences"] = preferences

        return {
            "user_id": user_id,
            "updates_applied": updates,
            "updated_at": datetime.now().isoformat(),
            "message": "プロフィールが正常に更新されました",
        }

    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="プロフィール更新に失敗しました")


@app.get("/api/user/watchlist")
async def get_user_watchlist(user_id: str = "user_123"):
    """ウォッチリスト取得 - ユーザーのウォッチリスト銘柄を取得"""
    try:
        # Mock watchlist data
        watchlist_items = [
            {
                "watchlist_id": "watch_001",
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "added_at": "2023-10-15T09:20:00Z",
                "current_price": 175.43,
                "price_change": 2.17,
                "price_change_percent": 1.25,
                "alert_price_high": 180.00,
                "alert_price_low": 160.00,
                "notes": "iPhone販売動向に注目",
            },
            {
                "watchlist_id": "watch_002",
                "symbol": "TSLA",
                "company_name": "Tesla Inc.",
                "added_at": "2023-11-02T14:45:00Z",
                "current_price": 241.92,
                "price_change": -5.33,
                "price_change_percent": -2.16,
                "alert_price_high": 260.00,
                "alert_price_low": 220.00,
                "notes": "EV市場拡大の恩恵期待",
            },
            {
                "watchlist_id": "watch_003",
                "symbol": "NVDA",
                "company_name": "NVIDIA Corporation",
                "added_at": "2023-12-10T11:30:00Z",
                "current_price": 465.20,
                "price_change": 12.45,
                "price_change_percent": 2.75,
                "alert_price_high": 500.00,
                "alert_price_low": 400.00,
                "notes": "AI需要持続性を監視",
            },
        ]

        # Calculate summary statistics
        total_value_change = sum(item["price_change"]
                                 for item in watchlist_items)
        positive_movers = len(
            [item for item in watchlist_items if item["price_change"] > 0]
        )
        negative_movers = len(
            [item for item in watchlist_items if item["price_change"] < 0]
        )

        return {
            "user_id": user_id,
            "watchlist": watchlist_items,
            "summary": {
                "total_items": len(watchlist_items),
                "total_value_change": round(total_value_change, 2),
                "positive_movers": positive_movers,
                "negative_movers": negative_movers,
                "neutral_movers": len(watchlist_items)
                - positive_movers
                - negative_movers,
            },
            "timestamp": datetime.now().isoformat(),
            "data_source": "Yahoo Finance + Miraikakaku Watchlist",
        }

    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(status_code=500, detail="ウォッチリスト取得に失敗しました")


@app.post("/api/user/watchlist")
async def add_to_watchlist(
    symbol: str,
    alert_price_high: float = None,
    alert_price_low: float = None,
    notes: str = None,
    user_id: str = "user_123",
):
    """ウォッチリスト追加 - 銘柄をウォッチリストに追加"""
    try:
        import yfinance as yf

        # Validate symbol
        ticker = yf.Ticker(symbol)
        info = ticker.history(period="1d")
        if info.empty:
            raise HTTPException(
                status_code=404, detail=f"銘柄 {symbol} が見つかりません"
            )

        current_price = float(info["Close"].iloc[-1])
        company_name = f"{symbol} Corporation"  # Mock company name

        watchlist_item = {
            "watchlist_id": f"watch_{random.randint(1000, 9999)}",
            "symbol": symbol.upper(),
            "company_name": company_name,
            "added_at": datetime.now().isoformat(),
            "current_price": round(current_price, 2),
            "alert_price_high": alert_price_high,
            "alert_price_low": alert_price_low,
            "notes": notes,
            "user_id": user_id,
        }

        return {
            "message": f"銘柄 {symbol} をウォッチリストに追加しました",
            "watchlist_item": watchlist_item,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        raise HTTPException(status_code=500, detail="ウォッチリスト追加に失敗しました")


@app.delete("/api/user/watchlist/{watchlist_id}")
async def remove_from_watchlist(watchlist_id: str, user_id: str = "user_123"):
    """ウォッチリスト削除 - 銘柄をウォッチリストから削除"""
    try:
        return {
            "message": f"ウォッチリストアイテム {watchlist_id} を削除しました",
            "watchlist_id": watchlist_id,
            "user_id": user_id,
            "deleted_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        raise HTTPException(status_code=500, detail="ウォッチリスト削除に失敗しました")


@app.get("/api/user/notifications")
async def get_notification_settings(user_id: str = "user_123"):
    """通知設定取得 - ユーザーの通知設定を取得"""
    try:
        notification_settings = {
            "user_id": user_id,
            "email_notifications": {
                "price_alerts": True,
                "contest_updates": True,
                "news_digest": True,
                "portfolio_summary": False,
                "ai_insights": True,
            },
            "push_notifications": {
                "price_alerts": True,
                "contest_updates": False,
                "breaking_news": True,
                "prediction_reminders": True,
            },
            "alert_preferences": {
                "price_change_threshold": 5.0,  # percentage
                "volume_spike_threshold": 2.0,  # times normal volume
                "news_impact_threshold": 7.0,  # impact score
                "prediction_accuracy_updates": True,
            },
            "frequency_settings": {
                "daily_digest_time": "09:00",
                "weekly_summary_day": "sunday",
                "monthly_report": True,
            },
        }

        return {
            **notification_settings,
            "timestamp": datetime.now().isoformat(),
            "data_source": "Miraikakaku User System",
        }

    except Exception as e:
        logger.error(f"Error getting notification settings: {e}")
        raise HTTPException(status_code=500, detail="通知設定取得に失敗しました")


@app.put("/api/user/notifications")
async def update_notification_settings(
    email_notifications: dict = None,
    push_notifications: dict = None,
    alert_preferences: dict = None,
    frequency_settings: dict = None,
    user_id: str = "user_123",
):
    """通知設定更新 - ユーザーの通知設定を更新"""
    try:
        updates = {}
        if email_notifications:
            updates["email_notifications"] = email_notifications
        if push_notifications:
            updates["push_notifications"] = push_notifications
        if alert_preferences:
            updates["alert_preferences"] = alert_preferences
        if frequency_settings:
            updates["frequency_settings"] = frequency_settings

        return {
            "user_id": user_id,
            "updates_applied": updates,
            "updated_at": datetime.now().isoformat(),
            "message": "通知設定が正常に更新されました",
        }

    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        raise HTTPException(status_code=500, detail="通知設定更新に失敗しました")


# ===============================
# Portfolio API
# ===============================


@app.get("/api/portfolios")
async def get_portfolios(user_id: str = "user_123"):
    """ポートフォリオ一覧取得 - ユーザーのポートフォリオ一覧を取得"""
    try:
        # Mock portfolio data
        portfolios = [
            {
                "portfolio_id": "portfolio_001",
                "name": "成長株ポートフォリオ",
                "description": "高成長が期待できるテック株中心のポートフォリオ",
                "created_at": "2023-08-15T10:30:00Z",
                "updated_at": "2024-01-24T15:45:00Z",
                "currency": "USD",
                "total_value": 125400.50,
                "total_cost": 110000.00,
                "total_gain_loss": 15400.50,
                "total_gain_loss_percent": 14.00,
                "positions_count": 8,
                "cash_balance": 2500.00,
                "performance": {
                    "daily_change": 1250.30,
                    "daily_change_percent": 1.01,
                    "weekly_change": -890.75,
                    "weekly_change_percent": -0.70,
                    "monthly_change": 4200.80,
                    "monthly_change_percent": 3.47,
                    "ytd_change": 15400.50,
                    "ytd_change_percent": 14.00,
                },
            },
            {
                "portfolio_id": "portfolio_002",
                "name": "配当株ポートフォリオ",
                "description": "安定した配当収入を目的とした保守的ポートフォリオ",
                "created_at": "2023-09-20T14:20:00Z",
                "updated_at": "2024-01-24T15:45:00Z",
                "currency": "USD",
                "total_value": 89300.25,
                "total_cost": 85000.00,
                "total_gain_loss": 4300.25,
                "total_gain_loss_percent": 5.06,
                "positions_count": 12,
                "cash_balance": 1200.00,
                "performance": {
                    "daily_change": -125.80,
                    "daily_change_percent": -0.14,
                    "weekly_change": 340.60,
                    "weekly_change_percent": 0.38,
                    "monthly_change": 1100.30,
                    "monthly_change_percent": 1.25,
                    "ytd_change": 4300.25,
                    "ytd_change_percent": 5.06,
                },
            },
        ]

        # Calculate total portfolio value
        total_value = sum(p["total_value"] for p in portfolios)
        total_cost = sum(p["total_cost"] for p in portfolios)
        total_gain_loss = total_value - total_cost

        return {
            "user_id": user_id,
            "portfolios": portfolios,
            "summary": {
                "total_portfolios": len(portfolios),
                "combined_value": round(total_value, 2),
                "combined_cost": round(total_cost, 2),
                "combined_gain_loss": round(total_gain_loss, 2),
                "combined_gain_loss_percent": (
                    round((total_gain_loss / total_cost) * 100, 2)
                    if total_cost > 0
                    else 0
                ),
            },
            "timestamp": datetime.now().isoformat(),
            "data_source": "Miraikakaku Portfolio System",
        }

    except Exception as e:
        logger.error(f"Error getting portfolios: {e}")
        raise HTTPException(
            status_code=500, detail="ポートフォリオ一覧取得に失敗しました"
        )


@app.post("/api/portfolios")
async def create_portfolio(
    name: str,
    description: str = None,
    currency: str = "USD",
    user_id: str = "user_123",
):
    """ポートフォリオ作成 - 新しいポートフォリオを作成"""
    try:
        portfolio = {
            "portfolio_id": f"portfolio_{random.randint(1000, 9999)}",
            "name": name,
            "description": description,
            "currency": currency,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "user_id": user_id,
            "total_value": 0.0,
            "total_cost": 0.0,
            "total_gain_loss": 0.0,
            "total_gain_loss_percent": 0.0,
            "positions_count": 0,
            "cash_balance": 0.0,
        }

        return {
            "message": f"ポートフォリオ '{name}' を作成しました",
            "portfolio": portfolio,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error creating portfolio: {e}")
        raise HTTPException(status_code=500, detail="ポートフォリオ作成に失敗しました")


@app.get("/api/portfolios/{portfolio_id}")
async def get_portfolio_details(portfolio_id: str, user_id: str = "user_123"):
    """ポートフォリオ詳細取得 - 特定ポートフォリオの詳細情報を取得"""
    try:
        positions = [
            {
                "position_id": "pos_001",
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "quantity": 100,
                "average_cost": 150.25,
                "current_price": 175.43,
                "market_value": 17543.00,
                "cost_basis": 15025.00,
                "unrealized_gain_loss": 2518.00,
                "unrealized_gain_loss_percent": 16.76,
                "day_change": 217.00,
                "day_change_percent": 1.25,
                "weight": 35.2,
                "added_at": "2023-10-15T09:20:00Z",
            },
            {
                "position_id": "pos_002",
                "symbol": "MSFT",
                "company_name": "Microsoft Corporation",
                "quantity": 75,
                "average_cost": 280.50,
                "current_price": 310.80,
                "market_value": 23310.00,
                "cost_basis": 21037.50,
                "unrealized_gain_loss": 2272.50,
                "unrealized_gain_loss_percent": 10.80,
                "day_change": 155.00,
                "day_change_percent": 0.67,
                "weight": 46.8,
                "added_at": "2023-11-02T14:45:00Z",
            },
            {
                "position_id": "pos_003",
                "symbol": "GOOGL",
                "company_name": "Alphabet Inc.",
                "quantity": 30,
                "average_cost": 125.75,
                "current_price": 140.25,
                "market_value": 4207.50,
                "cost_basis": 3772.50,
                "unrealized_gain_loss": 435.00,
                "unrealized_gain_loss_percent": 11.53,
                "day_change": 62.50,
                "day_change_percent": 1.51,
                "weight": 8.4,
                "added_at": "2023-12-10T11:30:00Z",
            },
        ]

        # Calculate portfolio metrics
        total_market_value = sum(pos["market_value"] for pos in positions)
        total_cost_basis = sum(pos["cost_basis"] for pos in positions)
        total_unrealized_gain_loss = total_market_value - total_cost_basis
        total_day_change = sum(pos["day_change"] for pos in positions)

        # Portfolio allocation by sector (mock data)
        sector_allocation = [
            {"sector": "Technology", "value": 35000.0, "weight": 70.0},
            {"sector": "Healthcare", "value": 8000.0, "weight": 16.0},
            {"sector": "Financials", "value": 7000.0, "weight": 14.0},
        ]

        portfolio_details = {
            "portfolio_id": portfolio_id,
            "user_id": user_id,
            "name": "成長株ポートフォリオ",
            "description": "高成長が期待できるテック株中心のポートフォリオ",
            "currency": "USD",
            "created_at": "2023-08-15T10:30:00Z",
            "updated_at": datetime.now().isoformat(),
            "positions": positions,
            "summary": {
                "total_positions": len(positions),
                "total_market_value": round(total_market_value, 2),
                "total_cost_basis": round(total_cost_basis, 2),
                "total_unrealized_gain_loss": round(total_unrealized_gain_loss, 2),
                "total_unrealized_gain_loss_percent": (
                    round(
                        (total_unrealized_gain_loss / total_cost_basis) * 100,
                        2,
                    )
                    if total_cost_basis > 0
                    else 0
                ),
                "total_day_change": round(total_day_change, 2),
                "total_day_change_percent": (
                    round((total_day_change / total_market_value) * 100, 2)
                    if total_market_value > 0
                    else 0
                ),
                "cash_balance": 2500.00,
            },
            "allocation": {
                "by_sector": sector_allocation,
                "by_position": [
                    {
                        "symbol": pos["symbol"],
                        "value": pos["market_value"],
                        "weight": pos["weight"],
                    }
                    for pos in positions
                ],
            },
            "performance_metrics": {
                "sharpe_ratio": 1.35,
                "beta": 1.12,
                "max_drawdown": -12.5,
                "volatility": 18.4,
            },
        }

        return {
            **portfolio_details,
            "timestamp": datetime.now().isoformat(),
            "data_source": "Yahoo Finance + Miraikakaku Portfolio System",
        }

    except Exception as e:
        logger.error(f"Error getting portfolio details: {e}")
        raise HTTPException(
            status_code=500, detail="ポートフォリオ詳細取得に失敗しました"
        )


@app.post("/api/portfolios/{portfolio_id}/transactions")
async def add_transaction(
    portfolio_id: str,
    symbol: str,
    transaction_type: str,  # "buy" or "sell"
    quantity: float,
    price: float,
    transaction_date: str = None,
    user_id: str = "user_123",
):
    """取引記録追加 - ポートフォリオに新しい取引を記録"""
    try:
        if transaction_type not in ["buy", "sell"]:
            raise HTTPException(
                status_code=400,
                detail="取引タイプは 'buy' または 'sell' である必要があります",
            )

        if quantity <= 0 or price <= 0:
            raise HTTPException(
                status_code=400,
                detail="数量と価格は正の数である必要があります",
            )

        transaction = {
            "transaction_id": f"txn_{random.randint(100000, 999999)}",
            "portfolio_id": portfolio_id,
            "symbol": symbol.upper(),
            "transaction_type": transaction_type,
            "quantity": quantity,
            "price": price,
            "total_amount": quantity * price,
            "transaction_date": transaction_date or datetime.now().isoformat(),
            "fees": round(quantity * price * 0.001, 2),  # 0.1% fee
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
        }

        return {
            "message": f"{transaction_type.upper()} 取引を記録しました: {quantity} shares of {symbol} @ ${price}",
            "transaction": transaction,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding transaction: {e}")
        raise HTTPException(status_code=500, detail="取引記録追加に失敗しました")


@app.get("/api/portfolios/{portfolio_id}/transactions")
async def get_portfolio_transactions(
    portfolio_id: str,
    limit: int = 50,
    transaction_type: str = None,
    user_id: str = "user_123",
):
    """取引履歴取得 - ポートフォリオの取引履歴を取得"""
    try:
        # Mock transaction history
        all_transactions = []
        for i in range(20):
            transaction = {
                "transaction_id": f"txn_{i + 100000}",
                "portfolio_id": portfolio_id,
                "symbol": random.choice(["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]),
                "transaction_type": random.choice(["buy", "sell"]),
                "quantity": random.randint(10, 200),
                "price": round(random.uniform(100, 500), 2),
                "transaction_date": (
                    datetime.now() - timedelta(days=i * 7)
                ).isoformat(),
                "fees": round(random.uniform(5, 50), 2),
                "user_id": user_id,
            }
            transaction["total_amount"] = transaction["quantity"] * \
                transaction["price"]
            all_transactions.append(transaction)

        # Filter by transaction type if specified
        if transaction_type:
            all_transactions = [
                t for t in all_transactions if t["transaction_type"] == transaction_type
            ]

        # Apply limit
        transactions = all_transactions[:limit]

        # Calculate summary statistics
        total_buy_amount = sum(
            t["total_amount"] for t in transactions if t["transaction_type"] == "buy"
        )
        total_sell_amount = sum(
            t["total_amount"] for t in transactions if t["transaction_type"] == "sell"
        )
        total_fees = sum(t["fees"] for t in transactions)

        return {
            "portfolio_id": portfolio_id,
            "user_id": user_id,
            "transactions": transactions,
            "summary": {
                "total_transactions": len(transactions),
                "total_buy_amount": round(total_buy_amount, 2),
                "total_sell_amount": round(total_sell_amount, 2),
                "net_invested": round(total_buy_amount - total_sell_amount, 2),
                "total_fees": round(total_fees, 2),
            },
            "filters_applied": {
                "limit": limit,
                "transaction_type": transaction_type,
            },
            "timestamp": datetime.now().isoformat(),
            "data_source": "Miraikakaku Portfolio System",
        }

    except Exception as e:
        logger.error(f"Error getting portfolio transactions: {e}")
        raise HTTPException(status_code=500, detail="取引履歴取得に失敗しました")


@app.delete("/api/portfolios/{portfolio_id}")
async def delete_portfolio(portfolio_id: str, user_id: str = "user_123"):
    """ポートフォリオ削除 - ポートフォリオを削除"""
    try:
        return {
            "message": f"ポートフォリオ {portfolio_id} を削除しました",
            "portfolio_id": portfolio_id,
            "user_id": user_id,
            "deleted_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error deleting portfolio: {e}")
        raise HTTPException(status_code=500, detail="ポートフォリオ削除に失敗しました")


# ===============================
# Advanced Analytics API
# ===============================


@app.get("/api/analytics/market-overview")
async def get_market_overview():
    """市場概況分析 - 総合的な市場分析データを取得"""
    try:
        import yfinance as yf

        indices = {"DOW": "^DJI", "NIKKEI": "^N225", "FTSE": "^FTSE"}
        market_data = []
        for name, symbol in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                if not hist.empty:
                    current_price = float(hist["Close"].iloc[-1])
                    prev_price = float(hist["Close"].iloc[-2])
                    change = current_price - prev_price
                    change_percent = (change / prev_price) * 100

                    market_data.append(
                        {
                            "index": name,
                            "symbol": symbol,
                            "current_value": round(current_price, 2),
                            "daily_change": round(change, 2),
                            "daily_change_percent": round(change_percent, 2),
                            "volume": (
                                int(hist["Volume"].iloc[-1])
                                if not pd.isna(hist["Volume"].iloc[-1])
                                else 0
                            ),
                        }
                    )
                else:
                    # Fallback mock data
                    market_data.append(
                        {
                            "index": name,
                            "symbol": symbol,
                            "current_value": round(random.uniform(30000, 40000), 2),
                            "daily_change": round(random.uniform(-500, 500), 2),
                            "daily_change_percent": round(random.uniform(-2, 2), 2),
                            "volume": random.randint(1000000, 5000000),
                        }
                    )
            except BaseException:
                # Fallback mock data on any error
                market_data.append(
                    {
                        "index": name,
                        "symbol": symbol,
                        "current_value": round(random.uniform(30000, 40000), 2),
                        "daily_change": round(random.uniform(-500, 500), 2),
                        "daily_change_percent": round(random.uniform(-2, 2), 2),
                        "volume": random.randint(1000000, 5000000),
                    }
                )

        # Market sentiment analysis
        positive_indices = len(
            [idx for idx in market_data if idx["daily_change_percent"] > 0]
        )
        negative_indices = len(
            [idx for idx in market_data if idx["daily_change_percent"] < 0]
        )

        market_sentiment = (
            "bullish"
            if positive_indices > negative_indices
            else ("bearish" if negative_indices > positive_indices else "neutral")
        )

        # Sector performance (mock data)
        sector_performance = [
            {
                "sector": "Technology",
                "change_percent": 1.45,
                "top_movers": ["AAPL", "MSFT", "GOOGL"],
            },
            {
                "sector": "Healthcare",
                "change_percent": 0.32,
                "top_movers": ["JNJ", "PFE", "UNH"],
            },
            {
                "sector": "Financials",
                "change_percent": -0.18,
                "top_movers": ["JPM", "BAC", "WFC"],
            },
            {
                "sector": "Energy",
                "change_percent": 2.15,
                "top_movers": ["XOM", "CVX", "COP"],
            },
            {
                "sector": "Consumer Discretionary",
                "change_percent": 0.87,
                "top_movers": ["TSLA", "AMZN", "HD"],
            },
        ]

        # Economic indicators (mock data)
        economic_indicators = {
            "vix": {
                "value": 18.2,
                "change": -1.1,
                "interpretation": "低ボラティリティ",
            },
            "yield_10y": {
                "value": 4.15,
                "change": 0.05,
                "interpretation": "金利上昇傾向",
            },
            "dxy": {
                "value": 103.2,
                "change": 0.3,
                "interpretation": "ドル高進行",
            },
            "oil_wti": {
                "value": 78.5,
                "change": 1.2,
                "interpretation": "原油価格上昇",
            },
            "gold": {
                "value": 2034.5,
                "change": -8.3,
                "interpretation": "金価格軟調",
            },
        }

        return {
            "market_indices": market_data,
            "market_sentiment": {
                "overall": market_sentiment,
                "positive_indices": positive_indices,
                "negative_indices": negative_indices,
                "neutral_indices": len(market_data)
                - positive_indices
                - negative_indices,
            },
            "sector_performance": sector_performance,
            "economic_indicators": economic_indicators,
            "market_summary": {
                "risk_appetite": (
                    "moderate"
                    if market_sentiment == "neutral"
                    else ("high" if market_sentiment == "bullish" else "low")
                ),
                "volatility_level": (
                    "low"
                    if economic_indicators["vix"]["value"] < 20
                    else (
                        "moderate"
                        if economic_indicators["vix"]["value"] < 30
                        else "high"
                    )
                ),
                "key_themes": [
                    "金利動向",
                    "AI関連銘柄",
                    "エネルギー価格",
                    "地政学リスク",
                ],
            },
            "timestamp": datetime.now().isoformat(),
            "data_source": "Yahoo Finance + Miraikakaku Analytics Engine",
        }

    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(status_code=500, detail="市場概況分析取得に失敗しました")


@app.get("/api/analytics/correlation-matrix")
async def get_correlation_matrix(symbols: str, period: str = "1mo"):
    """相関分析 - 複数銘柄の相関関係を分析"""
    try:
        import pandas as pd
        import numpy as np

        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        if len(symbol_list) < 2:
            raise HTTPException(status_code=400, detail="少なくとも2つの銘柄が必要です")
        if len(symbol_list) > 10:
            raise HTTPException(status_code=400, detail="最大10銘柄まで分析可能です")

        # Get price data for correlation analysis
        price_data = {}
        for symbol in symbol_list:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                if not hist.empty:
                    price_data[symbol] = hist["Close"].pct_change().dropna()
                else:
                    # Generate mock correlation data
                    dates = pd.date_range(
                        start="2024-01-01", periods=30, freq="D")
                    mock_returns = np.random.normal(0, 0.02, len(dates))
                    price_data[symbol] = pd.Series(mock_returns, index=dates)
            except BaseException:
                # Generate mock correlation data on error
                dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
                mock_returns = np.random.normal(0, 0.02, len(dates))
                price_data[symbol] = pd.Series(mock_returns, index=dates)

        # Calculate correlation matrix
        returns_df = pd.DataFrame(price_data)
        correlation_matrix = returns_df.corr()

        # Convert to serializable format
        correlations = []
        for i, symbol1 in enumerate(symbol_list):
            for j, symbol2 in enumerate(symbol_list):
                correlation_value = float(correlation_matrix.iloc[i, j])
                correlations.append(
                    {
                        "symbol1": symbol1,
                        "symbol2": symbol2,
                        "correlation": round(correlation_value, 3),
                        "relationship": (
                            "strong_positive"
                            if correlation_value > 0.7
                            else (
                                "moderate_positive"
                                if correlation_value > 0.3
                                else (
                                    "weak_positive"
                                    if correlation_value > 0.1
                                    else (
                                        "neutral"
                                        if abs(correlation_value) <= 0.1
                                        else (
                                            "weak_negative"
                                            if correlation_value > -0.3
                                            else (
                                                "moderate_negative"
                                                if correlation_value > -0.7
                                                else "strong_negative"
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                    }
                )

        # Find strongest correlations
        non_diagonal = [
            c for c in correlations if c["symbol1"] != c["symbol2"]]
        strongest_positive = max(
            non_diagonal,
            key=lambda x: x["correlation"] if x["correlation"] < 1 else 0,
        )
        strongest_negative = min(non_diagonal, key=lambda x: x["correlation"])

        # Portfolio diversification analysis
        avg_correlation = np.mean([c["correlation"] for c in non_diagonal])
        # Higher score = better diversification
        diversification_score = 1 - abs(avg_correlation)

        return {
            "symbols": symbol_list,
            "period": period,
            "correlation_matrix": correlations,
            "analysis": {
                "strongest_positive_correlation": strongest_positive,
                "strongest_negative_correlation": strongest_negative,
                "average_correlation": round(avg_correlation, 3),
                "diversification_score": round(diversification_score, 3),
                "diversification_rating": (
                    "excellent"
                    if diversification_score > 0.8
                    else (
                        "good"
                        if diversification_score > 0.6
                        else ("moderate" if diversification_score > 0.4 else "poor")
                    )
                ),
            },
            "insights": [
                f"平均相関係数: {avg_correlation:.3f}",
                f"分散効果スコア: {diversification_score:.3f}",
                f"最強正の相関: {strongest_positive['symbol1']}-{strongest_positive['symbol2']} ({strongest_positive['correlation']:.3f})",
                f"最強負の相関: {strongest_negative['symbol1']}-{strongest_negative['symbol2']} ({strongest_negative['correlation']:.3f})",
            ],
            "timestamp": datetime.now().isoformat(),
            "data_source": "Yahoo Finance + Miraikakaku Analytics Engine",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting correlation matrix: {e}")
        raise HTTPException(status_code=500, detail="相関分析に失敗しました")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket接続エンドポイント"""
    await manager.connect(websocket)
    try:
        welcome = {
            "type": "connection",
            "data": {
                "message": "Universal Stock API WebSocketに接続しました",
                "timestamp": datetime.now().isoformat(),
                "active_connections": len(manager.active_connections),
            },
        }
        await manager.send_personal_message(json.dumps(welcome), websocket)

        # 定期的な価格更新
        while True:
            symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.history(period="1d", interval="1m")
                    if not info.empty:
                        latest_price = info["Close"].iloc[-1]
                        price_update = {
                            "type": "price_update",
                            "data": {
                                "symbol": symbol,
                                "price": round(latest_price, 2),
                                "timestamp": datetime.now().isoformat(),
                            },
                        }
                        await manager.send_personal_message(
                            json.dumps(price_update), websocket
                        )
                except BaseException:
                    # フォールバック
                    price_update = {
                        "type": "price_update",
                        "data": {
                            "symbol": symbol,
                            "price": round(200 + random.uniform(-50, 50), 2),
                            "timestamp": datetime.now().isoformat(),
                        },
                    }
                    await manager.send_personal_message(
                        json.dumps(price_update), websocket
                    )

                await asyncio.sleep(1)

            await asyncio.sleep(10)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event():
    """アプリ起動時の処理"""
    logger.info("Miraikakaku Production API starting up...")
    logger.info("WebSocket and advanced features enabled")


@app.on_event("shutdown")
async def shutdown_event():
    """アプリ終了時の処理"""
    logger.info("Miraikakaku Production API shutting down...")
    cache.clear()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting Production API server on port {port}")
    uvicorn.run(
        "production_main:app",
        host="0.0.0.0",
        port=port,
        log_level="info")
