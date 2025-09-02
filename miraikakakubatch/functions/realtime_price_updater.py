#!/usr/bin/env python3
"""
リアルタイム価格更新システム - Yahoo Finance API使用
"""

import pymysql
import yfinance as yf
import logging
from datetime import datetime, timedelta
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealtimePriceUpdater:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user",
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
            "charset": "utf8mb4"
        }
    
    def update_realtime_prices(self, batch_size=500, max_symbols=2000):
        """リアルタイム価格更新"""
        connection = pymysql.connect(**self.db_config)
        
        try:
            with connection.cursor() as cursor:
                logger.info("📈 リアルタイム価格更新開始")
                
                # アクティブ銘柄取得（優先度順）
                cursor.execute("""
                    SELECT symbol FROM stock_master 
                    WHERE is_active = 1 
                    AND symbol LIKE '%.%' = FALSE
                    ORDER BY 
                        CASE WHEN symbol RLIKE '^[A-Z]{1,5}$' THEN 1 ELSE 2 END,
                        CHAR_LENGTH(symbol),
                        symbol
                    LIMIT %s
                """, (max_symbols,))
                
                symbols = [row[0] for row in cursor.fetchall()]
                logger.info(f"🎯 更新対象: {len(symbols):,}銘柄")
                
                # バッチ処理
                total_updated = 0
                total_errors = 0
                
                for batch_start in range(0, len(symbols), batch_size):
                    batch_symbols = symbols[batch_start:batch_start + batch_size]
                    
                    # 並列処理で価格取得
                    updated_count, error_count = self.process_batch_parallel(cursor, batch_symbols)
                    total_updated += updated_count
                    total_errors += error_count
                    
                    connection.commit()
                    
                    progress = ((batch_start + len(batch_symbols)) / len(symbols)) * 100
                    logger.info(f"📊 進捗: {progress:.1f}% (更新{total_updated:,}件, エラー{total_errors}件)")
                    
                    # API制限対策
                    time.sleep(1)
                
                logger.info(f"✅ リアルタイム更新完了: 成功{total_updated:,}件, エラー{total_errors}件")
                return total_updated
                
        except Exception as e:
            logger.error(f"❌ リアルタイム更新エラー: {e}")
            return 0
        finally:
            connection.close()
    
    def process_batch_parallel(self, cursor, symbols):
        """並列バッチ処理"""
        updated_count = 0
        error_count = 0
        
        # 並列度を制限してAPI制限を回避
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {
                executor.submit(self.fetch_single_price, symbol): symbol 
                for symbol in symbols
            }
            
            price_updates = []
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    price_data = future.result()
                    if price_data:
                        price_updates.append(price_data)
                        updated_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ {symbol}: {e}")
                    error_count += 1
            
            # バッチ挿入
            if price_updates:
                self.batch_insert_prices(cursor, price_updates)
        
        return updated_count, error_count
    
    def fetch_single_price(self, symbol):
        """個別銘柄の価格取得"""
        try:
            ticker = yf.Ticker(symbol)
            
            # 過去2日のデータ取得（最新を確保）
            hist = ticker.history(period="2d", interval="1d")
            
            if hist.empty:
                return None
            
            # 最新データを取得
            latest_data = hist.iloc[-1]
            latest_date = hist.index[-1].date()
            
            return {
                'symbol': symbol,
                'date': latest_date,
                'open': round(float(latest_data['Open']), 2),
                'high': round(float(latest_data['High']), 2),
                'low': round(float(latest_data['Low']), 2),
                'close': round(float(latest_data['Close']), 2),
                'volume': int(latest_data['Volume'])
            }
            
        except Exception as e:
            logger.debug(f"🔍 {symbol}: 取得失敗 - {e}")
            return None
    
    def batch_insert_prices(self, cursor, price_data_list):
        """価格データのバッチ挿入"""
        try:
            insert_data = []
            for data in price_data_list:
                insert_data.append((
                    data['symbol'], data['date'], data['open'], data['high'],
                    data['low'], data['close'], data['volume']
                ))
            
            cursor.executemany("""
                INSERT INTO stock_price_history 
                (symbol, date, open_price, high_price, low_price, close_price, volume, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                open_price = VALUES(open_price),
                high_price = VALUES(high_price),
                low_price = VALUES(low_price), 
                close_price = VALUES(close_price),
                volume = VALUES(volume),
                updated_at = NOW()
            """, insert_data)
            
        except Exception as e:
            logger.error(f"❌ バッチ挿入エラー: {e}")
    
    def update_missing_symbols_only(self):
        """価格データが不足している銘柄のみ更新"""
        connection = pymysql.connect(**self.db_config)
        
        try:
            with connection.cursor() as cursor:
                logger.info("🎯 不足データ優先更新開始")
                
                # 価格データが古いか存在しない銘柄を特定
                cursor.execute("""
                    SELECT DISTINCT sm.symbol 
                    FROM stock_master sm
                    LEFT JOIN stock_price_history ph ON sm.symbol = ph.symbol
                    WHERE sm.is_active = 1 
                    AND (ph.symbol IS NULL OR ph.date < DATE_SUB(CURDATE(), INTERVAL 3 DAY))
                    AND sm.symbol RLIKE '^[A-Z]{1,5}$'
                    ORDER BY sm.symbol
                    LIMIT 1000
                """)
                
                missing_symbols = [row[0] for row in cursor.fetchall()]
                logger.info(f"🔴 不足データ銘柄: {len(missing_symbols):,}個")
                
                if not missing_symbols:
                    logger.info("✅ 不足データなし")
                    return 0
                
                # 高優先度で更新
                updated_count = 0
                batch_size = 100
                
                for i in range(0, len(missing_symbols), batch_size):
                    batch = missing_symbols[i:i+batch_size]
                    
                    batch_updated, _ = self.process_batch_parallel(cursor, batch)
                    updated_count += batch_updated
                    
                    connection.commit()
                    
                    progress = ((i + len(batch)) / len(missing_symbols)) * 100
                    logger.info(f"📈 不足データ更新: {progress:.1f}% ({updated_count:,}件更新)")
                    
                    time.sleep(2)  # API制限対策
                
                logger.info(f"✅ 不足データ更新完了: {updated_count:,}件")
                return updated_count
                
        except Exception as e:
            logger.error(f"❌ 不足データ更新エラー: {e}")
            return 0
        finally:
            connection.close()
    
    def verify_update_results(self):
        """更新結果の検証"""
        connection = pymysql.connect(**self.db_config)
        
        try:
            with connection.cursor() as cursor:
                # 今日更新されたデータ
                cursor.execute("""
                    SELECT COUNT(DISTINCT symbol) FROM stock_price_history 
                    WHERE date = CURDATE()
                """)
                today_updated = cursor.fetchone()[0]
                
                # 直近3日以内のデータがある銘柄
                cursor.execute("""
                    SELECT COUNT(DISTINCT symbol) FROM stock_price_history 
                    WHERE date >= DATE_SUB(CURDATE(), INTERVAL 3 DAY)
                """)
                recent_updated = cursor.fetchone()[0]
                
                # 総銘柄数
                cursor.execute("SELECT COUNT(*) FROM stock_master WHERE is_active = 1")
                total_symbols = cursor.fetchone()[0]
                
                fresh_rate = (recent_updated / total_symbols) * 100
                
                logger.info("=== 📊 更新結果検証 ===")
                logger.info(f"📅 今日更新: {today_updated:,}銘柄")
                logger.info(f"🕐 直近3日: {recent_updated:,}銘柄")
                logger.info(f"📊 鮮度率: {fresh_rate:.1f}%")
                
                if fresh_rate >= 70:
                    logger.info("🎉 優秀な鮮度を達成!")
                elif fresh_rate >= 50:
                    logger.info("👍 良好な鮮度")
                else:
                    logger.info("🔧 更なる改善が必要")
                
                return fresh_rate
                
        except Exception as e:
            logger.error(f"❌ 検証エラー: {e}")
            return 0
        finally:
            connection.close()

def main():
    updater = RealtimePriceUpdater()
    
    logger.info("🚀 リアルタイム価格更新システム開始")
    
    # Step 1: 不足データの優先更新
    logger.info("=== 🎯 不足データ優先更新 ===")
    missing_updated = updater.update_missing_symbols_only()
    
    # Step 2: 結果検証
    logger.info("=== 📊 更新結果検証 ===")
    fresh_rate = updater.verify_update_results()
    
    logger.info("=== 📋 更新完了レポート ===")
    logger.info(f"🎯 不足データ更新: {missing_updated:,}件")
    logger.info(f"📊 最終鮮度率: {fresh_rate:.1f}%")
    logger.info("✅ リアルタイム価格更新システム完了")

if __name__ == "__main__":
    main()