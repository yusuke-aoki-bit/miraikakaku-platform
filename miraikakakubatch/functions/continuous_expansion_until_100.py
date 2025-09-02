#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import yfinance as yf
import pandas as pd
import logging
import time
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContinuousExpansionUntil100:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user",
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
            "charset": "utf8mb4"
        }

    def get_current_coverage(self):
        """現在のカバー率を取得"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM stock_master WHERE is_active = 1")
                total = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(DISTINCT symbol) FROM stock_price_history 
                    WHERE data_source = 'yfinance'
                """)
                covered = cursor.fetchone()[0]
                
                coverage = (covered / total * 100) if total > 0 else 0
                return total, covered, coverage
        except Exception as e:
            logger.error(f"カバー率確認エラー: {e}")
            return 0, 0, 0
        finally:
            if 'connection' in locals():
                connection.close()

    def get_next_batch_symbols(self, batch_size=100):
        """次のバッチ対象銘柄を取得"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT sm.symbol, sm.name, sm.country, sm.exchange, sm.sector
                    FROM stock_master sm
                    WHERE sm.is_active = 1
                    AND sm.symbol NOT IN (
                        SELECT DISTINCT symbol FROM stock_price_history 
                        WHERE data_source = 'yfinance'
                    )
                    ORDER BY 
                        CASE 
                            WHEN sm.country IN ('US', 'United States') THEN 1
                            WHEN sm.country = 'Japan' THEN 2
                            WHEN sm.exchange IN ('NYSE', 'NASDAQ', 'TSE') THEN 3
                            ELSE 4
                        END,
                        RAND()
                    LIMIT %s
                """, (batch_size,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"バッチ銘柄取得エラー: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()

    def smart_yfinance_fetch(self, symbol_info):
        """スマートyfinance取得"""
        symbol, name, country, exchange, sector = symbol_info
        
        try:
            # シンボル変換
            if country == 'Japan' and symbol.isdigit() and len(symbol) >= 4:
                yf_symbol = f"{symbol}.T"
            elif symbol.endswith('=X'):
                yf_symbol = symbol
            elif exchange == 'LSE':
                yf_symbol = f"{symbol}.L"
            elif exchange == 'EPA' or 'Paris' in str(exchange):
                yf_symbol = f"{symbol}.PA"
            else:
                yf_symbol = symbol
            
            ticker = yf.Ticker(yf_symbol)
            
            # 短期間で高速取得
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            hist_data = ticker.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1d'
            )
            
            if hist_data.empty or len(hist_data) < 10:
                return {'symbol': symbol, 'status': 'no_data', 'data': None}
                
            price_data = []
            for date, row in hist_data.iterrows():
                try:
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
                        'data_quality_score': 0.96
                    })
                except (ValueError, OverflowError):
                    continue
            
            return {
                'symbol': symbol, 
                'status': 'success', 
                'data': price_data,
                'yf_symbol': yf_symbol,
                'count': len(price_data)
            }
            
        except Exception as e:
            return {'symbol': symbol, 'status': 'error', 'data': None, 'error': str(e)}

    def save_expansion_data(self, price_data_list):
        """拡張データ保存"""
        if not price_data_list:
            return 0
            
        try:
            connection = pymysql.connect(**self.db_config)
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
            logger.error(f"拡張保存エラー: {e}")
            return 0
        finally:
            if 'connection' in locals():
                connection.close()

    def continuous_expansion_cycle(self):
        """継続拡張サイクル"""
        cycle = 1
        
        while True:
            logger.info(f"🔄 継続拡張サイクル {cycle} 開始")
            
            # 現在のカバー率確認
            total, covered, coverage = self.get_current_coverage()
            logger.info(f"📊 現在のカバー率: {coverage:.1f}% ({covered:,}/{total:,})")
            
            if coverage >= 70.0:
                logger.info("🎯 70%目標達成！継続拡張完了")
                break
            
            if coverage >= 100.0:
                logger.info("🏆 100%カバー率達成！")
                break
            
            # 次のバッチ取得
            next_symbols = self.get_next_batch_symbols(batch_size=200)
            
            if not next_symbols:
                logger.info("⚠️ 処理対象銘柄なし - 継続拡張完了")
                break
            
            logger.info(f"📋 サイクル {cycle}: {len(next_symbols)}銘柄処理開始")
            
            # 並列処理
            successful = 0
            failed = 0
            all_data = []
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {
                    executor.submit(self.smart_yfinance_fetch, symbol_info): symbol_info[0]
                    for symbol_info in next_symbols
                }
                
                for future in as_completed(futures):
                    symbol = futures[future]
                    try:
                        result = future.result()
                        
                        if result['status'] == 'success':
                            successful += 1
                            all_data.extend(result['data'])
                            logger.info(f"✅ {symbol}: {result['count']}件")
                        else:
                            failed += 1
                            if result['status'] != 'no_data':
                                logger.warning(f"⚠️ {symbol}: {result['status']}")
                                
                    except Exception as e:
                        failed += 1
                        logger.error(f"❌ {symbol}: {e}")
            
            # データ保存
            if all_data:
                saved_count = self.save_expansion_data(all_data)
                logger.info(f"💾 サイクル {cycle} 保存: {saved_count:,}件")
            
            # サイクル結果
            success_rate = (successful / (successful + failed)) * 100 if (successful + failed) > 0 else 0
            logger.info(f"🔄 サイクル {cycle} 完了: 成功{successful}, 失敗{failed} ({success_rate:.1f}%)")
            
            # 成功がない場合は終了
            if successful == 0:
                logger.info("⚠️ 成功銘柄なし - 継続拡張終了")
                break
            
            cycle += 1
            
            # サイクル間の待機
            time.sleep(2.0)
        
        # 最終評価
        logger.info("📊 継続拡張終了 - 最終評価実行中...")
        import subprocess
        subprocess.run(["python3", "collation_safe_data_assessment.py"])

def main():
    logger.info("🚀 継続拡張システム開始 - 70%目標まで実行")
    
    expander = ContinuousExpansionUntil100()
    expander.continuous_expansion_cycle()

if __name__ == "__main__":
    main()