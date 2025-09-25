#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import yfinance as yf
import pandas as pd
import logging
import time
import asyncio
import aiohttp
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RapidBatchRealDataCollector:
    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres",
            "password": "miraikakaku-postgres-secure-2024",
            "database": "miraikakaku",
            "port": 5432
        }
        self.lock = threading.Lock()
        self.batch_results = []

    def get_high_priority_missing_symbols(self, limit=500):
        """高優先度で未処理銘柄を取得"""
        try:
            connection = psycopg2.connect(**self.db_config)
            with connection.cursor() as cursor:
                # 優先度付き銘柄取得（US, 日本, 主要取引所優先）
                cursor.execute("""
                    SELECT sm.symbol, sm.name, sm.country, sm.exchange, sm.sector
                    FROM stock_master sm
                    WHERE sm.is_active = 1 
                    AND sm.symbol NOT IN (
                        SELECT DISTINCT symbol FROM stock_price_history 
                        WHERE data_source = 'yfinance' AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    )
                    ORDER BY 
                        CASE 
                            WHEN sm.country IN ('US', 'United States') THEN 1
                            WHEN sm.country = 'Japan' THEN 2
                            WHEN sm.exchange IN ('NYSE', 'NASDAQ', 'TSE', 'LSE') THEN 3
                            ELSE 4
                        END,
                        CASE 
                            WHEN sm.sector IN ('Technology', 'Healthcare', 'Finance') THEN 1
                            WHEN sm.sector IN ('Energy', 'Consumer', 'Industrial') THEN 2
                            ELSE 3
                        END,
                        CHAR_LENGTH(sm.symbol) ASC,
                        sm.symbol
                    LIMIT %s
                """, (limit,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"優先度銘柄取得エラー: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()

    def smart_symbol_conversion(self, symbol, country, exchange):
        """スマートなシンボル変換"""
        # 日本株
        if country == 'Japan' or exchange == 'TSE':
            if symbol.isdigit() and len(symbol) >= 4:
                return f"{symbol}.T"
        
        # 通貨ペア
        if symbol.endswith('=X') or 'USD' in symbol or 'EUR' in symbol:
            return symbol
        
        # 欧州株
        european_exchanges = ['LSE', 'EPA', 'AMS', 'SWX', 'FRA']
        if exchange in european_exchanges:
            if exchange == 'LSE':
                return f"{symbol}.L"
            elif exchange == 'EPA':
                return f"{symbol}.PA"
            elif exchange == 'AMS':
                return f"{symbol}.AS"
        
        # デフォルトはそのまま（US株）
        return symbol

    def fetch_yfinance_optimized(self, symbol_info):
        """最適化されたyfinanceデータ取得"""
        symbol, name, country, exchange, sector = symbol_info
        
        try:
            # シンボル変換
            yf_symbol = self.smart_symbol_conversion(symbol, country, exchange)
            
            # yfinance ticker取得
            ticker = yf.Ticker(yf_symbol)
            
            # 期間設定（過去6ヶ月で高速化）
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            # データ取得（複数試行）
            hist_data = None
            for attempt in range(2):  # 試行回数削減
                try:
                    hist_data = ticker.history(
                        start=start_date.strftime('%Y-%m-%d'),
                        end=end_date.strftime('%Y-%m-%d'),
                        interval='1d',
                        auto_adjust=True,
                        prepost=False
                    )
                    if not hist_data.empty:
                        break
                except Exception as e:
                    if attempt == 0:
                        time.sleep(0.5)
                    continue
            
            if hist_data is None or hist_data.empty:
                return {'symbol': symbol, 'status': 'no_data', 'data': None, 'count': 0}
                
            # データ処理
            price_data = []
            for date, row in hist_data.iterrows():
                try:
                    # 基本検証
                    values = [row['Open'], row['High'], row['Low'], row['Close'], row['Volume']]
                    if any(pd.isna(values)) or any(v <= 0 for v in values[:4]) or row['Volume'] < 0:
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
                except (ValueError, OverflowError, KeyError):
                    continue
            
            if len(price_data) >= 30:  # 最低30日分のデータがある場合のみ成功
                return {
                    'symbol': symbol, 
                    'status': 'success', 
                    'data': price_data, 
                    'count': len(price_data),
                    'yf_symbol': yf_symbol
                }
            else:
                return {'symbol': symbol, 'status': 'insufficient_data', 'data': None, 'count': len(price_data)}
                
        except Exception as e:
            return {'symbol': symbol, 'status': 'error', 'data': None, 'count': 0, 'error': str(e)}

    def save_batch_data_optimized(self, batch_data):
        """最適化されたバッチデータ保存"""
        if not batch_data:
            return 0
            
        try:
            connection = psycopg2.connect(**self.db_config)
            with connection.cursor() as cursor:
                insert_data = []
                for data in batch_data:
                    insert_data.append((
                        data['symbol'], data['date'],
                        data['open_price'], data['high_price'],
                        data['low_price'], data['close_price'],
                        data['volume'], data['adjusted_close'],
                        data['data_source'], data['is_valid'],
                        data['data_quality_score']
                    ))
                
                # 大容量一括挿入
                cursor.executemany("""
                    INSERT IGNORE INTO stock_price_history 
                    (symbol, date, open_price, high_price, low_price, close_price,
                     volume, adjusted_close, data_source, is_valid, data_quality_score, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, insert_data)
                
                connection.commit()
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"バッチ保存エラー: {e}")
            return 0
        finally:
            if 'connection' in locals():
                connection.close()

    def process_symbol_batch(self, symbol_batch):
        """シンボルバッチの並列処理"""
        batch_results = []
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            # 並列でyfinanceデータ取得
            futures = {
                executor.submit(self.fetch_yfinance_optimized, symbol_info): symbol_info[0]
                for symbol_info in symbol_batch
            }
            
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    result = future.result()
                    batch_results.append(result)
                    
                    if result['status'] == 'success':
                        logger.info(f"✅ {symbol}: {result['count']}件取得 ({result.get('yf_symbol', symbol)})")
                    else:
                        logger.warning(f"⚠️ {symbol}: {result['status']}")
                        
                except Exception as e:
                    logger.error(f"❌ {symbol}: 処理エラー - {e}")
                    batch_results.append({'symbol': symbol, 'status': 'error', 'data': None})
        
        return batch_results

    def rapid_collect_real_data(self, target_symbols=1000, batch_size=50):
        """高速実データ収集"""
        logger.info(f"🚀 高速実データ収集開始 - 目標: {target_symbols}銘柄")
        
        # 高優先度銘柄取得
        missing_symbols = self.get_high_priority_missing_symbols(target_symbols)
        logger.info(f"📋 高優先度対象: {len(missing_symbols)}銘柄")
        
        if not missing_symbols:
            logger.info("⚠️ 処理対象銘柄なし")
            return {'total': 0, 'successful': 0, 'failed': 0, 'total_records': 0}
        
        # バッチ処理
        total_successful = 0
        total_failed = 0
        total_records = 0
        
        for batch_start in range(0, len(missing_symbols), batch_size):
            batch_end = min(batch_start + batch_size, len(missing_symbols))
            symbol_batch = missing_symbols[batch_start:batch_end]
            
            logger.info(f"📦 バッチ処理 {batch_start//batch_size + 1}: {len(symbol_batch)}銘柄")
            
            # バッチ処理実行
            batch_results = self.process_symbol_batch(symbol_batch)
            
            # 成功データの一括保存
            successful_data = []
            batch_successful = 0
            batch_failed = 0
            
            for result in batch_results:
                if result['status'] == 'success' and result['data']:
                    successful_data.extend(result['data'])
                    batch_successful += 1
                else:
                    batch_failed += 1
            
            # バッチ保存
            if successful_data:
                saved_count = self.save_batch_data_optimized(successful_data)
                total_records += saved_count
                logger.info(f"💾 バッチ保存: {saved_count:,}件 ({len(successful_data):,}件中)")
            
            total_successful += batch_successful
            total_failed += batch_failed
            
            # 進捗報告
            progress = ((batch_end) / len(missing_symbols)) * 100
            success_rate = (total_successful / (total_successful + total_failed)) * 100 if (total_successful + total_failed) > 0 else 0
            
            logger.info(f"📈 進捗: {progress:.1f}% | 成功: {total_successful}, 失敗: {total_failed} | 成功率: {success_rate:.1f}%")
            logger.info(f"📊 累積データ: {total_records:,}件")
            
            # レート制限対応（バッチ間）
            time.sleep(1.0)
        
        # 最終結果
        total_processed = total_successful + total_failed
        final_success_rate = (total_successful / total_processed * 100) if total_processed > 0 else 0
        
        logger.info(f"🎯 高速実データ収集完了:")
        logger.info(f"   - 処理銘柄: {total_processed}")
        logger.info(f"   - 成功銘柄: {total_successful} ({final_success_rate:.1f}%)")
        logger.info(f"   - 失敗銘柄: {total_failed}")
        logger.info(f"   - 収集データ: {total_records:,}件")
        
        return {
            'total': total_processed,
            'successful': total_successful,
            'failed': total_failed,
            'total_records': total_records,
            'success_rate': final_success_rate
        }

def main():
    logger.info("🔥 高速バッチ実データ収集システム開始")
    
    collector = RapidBatchRealDataCollector()
    
    # 高速バッチ収集実行（500銘柄、バッチサイズ50）
    result = collector.rapid_collect_real_data(target_symbols=500, batch_size=50)
    
    if result['successful'] > 0:
        logger.info("✅ 高速バッチ収集成功 - 評価実行中...")
        
        # 収集後の評価
        import subprocess
        subprocess.run(["python3", "collation_safe_data_assessment.py"])
    else:
        logger.error("❌ 高速バッチ収集失敗")

if __name__ == "__main__":
    main()