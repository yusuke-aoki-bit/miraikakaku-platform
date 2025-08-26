"""
Miraikakaku API - Enhanced Production Version
Cloud SQL統合・LSTM予測連携・高度な分析機能付き
"""

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
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
import json

# 新しいモジュールのインポート
try:
    from database.cloud_sql import StockDataRepository, get_db
    from models.lstm_predictor import LSTMStockPredictor

    ADVANCED_FEATURES = True
except ImportError as e:
    logging.warning(f"Advanced features not available: {e}")
    ADVANCED_FEATURES = False

load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Miraikakaku API - Enhanced",
    description="Cloud SQL統合・LSTM予測機能付き金融分析API",
    version="3.0.0",
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

# メモリキャッシュ（拡張版）
cache = {}
cache_timeout = 300  # 5分


class EnhancedCache:
    """拡張キャッシュ管理"""

    @staticmethod
    def get_cached_data(key: str) -> Optional[Any]:
        """キャッシュからデータ取得"""
        if key in cache:
            data, timestamp = cache[key]
            if datetime.now() - timestamp < timedelta(seconds=cache_timeout):
                return data
        return None

    @staticmethod
    def set_cached_data(key: str, data: Any, timeout: int = None):
        """キャッシュにデータ保存"""
        cache_time = timeout or cache_timeout
        cache[key] = (data, datetime.now())

    @staticmethod
    def invalidate_cache(pattern: str = None):
        """キャッシュ無効化"""
        if pattern:
            keys_to_remove = [k for k in cache.keys() if pattern in k]
            for key in keys_to_remove:
                cache.pop(key, None)
        else:
            cache.clear()


# APIエンドポイント


@app.get("/")
async def root():
    return {
        "message": "Miraikakaku Enhanced API Server",
        "version": "3.0.0",
        "status": "running",
        "features": {
            "cloud_sql": ADVANCED_FEATURES,
            "lstm_predictions": ADVANCED_FEATURES,
            "advanced_analytics": ADVANCED_FEATURES,
            "real_time_data": True,
        },
    }


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    health_status = {
        "status": "healthy",
        "service": "miraikakaku-api-enhanced",
        "environment": os.getenv("NODE_ENV", "production"),
        "database": "connected" if ADVANCED_FEATURES else "fallback",
        "cache_size": len(cache),
        "timestamp": datetime.now().isoformat(),
    }

    # データベース接続確認
    if ADVANCED_FEATURES:
        try:
            db_repo = StockDataRepository()
            symbols = db_repo.get_stock_symbols()
            health_status["database_symbols"] = len(symbols)
        except Exception as e:
            health_status["database"] = "error"
            health_status["database_error"] = str(e)

    return health_status


