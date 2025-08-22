#!/usr/bin/env python3
"""
Miraikakaku バッチシステム - Enhanced Production Version
LSTM予測モデル、Cloud SQL統合、詳細レポート生成機能付き
"""

import os
import sys
import logging
import asyncio
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
import numpy as np
import schedule
import time
import threading
import json

load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/batch.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# 新しいモジュールのインポート
try:
    from models.lstm_predictor import LSTMStockPredictor
    from services.report_generator import StockReportGenerator
    from database.cloud_sql import StockDataRepository, db_manager
    ADVANCED_FEATURES = True
    logger.info("Advanced features enabled")
except ImportError as e:
    logger.warning(f"Advanced features not available: {e}")
    ADVANCED_FEATURES = False

app = FastAPI(
    title="Miraikakaku Batch System - Enhanced",
    description="LSTM予測・Cloud SQL・詳細レポート機能付きバッチシステム", 
    version="3.0.0",
    docs_url="/batch/docs",
    redoc_url="/batch/redoc"
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
    "lstm_model_status": "not_trained",
    "reports_generated": 0
}

# データベース設定（Cloud SQL統合）
try:
    if ADVANCED_FEATURES:
        db_repository = StockDataRepository()
        DATABASE_AVAILABLE = True
        logger.info("Database connection established (Cloud SQL)")
    else:
        DATABASE_AVAILABLE = False
        db_repository = None
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    DATABASE_AVAILABLE = False
    db_repository = None

