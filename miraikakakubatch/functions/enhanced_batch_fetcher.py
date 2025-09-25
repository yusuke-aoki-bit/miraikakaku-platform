#!/usr/bin/env python3
"""
拡張バッチ価格取得システム
文字エンコーディング問題を回避しながら大量銘柄を処理
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

class EnhancedBatchFetcher:
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
            "failed": 0
        }

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def fetch_nyse_nasdaq_batch(self, limit=1000):
        """NYSE/NASDAQ銘柄を取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # NYSE/NASDAQからランダムに銘柄を選択
                cursor.execute("""
                    SELECT symbol, name, exchange 
                    FROM stock_master 
                    WHERE exchange IN ('NYSE', 'NASDAQ')
                    AND symbol NOT IN (
                        SELECT DISTINCT symbol FROM stock_price_history
                    )
                    ORDER BY RAND()
                    LIMIT %s
                """, (limit,))
                
                stocks = cursor.fetchall()
                logger.info(f"🇺🇸 NYSE/NASDAQ {len(stocks)}銘柄を処理開始")
                
                for stock in stocks:
                    symbol = stock[0]
                    name = stock[1][:100] if stock[1] else symbol
                    
                    self.fetch_and_save_price(symbol, name, "US Batch Enhanced")
                    self.stats["processed"] += 1
                    
                    if self.stats["processed"] % 50 == 0:
                        logger.info(f"📈 進捗: {self.stats['processed']}件処理 (成功: {self.stats['successful']})")
                    
                    time.sleep(0.08)  # レート制限
                    
        finally:
            connection.close()

    def fetch_japan_batch(self, limit=500):
        """日本市場銘柄を取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 日本市場（Prime/Standard/Growth）からランダムに選択
                cursor.execute("""
                    SELECT symbol, name, exchange 
                    FROM stock_master 
                    WHERE (exchange LIKE '%Prime%' 
                        OR exchange LIKE '%Standard%' 
                        OR exchange LIKE '%Growth%')
                    AND exchange LIKE '%Domestic%'
                    AND symbol NOT IN (
                        SELECT DISTINCT symbol FROM stock_price_history
                    )
                    ORDER BY RAND()
                    LIMIT %s
                """, (limit,))
                
                stocks = cursor.fetchall()
                logger.info(f"🇯🇵 日本市場 {len(stocks)}銘柄を処理開始")
                
                for stock in stocks:
                    symbol = stock[0]
                    name = stock[1][:100] if stock[1] else symbol
                    
                    # 4桁数字なら.Tを付ける
                    yf_symbol = symbol
                    if len(symbol) == 4 and symbol.isdigit():
                        yf_symbol = symbol + '.T'
                    
                    self.fetch_and_save_price_jp(symbol, yf_symbol, name, "JP Batch Enhanced")
                    self.stats["processed"] += 1
                    
                    if self.stats["processed"] % 50 == 0:
                        logger.info(f"📈 進捗: {self.stats['processed']}件処理 (成功: {self.stats['successful']})")
                    
                    time.sleep(0.08)
                    
        finally:
            connection.close()

    def fetch_etf_batch(self, limit=300):
        """ETF銘柄を取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # ETF銘柄を取得
                cursor.execute("""
                    SELECT symbol, name, exchange 
                    FROM stock_master 
                    WHERE (exchange LIKE '%ETF%' OR name LIKE '%ETF%')
                    AND symbol NOT IN (
                        SELECT DISTINCT symbol FROM stock_price_history
                    )
                    ORDER BY RAND()
                    LIMIT %s
                """, (limit,))
                
                stocks = cursor.fetchall()
                logger.info(f"📊 ETF {len(stocks)}銘柄を処理開始")
                
                for stock in stocks:
                    symbol = stock[0]
                    name = stock[1][:100] if stock[1] else symbol
                    
                    self.fetch_and_save_price(symbol, name, "ETF Batch Enhanced")
                    self.stats["processed"] += 1
                    
                    if self.stats["processed"] % 50 == 0:
                        logger.info(f"📈 進捗: {self.stats['processed']}件処理 (成功: {self.stats['successful']})")
                    
                    time.sleep(0.08)
                    
        finally:
            connection.close()

    def fetch_europe_batch(self, limit=200):
        """欧州市場銘柄を取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 欧州市場を取得
                cursor.execute("""
                    SELECT symbol, name, exchange, country 
                    FROM stock_master 
                    WHERE country IN ('UK', 'DE', 'FR', 'CH', 'NL', 'IT', 'ES')
                    AND symbol NOT IN (
                        SELECT DISTINCT symbol FROM stock_price_history
                    )
                    ORDER BY RAND()
                    LIMIT %s
                """, (limit,))
                
                stocks = cursor.fetchall()
                logger.info(f"🇪🇺 欧州市場 {len(stocks)}銘柄を処理開始")
                
                for stock in stocks:
                    symbol = stock[0]
                    name = stock[1][:100] if stock[1] else symbol
                    country = stock[3]
                    
                    # 市場サフィックスを付ける
                    yf_symbol = symbol
                    if country == 'UK' and not symbol.endswith('.L'):
                        yf_symbol = symbol + '.L'
                    elif country == 'DE' and not symbol.endswith('.DE'):
                        yf_symbol = symbol + '.DE'
                    elif country == 'FR' and not symbol.endswith('.PA'):
                        yf_symbol = symbol + '.PA'
                    elif country == 'CH' and not symbol.endswith('.SW'):
                        yf_symbol = symbol + '.SW'
                    
                    self.fetch_and_save_price_intl(symbol, yf_symbol, name, "EU Batch Enhanced")
                    self.stats["processed"] += 1
                    
                    if self.stats["processed"] % 50 == 0:
                        logger.info(f"📈 進捗: {self.stats['processed']}件処理 (成功: {self.stats['successful']})")
                    
                    time.sleep(0.08)
                    
        finally:
            connection.close()

    def fetch_and_save_price(self, symbol, name, source):
        """価格データ取得と保存（米国版）"""
        try:
            ticker = yf.Ticker(symbol)
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
                        symbol,
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
                logger.info(f"✅ {symbol}: ${latest_data['Close']:.2f}")
                return True
                
            finally:
                connection.close()
                
        except Exception as e:
            self.stats["failed"] += 1
            return False

    def fetch_and_save_price_jp(self, original_symbol, yf_symbol, name, source):
        """価格データ取得と保存（日本版）"""
        try:
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
                logger.info(f"✅ {yf_symbol}: ¥{latest_data['Close']:.0f}")
                return True
                
            finally:
                connection.close()
                
        except Exception as e:
            self.stats["failed"] += 1
            return False

    def fetch_and_save_price_intl(self, original_symbol, yf_symbol, name, source):
        """価格データ取得と保存（国際版）"""
        try:
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
                logger.info(f"✅ {yf_symbol}: {latest_data['Close']:.2f}")
                return True
                
            finally:
                connection.close()
                
        except Exception as e:
            self.stats["failed"] += 1
            return False

    def run_enhanced_batch(self):
        """拡張バッチ実行"""
        start_time = datetime.now()
        logger.info(f"🚀 拡張バッチ価格取得開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 米国市場（1000銘柄）
        self.fetch_nyse_nasdaq_batch(1000)
        
        # 日本市場（500銘柄）
        self.fetch_japan_batch(500)
        
        # ETF（300銘柄）
        self.fetch_etf_batch(300)
        
        # 欧州市場（200銘柄）
        self.fetch_europe_batch(200)
        
        # 最終報告
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 70)
        logger.info("📊 拡張バッチ価格取得完了サマリー")
        logger.info(f"⏱️  実行時間: {duration:.1f}秒")
        logger.info(f"🎯 処理銘柄: {self.stats['processed']}銘柄")
        logger.info(f"✅ 成功: {self.stats['successful']}銘柄")
        logger.info(f"❌ 失敗: {self.stats['failed']}銘柄")
        logger.info(f"📈 成功率: {(self.stats['successful'] / max(1, self.stats['processed'])) * 100:.1f}%")
        logger.info("=" * 70)

if __name__ == "__main__":
    fetcher = EnhancedBatchFetcher()
    
    try:
        fetcher.run_enhanced_batch()
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()