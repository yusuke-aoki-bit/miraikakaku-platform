#!/usr/bin/env python3
"""
シンプルバッチ価格取得システム
文字エンコーディング問題を回避しながら価格データを取得
"""

import yfinance as yf
import pymysql
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleBatchPriceFetcher:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user", 
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
        }
        self.stats = {
            "processed": 0,
            "successful": 0,
            "failed": 0
        }

    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def fetch_us_stocks(self):
        """米国市場の銘柄を取得して価格データを取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # NYSEとNASDAQの銘柄を取得（上位500）
                cursor.execute("""
                    SELECT symbol, name, exchange 
                    FROM stock_master 
                    WHERE exchange IN ('NYSE', 'NASDAQ')
                    LIMIT 500
                """)
                
                us_stocks = cursor.fetchall()
                logger.info(f"🇺🇸 米国銘柄 {len(us_stocks)}件を処理開始")
                
                for stock in us_stocks:
                    symbol = stock[0]
                    name = stock[1][:100]
                    
                    self.fetch_and_save_price(symbol, name, "US Stock Batch")
                    self.stats["processed"] += 1
                    
                    if self.stats["processed"] % 50 == 0:
                        logger.info(f"📈 進捗: {self.stats['processed']}件処理 (成功: {self.stats['successful']})")
                    
                    time.sleep(0.1)  # レート制限対策
                    
        finally:
            connection.close()

    def fetch_japan_stocks(self):
        """日本市場の銘柄を取得して価格データを取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 日本市場の銘柄を取得（上位300）
                cursor.execute("""
                    SELECT symbol, name, exchange 
                    FROM stock_master 
                    WHERE exchange LIKE '%Market%' 
                    AND exchange LIKE '%Domestic%'
                    LIMIT 300
                """)
                
                jp_stocks = cursor.fetchall()
                logger.info(f"🇯🇵 日本銘柄 {len(jp_stocks)}件を処理開始")
                
                for stock in jp_stocks:
                    symbol = stock[0]
                    name = stock[1][:100]
                    
                    # 4桁の数字なら.Tを付ける
                    if len(symbol) == 4 and symbol.isdigit():
                        yf_symbol = symbol + '.T'
                    else:
                        yf_symbol = symbol
                    
                    self.fetch_and_save_price_jp(symbol, yf_symbol, name, "JP Stock Batch")
                    self.stats["processed"] += 1
                    
                    if self.stats["processed"] % 50 == 0:
                        logger.info(f"📈 進捗: {self.stats['processed']}件処理 (成功: {self.stats['successful']})")
                    
                    time.sleep(0.1)
                    
        finally:
            connection.close()

    def fetch_etf_stocks(self):
        """ETF銘柄を取得して価格データを取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # ETF銘柄を取得（上位200）
                cursor.execute("""
                    SELECT symbol, name, exchange 
                    FROM stock_master 
                    WHERE exchange LIKE '%ETF%' 
                    OR name LIKE '%ETF%'
                    LIMIT 200
                """)
                
                etf_stocks = cursor.fetchall()
                logger.info(f"📊 ETF銘柄 {len(etf_stocks)}件を処理開始")
                
                for stock in etf_stocks:
                    symbol = stock[0]
                    name = stock[1][:100]
                    
                    self.fetch_and_save_price(symbol, name, "ETF Batch")
                    self.stats["processed"] += 1
                    
                    if self.stats["processed"] % 50 == 0:
                        logger.info(f"📈 進捗: {self.stats['processed']}件処理 (成功: {self.stats['successful']})")
                    
                    time.sleep(0.1)
                    
        finally:
            connection.close()

    def fetch_and_save_price(self, symbol, name, source):
        """価格データ取得と保存（通常版）"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                self.stats["failed"] += 1
                return False
            
            latest_data = hist.iloc[-1]
            latest_date = hist.index[-1].strftime('%Y-%m-%d')
            
            # データベース保存
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
        """価格データ取得と保存（日本株版）"""
        try:
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                self.stats["failed"] += 1
                return False
            
            latest_data = hist.iloc[-1]
            latest_date = hist.index[-1].strftime('%Y-%m-%d')
            
            # データベース保存（元のシンボルで保存）
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

    def run_batch_fetch(self):
        """バッチ取得実行"""
        start_time = datetime.now()
        logger.info(f"🚀 バッチ価格取得開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 米国市場
        self.fetch_us_stocks()
        
        # 日本市場
        self.fetch_japan_stocks()
        
        # ETF
        self.fetch_etf_stocks()
        
        # 最終報告
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 70)
        logger.info("📊 バッチ価格取得完了サマリー")
        logger.info(f"⏱️  実行時間: {duration:.1f}秒")
        logger.info(f"🎯 処理銘柄: {self.stats['processed']}銘柄")
        logger.info(f"✅ 成功: {self.stats['successful']}銘柄")
        logger.info(f"❌ 失敗: {self.stats['failed']}銘柄")
        logger.info(f"📈 成功率: {(self.stats['successful'] / max(1, self.stats['processed'])) * 100:.1f}%")
        logger.info("=" * 70)

if __name__ == "__main__":
    fetcher = SimpleBatchPriceFetcher()
    
    try:
        fetcher.run_batch_fetch()
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()