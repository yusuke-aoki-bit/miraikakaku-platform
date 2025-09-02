#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import requests
import json
import logging
import time
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiSourceRealDataExpander:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user",
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
            "charset": "utf8mb4"
        }

    def get_uncovered_symbols_fast(self, limit=300):
        """カバー率の低い銘柄を高速取得"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                # 価格データが不足している銘柄を効率的に取得
                cursor.execute("""
                    SELECT sm.symbol, sm.name, sm.country, sm.exchange
                    FROM stock_master sm
                    WHERE sm.is_active = 1
                    AND (
                        SELECT COUNT(*) FROM stock_price_history sph 
                        WHERE sph.symbol = sm.symbol 
                        AND sph.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    ) = 0
                    ORDER BY 
                        CASE WHEN sm.country = 'US' THEN 1 ELSE 2 END,
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

    def fetch_yahoo_csv_data(self, symbol, country=None):
        """Yahoo Finance CSV APIでデータ取得"""
        try:
            # シンボル変換
            if country == 'Japan' and symbol.isdigit():
                yf_symbol = f"{symbol}.T"
            else:
                yf_symbol = symbol
            
            # Yahoo Finance CSV API
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            url = f"https://query1.finance.yahoo.com/v7/finance/download/{yf_symbol}"
            params = {
                'period1': int(start_date.timestamp()),
                'period2': int(end_date.timestamp()),
                'interval': '1d',
                'events': 'history'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            # CSV解析
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                return None
            
            price_data = []
            for line in lines[1:]:
                try:
                    values = line.split(',')
                    if len(values) < 7:
                        continue
                    
                    date_str = values[0]
                    open_price = float(values[1])
                    high_price = float(values[2])
                    low_price = float(values[3])
                    close_price = float(values[4])
                    adj_close = float(values[5])
                    volume = int(values[6])
                    
                    # 有効性チェック
                    if any(v <= 0 for v in [open_price, high_price, low_price, close_price]) or volume < 0:
                        continue
                    
                    price_data.append({
                        'symbol': symbol,
                        'date': datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d'),
                        'open_price': open_price,
                        'high_price': high_price,
                        'low_price': low_price,
                        'close_price': close_price,
                        'adjusted_close': adj_close,
                        'volume': volume,
                        'data_source': 'yahoo_csv',
                        'is_valid': 1,
                        'data_quality_score': 0.93
                    })
                except (ValueError, IndexError):
                    continue
            
            return price_data if len(price_data) >= 20 else None
            
        except Exception as e:
            logger.warning(f"Yahoo CSV失敗 {symbol}: {e}")
            return None

    def fetch_financial_modeling_prep(self, symbol):
        """Financial Modeling Prep API（無料版）"""
        try:
            # 無料版のFMP API（制限あり）
            url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}"
            params = {
                'apikey': 'demo',  # デモキー（制限あり）
                'from': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
                'to': datetime.now().strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'historical' not in data:
                return None
            
            price_data = []
            for record in data['historical'][:50]:  # 制限対応
                try:
                    price_data.append({
                        'symbol': symbol,
                        'date': record['date'],
                        'open_price': float(record['open']),
                        'high_price': float(record['high']),
                        'low_price': float(record['low']),
                        'close_price': float(record['close']),
                        'adjusted_close': float(record['adjClose']),
                        'volume': int(record['volume']),
                        'data_source': 'fmp_api',
                        'is_valid': 1,
                        'data_quality_score': 0.90
                    })
                except (KeyError, ValueError):
                    continue
            
            return price_data if price_data else None
            
        except Exception as e:
            logger.warning(f"FMP API失敗 {symbol}: {e}")
            return None

    def fetch_alphavantage_demo(self, symbol):
        """Alpha Vantage デモデータ取得"""
        try:
            # Alpha Vantage デモAPI
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': 'demo',
                'outputsize': 'compact'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                return None
            
            price_data = []
            time_series = data['Time Series (Daily)']
            
            for date_str, values in list(time_series.items())[:30]:  # 制限対応
                try:
                    price_data.append({
                        'symbol': symbol,
                        'date': date_str,
                        'open_price': float(values['1. open']),
                        'high_price': float(values['2. high']),
                        'low_price': float(values['3. low']),
                        'close_price': float(values['4. close']),
                        'adjusted_close': float(values['4. close']),
                        'volume': int(values['5. volume']),
                        'data_source': 'alphavantage',
                        'is_valid': 1,
                        'data_quality_score': 0.92
                    })
                except (KeyError, ValueError):
                    continue
            
            return price_data if price_data else None
            
        except Exception as e:
            logger.warning(f"Alpha Vantage失敗 {symbol}: {e}")
            return None

    def multi_source_fetch(self, symbol_info):
        """複数ソースからのデータ取得試行"""
        symbol, name, country, exchange = symbol_info
        
        # データソース優先順位
        fetch_methods = [
            ('yahoo_csv', self.fetch_yahoo_csv_data),
            ('fmp', self.fetch_financial_modeling_prep),
            ('alphavantage', self.fetch_alphavantage_demo)
        ]
        
        for source_name, fetch_method in fetch_methods:
            try:
                if source_name == 'yahoo_csv':
                    result = fetch_method(symbol, country)
                else:
                    result = fetch_method(symbol)
                
                if result and len(result) >= 10:  # 最低10件のデータ
                    return {
                        'symbol': symbol,
                        'status': 'success',
                        'source': source_name,
                        'data': result,
                        'count': len(result)
                    }
                
                # 失敗時は少し待機
                time.sleep(0.2)
                
            except Exception as e:
                logger.warning(f"{source_name} {symbol}失敗: {e}")
                continue
        
        return {
            'symbol': symbol,
            'status': 'all_failed',
            'source': 'none',
            'data': None,
            'count': 0
        }

    def save_multi_source_data(self, data_list):
        """マルチソースデータの保存"""
        if not data_list:
            return 0
            
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                insert_data = []
                for data in data_list:
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
            logger.error(f"マルチソース保存エラー: {e}")
            return 0
        finally:
            if 'connection' in locals():
                connection.close()

    def expand_with_multi_sources(self, target_symbols=200, max_workers=6):
        """マルチソースでの実データ拡張"""
        logger.info(f"🌐 マルチソース実データ拡張開始 - 目標: {target_symbols}銘柄")
        
        # 未カバー銘柄取得
        uncovered_symbols = self.get_uncovered_symbols_fast(target_symbols)
        logger.info(f"📋 未カバー銘柄: {len(uncovered_symbols)}銘柄")
        
        if not uncovered_symbols:
            logger.info("⚠️ 処理対象銘柄なし")
            return {'total': 0, 'successful': 0, 'failed': 0, 'total_records': 0}
        
        successful = 0
        failed = 0
        total_records = 0
        source_stats = {}
        
        # 並列処理でマルチソースデータ取得
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.multi_source_fetch, symbol_info): symbol_info[0]
                for symbol_info in uncovered_symbols
            }
            
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    result = future.result()
                    
                    if result['status'] == 'success':
                        # データ保存
                        saved_count = self.save_multi_source_data(result['data'])
                        if saved_count > 0:
                            successful += 1
                            total_records += saved_count
                            source = result['source']
                            source_stats[source] = source_stats.get(source, 0) + 1
                            logger.info(f"✅ {symbol} ({source}): {saved_count}件保存")
                        else:
                            failed += 1
                            logger.warning(f"⚠️ {symbol}: 保存失敗")
                    else:
                        failed += 1
                        logger.warning(f"❌ {symbol}: 全ソース失敗")
                    
                    # 進捗報告
                    if (successful + failed) % 25 == 0:
                        progress = ((successful + failed) / len(uncovered_symbols)) * 100
                        success_rate = (successful / (successful + failed)) * 100
                        logger.info(f"📈 進捗: {progress:.1f}% | 成功率: {success_rate:.1f}% | データ: {total_records:,}件")
                
                except Exception as e:
                    failed += 1
                    logger.error(f"❌ {symbol}: 処理エラー - {e}")
        
        # 最終結果
        total_processed = successful + failed
        final_success_rate = (successful / total_processed * 100) if total_processed > 0 else 0
        
        logger.info(f"🎯 マルチソース実データ拡張完了:")
        logger.info(f"   - 処理銘柄: {total_processed}")
        logger.info(f"   - 成功銘柄: {successful} ({final_success_rate:.1f}%)")
        logger.info(f"   - 失敗銘柄: {failed}")
        logger.info(f"   - 収集データ: {total_records:,}件")
        
        logger.info("📊 ソース別成功数:")
        for source, count in source_stats.items():
            logger.info(f"   - {source}: {count}銘柄")
        
        return {
            'total': total_processed,
            'successful': successful,
            'failed': failed,
            'total_records': total_records,
            'success_rate': final_success_rate,
            'source_stats': source_stats
        }

def main():
    logger.info("🌐 マルチソース実データ拡張システム開始")
    
    expander = MultiSourceRealDataExpander()
    result = expander.expand_with_multi_sources(target_symbols=200, max_workers=6)
    
    if result['successful'] > 0:
        logger.info("✅ マルチソース拡張成功 - 評価実行中...")
        
        # 拡張後の評価
        import subprocess
        subprocess.run(["python3", "collation_safe_data_assessment.py"])
    else:
        logger.error("❌ マルチソース拡張失敗")

if __name__ == "__main__":
    main()