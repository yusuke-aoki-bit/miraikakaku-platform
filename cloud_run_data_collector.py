#!/usr/bin/env python3
"""
Cloud Run データ収集サービス - GCP Batch代替システム
高可用性・低レイテンシでのデータ収集実行
"""

import os
import asyncio
import aiohttp
import psycopg2
import psycopg2.extras
import yfinance as yf
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
from dataclasses import dataclass
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CloudRun-DataCollector - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CollectionTask:
    task_id: str
    symbols: List[str]
    priority: str
    start_time: datetime
    status: str = "pending"

class CollectionRequest(BaseModel):
    mode: str = "standard"  # standard, priority, full
    symbols: Optional[List[str]] = None
    days_back: int = 30

class CloudRunDataCollector:
    def __init__(self):
        self.db_config = {
            "host": os.getenv("DB_HOST", "34.173.9.214"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "os.getenv('DB_PASSWORD', '')"),
            "database": os.getenv("DB_NAME", "miraikakaku"),
            "port": int(os.getenv("DB_PORT", "5432"))
        }

        # Rate limiting configuration
        self.api_limits = {
            "yahoo_finance": {
                "requests_per_minute": 60,
                "requests_per_second": 1,
                "backoff_multiplier": 2,
                "max_retries": 3
            },
            "alpha_vantage": {
                "requests_per_minute": 5,
                "requests_per_second": 0.1,
                "backoff_multiplier": 3,
                "max_retries": 2
            }
        }

        self.request_history = {}
        self.last_request_time = {}

        # Task tracking
        self.active_tasks = {}

    async def rate_limit_wait(self, api_name: str):
        """API rate limiting implementation"""
        config = self.api_limits.get(api_name, self.api_limits["yahoo_finance"])

        current_time = time.time()
        last_request = self.last_request_time.get(api_name, 0)

        # Ensure minimum time between requests
        min_interval = 1.0 / config["requests_per_second"]
        time_since_last = current_time - last_request

        if time_since_last < min_interval:
            wait_time = min_interval - time_since_last
            logger.debug(f"Rate limiting {api_name}: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)

        self.last_request_time[api_name] = time.time()

    def get_database_connection(self):
        """Database connection with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                conn = psycopg2.connect(**self.db_config)
                return conn
            except Exception as e:
                logger.warning(f"DB connection attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    async def fetch_stock_data(self, symbol: str, days_back: int = 30) -> Dict:
        """単一銘柄のデータ取得"""
        try:
            await self.rate_limit_wait("yahoo_finance")

            # yfinance with timeout
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=f"{days_back}d", timeout=10)

            if hist.empty:
                logger.warning(f"No data for {symbol}")
                return {"symbol": symbol, "status": "no_data", "data": []}

            # Convert to records
            records = []
            for date, row in hist.iterrows():
                records.append({
                    "symbol": symbol,
                    "date": date.date(),
                    "open": float(row["Open"]) if not pd.isna(row["Open"]) else None,
                    "high": float(row["High"]) if not pd.isna(row["High"]) else None,
                    "low": float(row["Low"]) if not pd.isna(row["Low"]) else None,
                    "close": float(row["Close"]) if not pd.isna(row["Close"]) else None,
                    "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else None,
                })

            logger.info(f"✅ {symbol}: {len(records)} records fetched")
            return {"symbol": symbol, "status": "success", "data": records}

        except Exception as e:
            logger.error(f"❌ Error fetching {symbol}: {e}")
            return {"symbol": symbol, "status": "error", "error": str(e), "data": []}

    async def bulk_insert_price_data(self, price_data: List[Dict]):
        """価格データの一括挿入"""
        if not price_data:
            return 0

        conn = self.get_database_connection()
        try:
            with conn.cursor() as cursor:
                # Prepare data for insertion
                insert_data = []
                for record in price_data:
                    insert_data.append((
                        record["symbol"],
                        record["date"],
                        record["open"],
                        record["high"],
                        record["low"],
                        record["close"],
                        record["volume"]
                    ))

                # Bulk insert with conflict handling
                cursor.executemany("""
                    INSERT INTO stock_prices
                    (symbol, date, open_price, high_price, low_price, close_price, volume, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (symbol, date)
                    DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume,
                        updated_at = NOW()
                """, insert_data)

                conn.commit()
                inserted_count = cursor.rowcount
                logger.info(f"📊 Inserted/updated {inserted_count} price records")
                return inserted_count

        except Exception as e:
            logger.error(f"❌ Bulk insert error: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    async def get_active_symbols(self, limit: int = 500) -> List[str]:
        """アクティブ銘柄リストの取得"""
        conn = self.get_database_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT symbol FROM stock_master
                    WHERE is_active = true
                    ORDER BY
                        CASE WHEN market = 'US' THEN 1
                             WHEN market = 'JP' THEN 2
                             ELSE 3 END,
                        symbol
                    LIMIT %s
                """, (limit,))

                symbols = [row[0] for row in cursor.fetchall()]
                logger.info(f"📋 Retrieved {len(symbols)} active symbols")
                return symbols

        except Exception as e:
            logger.error(f"❌ Error getting symbols: {e}")
            return []
        finally:
            conn.close()

    async def process_collection_batch(self, symbols: List[str], days_back: int = 30) -> Dict:
        """バッチ処理実行"""
        task_id = f"collect_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(symbols)}"

        logger.info(f"🚀 Starting collection batch {task_id}: {len(symbols)} symbols")
        start_time = datetime.now()

        # Track task
        self.active_tasks[task_id] = CollectionTask(
            task_id=task_id,
            symbols=symbols,
            priority="standard",
            start_time=start_time,
            status="running"
        )

        # Process symbols in smaller batches
        batch_size = 50  # Smaller batches for reliability
        results = {"success": [], "failed": [], "total_records": 0}

        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i + batch_size]
            logger.info(f"📦 Processing batch {i//batch_size + 1}: {len(batch_symbols)} symbols")

            # Fetch data for batch
            batch_tasks = []
            for symbol in batch_symbols:
                batch_tasks.append(self.fetch_stock_data(symbol, days_back))

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Process batch results
            batch_price_data = []
            for result in batch_results:
                if isinstance(result, Exception):
                    results["failed"].append({"symbol": "unknown", "error": str(result)})
                    continue

                if result["status"] == "success":
                    results["success"].append(result["symbol"])
                    batch_price_data.extend(result["data"])
                else:
                    results["failed"].append(result)

            # Insert batch data
            if batch_price_data:
                inserted = await self.bulk_insert_price_data(batch_price_data)
                results["total_records"] += inserted

            # Small delay between batches
            await asyncio.sleep(1)

        # Update task status
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.active_tasks[task_id].status = "completed"

        final_results = {
            "task_id": task_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "symbols_processed": len(symbols),
            "symbols_success": len(results["success"]),
            "symbols_failed": len(results["failed"]),
            "total_records_inserted": results["total_records"],
            "success_rate": (len(results["success"]) / len(symbols)) * 100 if symbols else 0
        }

        logger.info(f"✅ Collection batch {task_id} completed: "
                   f"{final_results['symbols_success']}/{len(symbols)} symbols, "
                   f"{final_results['total_records_inserted']} records, "
                   f"{final_results['success_rate']:.1f}% success rate")

        return final_results

