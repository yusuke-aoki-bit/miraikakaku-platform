#!/usr/bin/env python3
"""
Collation-safe batch price fetcher
Avoids MySQL collation errors by using simple symbol lists
"""

import yfinance as yf
import psycopg2
import psycopg2.extras
import logging
import time
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollationSafeBatchFetcher:
    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres", 
            "password": "miraikakaku-postgres-secure-2024",
            "database": "miraikakaku",
        }
        self.stats = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0
        }

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def get_all_symbols_paginated(self, offset=0, limit=1000):
        """ページネーションで全シンボルを取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT symbol, name, exchange, country 
                    FROM stock_master 
                    ORDER BY symbol
                    LIMIT %s OFFSET %s
                """, (limit, offset))
                
                return cursor.fetchall()
                
        finally:
            connection.close()

    def check_symbol_has_price(self, symbol):
        """シンボルが価格データを持っているかチェック"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM stock_price_history 
                    WHERE symbol = %s
                """, (symbol,))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        finally:
            connection.close()

    def fetch_and_save_price(self, symbol, name, exchange, country, source="Collation Safe Batch"):
        """価格データ取得と保存"""
        # 既に価格データがある場合はスキップ
        if self.check_symbol_has_price(symbol):
            self.stats["skipped"] += 1
            return False

        try:
            # Yahoo Finance用のシンボル準備
            yf_symbol = symbol
            original_symbol = symbol
            
            # 日本株の場合は.Tを付ける
            if exchange and 'Market' in str(exchange) and 'Domestic' in str(exchange):
                if len(symbol) == 4 and symbol.isdigit():
                    yf_symbol = symbol + '.T'
            
            # 韓国市場
            elif country == 'KR':
                if not symbol.endswith('.KS'):
                    yf_symbol = symbol + '.KS'
            
            # 英国市場
            elif country == 'UK':
                if not symbol.endswith('.L'):
                    yf_symbol = symbol + '.L'
            
            # ドイツ市場
            elif country == 'DE':
                if not symbol.endswith('.DE'):
                    yf_symbol = symbol + '.DE'

            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                self.stats["failed"] += 1
                return False
            
            latest_data = hist.iloc[-1]
            latest_date = hist.index[-1].strftime('%Y-%m-%d')
            
            connection = self.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO stock_price_history 
                        (symbol, date, open_price, high_price, low_price, close_price, volume, 
                         data_source, created_at, updated_at, is_valid, data_quality_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), 1, 0.95)
                        ON DUPLICATE KEY UPDATE
                        close_price = VALUES(close_price),
                        volume = VALUES(volume),
                        updated_at = NOW()
                    """, (
                        original_symbol,
                        latest_date,
                        float(latest_data['Open']),
                        float(latest_data['High']),
                        float(latest_data['Low']),
                        float(latest_data['Close']),
                        int(latest_data['Volume']),
                        source
                    ))
                    
                connection.commit()
                self.stats["successful"] += 1
                logger.info(f"✅ {yf_symbol}: ${latest_data['Close']:.2f}")
                return True
                
            finally:
                connection.close()
                
        except Exception as e:
            self.stats["failed"] += 1
            return False

    def run_safe_batch(self, target_count=2000):
        """コレーション安全なバッチ実行"""
        start_time = datetime.now()
        logger.info(f"🚀 Collation Safe バッチ価格取得開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📊 目標取得数: {target_count}銘柄")
        
        offset = 0
        page_size = 1000
        processed_count = 0
        
        while processed_count < target_count:
            # ページネーションで銘柄を取得
            symbols = self.get_all_symbols_paginated(offset, page_size)
            
            if not symbols:
                logger.info("✅ すべての銘柄を処理しました")
                break
            
            logger.info(f"🔄 ページ処理開始: オフセット {offset}, {len(symbols)}銘柄")
            
            # シャッフルして多様性を確保
            symbols_list = list(symbols)
            random.shuffle(symbols_list)
            
            for symbol_data in symbols_list:
                if processed_count >= target_count:
                    break
                    
                symbol = symbol_data[0]
                name = symbol_data[1][:100] if symbol_data[1] else symbol
                exchange = symbol_data[2]
                country = symbol_data[3]
                
                self.fetch_and_save_price(symbol, name, exchange, country)
                self.stats["processed"] += 1
                processed_count += 1
                
                # 進捗報告
                if self.stats["processed"] % 50 == 0:
                    logger.info(f"📈 進捗: {self.stats['processed']}件処理 (成功: {self.stats['successful']}, スキップ: {self.stats['skipped']})")
                
                # レート制限
                time.sleep(0.1)
            
            offset += page_size
        
        # 最終報告
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 70)
        logger.info("📊 Collation Safe バッチ価格取得完了サマリー")
        logger.info(f"⏱️  実行時間: {duration:.1f}秒")
        logger.info(f"🎯 処理銘柄: {self.stats['processed']}銘柄")
        logger.info(f"✅ 成功: {self.stats['successful']}銘柄")
        logger.info(f"⏭️  スキップ: {self.stats['skipped']}銘柄")
        logger.info(f"❌ 失敗: {self.stats['failed']}銘柄")
        logger.info(f"📈 成功率: {(self.stats['successful'] / max(1, self.stats['processed'] - self.stats['skipped'])) * 100:.1f}%")
        logger.info("=" * 70)
        
        return self.stats

if __name__ == "__main__":
    fetcher = CollationSafeBatchFetcher()
    
    try:
        # 2000銘柄を目標に実行
        fetcher.run_safe_batch(target_count=2000)
        
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()