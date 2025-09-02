#!/usr/bin/env python3
"""
継続的バッチ価格取得システム
9,512銘柄から価格データを継続的に取得
"""

import yfinance as yf
import pymysql
import logging
import time
from datetime import datetime
from typing import List, Dict
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContinuousBatchFetcher:
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
            "failed": 0,
            "already_has_price": 0
        }

    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def get_next_batch_symbols(self, batch_size=500) -> List[Dict]:
        """価格データがない銘柄を次のバッチとして取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 価格データがない銘柄をランダムに取得（多様性確保）
                cursor.execute("""
                    SELECT 
                        sm.symbol,
                        sm.name,
                        sm.exchange,
                        sm.country
                    FROM stock_master sm
                    WHERE sm.symbol NOT IN (
                        SELECT DISTINCT symbol FROM stock_price_history
                    )
                    ORDER BY RAND()
                    LIMIT %s
                """, (batch_size,))
                
                results = cursor.fetchall()
                
                symbols_list = []
                for row in results:
                    symbol = row[0]
                    exchange = row[2]
                    country = row[3]
                    
                    # 日本市場の銘柄処理
                    if exchange and 'Market' in exchange and 'Domestic' in exchange:
                        if len(symbol) == 4 and symbol.isdigit():
                            symbol += '.T'
                    # 韓国市場
                    elif country == 'KR' or exchange == 'KRX':
                        if not symbol.endswith('.KS'):
                            symbol += '.KS'
                    # 英国市場
                    elif country == 'UK' or exchange == 'LSE':
                        if not symbol.endswith('.L'):
                            symbol += '.L'
                    # ドイツ市場
                    elif country == 'DE' or exchange == 'XETRA':
                        if not symbol.endswith('.DE'):
                            symbol += '.DE'
                    # フランス市場
                    elif country == 'FR' or exchange == 'EPA':
                        if not symbol.endswith('.PA'):
                            symbol += '.PA'
                    # オーストラリア市場
                    elif country == 'AU' or exchange == 'ASX':
                        if not symbol.endswith('.AX'):
                            symbol += '.AX'
                    
                    symbols_list.append({
                        'symbol': symbol,
                        'original_symbol': row[0],
                        'name': row[1][:100] if row[1] else row[0],
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
            hist = ticker.history(period="5d")
            
            if hist.empty:
                self.stats["failed"] += 1
                return False
            
            # 最新データ取得
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
                        original_symbol,
                        latest_date,
                        float(latest_data['Open']),
                        float(latest_data['High']),
                        float(latest_data['Low']),
                        float(latest_data['Close']),
                        int(latest_data['Volume']),
                        "Continuous Batch"
                    ))
                    
                connection.commit()
                self.stats["successful"] += 1
                
                # 前日比計算
                if len(hist) > 1:
                    prev_close = hist.iloc[-2]['Close']
                    change_pct = ((latest_data['Close'] - prev_close) / prev_close) * 100
                else:
                    change_pct = 0
                
                logger.info(f"✅ {symbol}: ${latest_data['Close']:.2f} ({change_pct:+.2f}%)")
                return True
                
            finally:
                connection.close()
                
        except Exception as e:
            self.stats["failed"] += 1
            if "Delisted" not in str(e) and "404" not in str(e):
                logger.debug(f"⚠️ {symbol}: {str(e)[:30]}")
            return False

    def run_batch(self, target_count=2000):
        """バッチ実行"""
        start_time = datetime.now()
        logger.info(f"🚀 継続的バッチ価格取得開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📊 目標取得数: {target_count}銘柄")
        
        # 複数のバッチに分割して処理
        batch_size = 100
        total_batches = target_count // batch_size
        
        for batch_num in range(1, total_batches + 1):
            # 次のバッチ銘柄を取得
            symbols = self.get_next_batch_symbols(batch_size)
            
            if not symbols:
                logger.info("✅ 処理可能な銘柄がなくなりました")
                break
            
            logger.info(f"🔄 バッチ {batch_num}/{total_batches} 処理開始: {len(symbols)}銘柄")
            
            # 各銘柄を処理
            for symbol_info in symbols:
                self.fetch_and_save_price(symbol_info)
                self.stats["processed"] += 1
                
                # 進捗報告
                if self.stats["processed"] % 50 == 0:
                    logger.info(f"📈 進捗: {self.stats['processed']}件処理 (成功: {self.stats['successful']})")
                
                # レート制限対策
                time.sleep(0.1)
            
            # バッチ間の休憩
            if batch_num < total_batches:
                time.sleep(2)
        
        # 最終報告
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 70)
        logger.info("📊 継続的バッチ価格取得完了サマリー")
        logger.info(f"⏱️  実行時間: {duration:.1f}秒")
        logger.info(f"🎯 処理銘柄: {self.stats['processed']}銘柄")
        logger.info(f"✅ 成功: {self.stats['successful']}銘柄")
        logger.info(f"❌ 失敗: {self.stats['failed']}銘柄")
        logger.info(f"📈 成功率: {(self.stats['successful'] / max(1, self.stats['processed'])) * 100:.1f}%")
        logger.info("=" * 70)
        
        return self.stats

    def get_current_status(self) -> Dict:
        """現在のデータベース状況を取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 価格データがある銘柄数
                cursor.execute("""
                    SELECT COUNT(DISTINCT symbol) FROM stock_price_history
                """)
                has_price = cursor.fetchone()[0]
                
                # 価格データがない銘柄数
                cursor.execute("""
                    SELECT COUNT(*) FROM stock_master sm
                    WHERE sm.symbol NOT IN (
                        SELECT DISTINCT symbol FROM stock_price_history
                    )
                """)
                no_price = cursor.fetchone()[0]
                
                return {
                    "has_price": has_price,
                    "no_price": no_price,
                    "total": has_price + no_price
                }
                
        finally:
            connection.close()

if __name__ == "__main__":
    fetcher = ContinuousBatchFetcher()
    
    try:
        # 現在の状況を表示
        status = fetcher.get_current_status()
        logger.info("📊 現在のデータベース状況")
        logger.info(f"  価格データあり: {status['has_price']:,}銘柄")
        logger.info(f"  価格データなし: {status['no_price']:,}銘柄")
        logger.info(f"  総銘柄数: {status['total']:,}銘柄")
        logger.info("")
        
        # 2000銘柄を目標に実行
        fetcher.run_batch(target_count=2000)
        
        # 実行後の状況
        status_after = fetcher.get_current_status()
        logger.info("")
        logger.info("📊 実行後のデータベース状況")
        logger.info(f"  価格データあり: {status_after['has_price']:,}銘柄")
        logger.info(f"  価格データなし: {status_after['no_price']:,}銘柄")
        logger.info(f"  新規追加: {status_after['has_price'] - status['has_price']:,}銘柄")
        
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()