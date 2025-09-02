#!/usr/bin/env python3
"""
メガ株価取得システム - 8,882銘柄の価格データを一括取得
NYSE、NASDAQ、日本市場、ETFを含む全銘柄対応
"""

import yfinance as yf
import pymysql
import logging
import time
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MegaStockPriceFetcher:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user", 
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
        }
        self.stats = {
            "total_symbols": 0,
            "successful": 0,
            "failed": 0,
            "already_has_price": 0
        }
        self.lock = threading.Lock()

    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def get_symbols_without_prices(self, limit=None) -> List[Dict]:
        """価格データがない銘柄を取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 価格データがない銘柄を取得
                query = """
                    SELECT DISTINCT sm.symbol, sm.name, sm.exchange, sm.country
                    FROM stock_master sm
                    WHERE NOT EXISTS (
                        SELECT 1 FROM stock_price_history sph 
                        WHERE sph.symbol = sm.symbol
                    )
                    AND sm.is_active = 1
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query)
                results = cursor.fetchall()
                
                symbols_list = []
                for row in results:
                    symbol = row[0]
                    exchange = row[2]
                    country = row[3]
                    
                    # 日本市場の銘柄には.Tを付ける
                    if exchange in ['Prime Market', 'Standard Market', 'Growth Market', 'TSE'] or \
                       'Market' in str(exchange) and 'Domestic' in str(exchange):
                        if not symbol.endswith('.T') and symbol.isdigit() and len(symbol) == 4:
                            symbol += '.T'
                    
                    symbols_list.append({
                        'symbol': symbol,
                        'original_symbol': row[0],
                        'name': row[1],
                        'exchange': exchange,
                        'country': country
                    })
                
                return symbols_list
                
        finally:
            connection.close()

    def fetch_and_save_price(self, symbol_info: Dict) -> bool:
        """単一銘柄の価格取得と保存"""
        symbol = symbol_info['symbol']
        original_symbol = symbol_info['original_symbol']
        
        try:
            ticker = yf.Ticker(symbol)
            
            # 過去5日間のデータ取得
            hist = ticker.history(period="5d")
            
            if hist.empty:
                with self.lock:
                    self.stats['failed'] += 1
                return False
            
            # 最新データ
            latest_data = hist.iloc[-1]
            latest_date = hist.index[-1].strftime('%Y-%m-%d')
            
            # 前日比計算
            if len(hist) > 1:
                prev_close = hist.iloc[-2]['Close']
                change = latest_data['Close'] - prev_close
                change_percent = (change / prev_close) * 100
            else:
                change_percent = 0
            
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
                        original_symbol,
                        latest_date,
                        float(latest_data['Open']),
                        float(latest_data['High']),
                        float(latest_data['Low']),
                        float(latest_data['Close']),
                        int(latest_data['Volume']),
                        "Mega Fetch"
                    ))
                    
                connection.commit()
                
                with self.lock:
                    self.stats['successful'] += 1
                
                logger.info(f"✅ {symbol}: ${latest_data['Close']:.2f} ({change_percent:+.2f}%)")
                return True
                
            finally:
                connection.close()
                
        except Exception as e:
            with self.lock:
                self.stats['failed'] += 1
            logger.debug(f"⚠️ {symbol}: {str(e)[:50]}")
            return False

    def process_batch(self, symbols_batch: List[Dict], batch_num: int):
        """バッチ処理"""
        logger.info(f"🔄 バッチ {batch_num} 開始: {len(symbols_batch)}銘柄")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for symbol_info in symbols_batch:
                future = executor.submit(self.fetch_and_save_price, symbol_info)
                futures.append(future)
                time.sleep(0.05)  # レート制限対策
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.debug(f"バッチ処理エラー: {e}")
        
        logger.info(f"✅ バッチ {batch_num} 完了: 成功 {self.stats['successful']}, 失敗 {self.stats['failed']}")

    def run_mega_fetch(self, target_count=1000):
        """メガ取得実行"""
        start_time = datetime.now()
        logger.info(f"🚀 メガ株価取得開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 価格データがない銘柄を取得
        symbols_without_prices = self.get_symbols_without_prices(limit=target_count)
        self.stats['total_symbols'] = len(symbols_without_prices)
        
        logger.info(f"📊 対象銘柄数: {self.stats['total_symbols']}")
        
        if not symbols_without_prices:
            logger.info("✅ すべての銘柄に価格データが存在します")
            return
        
        # バッチサイズを設定
        batch_size = 50
        batches = [symbols_without_prices[i:i+batch_size] 
                  for i in range(0, len(symbols_without_prices), batch_size)]
        
        # バッチごとに処理
        for batch_num, batch in enumerate(batches, 1):
            self.process_batch(batch, batch_num)
            
            # 進捗報告
            if batch_num % 5 == 0:
                progress = (batch_num * batch_size / self.stats['total_symbols']) * 100
                logger.info(f"📈 進捗: {progress:.1f}% ({self.stats['successful']}/{self.stats['total_symbols']})")
        
        # 最終報告
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 70)
        logger.info("📊 メガ株価取得完了サマリー")
        logger.info(f"⏱️  実行時間: {duration:.1f}秒")
        logger.info(f"🎯 対象銘柄: {self.stats['total_symbols']}銘柄")
        logger.info(f"✅ 成功: {self.stats['successful']}銘柄")
        logger.info(f"❌ 失敗: {self.stats['failed']}銘柄")
        logger.info(f"📈 成功率: {(self.stats['successful'] / max(1, self.stats['total_symbols'])) * 100:.1f}%")
        logger.info("=" * 70)

if __name__ == "__main__":
    fetcher = MegaStockPriceFetcher()
    
    try:
        # 最初は1000銘柄でテスト
        fetcher.run_mega_fetch(target_count=1000)
        
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ システムエラー: {e}")
        import traceback
        traceback.print_exc()