@app.get("/api/finance/stocks")
async def get_stocks_enhanced(
    limit: int = Query(10, ge=1, le=100),
    sector: Optional[str] = None,
    search: Optional[str] = None,
    use_cache: bool = Query(True),
    # db: Optional[Session] = Depends(get_db) if ADVANCED_FEATURES else None
):
    """株式リストを取得 - Cloud SQL統合版"""
    cache_key = f"stocks_enhanced_{limit}_{sector}_{search}"

    if use_cache:
        cached = EnhancedCache.get_cached_data(cache_key)
        if cached:
            return cached

    try:
        # Cloud SQLからデータ取得を試行
        if ADVANCED_FEATURES:
            try:
                db_session = get_db()
                db_repo = StockDataRepository(db_session)
                symbols = db_repo.get_stock_symbols()[:limit]

                stocks_data = []
                for symbol in symbols:
                    # 最新の価格データを取得
                    df = db_repo.get_stock_prices(symbol)
                    if not df.empty:
                        latest_price = df["Close"].iloc[-1]
                        prev_price = (
                            df["Close"].iloc[-2] if len(df) > 1 else latest_price
                        )
                        change = (
                            ((latest_price - prev_price) / prev_price * 100)
                            if prev_price
                            else 0
                        )

                        # 追加情報をYahoo Financeから取得
                        try:
                            ticker = yf.Ticker(symbol)
                            info = ticker.info

                            stocks_data.append(
                                {
                                    "symbol": symbol,
                                    "name": info.get("longName", symbol),
                                    "price": round(latest_price, 2),
                                    "change": round(change, 2),
                                    "volume": (
                                        int(df["Volume"].iloc[-1])
                                        if "Volume" in df
                                        else 0
                                    ),
                                    "marketCap": info.get("marketCap", 0),
                                    "sector": info.get("sector", "Unknown"),
                                    "data_source": "cloud_sql",
                                    "last_updated": df.index[-1].strftime("%Y-%m-%d"),
                                }
                            )
                        except Exception as yf_error:
                            logger.warning(
                                f"Yahoo Finance info failed for {symbol}: {yf_error}"
                            )
                            stocks_data.append(
                                {
                                    "symbol": symbol,
                                    "name": symbol,
                                    "price": round(latest_price, 2),
                                    "change": round(change, 2),
                                    "volume": (
                                        int(df["Volume"].iloc[-1])
                                        if "Volume" in df
                                        else 0
                                    ),
                                    "data_source": "cloud_sql_only",
                                    "last_updated": df.index[-1].strftime("%Y-%m-%d"),
                                }
                            )

                if stocks_data:
                    result = {
                        "stocks": stocks_data,
                        "count": len(stocks_data),
                        "source": "cloud_sql",
                    }
                    EnhancedCache.set_cached_data(cache_key, result)
                    return result

            except Exception as db_error:
                logger.error(f"Cloud SQL query failed: {db_error}")

        # フォールバック: Yahoo Finance直接取得
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
                        "data_source": "yahoo_finance",
                    }
                )
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                continue

        result = {
            "stocks": stocks_data,
            "count": len(stocks_data),
            "source": "yahoo_finance",
        }
        EnhancedCache.set_cached_data(cache_key, result)
        return result

    except Exception as e:
        logger.error(f"Error fetching stocks: {e}")
        # 最後のフォールバック
        return {
            "stocks": [
                {
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "price": 150.0,
                    "change": 2.5,
                    "sector": "Technology",
                    "data_source": "fallback",
                },
                {
                    "symbol": "GOOGL",
                    "name": "Alphabet Inc.",
                    "price": 2500.0,
                    "change": -1.2,
                    "sector": "Technology",
                    "data_source": "fallback",
                },
                {
                    "symbol": "TSLA",
                    "name": "Tesla Inc.",
                    "price": 800.0,
                    "change": 5.3,
                    "sector": "Automotive",
                    "data_source": "fallback",
                },
            ],
            "count": 3,
            "source": "fallback",
        }


@app.get("/api/finance/predictions/{symbol}")
async def get_stock_predictions(
    symbol: str,
    days: int = Query(7, ge=1, le=30),
    # db: Optional[Session] = Depends(get_db) if ADVANCED_FEATURES else None
):
    """LSTM予測結果を取得"""
    cache_key = f"predictions_{symbol}_{days}"
    cached = EnhancedCache.get_cached_data(cache_key)
    if cached:
        return cached

    try:
        # Cloud SQLから最新予測を取得
        if ADVANCED_FEATURES:
            db_repo = StockDataRepository(db)
            predictions = db_repo.get_latest_predictions(symbol=symbol, limit=1)

            if predictions:
                latest_pred = predictions[0]
                result = {
                    "symbol": symbol,
                    "prediction": latest_pred,
                    "source": "cloud_sql_lstm",
                    "generated_at": datetime.now().isoformat(),
                }
                EnhancedCache.set_cached_data(cache_key, result)
                return result

        # フォールバック: リアルタイム簡易予測
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period="1mo")

        if hist.empty:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")

        # 簡易予測（移動平均ベース）
        current_price = hist["Close"].iloc[-1]
        ma_20 = hist["Close"].rolling(20).mean().iloc[-1]
        volatility = hist["Close"].pct_change().std()

        # 簡単な予測ロジック
        trend_factor = 1.02 if current_price > ma_20 else 0.98
        predicted_price = current_price * trend_factor

        result = {
            "symbol": symbol.upper(),
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted_price, 2),
            "prediction_days": days,
            "confidence_score": max(50, 100 - (volatility * 100)),
            "potential_return": round(
                (predicted_price - current_price) / current_price * 100, 2
            ),
            "risk_level": (
                "high"
                if volatility > 0.05
                else "medium" if volatility > 0.02 else "low"
            ),
            "source": "fallback_technical",
            "generated_at": datetime.now().isoformat(),
        }

        EnhancedCache.set_cached_data(cache_key, result)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating prediction for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate prediction")


