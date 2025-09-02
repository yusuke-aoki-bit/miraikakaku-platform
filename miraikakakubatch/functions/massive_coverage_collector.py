#!/usr/bin/env python3
"""
100%カバレッジを目指す大規模データ収集
"""

import pymysql
import yfinance as yf
import pandas_datareader.data as web
from datetime import datetime, timedelta
import logging
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MassiveCoverageCollector:
    def __init__(self):
        self.db_config = {
            "host": os.getenv("DB_HOST", "34.58.103.36"),
            "user": os.getenv("DB_USER", "miraikakaku-user"),
            "password": os.getenv("DB_PASSWORD", "miraikakaku-secure-pass-2024"),
            "database": os.getenv("DB_NAME", "miraikakaku"),
            "charset": "utf8mb4"
        }
        
        self.worker_id = int(os.getenv("BATCH_TASK_INDEX", "0"))
        
    def get_uncovered_stocks(self, batch_size=100):
        """未収集の銘柄を取得"""
        connection = pymysql.connect(**self.db_config)
        
        try:
            with connection.cursor() as cursor:
                # ワーカーIDに応じてオフセット
                offset = self.worker_id * batch_size
                
                cursor.execute("""
                    SELECT sm.symbol, sm.name, sm.market, sm.country
                    FROM stock_master sm
                    LEFT JOIN stock_price_history sph ON sm.symbol = sph.symbol
                    WHERE sm.is_active = 1 AND sph.symbol IS NULL
                    ORDER BY 
                        CASE 
                            WHEN sm.market = 'US' THEN 1
                            WHEN sm.market = 'NASDAQ' THEN 2
                            WHEN sm.market = 'NYSE' THEN 3
                            WHEN sm.country = 'Japan' THEN 4
                            ELSE 5
                        END,
                        sm.symbol
                    LIMIT %s OFFSET %s
                """, (batch_size, offset))
                
                return cursor.fetchall()
        finally:
            connection.close()
    
    def collect_with_multiple_sources(self, symbol, market, country):
        """複数のソースでデータ収集"""
        success_count = 0
        
        # 1. yfinanceを試行
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if not hist.empty:
                success_count += self.save_data(symbol, hist, 'yfinance')
                logger.info(f"✅ {symbol} (yfinance): {len(hist)}件")
                return success_count
        except Exception as e:
            logger.debug(f"yfinance failed for {symbol}: {e}")
        
        # 2. Stooq (pandas-datareader)を試行
        try:
            stooq_symbol = f"{symbol}.US" if market in ['US', 'NASDAQ', 'NYSE'] else symbol
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            df = web.DataReader(stooq_symbol, 'stooq', start_date, end_date)
            
            if not df.empty:
                success_count += self.save_data(symbol, df, 'stooq')
                logger.info(f"✅ {symbol} (stooq): {len(df)}件")
                return success_count
        except Exception as e:
            logger.debug(f"stooq failed for {symbol}: {e}")
        
        # 3. 代替シンボルで試行（.TO, .L, .T など）
        alternative_symbols = []
        if country == 'Japan':
            alternative_symbols = [f"{symbol}.T"]
        elif country == 'Canada':
            alternative_symbols = [f"{symbol}.TO"]
        elif country == 'UK':
            alternative_symbols = [f"{symbol}.L"]
        elif country == 'Germany':
            alternative_symbols = [f"{symbol}.DE"]
        
        for alt_symbol in alternative_symbols:
            try:
                ticker = yf.Ticker(alt_symbol)
                hist = ticker.history(period="5d")
                
                if not hist.empty:
                    success_count += self.save_data(symbol, hist, 'yfinance_alt')
                    logger.info(f"✅ {symbol} (alt: {alt_symbol}): {len(hist)}件")
                    return success_count
            except Exception as e:
                logger.debug(f"Alternative {alt_symbol} failed: {e}")
        
        return success_count
    
    def save_data(self, symbol, df, source):
        """データをデータベースに保存"""
        connection = pymysql.connect(**self.db_config)
        saved_count = 0
        
        try:
            with connection.cursor() as cursor:
                for date, row in df.iterrows():
                    try:
                        cursor.execute("""
                            INSERT INTO stock_price_history 
                            (symbol, date, open_price, high_price, low_price, 
                             close_price, volume, adjusted_close, data_source, 
                             is_valid, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW(), NOW())
                            ON DUPLICATE KEY UPDATE
                            close_price = VALUES(close_price),
                            volume = VALUES(volume),
                            data_source = VALUES(data_source),
                            updated_at = NOW()
                        """, (
                            symbol,
                            date.date() if hasattr(date, 'date') else date,
                            float(row.get('Open', 0)),
                            float(row.get('High', 0)),
                            float(row.get('Low', 0)),
                            float(row.get('Close', 0)),
                            int(row.get('Volume', 0)),
                            float(row.get('Close', 0)),
                            source
                        ))
                        saved_count += 1
                    except Exception as save_error:
                        logger.debug(f"Save error for {symbol}: {save_error}")
                        continue
                
                connection.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")
            connection.rollback()
        finally:
            connection.close()
        
        return saved_count
    
    def run_massive_collection(self):
        """大規模データ収集実行"""
        logger.info(f"🚀 Massive Coverage Worker {self.worker_id} started")
        
        # 未収集銘柄を取得
        uncovered_stocks = self.get_uncovered_stocks(batch_size=150)
        logger.info(f"📊 Worker {self.worker_id}: {len(uncovered_stocks)}銘柄を処理")
        
        if not uncovered_stocks:
            logger.info("✅ 処理対象なし")
            return 0
        
        total_success = 0
        total_processed = 0
        
        for symbol, name, market, country in uncovered_stocks:
            try:
                success_count = self.collect_with_multiple_sources(symbol, market, country)
                total_success += success_count
                total_processed += 1
                
                # 進捗報告
                if total_processed % 20 == 0:
                    progress = (total_processed / len(uncovered_stocks)) * 100
                    logger.info(f"📈 進捗: {progress:.1f}% ({total_processed}/{len(uncovered_stocks)}) - 成功: {total_success}")
                
                # API制限対策
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ {symbol} processing error: {e}")
                continue
        
        final_progress = (total_processed / len(uncovered_stocks)) * 100
        logger.info(f"🎯 Worker {self.worker_id} 完了: {final_progress:.1f}% - {total_success}/{total_processed}")
        
        return total_success

def main():
    collector = MassiveCoverageCollector()
    result = collector.run_massive_collection()
    
    if result > 0:
        logger.info(f"✅ 収集完了: {result}件のデータを追加")
    else:
        logger.info("⚠️ 新規データなし")

if __name__ == "__main__":
    main()