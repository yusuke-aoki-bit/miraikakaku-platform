#!/usr/bin/env python3
"""
シンプルなテスト用データ収集
"""

import pymysql
import yfinance as yf
from datetime import datetime, timedelta
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db_config = {
        "host": os.getenv("DB_HOST", "34.58.103.36"),
        "user": os.getenv("DB_USER", "miraikakaku-user"),
        "password": os.getenv("DB_PASSWORD", "miraikakaku-secure-pass-2024"),
        "database": os.getenv("DB_NAME", "miraikakaku"),
        "charset": "utf8mb4"
    }
    
    worker_id = int(os.getenv("BATCH_TASK_INDEX", "0"))
    logger.info(f"🚀 Worker {worker_id} started")
    
    # テスト用の主要銘柄
    test_symbols = [
        "AAPL", "GOOGL", "MSFT", "AMZN", "META",
        "TSLA", "NVDA", "JPM", "V", "WMT"
    ]
    
    # ワーカーごとに異なる銘柄を処理
    start_idx = worker_id * 3
    end_idx = min(start_idx + 3, len(test_symbols))
    symbols = test_symbols[start_idx:end_idx]
    
    logger.info(f"Processing symbols: {symbols}")
    
    connection = pymysql.connect(**db_config)
    success_count = 0
    
    try:
        with connection.cursor() as cursor:
            for symbol in symbols:
                try:
                    # Yahoo Financeからデータ取得
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="5d")
                    
                    if not hist.empty:
                        for date, row in hist.iterrows():
                            cursor.execute("""
                                INSERT INTO stock_price_history 
                                (symbol, date, open_price, high_price, low_price, 
                                 close_price, volume, adjusted_close, data_source, 
                                 is_valid, created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW(), NOW())
                                ON DUPLICATE KEY UPDATE
                                close_price = VALUES(close_price),
                                volume = VALUES(volume),
                                updated_at = NOW()
                            """, (
                                symbol,
                                date.date(),
                                float(row['Open']),
                                float(row['High']),
                                float(row['Low']),
                                float(row['Close']),
                                int(row['Volume']),
                                float(row['Close']),
                                'yfinance'
                            ))
                        
                        connection.commit()
                        success_count += 1
                        logger.info(f"✅ {symbol}: {len(hist)} records saved")
                    
                except Exception as e:
                    logger.error(f"❌ {symbol}: {e}")
                    continue
            
            logger.info(f"🎯 Worker {worker_id} completed: {success_count}/{len(symbols)} symbols")
            
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        exit(1)
    finally:
        connection.close()

if __name__ == "__main__":
    main()