@app.get("/api/finance/analysis/portfolio")
async def get_portfolio_analysis(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    # db: Optional[Session] = Depends(get_db) if ADVANCED_FEATURES else None
):
    """ポートフォリオ分析"""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    cache_key = f"portfolio_analysis_{'-'.join(symbol_list)}"

    cached = EnhancedCache.get_cached_data(cache_key)
    if cached:
        return cached

    try:
        portfolio_data = {}

        for symbol in symbol_list:
            try:
                # 個別株式データ取得
                if ADVANCED_FEATURES:
                    db_session = get_db()
                    db_repo = StockDataRepository(db_session)
                    df = db_repo.get_stock_prices(symbol)

                    if not df.empty:
                        returns = df["Close"].pct_change().dropna()
                        portfolio_data[symbol] = {
                            "current_price": df["Close"].iloc[-1],
                            "returns": returns.tolist()[-30:],  # 最近30日
                            "volatility": returns.std() * np.sqrt(252),
                            "data_points": len(df),
                        }
                        continue

                # フォールバック
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")

                if not hist.empty:
                    returns = hist["Close"].pct_change().dropna()
                    portfolio_data[symbol] = {
                        "current_price": hist["Close"].iloc[-1],
                        "returns": returns.tolist(),
                        "volatility": returns.std() * np.sqrt(252),
                        "data_points": len(hist),
                    }

            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                continue

        if not portfolio_data:
            raise HTTPException(status_code=404, detail="No valid symbols found")

        # ポートフォリオ分析計算
        all_returns = []
        weights = {}
        total_value = sum(data["current_price"] for data in portfolio_data.values())

        for symbol, data in portfolio_data.items():
            weights[symbol] = data["current_price"] / total_value
            all_returns.extend(data["returns"])

        portfolio_return = np.mean(all_returns) if all_returns else 0
        portfolio_volatility = np.std(all_returns) if all_returns else 0
        sharpe_ratio = (
            portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
        )

        # リスク評価
        var_95 = np.percentile(all_returns, 5) if all_returns else 0

        result = {
            "symbols": symbol_list,
            "portfolio_metrics": {
                "expected_return": round(portfolio_return * 252 * 100, 2),  # 年率%
                # 年率%
                "volatility": round(portfolio_volatility * np.sqrt(252) * 100, 2),
                "sharpe_ratio": round(sharpe_ratio * np.sqrt(252), 3),
                "var_95": round(var_95 * 100, 2),  # 95% VaR
            },
            "individual_weights": {k: round(v, 3) for k, v in weights.items()},
            "individual_metrics": {
                symbol: {
                    "price": round(data["current_price"], 2),
                    "volatility": round(data["volatility"] * 100, 2),
                    "weight": round(weights[symbol], 3),
                }
                for symbol, data in portfolio_data.items()
            },
            "analysis_date": datetime.now().isoformat(),
            "data_source": "cloud_sql" if ADVANCED_FEATURES else "yahoo_finance",
        }

        EnhancedCache.set_cached_data(cache_key, result, timeout=600)  # 10分キャッシュ
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio analysis error: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to perform portfolio analysis"
        )


