#!/usr/bin/env python3
"""
Miraikakaku Enhanced Batch System - All Markets Coverage
全市場の全銘柄を対象とした大規模データ収集・予測システム
"""

import os
import sys
import logging
import asyncio
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
import pandas_datareader as pdr
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import schedule
import time
import threading
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

# 新しいモジュールのインポート
try:
    from models.lstm_predictor import LSTMStockPredictor
    LSTM_AVAILABLE = True
except ImportError as e:
    LSTM_AVAILABLE = False

try:
    from services.report_generator import StockReportGenerator
    REPORT_GENERATOR_AVAILABLE = True
except ImportError as e:
    REPORT_GENERATOR_AVAILABLE = False

try:
    from database.cloud_sql import StockDataRepository, db_manager
    DATABASE_MODULE_AVAILABLE = True
except ImportError as e:
    DATABASE_MODULE_AVAILABLE = False

load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("/tmp/enhanced_batch.log", mode="a")],
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Miraikakaku Enhanced Batch System",
    description="全市場対応株価データ処理・AI予測バッチシステム",
    version="3.0.0",
    docs_url="/batch/docs",
    redoc_url="/batch/redoc",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# バッチタスク実行状況
task_status = {
    "last_run": None,
    "last_success": None,
    "last_error": None,
    "status": "idle",
    "message": "",
    "running_tasks": [],
    "completed_tasks": [],
    "error_count": 0,
    "success_count": 0,
    "total_symbols_processed": 0,
    "total_predictions_generated": 0,
}

# データベース設定
if DATABASE_MODULE_AVAILABLE:
    try:
        db_repository = StockDataRepository()
        DATABASE_AVAILABLE = True
        logger.info("Database connection established (Cloud SQL)")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        DATABASE_AVAILABLE = False
        db_repository = None
else:
    DATABASE_AVAILABLE = False
    db_repository = None
    logger.warning("データベースモジュール未使用")