# FastAPI Application
app = FastAPI(title="Miraikakaku Cloud Run Data Collector", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global collector instance
collector = CloudRunDataCollector()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = collector.get_database_connection()
        conn.close()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "miraikakaku-data-collector",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/readiness")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "active_tasks": len(collector.active_tasks)
    }

@app.post("/collect")
async def collect_data(request: CollectionRequest, background_tasks: BackgroundTasks):
    """データ収集エンドポイント"""
    try:
        logger.info(f"📥 Collection request: mode={request.mode}, days_back={request.days_back}")

        # Get symbols based on mode
        if request.symbols:
            symbols = request.symbols
        else:
            if request.mode == "priority":
                # High-priority symbols (US major stocks)
                symbols = await collector.get_active_symbols(limit=100)
            elif request.mode == "full":
                # Full collection
                symbols = await collector.get_active_symbols(limit=2000)
            else:
                # Standard collection
                symbols = await collector.get_active_symbols(limit=500)

        if not symbols:
            raise HTTPException(status_code=400, detail="No symbols available for collection")

        # Start collection in background
        task_id = f"collect_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        background_tasks.add_task(
            collector.process_collection_batch,
            symbols,
            request.days_back
        )

        return {
            "status": "started",
            "task_id": task_id,
            "symbols_count": len(symbols),
            "mode": request.mode,
            "message": "Data collection started in background"
        }

    except Exception as e:
        logger.error(f"❌ Collection request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
async def get_tasks():
    """アクティブタスクの状況"""
    return {
        "active_tasks": len(collector.active_tasks),
        "tasks": [
            {
                "task_id": task.task_id,
                "symbols_count": len(task.symbols),
                "priority": task.priority,
                "start_time": task.start_time.isoformat(),
                "status": task.status
            }
            for task in collector.active_tasks.values()
        ]
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Miraikakaku Cloud Run Data Collector",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "readiness": "/readiness",
            "collect": "/collect",
            "tasks": "/tasks"
        }
    }

@app.on_event("startup")
async def startup_event():
    """起動時に定期データ更新タスクを開始"""
    asyncio.create_task(scheduled_data_collection())
    logger.info("🔄 定期データ更新タスクを開始しました")

async def scheduled_data_collection():
    """定期的なデータ収集を実行"""
    collector = CloudRunDataCollector()

    while True:
        try:
            current_time = datetime.now()

            # 市場時間中（平日9:00-15:30 JST）は30分間隔
            if (current_time.weekday() < 5 and
                9 <= current_time.hour < 16 and
                not (current_time.hour == 15 and current_time.minute > 30)):

                logger.info("📊 市場時間中 - 高頻度データ収集実行")
                # 優先度の高いシンボルを収集
                priority_symbols = await collector.get_priority_symbols(limit=500)
                if priority_symbols:
                    await collector.collect_symbols(priority_symbols)
                await asyncio.sleep(1800)  # 30分間隔

            # 市場外時間は2時間間隔
            else:
                logger.info("🌙 市場外時間 - 定期データ収集実行")
                # 標準的なデータ収集
                standard_symbols = await collector.get_active_symbols(limit=200)
                if standard_symbols:
                    await collector.collect_symbols(standard_symbols)
                await asyncio.sleep(7200)  # 2時間間隔

        except Exception as e:
            logger.error(f"定期収集エラー: {e}")
            await asyncio.sleep(1800)  # エラー時は30分待機

@app.post("/collect/trigger")
async def trigger_collection(background_tasks: BackgroundTasks):
    """手動でデータ収集をトリガー"""
    collector = CloudRunDataCollector()

    # 即座にデータ収集を実行
    try:
        symbols = await collector.get_active_symbols(limit=1000)
        if symbols:
            background_tasks.add_task(collector.collect_symbols, symbols)

        return {
            "status": "triggered",
            "message": f"データ収集を開始しました ({len(symbols)}シンボル)",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"データ収集トリガーエラー: {e}")
        return {
            "status": "error",
            "message": f"データ収集の開始に失敗: {e}",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import pandas as pd
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"🚀 Starting Cloud Run Data Collector on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)