@app.get("/api/finance/market-sentiment")
async def get_market_sentiment():
    """市場センチメント分析"""
    cache_key = "market_sentiment"
    cached = EnhancedCache.get_cached_data(cache_key)
    if cached:
        return cached

    try:
        # 主要指数のデータ取得
        indices = {"^GSPC": "SP500", "^IXIC": "NASDAQ", "^DJI": "DOW"}

        sentiment_data = {}
        overall_score = 0
        valid_indices = 0

        for index_symbol, index_name in indices.items():
            try:
                ticker = yf.Ticker(index_symbol)
                hist = ticker.history(period="1mo")

                if not hist.empty:
                    # 短期・長期トレンド分析
                    recent_return = (
                        hist["Close"].iloc[-1] - hist["Close"].iloc[-5]
                    ) / hist["Close"].iloc[-5]
                    month_return = (
                        hist["Close"].iloc[-1] - hist["Close"].iloc[0]
                    ) / hist["Close"].iloc[0]
                    volatility = hist["Close"].pct_change().std()

                    # センチメントスコア計算 (-100 to +100)
                    score = (
                        (recent_return * 100) + (month_return * 50) - (volatility * 100)
                    )
                    score = max(-100, min(100, score))

                    sentiment_data[index_name] = {
                        "score": round(score, 2),
                        "recent_return": round(recent_return * 100, 2),
                        "month_return": round(month_return * 100, 2),
                        "volatility": round(volatility * 100, 2),
                        "trend": (
                            "bullish"
                            if score > 10
                            else "bearish" if score < -10 else "neutral"
                        ),
                    }

                    overall_score += score
                    valid_indices += 1

            except Exception as e:
                logger.error(f"Error analyzing {index_name}: {e}")

        if valid_indices > 0:
            overall_score /= valid_indices

        # 全体的なセンチメント判定
        if overall_score > 20:
            overall_sentiment = "very_bullish"
        elif overall_score > 5:
            overall_sentiment = "bullish"
        elif overall_score > -5:
            overall_sentiment = "neutral"
        elif overall_score > -20:
            overall_sentiment = "bearish"
        else:
            overall_sentiment = "very_bearish"

        result = {
            "overall_sentiment": overall_sentiment,
            "overall_score": round(overall_score, 2),
            "indices_analysis": sentiment_data,
            "market_summary": {
                "bullish_indices": sum(
                    1 for data in sentiment_data.values() if data["trend"] == "bullish"
                ),
                "bearish_indices": sum(
                    1 for data in sentiment_data.values() if data["trend"] == "bearish"
                ),
                "neutral_indices": sum(
                    1 for data in sentiment_data.values() if data["trend"] == "neutral"
                ),
            },
            "analysis_time": datetime.now().isoformat(),
            "disclaimer": "This sentiment analysis is for informational purposes only",
        }

        EnhancedCache.set_cached_data(cache_key, result, timeout=900)  # 15分キャッシュ
        return result

    except Exception as e:
        logger.error(f"Market sentiment analysis error: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to analyze market sentiment"
        )


@app.post("/api/cache/invalidate")
async def invalidate_cache(pattern: Optional[str] = None):
    """キャッシュ無効化"""
    try:
        EnhancedCache.invalidate_cache(pattern)
        return {
            "message": "Cache invalidated successfully",
            "pattern": pattern or "all",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to invalidate cache")


# 既存のAPIエンドポイントも継承・拡張


@app.get("/api/finance/stocks/{symbol}/price")
async def get_stock_price_enhanced(
    symbol: str,
    period: str = Query("1mo", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$"),
    use_db: bool = Query(True),
    # db: Optional[Session] = Depends(get_db) if ADVANCED_FEATURES else None
):
    """株価履歴取得 - Cloud SQL統合版"""
    cache_key = f"price_enhanced_{symbol}_{period}_{use_db}"
    cached = EnhancedCache.get_cached_data(cache_key)
    if cached:
        return cached

    try:
        # Cloud SQLから取得を試行
        if ADVANCED_FEATURES and use_db:
            try:
                db_session = get_db()
                db_repo = StockDataRepository(db_session)
                df = db_repo.get_stock_prices(symbol.upper())

                if not df.empty:
                    # 期間フィルタリング
                    if period != "max":
                        days_map = {
                            "1d": 1,
                            "5d": 5,
                            "1mo": 30,
                            "3mo": 90,
                            "6mo": 180,
                            "1y": 365,
                            "2y": 730,
                            "5y": 1825,
                        }
                        days = days_map.get(period, 30)
                        df = df.tail(days)

                    price_data = []
                    for date, row in df.iterrows():
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
                        "source": "cloud_sql",
                    }

                    EnhancedCache.set_cached_data(cache_key, result)
                    return result

            except Exception as db_error:
                logger.error(f"Cloud SQL query failed for {symbol}: {db_error}")

        # フォールバック: Yahoo Finance
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
            "source": "yahoo_finance",
        }

        EnhancedCache.set_cached_data(cache_key, result)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock price")


@app.on_event("startup")
async def startup_event():
    """アプリ起動時の処理"""
    logger.info("Miraikakaku Enhanced API starting up...")
    logger.info(f"Advanced features enabled: {ADVANCED_FEATURES}")
    logger.info("Enhanced API is ready to serve requests")


@app.on_event("shutdown")
async def shutdown_event():
    """アプリ終了時の処理"""
    logger.info("Miraikakaku Enhanced API shutting down...")
    cache.clear()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting Enhanced Production API server on port {port}")
    uvicorn.run("enhanced_main:app", host="0.0.0.0", port=port, log_level="info")
