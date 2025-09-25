#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import yfinance as yf
import pandas as pd
import logging
import time
from datetime import datetime, timedelta

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleRealDataExpansion:
    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres",
            "password": "miraikakaku-postgres-secure-2024",
            "database": "miraikakaku",
            "port": 5432
        }

    def get_symbols_without_yfinance_data(self, limit=300):
        """yfinanceデータがない銘柄を直接取得（コレーション安全）"""
        try:
            connection = psycopg2.connect(**self.db_config)
            with connection.cursor() as cursor:
                # 単純なクエリでyfinanceデータがない銘柄を取得
                cursor.execute("""
                    SELECT sm.symbol, sm.name, sm.country, sm.exchange
                    FROM stock_master sm
                    WHERE sm.is_active = 1 
                    ORDER BY RAND()
                    LIMIT %s
                """, (limit * 3,))  # 3倍取得してフィルタリング
                
                all_symbols = cursor.fetchall()
                
                # 既にyfinanceデータがある銘柄を別途取得
                cursor.execute("""
                    SELECT DISTINCT symbol 
                    FROM stock_price_history 
                    WHERE data_source = 'yfinance'
                """)
                existing_symbols = {row[0] for row in cursor.fetchall()}
                
                # フィルタリング
                missing_symbols = [
                    symbol for symbol in all_symbols 
                    if symbol[0] not in existing_symbols
                ][:limit]
                
                logger.info(f"📋 全銘柄: {len(all_symbols)}, 既存: {len(existing_symbols)}, 対象: {len(missing_symbols)}")
                return missing_symbols
                
        except Exception as e:
            logger.error(f"銘柄取得エラー: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()

    def fetch_yfinance_data(self, symbol, country=None):
        """yfinanceで価格データ取得"""
        try:
            # シンボル変換
            if country == 'Japan' and symbol.isdigit() and len(symbol) >= 4:
                yf_symbol = f"{symbol}.T"
            else:
                yf_symbol = symbol
            
            ticker = yf.Ticker(yf_symbol)
            
            # 過去1年分取得
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            hist_data = ticker.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1d'
            )
            
            if hist_data.empty:
                return None
                
            price_data = []
            for date, row in hist_data.iterrows():
                try:
                    # NaNチェック
                    if pd.isna([row['Open'], row['High'], row['Low'], row['Close'], row['Volume']]).any():
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
                except (ValueError, OverflowError):
                    continue
            
            return price_data if price_data else None
            
        except Exception as e:
            logger.warning(f"yfinance取得失敗 {symbol}({yf_symbol}): {e}")
            return None

    def save_price_data(self, price_data_list):
        """価格データの保存"""
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

    def expand_real_data(self, target_symbols=200):
        """実データ拡張の実行"""
        logger.info(f"🚀 シンプル実データ拡張開始 - 目標: {target_symbols}銘柄")
        
        # 対象銘柄取得
        missing_symbols = self.get_symbols_without_yfinance_data(target_symbols)
        logger.info(f"📋 処理対象銘柄: {len(missing_symbols)}銘柄")
        
        if not missing_symbols:
            logger.warning("⚠️ 処理対象銘柄なし")
            return {'total': 0, 'successful': 0, 'failed': 0}
        
        successful = 0
        failed = 0
        total_records = 0
        
        for i, (symbol, name, country, exchange) in enumerate(missing_symbols):
            try:
                logger.info(f"📊 処理中 {i+1}/{len(missing_symbols)}: {symbol} ({country})")
                
                # yfinanceデータ取得
                price_data = self.fetch_yfinance_data(symbol, country)
                
                if price_data:
                    saved_count = self.save_price_data(price_data)
                    if saved_count > 0:
                        successful += 1
                        total_records += saved_count
                        logger.info(f"✅ {symbol}: {saved_count}件保存成功")
                    else:
                        failed += 1
                        logger.warning(f"⚠️ {symbol}: 保存失敗")
                else:
                    failed += 1
                    logger.warning(f"❌ {symbol}: データ取得失敗")
                
                # レート制限対応
                time.sleep(0.5)
                
                # 進捗報告
                if (i + 1) % 25 == 0:
                    progress = ((i + 1) / len(missing_symbols)) * 100
                    success_rate = (successful / (i + 1)) * 100 if (i + 1) > 0 else 0
                    logger.info(f"📈 進捗: {progress:.1f}% | 成功: {successful}, 失敗: {failed} | 成功率: {success_rate:.1f}%")
                
            except Exception as e:
                failed += 1
                logger.error(f"❌ {symbol}: 処理エラー - {e}")
        
        # 最終結果
        total_processed = successful + failed
        success_rate = (successful / total_processed * 100) if total_processed > 0 else 0
        
        logger.info(f"🎯 シンプル実データ拡張完了:")
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
    logger.info("🔥 シンプル実データ拡張システム開始")
    
    expander = SimpleRealDataExpansion()
    result = expander.expand_real_data(target_symbols=200)
    
    if result['successful'] > 0:
        logger.info("✅ 実データ拡張成功 - 評価実行中...")
        # 拡張後の評価
        import subprocess
        subprocess.run(["python3", "collation_safe_data_assessment.py"])
    else:
        logger.error("❌ 実データ拡張失敗")

if __name__ == "__main__":
    main()