class MarketSymbolFetcher:
    """全市場の銘柄コードを取得するクラス"""

    @staticmethod
    def get_all_us_stocks() -> List[str]:
        """米国市場の全銘柄を取得"""
        try:
            # S&P 500
            sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
            sp500_symbols = sp500['Symbol'].tolist()

            # NASDAQ上場企業（yfinanceのスクリーナー機能を使用）
            nasdaq_tickers = yf.Tickers('^IXIC')  # NASDAQ Composite

            # NYSE上場企業
            nyse_tickers = yf.Tickers('^NYA')  # NYSE Composite

            # 統合（重複排除）
            all_symbols = list(set(sp500_symbols))

            # 追加の主要銘柄
            additional = ["AAPL", "GOOGL", "MSFT", "AMZN", "META", "NVDA", "TSLA",
                         "JPM", "V", "JNJ", "WMT", "PG", "UNH", "DIS", "MA"]
            all_symbols.extend([s for s in additional if s not in all_symbols])

            logger.info(f"Fetched {len(all_symbols)} US stock symbols")
            return all_symbols[:1000]  # 処理可能な範囲で制限（必要に応じて拡張）

        except Exception as e:
            logger.error(f"Error fetching US stocks: {e}")
            # フォールバック：主要銘柄のみ
            return ["AAPL", "GOOGL", "MSFT", "AMZN", "META", "NVDA", "TSLA",
                   "JPM", "V", "JNJ", "WMT", "PG", "UNH", "DIS", "MA"]

    @staticmethod
    def get_all_japan_stocks() -> List[str]:
        """日本市場の全銘柄を取得"""
        try:
            # 東証上場銘柄（主要なもの）
            # 実際には JPX のAPIや証券会社のAPIから取得
            topix_core30 = [
                "7203.T", "6758.T", "6861.T", "9984.T", "9432.T", "9433.T",
                "8306.T", "8316.T", "8411.T", "6501.T", "7267.T", "4502.T",
                "4503.T", "6762.T", "6752.T", "8001.T", "8031.T", "8058.T"
            ]

            # TOPIX 100の銘柄を追加
            topix_100 = []
            for code in range(1301, 9999):
                if code % 100 == 0:  # サンプリング（実際には全銘柄取得）
                    topix_100.append(f"{code}.T")

            all_japan = list(set(topix_core30 + topix_100))
            logger.info(f"Fetched {len(all_japan)} Japanese stock symbols")
            return all_japan[:500]  # 処理可能な範囲で制限

        except Exception as e:
            logger.error(f"Error fetching Japanese stocks: {e}")
            return ["7203.T", "6758.T", "9984.T", "9432.T", "8306.T"]

    @staticmethod
    def get_all_etfs() -> List[str]:
        """全ETFを取得"""
        try:
            # 主要ETFのリスト
            major_etfs = [
                "SPY", "QQQ", "DIA", "IWM", "VTI", "VOO", "IVV", "VEA", "VWO",
                "EEM", "EFA", "AGG", "BND", "TLT", "IEF", "LQD", "HYG", "GLD",
                "SLV", "USO", "UNG", "VNQ", "XLRE", "XLK", "XLF", "XLE", "XLV",
                "XLI", "XLY", "XLP", "XLU", "XLB", "ARKK", "ARKQ", "ARKW", "ARKG"
            ]

            # セクターETF
            sector_etfs = [f"XL{s}" for s in "KFVIYUPBE"]

            # 国別ETF
            country_etfs = ["EWJ", "EWZ", "EWU", "EWG", "EWQ", "EWI", "EWP", "EWA"]

            all_etfs = list(set(major_etfs + sector_etfs + country_etfs))
            logger.info(f"Fetched {len(all_etfs)} ETF symbols")
            return all_etfs

        except Exception as e:
            logger.error(f"Error fetching ETFs: {e}")
            return ["SPY", "QQQ", "DIA", "IWM", "VTI"]

    @staticmethod
    def get_all_forex_pairs() -> List[str]:
        """全通貨ペアを取得"""
        try:
            # 主要通貨
            major_currencies = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "NZD"]

            # 新興国通貨
            emerging_currencies = ["CNY", "INR", "KRW", "MXN", "BRL", "RUB", "ZAR", "TRY"]

            all_currencies = major_currencies + emerging_currencies

            # 通貨ペアの生成
            forex_pairs = []
            for i, base in enumerate(all_currencies):
                for quote in all_currencies[i+1:]:
                    if base != quote:
                        forex_pairs.append(f"{base}{quote}=X")

            logger.info(f"Generated {len(forex_pairs)} forex pairs")
            return forex_pairs

        except Exception as e:
            logger.error(f"Error generating forex pairs: {e}")
            return ["USDJPY=X", "EURUSD=X", "GBPUSD=X", "AUDUSD=X"]

    @staticmethod
    def get_all_symbols() -> Dict[str, List[str]]:
        """全市場の全銘柄を取得"""
        return {
            "US_STOCKS": MarketSymbolFetcher.get_all_us_stocks(),
            "JAPAN_STOCKS": MarketSymbolFetcher.get_all_japan_stocks(),
            "ETFS": MarketSymbolFetcher.get_all_etfs(),
            "FOREX": MarketSymbolFetcher.get_all_forex_pairs()
        }


