#!/usr/bin/env python3
"""実データのみを使用した包括的価格データ収集システム"""

import pymysql
import yfinance as yf
import requests
import time
import pandas as pd
from datetime import datetime, timedelta
import logging
import concurrent.futures
import threading

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealDataCollector:
    def __init__(self):
        # データベース接続設定
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user",
            "password": "miraikakaku-secure-pass-2024", 
            "database": "miraikakaku",
            "charset": "utf8mb4"
        }
        
        # レート制限対応
        self.yfinance_delay = 0.5  # Yahoo Finance
        self.lock = threading.Lock()
        
    def get_missing_symbols_batch(self, limit=500):
        """実データが不足している銘柄を取得"""
        connection = pymysql.connect(**self.db_config)
        try:
            with connection.cursor() as cursor:
                # 実データがない銘柄を優先度順に取得
                cursor.execute("""
                    SELECT sm.symbol, sm.name, sm.exchange, sm.country, sm.sector
                    FROM stock_master sm
                    LEFT JOIN stock_price_history sph ON sm.symbol = sph.symbol
                    WHERE sm.is_active = 1
                    AND sph.symbol IS NULL
                    ORDER BY 
                        CASE 
                            WHEN sm.country IN ('US', 'United States') THEN 1
                            WHEN sm.country = 'Japan' THEN 2
                            WHEN sm.exchange IN ('NYSE', 'NASDAQ', 'TSE') THEN 3
                            ELSE 4
                        END,
                        sm.symbol
                    LIMIT %s
                """, (limit,))
                return cursor.fetchall()
        finally:
            connection.close()
    
    def fetch_yfinance_data(self, symbol, period='1y'):
        """Yahoo Financeから実データ取得"""
        try:
            # シンボル変換（日本株対応）
            if symbol.isdigit() and len(symbol) >= 4:
                yf_symbol = f"{symbol}.T"  # 日本株
            elif symbol.endswith('=X'):
                yf_symbol = symbol  # 通貨ペア
            else:
                yf_symbol = symbol  # US株等
            
            # Yahoo Financeからデータ取得
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period=period, auto_adjust=True, prepost=False)
            
            if hist.empty:
                logger.warning(f"yfinance: {symbol} データなし")
                return None
            
            price_data = []
            for date, row in hist.iterrows():
                try:
                    # NaNチェック
                    if pd.isna(row['Open']) or pd.isna(row['Close']) or pd.isna(row['Volume']):
                        continue
                        
                    price_data.append({
                        'symbol': symbol,
                        'date': date.date(),
                        'open_price': float(row['Open']),
                        'high_price': float(row['High']),
                        'low_price': float(row['Low']),
                        'close_price': float(row['Close']),
                        'adjusted_close': float(row['Close']),  # auto_adjust=Trueなので同じ
                        'volume': int(row['Volume']),
                        'data_source': 'yfinance_real',
                        'is_valid': 1,
                        'data_quality_score': 0.95
                    })
                except (ValueError, TypeError) as e:
                    logger.warning(f"yfinance: {symbol} 日付{date}のデータエラー: {e}")
                    continue
            
            logger.info(f"yfinance: {symbol} - {len(price_data)}件取得")
            return price_data
            
        except Exception as e:
            logger.error(f"yfinance: {symbol} 取得エラー - {e}")
            return None
    
    def fetch_alpha_vantage_data_real(self, symbol, api_key):
        """Alpha Vantage実APIから本物データ取得"""
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': api_key,
                'outputsize': 'full'  # フルデータ
            }
            
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            # APIエラーチェック
            if 'Error Message' in data:
                logger.error(f"Alpha Vantage: {symbol} - {data['Error Message']}")
                return None
                
            if 'Note' in data:
                logger.warning(f"Alpha Vantage: API制限 - {data['Note']}")
                return None
                
            if 'Time Series (Daily)' not in data:
                logger.warning(f"Alpha Vantage: {symbol} データなし")
                return None
            
            time_series = data['Time Series (Daily)']
            price_data = []
            
            for date_str, values in time_series.items():
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    
                    price_data.append({
                        'symbol': symbol,
                        'date': date_obj,
                        'open_price': float(values['1. open']),
                        'high_price': float(values['2. high']),
                        'low_price': float(values['3. low']),
                        'close_price': float(values['4. close']),
                        'adjusted_close': float(values['5. adjusted close']),
                        'volume': int(values['6. volume']),
                        'data_source': 'AlphaVantage_real',
                        'is_valid': 1,
                        'data_quality_score': 0.98
                    })
                except (ValueError, KeyError) as e:
                    logger.warning(f"Alpha Vantage: {symbol} 日付{date_str}のデータエラー: {e}")
                    continue
            
            logger.info(f"Alpha Vantage: {symbol} - {len(price_data)}件取得")
            return price_data
            
        except Exception as e:
            logger.error(f"Alpha Vantage: {symbol} 取得エラー - {e}")
            return None
    
    def save_real_data_batch(self, price_data_list):
        """実データをデータベースに保存"""
        if not price_data_list:
            return 0
            
        connection = pymysql.connect(**self.db_config)
        try:
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
            logger.error(f"データベース保存エラー: {e}")
            return 0
        finally:
            connection.close()
    
    def collect_single_symbol(self, symbol_info):
        """単一銘柄のデータ収集"""
        symbol, name, exchange, country, sector = symbol_info
        
        with self.lock:
            logger.info(f"🔍 {symbol}: データ収集開始")
        
        # Yahoo Financeで取得試行
        price_data = self.fetch_yfinance_data(symbol)
        
        if price_data:
            saved_count = self.save_real_data_batch(price_data)
            with self.lock:
                logger.info(f"✅ {symbol}: {saved_count}件保存 (yfinance)")
            time.sleep(self.yfinance_delay)
            return saved_count
        else:
            with self.lock:
                logger.warning(f"❌ {symbol}: 取得失敗")
            return 0
    
    def collect_comprehensive_real_data(self, max_symbols=300, max_workers=5):
        """包括的実データ収集"""
        logger.info(f"🚀 実データ収集開始 - 最大{max_symbols}銘柄")
        
        # 不足銘柄取得
        missing_symbols = self.get_missing_symbols_batch(max_symbols)
        if not missing_symbols:
            logger.info("✅ 実データ不足銘柄なし")
            return
        
        logger.info(f"💫 {len(missing_symbols)}銘柄の実データ収集開始")
        
        total_collected = 0
        successful_symbols = 0
        
        # 並列処理で効率化
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 全銘柄のタスクを投入
            future_to_symbol = {
                executor.submit(self.collect_single_symbol, symbol_info): symbol_info[0] 
                for symbol_info in missing_symbols
            }
            
            # 結果収集
            for i, future in enumerate(concurrent.futures.as_completed(future_to_symbol)):
                symbol = future_to_symbol[future]
                try:
                    saved_count = future.result()
                    if saved_count > 0:
                        total_collected += saved_count
                        successful_symbols += 1
                except Exception as e:
                    logger.error(f"❌ {symbol}: 並列処理エラー - {e}")
                
                # 進捗報告
                if (i + 1) % 50 == 0:
                    progress = ((i + 1) / len(missing_symbols)) * 100
                    logger.info(f"📈 進捗: {progress:.0f}% - {successful_symbols}/{i+1}成功, {total_collected:,}件収集")
        
        # 結果サマリー
        success_rate = (successful_symbols / len(missing_symbols)) * 100
        logger.info(f"🎯 実データ収集完了:")
        logger.info(f"  - 対象銘柄: {len(missing_symbols)}銘柄")
        logger.info(f"  - 成功銘柄: {successful_symbols}銘柄 ({success_rate:.1f}%)")
        logger.info(f"  - 収集データ: {total_collected:,}件")
        
        return {
            'total_symbols': len(missing_symbols),
            'successful': successful_symbols,
            'total_records': total_collected,
            'success_rate': success_rate
        }

def main():
    collector = RealDataCollector()
    
    # 実データ収集実行
    result = collector.collect_comprehensive_real_data(max_symbols=300, max_workers=5)
    
    if result:
        logger.info(f"🏆 最終結果: {result['total_records']:,}件の実データを収集完了")
    else:
        logger.info("⚠️ 収集対象銘柄なし")

if __name__ == "__main__":
    main()