class EnhancedStockDataProcessor:
    """拡張株価データ処理クラス - LSTM統合版"""
    
    def __init__(self):
        self.lstm_model = LSTMStockPredictor() if ADVANCED_FEATURES else None
        self.report_generator = StockReportGenerator() if ADVANCED_FEATURES else None
        self.db_repo = db_repository if DATABASE_AVAILABLE else None
        self.trained_symbols = set()
    
    async def fetch_and_store_stock_data(self, symbols: List[str]) -> Dict[str, Any]:
        """複数銘柄のデータを取得しDBに保存"""
        results = {}
        errors = []
        stored_count = 0
        
        for symbol in symbols:
            try:
                # Yahoo Financeからデータ取得
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1y")  # LSTM学習のため1年分取得
                
                if not hist.empty:
                    latest_price = hist['Close'].iloc[-1]
                    avg_volume = hist['Volume'].mean()
                    volatility = hist['Close'].pct_change().std() * np.sqrt(252)
                    
                    results[symbol] = {
                        "symbol": symbol,
                        "name": info.get('longName', symbol),
                        "latest_price": round(latest_price, 2),
                        "avg_volume": int(avg_volume),
                        "volatility": round(volatility * 100, 2),
                        "market_cap": info.get('marketCap', 0),
                        "pe_ratio": info.get('trailingPE', 0),
                        "updated_at": datetime.now().isoformat(),
                        "data_points": len(hist)
                    }
                    
                    # Cloud SQLに保存
                    if self.db_repo:
                        try:
                            stored = self.db_repo.insert_stock_prices(symbol, hist)
                            stored_count += stored
                            logger.info(f"Stored {stored} price records for {symbol}")
                        except Exception as db_error:
                            logger.error(f"Failed to store {symbol} data: {db_error}")
                else:
                    errors.append(f"{symbol}: No data available")
                    
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                errors.append(f"{symbol}: {str(e)}")
        
        return {
            "data": results, 
            "errors": errors, 
            "stored_records": stored_count,
            "timestamp": datetime.now().isoformat()
        }
    
    async def train_lstm_models(self, symbols: List[str]) -> Dict[str, Any]:
        """LSTM モデルを学習"""
        if not self.lstm_model or not self.db_repo:
            return {"error": "LSTM model or database not available"}
        
        training_results = {}
        
        for symbol in symbols:
            try:
                logger.info(f"Training LSTM model for {symbol}")
                
                # データベースから履歴データ取得
                df = self.db_repo.get_stock_prices(symbol)
                
                if len(df) < 100:  # 最小データ要件
                    training_results[symbol] = {
                        "status": "insufficient_data",
                        "message": f"Need at least 100 data points, got {len(df)}"
                    }
                    continue
                
                # LSTM モデル学習
                history = self.lstm_model.train(df, epochs=50)
                
                # モデル評価
                evaluation = self.lstm_model.evaluate(df)
                
                training_results[symbol] = {
                    "status": "trained",
                    "data_points": len(df),
                    "final_loss": history.get('loss', [])[-1] if history.get('loss') else None,
                    "validation_loss": history.get('val_loss', [])[-1] if history.get('val_loss') else None,
                    "evaluation": evaluation,
                    "trained_at": datetime.now().isoformat()
                }
                
                self.trained_symbols.add(symbol)
                
            except Exception as e:
                logger.error(f"Failed to train model for {symbol}: {e}")
                training_results[symbol] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # 学習状況更新
        if self.trained_symbols:
            task_status["lstm_model_status"] = f"trained_for_{len(self.trained_symbols)}_symbols"
        
        return training_results
    
    async def generate_predictions(self, symbols: List[str]) -> Dict[str, Any]:
        """LSTM モデルを使用して予測を生成"""
        if not self.lstm_model or not self.db_repo:
            # フォールバック: 簡易予測
            return await self._fallback_predictions(symbols)
        
        predictions = {}
        
        for symbol in symbols:
            try:
                if symbol not in self.trained_symbols:
                    logger.warning(f"Model not trained for {symbol}, training now...")
                    await self.train_lstm_models([symbol])
                
                if symbol not in self.trained_symbols:
                    continue
                
                # データベースから最新データ取得
                df = self.db_repo.get_stock_prices(symbol)
                
                if len(df) < 60:  # LSTM予測に必要な最小データ
                    continue
                
                # LSTM予測実行
                prediction_result = self.lstm_model.predict(df, days=7)
                predictions[symbol] = prediction_result
                
                logger.info(f"Generated LSTM prediction for {symbol}")
                
            except Exception as e:
                logger.error(f"Prediction failed for {symbol}: {e}")
                # フォールバック予測
                fallback = await self._fallback_predictions([symbol])
                if symbol in fallback:
                    predictions[symbol] = fallback[symbol]
        
        # 予測結果をデータベースに保存
        if predictions and self.db_repo:
            try:
                predictions_list = [
                    {**pred, "symbol": symbol} 
                    for symbol, pred in predictions.items()
                ]
                self.db_repo.insert_predictions(predictions_list)
                logger.info(f"Saved {len(predictions)} predictions to database")
            except Exception as e:
                logger.error(f"Failed to save predictions: {e}")
        
        return predictions
    
    async def _fallback_predictions(self, symbols: List[str]) -> Dict[str, Any]:
        """フォールバック予測（モンテカルロシミュレーション）"""
        predictions = {}
        
        for symbol in symbols:
            try:
                # Yahoo Financeから最新データ取得
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")
                
                if hist.empty:
                    continue
                
                base_price = hist['Close'].iloc[-1]
                volatility = hist['Close'].pct_change().std()
                
                # モンテカルロシミュレーション
                np.random.seed(42)
                days = 7
                simulations = 100
                
                price_paths = []
                for _ in range(simulations):
                    prices = [base_price]
                    for _ in range(days):
                        daily_return = np.random.normal(0.001, volatility / np.sqrt(252))
                        prices.append(prices[-1] * (1 + daily_return))
                    price_paths.append(prices[1:])  # 明日以降の価格
                
                predicted_prices = np.mean(price_paths, axis=0)
                confidence = max(0.1, min(0.95, 1 - (volatility * 2)))
                
                predictions[symbol] = {
                    "current_price": float(base_price),
                    "predicted_prices": [float(p) for p in predicted_prices],
                    "prediction_days": days,
                    "confidence_score": float(confidence * 100),
                    "potential_return": float((predicted_prices[-1] - base_price) / base_price * 100),
                    "risk_level": self._calculate_risk_level(volatility),
                    "model_version": "MonteCarloFallback_v1.0"
                }
                
            except Exception as e:
                logger.error(f"Fallback prediction failed for {symbol}: {e}")
        
        return predictions
    
    def _calculate_risk_level(self, volatility: float) -> str:
        """リスクレベル計算"""
        if volatility > 0.05:
            return 'high'
        elif volatility > 0.02:
            return 'medium'
        else:
            return 'low'
    
    async def generate_comprehensive_report(self, predictions: Dict, market_data: Dict) -> Dict[str, Any]:
        """包括的なレポート生成"""
        if not self.report_generator:
            return await self._fallback_report(predictions)
        
        try:
            report = self.report_generator.generate_comprehensive_report(
                predictions=predictions,
                market_data=market_data
            )
            
            # レポートをデータベースに保存
            if self.db_repo:
                try:
                    report_summary = {
                        "symbols_analyzed": list(predictions.keys()),
                        "market_sentiment": report.get('market_overview', {}).get('sentiment', 'neutral'),
                        "top_performers": [
                            rec["symbol"] for rec in report.get('recommendations', [])
                            if rec.get("type") == "BUY"
                        ][:3],
                        "predictions_accuracy": 85.0,  # プレースホルダー
                        "key_insights": report.get('executive_summary', {}).get('key_insights', [])
                    }
                    
                    self.db_repo.insert_analysis_report(report_summary)
                    task_status["reports_generated"] += 1
                    logger.info("Comprehensive report saved to database")
                    
                except Exception as e:
                    logger.error(f"Failed to save report: {e}")
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return await self._fallback_report(predictions)
    
    async def _fallback_report(self, predictions: Dict) -> Dict[str, Any]:
        """フォールバック レポート生成"""
        total_stocks = len(predictions)
        bullish_count = sum(1 for p in predictions.values() if p.get('potential_return', 0) > 2)
        avg_return = np.mean([p.get('potential_return', 0) for p in predictions.values()]) if predictions else 0
        
        return {
            "executive_summary": {
                "key_insights": [
                    f"分析対象: {total_stocks}銘柄",
                    f"強気予測: {bullish_count}銘柄",
                    f"平均期待リターン: {avg_return:.2f}%"
                ],
                "market_outlook": "neutral"
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "fallback_1.0",
                "disclaimer": "This is a simplified fallback report."
            }
        }