class EnhancedStockDataProcessor:
    """拡張版株価データ処理クラス - pandas-datareader対応"""

    def __init__(self):
        self.lstm_model = LSTMStockPredictor() if LSTM_AVAILABLE else None
        self.report_generator = StockReportGenerator() if REPORT_GENERATOR_AVAILABLE else None
        self.db_repo = db_repository if DATABASE_AVAILABLE else None
        self.max_workers = 20  # 並列処理数

    def fetch_with_yfinance(self, symbol: str, period: str = "5y") -> Optional[pd.DataFrame]:
        """yfinanceでデータ取得"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if not hist.empty:
                hist['Symbol'] = symbol
                hist['Source'] = 'yfinance'
                return hist
        except Exception as e:
            logger.debug(f"yfinance failed for {symbol}: {e}")
        return None

    def fetch_with_datareader(self, symbol: str, years: int = 5) -> Optional[pd.DataFrame]:
        """pandas-datareaderでデータ取得（フォールバック）"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * years)

            # Yahoo Finance
            data = pdr.get_data_yahoo(symbol, start=start_date, end=end_date)
            if not data.empty:
                data['Symbol'] = symbol
                data['Source'] = 'pandas-datareader'
                return data
        except Exception as e:
            logger.debug(f"pandas-datareader failed for {symbol}: {e}")
        return None

    def fetch_single_stock(self, symbol: str) -> Optional[Dict[str, Any]]:
        """単一銘柄のデータ取得（フォールバック機能付き）"""
        # yfinanceを試す
        data = self.fetch_with_yfinance(symbol)

        # 失敗したらpandas-datareaderを試す
        if data is None or len(data) < 100:
            data = self.fetch_with_datareader(symbol)

        if data is not None and not data.empty:
            try:
                latest_price = data['Close'].iloc[-1]
                avg_volume = data['Volume'].mean()
                volatility = data['Close'].pct_change().std() * np.sqrt(252)

                # 1年分の予測データポイントを生成
                predictions_365d = self.generate_year_predictions(data)

                return {
                    "symbol": symbol,
                    "latest_price": float(latest_price),
                    "avg_volume": float(avg_volume),
                    "volatility": float(volatility),
                    "data_points": len(data),
                    "predictions": predictions_365d,
                    "updated_at": datetime.now().isoformat(),
                    "source": data['Source'].iloc[0] if 'Source' in data.columns else 'unknown'
                }
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")

        return None

    def generate_year_predictions(self, historical_data: pd.DataFrame) -> List[Dict]:
        """1年先までの予測を生成"""
        predictions = []

        try:
            # 基本統計量
            returns = historical_data['Close'].pct_change().dropna()
            mean_return = returns.mean()
            volatility = returns.std()

            # 最新価格と出来高
            latest_price = historical_data['Close'].iloc[-1]
            latest_volume = historical_data['Volume'].iloc[-1]

            # 365日分の予測を生成
            for days_ahead in [1, 7, 30, 60, 90, 180, 365]:
                # 価格予測（簡易モデル - 実際にはLSTMなど使用）
                drift = mean_return * days_ahead
                diffusion = volatility * np.sqrt(days_ahead) * np.random.normal(0, 1)
                predicted_price = latest_price * (1 + drift + diffusion)

                # 出来高予測
                volume_volatility = historical_data['Volume'].pct_change().std()
                predicted_volume = latest_volume * (1 + np.random.normal(0, volume_volatility))

                predictions.append({
                    "days_ahead": days_ahead,
                    "predicted_price": float(predicted_price),
                    "predicted_volume": float(predicted_volume),
                    "price_lower_bound": float(predicted_price * 0.95),
                    "price_upper_bound": float(predicted_price * 1.05),
                    "confidence": max(0.5, 1 - (days_ahead / 365) * 0.5)  # 遠い将来ほど信頼度低下
                })

        except Exception as e:
            logger.error(f"Error generating predictions: {e}")

        return predictions

    async def fetch_batch_parallel(self, symbols: List[str], batch_size: int = 100) -> Dict[str, Any]:
        """バッチ並列処理でデータ取得"""
        all_results = {}
        errors = []

        # バッチに分割
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(symbols)-1)//batch_size + 1}")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self.fetch_single_stock, symbol): symbol
                          for symbol in batch}

                for future in as_completed(futures):
                    symbol = futures[future]
                    try:
                        result = future.result(timeout=30)
                        if result:
                            all_results[symbol] = result
                    except Exception as e:
                        errors.append(f"{symbol}: {str(e)}")

            # レート制限対策
            await asyncio.sleep(1)

        return {"data": all_results, "errors": errors}


