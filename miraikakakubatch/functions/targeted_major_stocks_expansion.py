#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import yfinance as yf
import pandas as pd
import logging
import time
from datetime import datetime, timedelta

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TargetedMajorStocksExpansion:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user",
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
            "charset": "utf8mb4"
        }
        
        # 主要株式リスト（確実に取得できる銘柄）
        self.major_stocks = [
            # S&P 500主要銘柄
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META',
            'UNH', 'JNJ', 'JPM', 'V', 'PG', 'HD', 'CVX', 'MA', 'ABBV', 'PFE',
            'AVGO', 'KO', 'LLY', 'PEP', 'TMO', 'COST', 'WMT', 'ABT', 'MRK',
            'DHR', 'VZ', 'ACN', 'TXN', 'CRM', 'LIN', 'NEE', 'DIS', 'WFC',
            'BMY', 'NKE', 'RTX', 'PM', 'ORCL', 'INTC', 'T', 'COP', 'UPS',
            'LOW', 'SCHW', 'BA', 'CAT', 'SBUX', 'GS', 'DE', 'BLK', 'GILD',
            'MDT', 'AXP', 'AMT', 'BKNG', 'ADP', 'ISRG', 'TJX', 'SYK', 'CB',
            'MU', 'C', 'PLD', 'ZTS', 'LRCX', 'CSX', 'MDLZ', 'CVS', 'VRTX',
            'FIS', 'SO', 'REGN', 'NOC', 'PNC', 'CL', 'USB', 'DUK', 'TFC',
            'NSC', 'AON', 'BSX', 'ICE', 'MMM', 'FDX', 'SPGI', 'F', 'GM',
            
            # 日本主要株式
            '7203.T', '6758.T', '9984.T', '8306.T', '9432.T', '6861.T',
            '7267.T', '8316.T', '4063.T', '9020.T', '6098.T', '4519.T',
            '6367.T', '6594.T', '6954.T', '4901.T', '8058.T', '2914.T',
            '4502.T', '4568.T', '9983.T', '6702.T', '6501.T', '6503.T',
            '8035.T', '4755.T', '9201.T', '7974.T', '8001.T', '8002.T',
            
            # 欧州主要株式
            'ASML', 'NVEI', 'SAP', 'NESN.SW', 'OR.PA', 'RMS.PA',
            'MC.PA', 'AI.PA', 'SU.PA', 'CDI.PA', 'SAN.PA', 'TTE.PA',
            'SHEL', 'AZN', 'BP', 'VOD', 'GSK', 'DGE', 'ULVR', 'LLOY',
            
            # 中国・アジア主要株式
            'BABA', 'PDD', 'JD', 'BIDU', 'NIO', 'LI', 'XPEV',
            
            # ETF・インデックス
            'SPY', 'QQQ', 'VTI', 'IVV', 'VEA', 'IEFA', 'VWO', 'EEM',
            'GLD', 'SLV', 'USO', 'TLT', 'IEF', 'LQD', 'HYG', 'XLF',
            'XLK', 'XLE', 'XLV', 'XLI', 'XLU', 'XLB', 'XLRE', 'XLP',
            
            # 通貨ペア
            'EURUSD=X', 'USDJPY=X', 'GBPUSD=X', 'USDCHF=X', 'USDCAD=X',
            'AUDUSD=X', 'NZDUSD=X', 'EURJPY=X', 'GBPJPY=X', 'EURGBP=X'
        ]

    def check_existing_symbols(self):
        """既存のyfinanceデータを確認"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT symbol 
                    FROM stock_price_history 
                    WHERE data_source = 'yfinance'
                """)
                return {row[0] for row in cursor.fetchall()}
        except Exception as e:
            logger.error(f"既存データ確認エラー: {e}")
            return set()
        finally:
            if 'connection' in locals():
                connection.close()

    def add_major_symbol_to_master(self, symbol):
        """主要銘柄をstock_masterに追加"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                # シンボル情報の推定
                if symbol.endswith('.T'):
                    country, exchange = 'Japan', 'TSE'
                    name = f"Japanese Stock {symbol}"
                elif symbol.endswith('=X'):
                    country, exchange = 'Global', 'FX'
                    name = f"Currency Pair {symbol}"
                elif '.' in symbol:
                    country, exchange = 'Europe', 'European Exchange'
                    name = f"European Stock {symbol}"
                else:
                    country, exchange = 'US', 'NYSE/NASDAQ'
                    name = f"US Stock {symbol}"
                
                cursor.execute("""
                    INSERT IGNORE INTO stock_master 
                    (symbol, name, country, exchange, is_active)
                    VALUES (%s, %s, %s, %s, 1)
                """, (symbol, name, country, exchange))
                
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"master追加エラー {symbol}: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()

    def fetch_major_stock_data(self, symbol):
        """主要銘柄のデータ取得"""
        try:
            ticker = yf.Ticker(symbol)
            
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
                    
                    # 異常値チェック
                    if any(val <= 0 for val in [row['Open'], row['High'], row['Low'], row['Close']]):
                        continue
                        
                    if row['Volume'] < 0:
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
                        'data_quality_score': 0.98  # 主要銘柄なので高品質
                    })
                except (ValueError, OverflowError):
                    continue
            
            return price_data if price_data else None
            
        except Exception as e:
            logger.warning(f"データ取得失敗 {symbol}: {e}")
            return None

    def save_price_data_batch(self, price_data_list):
        """価格データの一括保存"""
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
            logger.error(f"保存エラー: {e}")
            return 0
        finally:
            if 'connection' in locals():
                connection.close()

    def expand_major_stocks(self):
        """主要銘柄の実データ拡張"""
        logger.info(f"🚀 主要銘柄実データ拡張開始 - 対象: {len(self.major_stocks)}銘柄")
        
        # 既存データ確認
        existing_symbols = self.check_existing_symbols()
        logger.info(f"📊 既存yfinanceデータ: {len(existing_symbols)}銘柄")
        
        # 未処理銘柄フィルタリング
        target_symbols = [s for s in self.major_stocks if s not in existing_symbols]
        logger.info(f"📋 処理対象銘柄: {len(target_symbols)}銘柄")
        
        if not target_symbols:
            logger.info("⚠️ すべての主要銘柄は既に処理済み")
            return {'total': 0, 'successful': 0, 'failed': 0}
        
        successful = 0
        failed = 0
        total_records = 0
        
        for i, symbol in enumerate(target_symbols):
            try:
                logger.info(f"📊 処理中 {i+1}/{len(target_symbols)}: {symbol}")
                
                # stock_masterに追加
                self.add_major_symbol_to_master(symbol)
                
                # 価格データ取得
                price_data = self.fetch_major_stock_data(symbol)
                
                if price_data:
                    saved_count = self.save_price_data_batch(price_data)
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
                time.sleep(0.3)
                
                # 進捗報告
                if (i + 1) % 20 == 0:
                    progress = ((i + 1) / len(target_symbols)) * 100
                    success_rate = (successful / (i + 1)) * 100
                    logger.info(f"📈 進捗: {progress:.1f}% | 成功: {successful}, 失敗: {failed} | 成功率: {success_rate:.1f}%")
                
            except Exception as e:
                failed += 1
                logger.error(f"❌ {symbol}: 処理エラー - {e}")
        
        # 最終結果
        total_processed = successful + failed
        success_rate = (successful / total_processed * 100) if total_processed > 0 else 0
        
        logger.info(f"🎯 主要銘柄実データ拡張完了:")
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
    logger.info("🔥 主要銘柄ターゲット実データ拡張開始")
    
    expander = TargetedMajorStocksExpansion()
    result = expander.expand_major_stocks()
    
    if result['successful'] > 0:
        logger.info("✅ 主要銘柄拡張成功 - 評価実行中...")
        # 拡張後の評価
        import subprocess
        subprocess.run(["python3", "collation_safe_data_assessment.py"])
    else:
        logger.error("❌ 主要銘柄拡張失敗")

if __name__ == "__main__":
    main()