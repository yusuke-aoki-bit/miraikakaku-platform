#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import yfinance as yf
import pandas as pd
import logging
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TurboReliableExpansion:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user",
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
            "charset": "utf8mb4"
        }
        
        # 超高確率成功銘柄（Fortune 500 + 主要インデックス）
        self.turbo_symbols = [
            # Mega Cap Tech
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
            'NFLX', 'ADBE', 'CRM', 'INTC', 'AMD', 'QCOM', 'AVGO',
            
            # Major Banks & Finance
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW',
            'USB', 'PNC', 'TFC', 'COF', 'CME', 'ICE', 'SPGI', 'MCO',
            
            # Healthcare Giants
            'JNJ', 'PFE', 'UNH', 'MRK', 'ABBV', 'TMO', 'ABT', 'LLY',
            'BMY', 'AMGN', 'GILD', 'MDT', 'DHR', 'SYK', 'BSX', 'ZTS',
            
            # Consumer Staples
            'PG', 'KO', 'PEP', 'WMT', 'COST', 'MCD', 'SBUX', 'NKE',
            'TGT', 'HD', 'LOW', 'TJX', 'MDLZ', 'CL', 'KMB', 'GIS',
            
            # Energy & Utilities
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC',
            'NEE', 'SO', 'DUK', 'AEP', 'EXC', 'XEL', 'SRE', 'D',
            
            # Industrial
            'CAT', 'BA', 'GE', 'MMM', 'HON', 'UPS', 'FDX', 'RTX',
            'LMT', 'NOC', 'DE', 'EMR', 'ITW', 'CSX', 'NSC', 'UNP',
            
            # Major ETFs
            'SPY', 'QQQ', 'IWM', 'VTI', 'VTV', 'VUG', 'VEA', 'VWO',
            'GLD', 'SLV', 'TLT', 'IEF', 'LQD', 'HYG', 'AGG', 'BND',
            
            # Popular Growth
            'ROKU', 'ZM', 'SHOP', 'SQ', 'PYPL', 'SNAP', 'TWTR', 'UBER',
            'LYFT', 'ABNB', 'COIN', 'HOOD', 'RBLX', 'PLTR', 'SNOW',
            
            # 日本主要株（確実取得可能）
            '7203.T', '6758.T', '9984.T', '8306.T', '9432.T', '6861.T',
            '7267.T', '8316.T', '4063.T', '9020.T', '6098.T', '4519.T'
        ]

    def get_missing_turbo_symbols(self):
        """ターボ銘柄の未取得リストを作成"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                # 既存のyfinanceデータがある銘柄を取得
                cursor.execute("""
                    SELECT DISTINCT symbol FROM stock_price_history 
                    WHERE data_source = 'yfinance'
                """)
                existing = {row[0] for row in cursor.fetchall()}
                
                # 未取得の銘柄をフィルタ
                missing = [s for s in self.turbo_symbols if s not in existing]
                return missing
                
        except Exception as e:
            logger.error(f"ターボ銘柄確認エラー: {e}")
            return self.turbo_symbols
        finally:
            if 'connection' in locals():
                connection.close()

    def turbo_fetch_yfinance(self, symbol):
        """ターボモードyfinance取得（最適化済み）"""
        try:
            ticker = yf.Ticker(symbol)
            
            # 3ヶ月データで超高速化
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            hist_data = ticker.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1d',
                auto_adjust=True,
                prepost=False,
                repair=True
            )
            
            if hist_data.empty or len(hist_data) < 10:
                return None
                
            price_data = []
            for date, row in hist_data.iterrows():
                try:
                    # 最小限の検証
                    if pd.isna([row['Open'], row['Close'], row['Volume']]).any():
                        continue
                        
                    if row['Open'] <= 0 or row['Close'] <= 0:
                        continue
                    
                    price_data.append({
                        'symbol': symbol,
                        'date': date.strftime('%Y-%m-%d'),
                        'open_price': float(row['Open']),
                        'high_price': float(row['High']) if not pd.isna(row['High']) else float(row['Open']),
                        'low_price': float(row['Low']) if not pd.isna(row['Low']) else float(row['Open']),
                        'close_price': float(row['Close']),
                        'adjusted_close': float(row['Close']),
                        'volume': int(max(row['Volume'], 0)) if not pd.isna(row['Volume']) else 0,
                        'data_source': 'yfinance',
                        'is_valid': 1,
                        'data_quality_score': 0.98
                    })
                except (ValueError, OverflowError):
                    continue
            
            return price_data if len(price_data) >= 10 else None
            
        except Exception as e:
            logger.warning(f"ターボ取得失敗 {symbol}: {e}")
            return None

    def turbo_add_to_master(self, symbols_batch):
        """ターボ銘柄一括master追加"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                insert_data = []
                for symbol in symbols_batch:
                    if symbol.endswith('.T'):
                        country, exchange = 'Japan', 'TSE'
                        name = f"JP-{symbol.replace('.T', '')}"
                    elif symbol in ['SPY', 'QQQ', 'GLD', 'TLT']:
                        country, exchange = 'US', 'NYSE'
                        name = f"ETF-{symbol}"
                    else:
                        country, exchange = 'US', 'NYSE/NASDAQ'
                        name = f"US-{symbol}"
                    
                    insert_data.append((symbol, name, country, exchange))
                
                cursor.executemany("""
                    INSERT IGNORE INTO stock_master 
                    (symbol, name, country, exchange, sector, is_active)
                    VALUES (%s, %s, %s, %s, 'Major', 1)
                """, insert_data)
                
                connection.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"ターボmaster追加エラー: {e}")
            return 0
        finally:
            if 'connection' in locals():
                connection.close()

    def turbo_save_batch(self, all_price_data):
        """ターボ一括保存"""
        if not all_price_data:
            return 0
            
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                insert_data = []
                for data in all_price_data:
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
            logger.error(f"ターボ保存エラー: {e}")
            return 0
        finally:
            if 'connection' in locals():
                connection.close()

    def turbo_parallel_expansion(self, max_workers=10):
        """ターボ並列拡張"""
        logger.info("🚀 ターボ並列拡張開始")
        
        # 未取得銘柄確認
        missing_symbols = self.get_missing_turbo_symbols()
        logger.info(f"⚡ ターボ対象銘柄: {len(missing_symbols)}銘柄")
        
        if not missing_symbols:
            logger.info("✅ 全ターボ銘柄が既に存在")
            return {'total': 0, 'successful': 0, 'failed': 0, 'total_records': 0}
        
        # master追加
        self.turbo_add_to_master(missing_symbols)
        
        successful = 0
        failed = 0
        all_price_data = []
        
        # 並列取得
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.turbo_fetch_yfinance, symbol): symbol 
                for symbol in missing_symbols
            }
            
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    result = future.result()
                    
                    if result:
                        successful += 1
                        all_price_data.extend(result)
                        logger.info(f"⚡ {symbol}: {len(result)}件取得")
                    else:
                        failed += 1
                        logger.warning(f"⚠️ {symbol}: 取得失敗")
                        
                except Exception as e:
                    failed += 1
                    logger.error(f"❌ {symbol}: エラー - {e}")
        
        # 一括保存
        total_records = 0
        if all_price_data:
            total_records = self.turbo_save_batch(all_price_data)
            logger.info(f"💾 一括保存: {total_records:,}件")
        
        # 結果
        total_processed = successful + failed
        success_rate = (successful / total_processed * 100) if total_processed > 0 else 0
        
        logger.info(f"🎯 ターボ並列拡張完了:")
        logger.info(f"   - 処理銘柄: {total_processed}")
        logger.info(f"   - 成功銘柄: {successful} ({success_rate:.1f}%)")
        logger.info(f"   - 失敗銘柄: {failed}")
        logger.info(f"   - 収集データ: {total_records:,}件")
        
        return {
            'total': total_processed,
            'successful': successful,
            'failed': failed,
            'total_records': total_records,
            'success_rate': success_rate
        }

def main():
    logger.info("🚀 ターボ並列拡張システム開始")
    
    expander = TurboReliableExpansion()
    result = expander.turbo_parallel_expansion(max_workers=10)
    
    if result['total_records'] > 0:
        logger.info("✅ ターボ拡張成功 - 評価実行中...")
        
        # 評価
        import subprocess
        subprocess.run(["python3", "collation_safe_data_assessment.py"])
    else:
        logger.info("ℹ️ ターボ拡張完了（新規データなし）")

if __name__ == "__main__":
    main()