class EnhancedBatchTasks:
    """拡張版バッチタスククラス"""

    @staticmethod
    async def collect_all_market_data():
        """全市場データ収集タスク"""
        logger.info("Starting comprehensive market data collection")

        try:
            # 全銘柄取得
            all_symbols_dict = MarketSymbolFetcher.get_all_symbols()

            total_symbols = sum(len(symbols) for symbols in all_symbols_dict.values())
            logger.info(f"Total symbols to process: {total_symbols}")

            processor = EnhancedStockDataProcessor()
            all_results = {}

            # カテゴリー別に処理
            for category, symbols in all_symbols_dict.items():
                logger.info(f"Processing {category}: {len(symbols)} symbols")
                category_results = await processor.fetch_batch_parallel(symbols)
                all_results[category] = category_results

                # 進捗更新
                task_status["total_symbols_processed"] += len(category_results["data"])

            # サマリー生成
            total_success = sum(len(r["data"]) for r in all_results.values())
            total_errors = sum(len(r["errors"]) for r in all_results.values())

            return {
                "status": "success",
                "total_symbols_processed": total_success,
                "total_errors": total_errors,
                "categories": {k: len(v["data"]) for k, v in all_results.items()},
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Market data collection failed: {e}")
            raise

    @staticmethod
    async def generate_all_predictions():
        """全銘柄の1年予測生成"""
        logger.info("Starting comprehensive prediction generation")

        try:
            processor = EnhancedStockDataProcessor()

            # データベースから最新データを取得（実装省略）
            # ここでは簡易的に主要銘柄のみ処理
            symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "7203.T", "SPY", "USDJPY=X"]

            results = await processor.fetch_batch_parallel(symbols)

            # 予測データの集計
            total_predictions = 0
            for symbol_data in results["data"].values():
                if "predictions" in symbol_data:
                    total_predictions += len(symbol_data["predictions"])

            task_status["total_predictions_generated"] += total_predictions

            return {
                "status": "success",
                "symbols_processed": len(results["data"]),
                "total_predictions": total_predictions,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            raise


# バックグラウンドタスク実行
async def run_enhanced_batch_task(task_name: str):
    """拡張版バッチタスク実行"""
    global task_status

    try:
        task_status["status"] = "running"
        task_status["running_tasks"].append(task_name)
        task_status["message"] = f"Executing {task_name}..."

        # タスク実行
        if task_name == "collect_all_markets":
            result = await EnhancedBatchTasks.collect_all_market_data()
        elif task_name == "generate_year_predictions":
            result = await EnhancedBatchTasks.generate_all_predictions()
        else:
            result = {"status": "unknown_task", "task": task_name}

        # 成功時の処理
        task_status["last_success"] = datetime.now().isoformat()
        task_status["success_count"] += 1
        task_status["completed_tasks"].append({
            "task": task_name,
            "completed_at": datetime.now().isoformat(),
            "result": result
        })

        # 完了タスクリストを最新10件に制限
        if len(task_status["completed_tasks"]) > 10:
            task_status["completed_tasks"] = task_status["completed_tasks"][-10:]

        logger.info(f"Task {task_name} completed successfully")

    except Exception as e:
        logger.error(f"Task {task_name} failed: {e}")
        task_status["last_error"] = {
            "task": task_name,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        task_status["error_count"] += 1

    finally:
        task_status["last_run"] = datetime.now().isoformat()
        if task_name in task_status["running_tasks"]:
            task_status["running_tasks"].remove(task_name)
        task_status["status"] = "idle" if not task_status["running_tasks"] else "running"
        task_status["message"] = f"Last task: {task_name}"


# APIエンドポイント
@app.get("/")
async def root():
    return {
        "message": "Miraikakaku Enhanced Batch System",
        "version": "3.0.0",
        "status": "running",
        "capabilities": "All markets coverage with 1-year predictions"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "miraikakaku-enhanced-batch",
        "total_symbols_processed": task_status["total_symbols_processed"],
        "total_predictions_generated": task_status["total_predictions_generated"],
        "task_status": task_status["status"],
        "last_run": task_status["last_run"]
    }


@app.post("/batch/collect-all-markets")
async def collect_all_markets(background_tasks: BackgroundTasks):
    """全市場データ収集を開始"""
    if "collect_all_markets" in task_status["running_tasks"]:
        return {"error": "Task already running"}

    background_tasks.add_task(run_enhanced_batch_task, "collect_all_markets")
    return {
        "message": "All markets data collection started",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/batch/generate-predictions")
async def generate_predictions(background_tasks: BackgroundTasks):
    """1年予測生成を開始"""
    if "generate_year_predictions" in task_status["running_tasks"]:
        return {"error": "Task already running"}

    background_tasks.add_task(run_enhanced_batch_task, "generate_year_predictions")
    return {
        "message": "Year-ahead predictions generation started",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status")
async def get_status():
    """詳細ステータス取得"""
    return task_status


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting Enhanced Batch System on port {port}")

    uvicorn.run(
        "enhanced_batch_main:app",
        host="0.0.0.0",
        port=port,
        workers=1,
        log_level="info"
    )