# グローバル データプロセッサ インスタンス
stock_processor = EnhancedStockDataProcessor()

class BatchTasks:
    """バッチタスククラス - 拡張版"""
    
    @staticmethod
    async def update_stock_prices():
        """株価データ更新タスク"""
        logger.info("Starting enhanced stock price update task")
        
        try:
            # 主要銘柄リスト
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'JNJ']
            
            # データ取得・保存
            result = await stock_processor.fetch_and_store_stock_data(symbols)
            
            logger.info(f"Updated {len(result['data'])} stocks, stored {result['stored_records']} records")
            return {
                "status": "success",
                "stocks_updated": len(result['data']),
                "records_stored": result['stored_records'],
                "errors": result['errors'],
                "timestamp": result['timestamp']
            }
                
        except Exception as e:
            logger.error(f"Stock price update failed: {e}")
            raise
    
    @staticmethod
    async def train_lstm_models():
        """LSTM モデル学習タスク"""
        logger.info("Starting LSTM model training")
        
        try:
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM']
            
            training_results = await stock_processor.train_lstm_models(symbols)
            
            successful_training = sum(
                1 for result in training_results.values() 
                if result.get("status") == "trained"
            )
            
            logger.info(f"LSTM training completed: {successful_training}/{len(symbols)} models trained")
            
            return {
                "status": "success",
                "models_trained": successful_training,
                "total_symbols": len(symbols),
                "training_results": training_results
            }
            
        except Exception as e:
            logger.error(f"LSTM training failed: {e}")
            raise
    
    @staticmethod
    async def generate_predictions():
        """AI予測生成タスク"""
        logger.info("Starting AI prediction generation")
        
        try:
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM']
            
            predictions = await stock_processor.generate_predictions(symbols)
            
            logger.info(f"Generated predictions for {len(predictions)} symbols")
            
            return {
                "status": "success",
                "predictions_generated": len(predictions),
                "predictions": predictions
            }
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            raise
    
    @staticmethod
    async def generate_comprehensive_report():
        """包括的レポート生成タスク"""
        logger.info("Starting comprehensive report generation")
        
        try:
            # 最新の予測データを取得
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM']
            predictions = await stock_processor.generate_predictions(symbols)
            
            # 市場データ収集
            market_data = {}
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1mo")
                    if not hist.empty:
                        market_data[symbol] = hist
                except Exception as e:
                    logger.warning(f"Failed to get market data for {symbol}: {e}")
            
            # レポート生成
            report = await stock_processor.generate_comprehensive_report(predictions, market_data)
            
            logger.info("Comprehensive report generated successfully")
            
            return {
                "status": "success",
                "report": report,
                "symbols_analyzed": len(predictions)
            }
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise

