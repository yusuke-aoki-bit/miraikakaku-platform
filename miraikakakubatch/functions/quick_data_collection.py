#!/usr/bin/env python3
"""
高速データ収集システム
有望な銘柄に絞って効率的にデータ収集
"""

import yfinance as yf
import pymysql
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuickDataCollection:
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
            "by_market": {}
        }

    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def get_promising_symbols_without_data(self, limit: int = 500) -> list:
        """有望な銘柄に絞ってデータ収集対象を取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 価格データがある銘柄一覧
                cursor.execute("SELECT DISTINCT symbol FROM stock_price_history")
                existing_symbols = {row[0] for row in cursor.fetchall()}
                
                # 有望な銘柄取得（アクティブ、主要市場優先）
                cursor.execute("""
                    SELECT symbol, name, exchange, country
                    FROM stock_master 
                    WHERE is_active = 1
                    AND (
                        (country = 'US' AND (exchange LIKE '%%NYSE%%' OR exchange LIKE '%%NASDAQ%%'))
                        OR (country = 'JP' AND exchange LIKE '%%Market%%' AND exchange LIKE '%%Domestic%%')
                        OR (exchange LIKE '%%ETF%%' OR name LIKE '%%ETF%%')
                        OR country IN ('UK', 'DE', 'FR', 'KR')
                    )
                    ORDER BY 
                        CASE 
                            WHEN country = 'US' THEN 1
                            WHEN country = 'JP' THEN 2
                            WHEN exchange LIKE '%%ETF%%' THEN 3
                            ELSE 4
                        END,
                        RAND()
                    LIMIT %s
                """, (limit * 2,))  # 多めに取得して後でフィルタ
                
                all_candidates = cursor.fetchall()
                
                # データなし銘柄のみ抽出
                promising_symbols = []
                for symbol, name, exchange, country in all_candidates:
                    if symbol not in existing_symbols:
                        promising_symbols.append((symbol, name, exchange, country))
                        if len(promising_symbols) >= limit:
                            break
                
                logger.info(f"📊 有望銘柄（データなし）: {len(promising_symbols)}銘柄選択")
                
                # 市場別統計
                market_counts = {}
                for symbol, name, exchange, country in promising_symbols:
                    if country == 'US':
                        market = 'US'
                    elif country == 'JP':
                        market = 'JP'
                    elif 'ETF' in str(exchange) or 'ETF' in str(name):
                        market = 'ETF'
                    else:
                        market = country or 'OTHER'
                    
                    market_counts[market] = market_counts.get(market, 0) + 1
                
                logger.info("🌍 対象市場:")
                for market, count in sorted(market_counts.items()):
                    logger.info(f"  {market}: {count}銘柄")
                
                return promising_symbols
                
        finally:
            connection.close()

    def prepare_yf_symbol(self, symbol: str, exchange: str, country: str) -> str:
        """Yahoo Finance用シンボル準備"""
        # 日本市場
        if country == 'JP' and len(symbol) == 4 and symbol.isdigit():
            return symbol + '.T'
        
        # 韓国市場
        elif country == 'KR' and not symbol.endswith('.KS'):
            return symbol + '.KS'
        
        # 英国市場
        elif country == 'UK' and not symbol.endswith('.L'):
            return symbol + '.L'
        
        # ドイツ市場
        elif country == 'DE' and not symbol.endswith('.DE'):
            return symbol + '.DE'
        
        # フランス市場
        elif country == 'FR' and not symbol.endswith('.PA'):
            return symbol + '.PA'
        
        return symbol

    def fetch_and_save_single_stock(self, stock_info) -> dict:
        """単一銘柄のデータ取得・保存"""
        symbol, name, exchange, country = stock_info
        yf_symbol = self.prepare_yf_symbol(symbol, exchange, country)
        
        try:
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return {'symbol': symbol, 'success': False, 'error': 'No data'}
            
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
                        symbol, latest_date,
                        float(latest_data['Open']),
                        float(latest_data['High']),
                        float(latest_data['Low']),
                        float(latest_data['Close']),
                        int(latest_data['Volume']),
                        f"Quick Collection - {country}"
                    ))
                    
                connection.commit()
                
                return {
                    'symbol': symbol,
                    'success': True,
                    'price': float(latest_data['Close']),
                    'date': latest_date,
                    'market': country
                }
                
            finally:
                connection.close()
                
        except Exception as e:
            return {'symbol': symbol, 'success': False, 'error': str(e)[:50]}

    def run_quick_collection(self, target_count: int = 500):
        """高速データ収集実行"""
        start_time = datetime.now()
        logger.info(f"🚀 高速データ収集開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 有望銘柄取得
        promising_symbols = self.get_promising_symbols_without_data(target_count)
        
        if not promising_symbols:
            logger.info("✅ 対象銘柄がありません")
            return
        
        logger.info(f"🎯 処理対象: {len(promising_symbols)}銘柄")
        
        # 並列処理実行
        results = []
        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_stock = {
                executor.submit(self.fetch_and_save_single_stock, stock): stock 
                for stock in promising_symbols
            }
            
            for future in as_completed(future_to_stock):
                result = future.result()
                results.append(result)
                
                self.stats["processed"] += 1
                
                if result['success']:
                    self.stats["successful"] += 1
                    market = result['market']
                    self.stats["by_market"][market] = self.stats["by_market"].get(market, 0) + 1
                    
                    if self.stats["successful"] % 50 == 0:
                        logger.info(f"✅ 進捗: {self.stats['successful']}/{self.stats['processed']} 成功")
                else:
                    self.stats["failed"] += 1
                
                time.sleep(0.05)  # レート制限
        
        # 最終レポート
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 60)
        logger.info("📊 高速データ収集完了レポート")
        logger.info(f"⏱️  実行時間: {duration:.1f}秒")
        logger.info(f"🎯 対象: {len(promising_symbols)}銘柄")
        logger.info(f"✅ 成功: {self.stats['successful']}銘柄")
        logger.info(f"❌ 失敗: {self.stats['failed']}銘柄")
        logger.info(f"📈 成功率: {(self.stats['successful']/self.stats['processed']*100):.1f}%")
        
        logger.info("🌍 市場別成功数:")
        for market, count in sorted(self.stats['by_market'].items()):
            logger.info(f"  {market}: {count}銘柄")
        
        if duration > 0:
            logger.info(f"⚡ 処理速度: {self.stats['processed']/duration:.1f}銘柄/秒")
        
        logger.info("=" * 60)
        
        return self.stats

if __name__ == "__main__":
    collector = QuickDataCollection()
    
    try:
        results = collector.run_quick_collection(target_count=1000)
        
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ システムエラー: {e}")
        import traceback
        traceback.print_exc()