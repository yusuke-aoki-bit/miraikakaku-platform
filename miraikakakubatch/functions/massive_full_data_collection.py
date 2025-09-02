#!/usr/bin/env python3
"""
大規模全銘柄データ収集システム
9,512銘柄すべてを対象とした包括的価格データ収集
"""

import yfinance as yf
import pymysql
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MassiveFullDataCollection:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user", 
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
        }
        self.stats = {
            "total_targets": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "by_market": {}
        }
        self.lock = threading.Lock()

    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def get_all_symbols_without_price_data(self) -> List[Tuple]:
        """価格データがないすべての銘柄を取得（コレーション安全版）"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 1. 価格データがある銘柄一覧を取得
                cursor.execute("SELECT DISTINCT symbol FROM stock_price_history")
                existing_symbols = {row[0] for row in cursor.fetchall()}
                logger.info(f"📊 価格データ保有銘柄: {len(existing_symbols):,}銘柄")
                
                # 2. 全銘柄データを取得
                cursor.execute("""
                    SELECT 
                        symbol,
                        name,
                        exchange,
                        country,
                        CASE 
                            WHEN exchange LIKE '%NYSE%' THEN 'US_NYSE'
                            WHEN exchange LIKE '%NASDAQ%' THEN 'US_NASDAQ'
                            WHEN exchange LIKE '%Market%' AND exchange LIKE '%Domestic%' THEN 'JP_MARKET'
                            WHEN exchange LIKE '%ETF%' OR name LIKE '%ETF%' THEN 'ETF'
                            WHEN country IN ('UK', 'DE', 'FR', 'CH') THEN 'EUROPE'
                            WHEN country = 'KR' THEN 'KOREA'
                            WHEN country = 'AU' THEN 'AUSTRALIA'
                            ELSE 'OTHER'
                        END as market_category
                    FROM stock_master
                    WHERE is_active = 1
                    ORDER BY RAND()
                """)
                
                all_symbols = cursor.fetchall()
                
                # 3. Python側でフィルタリング（価格データがない銘柄のみ）
                results = []
                for row in all_symbols:
                    symbol = row[0]
                    if symbol not in existing_symbols:
                        results.append(row)
                
                logger.info(f"📊 価格データなし銘柄: {len(results):,}銘柄発見")
                
                # 市場別統計
                market_counts = {}
                for row in results:
                    market = row[4]
                    market_counts[market] = market_counts.get(market, 0) + 1
                
                logger.info("🌍 市場別内訳:")
                for market, count in sorted(market_counts.items()):
                    logger.info(f"  {market}: {count:,}銘柄")
                
                return results
                
        finally:
            connection.close()

    def prepare_symbol_for_yfinance(self, symbol: str, exchange: str, country: str) -> str:
        """Yahoo Finance用のシンボル準備"""
        original_symbol = symbol
        
        # 日本市場
        if exchange and 'Market' in exchange and 'Domestic' in exchange:
            if len(symbol) == 4 and symbol.isdigit():
                return symbol + '.T'
        
        # 韓国市場
        elif country == 'KR':
            if not symbol.endswith('.KS'):
                return symbol + '.KS'
        
        # 英国市場
        elif country == 'UK':
            if not symbol.endswith('.L'):
                return symbol + '.L'
        
        # ドイツ市場
        elif country == 'DE':
            if not symbol.endswith('.DE'):
                return symbol + '.DE'
        
        # フランス市場
        elif country == 'FR':
            if not symbol.endswith('.PA'):
                return symbol + '.PA'
        
        # スイス市場
        elif country == 'CH':
            if not symbol.endswith('.SW'):
                return symbol + '.SW'
        
        # オーストラリア市場
        elif country == 'AU':
            if not symbol.endswith('.AX'):
                return symbol + '.AX'
        
        return original_symbol

    def fetch_single_symbol_data(self, symbol_data: Tuple) -> Dict:
        """単一銘柄のデータ取得"""
        symbol, name, exchange, country, market_category = symbol_data
        
        # Yahoo Finance用シンボル準備
        yf_symbol = self.prepare_symbol_for_yfinance(symbol, exchange, country)
        
        result = {
            'original_symbol': symbol,
            'yf_symbol': yf_symbol,
            'name': name[:100] if name else symbol,
            'market_category': market_category,
            'success': False,
            'error': None,
            'price_data': None
        }
        
        try:
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                result['error'] = 'No price data available'
                return result
            
            # 最新価格データ
            latest_data = hist.iloc[-1]
            latest_date = hist.index[-1].strftime('%Y-%m-%d')
            
            result['price_data'] = {
                'date': latest_date,
                'open': float(latest_data['Open']),
                'high': float(latest_data['High']),
                'low': float(latest_data['Low']),
                'close': float(latest_data['Close']),
                'volume': int(latest_data['Volume'])
            }
            
            result['success'] = True
            return result
            
        except Exception as e:
            result['error'] = str(e)[:100]
            return result

    def save_price_data(self, result: Dict) -> bool:
        """価格データをデータベースに保存"""
        if not result['success'] or not result['price_data']:
            return False
        
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                price = result['price_data']
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
                    result['original_symbol'],
                    price['date'],
                    price['open'],
                    price['high'],
                    price['low'],
                    price['close'],
                    price['volume'],
                    f"Massive Collection - {result['market_category']}"
                ))
                
            connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"DB保存エラー {result['original_symbol']}: {e}")
            return False
        finally:
            connection.close()

    def process_symbol_batch(self, symbol_batch: List[Tuple], batch_id: int):
        """銘柄バッチ処理"""
        logger.info(f"🔄 バッチ {batch_id} 開始: {len(symbol_batch)}銘柄")
        
        batch_stats = {"successful": 0, "failed": 0, "by_market": {}}
        
        for symbol_data in symbol_batch:
            # 価格データ取得
            result = self.fetch_single_symbol_data(symbol_data)
            
            # 統計更新
            with self.lock:
                self.stats["processed"] += 1
                
                if result['success']:
                    # データベース保存
                    if self.save_price_data(result):
                        self.stats["successful"] += 1
                        batch_stats["successful"] += 1
                        
                        # 市場別統計
                        market = result['market_category']
                        self.stats["by_market"][market] = self.stats["by_market"].get(market, 0) + 1
                        batch_stats["by_market"][market] = batch_stats["by_market"].get(market, 0) + 1
                        
                        if self.stats["successful"] % 100 == 0:
                            logger.info(f"✅ 進捗: {self.stats['successful']:,}銘柄成功 / {self.stats['processed']:,}処理済み")
                    else:
                        self.stats["failed"] += 1
                        batch_stats["failed"] += 1
                else:
                    self.stats["failed"] += 1
                    batch_stats["failed"] += 1
            
            # レート制限
            time.sleep(0.1)
        
        logger.info(f"✅ バッチ {batch_id} 完了: 成功{batch_stats['successful']}, 失敗{batch_stats['failed']}")

    def run_massive_collection(self, max_workers: int = 4, batch_size: int = 100):
        """大規模全銘柄収集実行"""
        start_time = datetime.now()
        logger.info(f"🚀 大規模全銘柄データ収集開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 対象銘柄取得
        target_symbols = self.get_all_symbols_without_price_data()
        
        if not target_symbols:
            logger.info("✅ すべての銘柄に価格データが存在します")
            return
        
        self.stats["total_targets"] = len(target_symbols)
        logger.info(f"📊 対象銘柄: {len(target_symbols):,}銘柄")
        
        # バッチに分割
        batches = []
        for i in range(0, len(target_symbols), batch_size):
            batch = target_symbols[i:i + batch_size]
            batches.append(batch)
        
        logger.info(f"🔄 {len(batches)}バッチで並列処理実行（最大{max_workers}スレッド）")
        
        # 並列処理実行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for batch_id, batch in enumerate(batches, 1):
                future = executor.submit(self.process_symbol_batch, batch, batch_id)
                futures.append(future)
                time.sleep(0.5)  # バッチ間の間隔
            
            # すべてのバッチ完了を待機
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"バッチ処理エラー: {e}")
        
        # 最終レポート
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("📊 大規模全銘柄データ収集完了レポート")
        logger.info("=" * 80)
        logger.info(f"⏱️  実行時間: {duration:.0f}秒 ({duration/60:.1f}分)")
        logger.info(f"🎯 対象銘柄: {self.stats['total_targets']:,}銘柄")
        logger.info(f"📊 処理済み: {self.stats['processed']:,}銘柄")
        logger.info(f"✅ 成功: {self.stats['successful']:,}銘柄")
        logger.info(f"❌ 失敗: {self.stats['failed']:,}銘柄")
        
        if self.stats['processed'] > 0:
            success_rate = (self.stats['successful'] / self.stats['processed']) * 100
            logger.info(f"📈 成功率: {success_rate:.1f}%")
        
        logger.info("🌍 市場別成功数:")
        for market, count in sorted(self.stats['by_market'].items()):
            logger.info(f"  {market}: {count:,}銘柄")
        
        # 処理速度
        if duration > 0:
            speed = self.stats['processed'] / duration
            logger.info(f"⚡ 処理速度: {speed:.1f}銘柄/秒")
        
        logger.info("=" * 80)
        
        return self.stats

if __name__ == "__main__":
    collector = MassiveFullDataCollection()
    
    try:
        # 大規模収集実行（4スレッド、100銘柄/バッチ）
        results = collector.run_massive_collection(max_workers=4, batch_size=100)
        
        # 最終状況確認
        logger.info("\n🔍 収集後のデータベース状況確認中...")
        connection = pymysql.connect(**collector.db_config)
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT COUNT(DISTINCT symbol) FROM stock_price_history')
                final_count = cursor.fetchone()[0]
                logger.info(f"📊 最終価格データ保有銘柄数: {final_count:,}銘柄")
        finally:
            connection.close()
        
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
        logger.info(f"⏸️ 中断時点: {collector.stats['successful']:,}銘柄成功")
    except Exception as e:
        logger.error(f"❌ システムエラー: {e}")
        import traceback
        traceback.print_exc()