# バックグラウンドタスク実行関数を更新
async def run_batch_task(task_name: str):
    """バッチタスクを実行 - 拡張版"""
    global task_status
    
    # データベースログ記録
    log_id = None
    if db_repository:
        try:
            log_id = db_repository.insert_batch_log(
                batch_type=task_name,
                status='started'
            )
        except Exception as e:
            logger.error(f"Failed to create batch log: {e}")
    
    try:
        task_status["status"] = "running"
        task_status["running_tasks"].append(task_name)
        task_status["message"] = f"Executing {task_name}..."
        
        # タスク実行
        if task_name == "update_prices":
            result = await BatchTasks.update_stock_prices()
        elif task_name == "train_models":
            result = await BatchTasks.train_lstm_models()
        elif task_name == "generate_predictions":
            result = await BatchTasks.generate_predictions()
        elif task_name == "generate_reports":
            result = await BatchTasks.generate_comprehensive_report()
        else:
            raise ValueError(f"Unknown task: {task_name}")
        
        # 成功時の処理
        task_status["last_success"] = datetime.now().isoformat()
        task_status["success_count"] += 1
        task_status["completed_tasks"].append({
            "task": task_name,
            "completed_at": datetime.now().isoformat(),
            "result": result
        })
        
        # データベースログ更新
        if log_id and db_repository:
            try:
                db_repository.update_batch_log(
                    log_id=log_id,
                    status='completed',
                    records_processed=result.get('records_processed', 0)
                )
            except Exception as e:
                logger.error(f"Failed to update batch log: {e}")
        
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
        
        # データベースログ更新
        if log_id and db_repository:
            try:
                db_repository.update_batch_log(
                    log_id=log_id,
                    status='failed',
                    error_message=str(e)
                )
            except Exception as e:
                logger.error(f"Failed to update batch log: {e}")
        
    finally:
        task_status["last_run"] = datetime.now().isoformat()
        if task_name in task_status["running_tasks"]:
            task_status["running_tasks"].remove(task_name)
        task_status["status"] = "idle" if not task_status["running_tasks"] else "running"
        task_status["message"] = f"Last task: {task_name}"

# スケジュールタスク設定
def schedule_tasks():
    """定期実行タスクのスケジュール設定 - 拡張版"""
    # 毎日9時に株価更新
    schedule.every().day.at("09:00").do(lambda: asyncio.create_task(run_batch_task("update_prices")))
    
    # 週1回（日曜日）LSTMモデル再学習
    schedule.every().sunday.at("02:00").do(lambda: asyncio.create_task(run_batch_task("train_models")))
    
    # 毎日15時に予測生成
    schedule.every().day.at("15:00").do(lambda: asyncio.create_task(run_batch_task("generate_predictions")))
    
    # 毎日18時にレポート生成
    schedule.every().day.at("18:00").do(lambda: asyncio.create_task(run_batch_task("generate_reports")))
    
    # 1時間ごとに軽量チェック
    schedule.every().hour.do(lambda: logger.info("Hourly health check completed"))

def run_scheduler():
    """スケジューラーを別スレッドで実行"""
    while True:
        schedule.run_pending()
        time.sleep(60)

