#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import yfinance as yf
import logging
import time
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedRealDataExpansion:
    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres",
            "password": "miraikakaku-postgres-secure-2024", 
            "database": "miraikakaku",
            "port": 5432
        }

    def get_missing_symbols_optimized(self, limit=500):
        """価格データ不足銘柄を優先度順で取得"""
        try:
            connection = psycopg2.connect(**self.db_config)
            with connection.cursor() as cursor:
                # 価格データがない銘柄を優先度順で取得
                cursor.execute("""
                    SELECT symbol, name, country, exchange, sector 
                    FROM stock_master 
                    WHERE is_active = 1 
                    AND symbol NOT IN (
                        SELECT DISTINCT symbol FROM stock_price_history 
                        WHERE data_source = 'yfinance'
                    )
                    ORDER BY 
                        CASE 
                            WHEN country IN ('US', 'United States') THEN 1
                            WHEN country = 'Japan' THEN 2
                            WHEN exchange IN ('NYSE', 'NASDAQ', 'TSE') THEN 3
                            ELSE 4
                        END,
                        RAND()
                    LIMIT %s
                """, (limit,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"銘柄取得エラー: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()

    def fetch_yfinance_data_smart(self, symbol, country=None):
        """改良版yfinanceデータ取得"""
        try:
            # シンボル変換ロジック
            if country == 'Japan' and symbol.isdigit() and len(symbol) >= 4:
                yf_symbol = f"{symbol}.T"
            elif symbol.endswith('=X'):  # 通貨ペア
                yf_symbol = symbol
            else:
                yf_symbol = symbol
            
            # yfinance使用
            ticker = yf.Ticker(yf_symbol)
            
            # 過去1年分のデータ取得
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            # データ取得（複数試行）
            hist_data = None
            for attempt in range(3):
                try:
                    hist_data = ticker.history(
                        start=start_date.strftime('%Y-%m-%d'),
                        end=end_date.strftime('%Y-%m-%d'),
                        interval='1d'
                    )
                    if not hist_data.empty:
                        break
                except Exception as e:
                    logger.warning(f"yfinance試行{attempt+1}: {yf_symbol} - {e}")
                    time.sleep(1)
            
            if hist_data is None or hist_data.empty:
                return None
                
            # データ処理
            price_data = []
            for date, row in hist_data.iterrows():
                try:
                    if any(pd.isna([row['Open'], row['High'], row['Low'], row['Close'], row['Volume']])):
                        continue
                    
                    price_data.append({
                        'symbol': symbol,
                        'date': date.strftime('%Y-%m-%d'),
                        'open_price': float(row['Open']),
                        'high_price': float(row['High']),
                        'low_price': float(row['Low']),
                        'close_price': float(row['Close']),
                        'adjusted_close': float(row['Close']),
                        'volume': int(row['Volume']),
                        'data_source': 'yfinance',
                        'is_valid': 1,
                        'data_quality_score': 0.95
                    })
                except Exception as e:
                    continue
            
            logger.info(f"✅ {symbol}({yf_symbol}): {len(price_data)}件取得")
            return price_data
            
        except Exception as e:
            logger.warning(f"❌ {symbol}: yfinance取得失敗 - {e}")
            return None

    def save_price_data_batch(self, price_data_list):
        """価格データの効率的保存"""
        if not price_data_list:
            return 0
            
        try:
            connection = psycopg2.connect(**self.db_config)
            with connection.cursor() as cursor:
                insert_data = []
                for data in price_data_list:
                    insert_data.append((
                        data['symbol'], data['date'],
                        data['open_price'], data['high_price'],
                        data['low_price'], data['close_price'],
                        data['volume'], data['adjusted_close'],
                        data['data_source'], data['is_valid'],
                        data['data_quality_score']
                    ))
                
                cursor.executemany("""
                    INSERT IGNORE INTO stock_price_history 
                    (symbol, date, open_price, high_price, low_price, close_price,
                     volume, adjusted_close, data_source, is_valid, data_quality_score, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, insert_data)
                
                connection.commit()
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"保存エラー: {e}")
            return 0
        finally:
            if 'connection' in locals():
                connection.close()

    def process_symbol(self, symbol_info):
        """単一銘柄の処理"""
        symbol, name, country, exchange, sector = symbol_info
        
        try:
            # 価格データ取得
            price_data = self.fetch_yfinance_data_smart(symbol, country)
            
            if price_data and len(price_data) > 0:
                # データ保存
                saved_count = self.save_price_data_batch(price_data)
                if saved_count > 0:
                    return {
                        'symbol': symbol,
                        'status': 'success',
                        'records': saved_count,
                        'message': f"{saved_count}件保存"
                    }
                else:
                    return {
                        'symbol': symbol,
                        'status': 'save_failed',
                        'records': 0,
                        'message': "保存失敗"
                    }
            else:
                return {
                    'symbol': symbol,
                    'status': 'no_data',
                    'records': 0,
                    'message': "データ取得失敗"
                }
                
        except Exception as e:
            return {
                'symbol': symbol,
                'status': 'error',
                'records': 0,
                'message': str(e)
            }

    def expand_real_data_optimized(self, target_symbols=500, max_workers=8):
        """最適化された実データ拡張"""
        logger.info(f"🚀 最適化実データ拡張開始 - 目標: {target_symbols}銘柄")
        
        # 不足銘柄取得
        missing_symbols = self.get_missing_symbols_optimized(target_symbols)
        logger.info(f"📋 処理対象: {len(missing_symbols)}銘柄")
        
        if not missing_symbols:
            logger.info("⚠️ 処理対象銘柄なし")
            return {'total_processed': 0, 'successful': 0, 'failed': 0}
        
        # 並列処理
        results = {
            'total_processed': 0,
            'successful': 0, 
            'failed': 0,
            'total_records': 0,
            'details': []
        }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # タスク送信
            future_to_symbol = {
                executor.submit(self.process_symbol, symbol_info): symbol_info[0] 
                for symbol_info in missing_symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    results['total_processed'] += 1
                    results['details'].append(result)
                    
                    if result['status'] == 'success':
                        results['successful'] += 1
                        results['total_records'] += result['records']
                        logger.info(f"✅ {symbol}: {result['records']}件保存")
                    else:
                        results['failed'] += 1
                        logger.warning(f"⚠️ {symbol}: {result['message']}")
                    
                    # 進捗報告
                    if results['total_processed'] % 50 == 0:
                        progress = (results['total_processed'] / len(missing_symbols)) * 100
                        success_rate = (results['successful'] / results['total_processed']) * 100
                        logger.info(f"📈 進捗: {progress:.1f}% | 成功率: {success_rate:.1f}% | データ: {results['total_records']:,}件")
                    
                    # API制限対策
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"❌ {symbol}: 処理エラー - {e}")
                    results['failed'] += 1
        
        # 最終結果
        success_rate = (results['successful'] / results['total_processed'] * 100) if results['total_processed'] > 0 else 0
        logger.info(f"🎯 最適化実データ拡張完了:")
        logger.info(f"   - 処理銘柄: {results['total_processed']}")
        logger.info(f"   - 成功銘柄: {results['successful']} ({success_rate:.1f}%)")
        logger.info(f"   - 失敗銘柄: {results['failed']}")
        logger.info(f"   - 収集データ: {results['total_records']:,}件")
        
        return results

def main():
    logger.info("🔥 最適化実データ拡張システム開始")
    
    expander = OptimizedRealDataExpansion()
    
    # 段階的拡張: まず300銘柄
    result = expander.expand_real_data_optimized(target_symbols=300, max_workers=6)
    
    if result['successful'] > 0:
        logger.info("✅ 最適化実データ拡張成功")
        
        # 拡張後の状況評価
        logger.info("📊 拡張後データ状況評価中...")
        import subprocess
        subprocess.run([
            "python3", 
            "collation_safe_data_assessment.py"
        ])
    else:
        logger.error("❌ 実データ拡張失敗")

if __name__ == "__main__":
    main()