from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
import numpy as np

load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Miraikakaku API",
    description="金融分析・株価予測API - Production Version",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番では制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Miraikakaku API Server",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "miraikakaku-api",
        "environment": os.getenv("NODE_ENV", "production"),
    }


# データベース接続（簡易版）
try:
    from database.database import get_db, init_database

    DATABASE_AVAILABLE = True
except ImportError:
    logger.warning("Database module not available, using mock data")
    DATABASE_AVAILABLE = False

    def get_db():
        return None


# メモリキャッシュ（簡易版）
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


@app.get("/api/finance/stocks")
async def get_stocks(
    limit: int = Query(10, ge=1, le=100),
    sector: Optional[str] = None,
    search: Optional[str] = None,
):
    """株式リストを取得"""
    cache_key = f"stocks_{limit}_{sector}_{search}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached

    try:
        # 実際の株式データを取得（Yahoo Finance使用）
        popular_stocks = [
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
        stocks_data = []

        for symbol in popular_stocks[:limit]:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                current_price = info.get(
                    "currentPrice", info.get("regularMarketPrice", 0)
                )
                previous_close = info.get("previousClose", current_price)
                change = (
                    ((current_price - previous_close) / previous_close * 100)
                    if previous_close
                    else 0
                )

                stocks_data.append(
                    {
                        "symbol": symbol,
                        "name": info.get("longName", symbol),
                        "price": round(current_price, 2),
                        "change": round(change, 2),
                        "volume": info.get("volume", 0),
                        "marketCap": info.get("marketCap", 0),
                        "sector": info.get("sector", "Technology"),
                    }
                )
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                continue

        result = {"stocks": stocks_data, "count": len(stocks_data)}
        set_cached_data(cache_key, result)
        return result

    except Exception as e:
        logger.error(f"Error fetching stocks: {e}")
        # フォールバックデータ
        return {
            "stocks": [
                {
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "price": 150.0,
                    "change": 2.5,
                    "sector": "Technology",
                },
                {
                    "symbol": "GOOGL",
                    "name": "Alphabet Inc.",
                    "price": 2500.0,
                    "change": -1.2,
                    "sector": "Technology",
                },
                {
                    "symbol": "TSLA",
                    "name": "Tesla Inc.",
                    "price": 800.0,
                    "change": 5.3,
                    "sector": "Automotive",
                },
            ],
            "count": 3,
        }


@app.get("/api/finance/market-overview")
async def market_overview():
    """マーケット概況を取得"""
    cache_key = "market_overview"
    cached = get_cached_data(cache_key)
    if cached:
        return cached

    try:
        # 主要指標のデータ取得
        indices = {
            "^GSPC": "SP500",
            "^IXIC": "NASDAQ",
            "^DJI": "DOW",
            "^N225": "NIKKEI",
        }

        market_data = {}
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d")

                if not hist.empty:
                    current = hist["Close"].iloc[-1]
                    prev_close = info.get("previousClose", current)
                    change = (
                        ((current - prev_close) / prev_close * 100) if prev_close else 0
                    )

                    market_data[name] = {
                        "value": round(current, 2),
                        "change": round(change, 2),
                        "volume": (
                            int(hist["Volume"].iloc[-1]) if "Volume" in hist else 0
                        ),
                    }
            except Exception as e:
                logger.error(f"Error fetching {name}: {e}")
                market_data[name] = {"value": 0, "change": 0, "volume": 0}

        # センチメント分析（簡易版）
        positive_count = sum(1 for _, data in market_data.items() if data["change"] > 0)
        sentiment = (
            "positive"
            if positive_count >= 2
            else "negative" if positive_count <= 1 else "neutral"
        )

        result = {
            "overview": {
                "indices": market_data,
                "sentiment": sentiment,
                "timestamp": datetime.now().isoformat(),
                "trading_day": datetime.now().strftime("%Y-%m-%d"),
            }
        }

        set_cached_data(cache_key, result)
        return result

    except Exception as e:
        logger.error(f"Error fetching market overview: {e}")
        # フォールバックデータ
        return {
            "overview": {
                "indices": {
                    "SP500": {"value": 4200.0, "change": 0.8, "volume": 1000000},
                    "NASDAQ": {"value": 13500.0, "change": 1.2, "volume": 2000000},
                    "DOW": {"value": 34000.0, "change": 0.5, "volume": 500000},
                    "NIKKEI": {"value": 28000.0, "change": -0.3, "volume": 800000},
                },
                "sentiment": "positive",
                "timestamp": datetime.now().isoformat(),
            }
        }


@app.get("/api/finance/stocks/{symbol}/price")
async def get_stock_price(
    symbol: str, period: str = Query("1mo", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$")
):
    """特定銘柄の価格履歴を取得"""
    cache_key = f"price_{symbol}_{period}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached

    try:
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=period)

        if hist.empty:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")

        price_data = []
        for date, row in hist.iterrows():
            price_data.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"]),
                }
            )

        result = {
            "symbol": symbol.upper(),
            "period": period,
            "data": price_data,
            "count": len(price_data),
        }

        set_cached_data(cache_key, result)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock price")


@app.get("/api/finance/rankings/growth-potential")
async def get_growth_rankings(limit: int = Query(10, ge=1, le=50)):
    """成長ポテンシャルランキング"""
    try:
        growth_stocks = [
            {
                "symbol": "NVDA",
                "name": "NVIDIA Corporation",
                "growth_potential": 35.2,
                "accuracy": 88.5,
            },
            {
                "symbol": "TSLA",
                "name": "Tesla, Inc.",
                "growth_potential": 28.7,
                "accuracy": 75.3,
            },
            {
                "symbol": "AMD",
                "name": "Advanced Micro Devices",
                "growth_potential": 25.1,
                "accuracy": 82.1,
            },
            {
                "symbol": "PLTR",
                "name": "Palantir Technologies",
                "growth_potential": 22.3,
                "accuracy": 71.8,
            },
            {
                "symbol": "NET",
                "name": "Cloudflare Inc.",
                "growth_potential": 20.5,
                "accuracy": 79.2,
            },
        ]

        return {
            "rankings": growth_stocks[:limit],
            "updated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching growth rankings: {e}")
        return {"rankings": [], "error": str(e)}


@app.on_event("startup")
async def startup_event():
    """アプリ起動時の処理"""
    logger.info("Miraikakaku API Production Version starting up...")
    logger.info("API is ready to serve requests")


@app.on_event("shutdown")
async def shutdown_event():
    """アプリ終了時の処理"""
    logger.info("Miraikakaku API shutting down...")
    cache.clear()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting Production API server on port {port}")
    uvicorn.run("simple_main:app", host="0.0.0.0", port=port, log_level="info")