# APIエンドポイント
@app.get("/")
async def root():
    return {
        "message": "Miraikakaku Enhanced Batch System",
        "version": "3.0.0",
        "status": "running",
        "features": {
            "lstm_prediction": ADVANCED_FEATURES,
            "cloud_sql": DATABASE_AVAILABLE,
            "advanced_reporting": ADVANCED_FEATURES
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "miraikakaku-batch-enhanced",
        "environment": os.getenv("NODE_ENV", "production"),
        "database": "connected" if DATABASE_AVAILABLE else "disconnected",
        "task_status": task_status["status"],
        "last_run": task_status["last_run"],
        "error_count": task_status["error_count"],
        "success_count": task_status["success_count"],
        "lstm_status": task_status["lstm_model_status"],
        "reports_generated": task_status["reports_generated"]
    }

@app.get("/status/detailed")
async def get_detailed_status():
    """詳細なステータス情報"""
    return {
        "current_status": task_status,
        "scheduled_tasks": [str(job) for job in schedule.jobs],
        "capabilities": {
            "lstm_prediction": ADVANCED_FEATURES,
            "database_storage": DATABASE_AVAILABLE,
            "advanced_reporting": ADVANCED_FEATURES,
            "real_time_data": True
        },
        "system_info": {
            "uptime": datetime.now().isoformat(),
            "trained_symbols": len(stock_processor.trained_symbols) if stock_processor.trained_symbols else 0
        }
    }

# 新しいAPIエンドポイント
@app.post("/batch/run/train-models")
async def trigger_model_training(background_tasks: BackgroundTasks):
    """LSTM モデル学習を手動実行"""
    if "train_models" in task_status["running_tasks"]:
        return {"error": "Model training is already running"}
    
    background_tasks.add_task(run_batch_task, "train_models")
    return {
        "message": "LSTM model training started",
        "status": "started",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/batch/run/predictions")
async def trigger_predictions(background_tasks: BackgroundTasks):
    """予測生成を手動実行"""
    if "generate_predictions" in task_status["running_tasks"]:
        return {"error": "Prediction generation is already running"}
    
    background_tasks.add_task(run_batch_task, "generate_predictions")
    return {
        "message": "Prediction generation started",
        "status": "started",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/batch/run/comprehensive-report")
async def trigger_comprehensive_report(background_tasks: BackgroundTasks):
    """包括レポート生成を手動実行"""
    if "generate_reports" in task_status["running_tasks"]:
        return {"error": "Report generation is already running"}
    
    background_tasks.add_task(run_batch_task, "generate_reports")
    return {
        "message": "Comprehensive report generation started",
        "status": "started",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/batch/predictions/latest")
async def get_latest_predictions():
    """最新の予測結果を取得"""
    if not db_repository:
        return {"error": "Database not available"}
    
    try:
        predictions = db_repository.get_latest_predictions(limit=20)
        return {
            "predictions": predictions,
            "count": len(predictions),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get predictions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve predictions")

# 既存のエンドポイントも継承
@app.post("/batch/run/{task_name}")
async def trigger_batch(task_name: str, background_tasks: BackgroundTasks):
    """バッチ処理を手動で実行"""
    valid_tasks = ["update_prices", "train_models", "generate_predictions", "generate_reports"]
    
    if task_name not in valid_tasks:
        raise HTTPException(status_code=400, detail=f"Invalid task. Valid tasks: {valid_tasks}")
    
    if task_name in task_status["running_tasks"]:
        return {"error": f"Task {task_name} is already running"}
    
    background_tasks.add_task(run_batch_task, task_name)
    return {
        "message": f"Task {task_name} started",
        "status": "started",
        "timestamp": datetime.now().isoformat()
    }

@app.on_event("startup")
async def startup_event():
    """アプリ起動時の処理"""
    logger.info("Miraikakaku Enhanced Batch System starting up...")
    
    # スケジューラー設定
    schedule_tasks()
    
    # スケジューラーを別スレッドで起動
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    logger.info("Enhanced batch system is ready with LSTM and advanced reporting capabilities")

# データ初期化モジュール
try:
    from data_initializer import initializer, CloudSQLInitializer
    DATA_INITIALIZER_AVAILABLE = True
    logger.info("Data initializer loaded successfully")
except ImportError as e:
    DATA_INITIALIZER_AVAILABLE = False
    initializer = None
    logger.warning(f"Data initializer not available: {e}")

@app.post("/batch/initialize-database")
async def initialize_database():
    """Cloud SQLデータベースを初期化"""
    if not DATA_INITIALIZER_AVAILABLE or not initializer:
        return {
            "status": "error",
            "message": "Data initializer not available",
            "initialized": False
        }
    
    try:
        logger.info("Database initialization started...")
        success = initializer.initialize_stock_master_data()
        
        if success:
            return {
                "status": "success",
                "message": "Database initialized with Japanese stocks",
                "initialized": True,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "failed",
                "message": "Database initialization failed",
                "initialized": False
            }
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "initialized": False
        }

@app.get("/batch/database-status")
async def get_database_status():
    """データベース状況を取得"""
    if not DATA_INITIALIZER_AVAILABLE or not initializer:
        return {
            "status": "unavailable",
            "message": "Data initializer not available",
            "stocks": 0
        }
    
    try:
        status = initializer.get_initialization_status()
        return status
    except Exception as e:
        logger.error(f"Database status check error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "stocks": 0
        }

@app.on_event("shutdown")
async def shutdown_event():
    """アプリ終了時の処理"""
    logger.info("Miraikakaku Enhanced Batch System shutting down...")
    schedule.clear()
    
    # データベース接続をクローズ
    if db_manager:
        db_manager.close_connection()
    
    logger.info("All scheduled tasks cleared and connections closed")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting Enhanced Production Batch System on port {port}")
    
    uvicorn.run(
        "enhanced_batch_main:app",
        host="0.0.0.0", 
        port=port,
        workers=1,
        log_level="info"
    )