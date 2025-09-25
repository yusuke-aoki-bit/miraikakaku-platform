#!/usr/bin/env python3
"""
pandas-datareaderを使用した多様なデータソースからの株価データ収集
"""

import psycopg2
import psycopg2.extras
import pandas as pd
import pandas_datareader.data as web
import numpy as np
from datetime import datetime, timedelta
import logging
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataReaderCollector:
    def __init__(self):
        self.db_config = {
            "host": os.getenv("DB_HOST", "34.58.103.36"),
            "user": os.getenv("DB_USER", "miraikakaku-user"),
            "password": os.getenv("DB_PASSWORD", "miraikakaku-secure-pass-2024"),
            "database": os.getenv("DB_NAME", "miraikakaku"),
            "port": 5432
        }
        
        # データソースの優先順位
        self.data_sources = [
            'yahoo',           # Yahoo Finance
            'stooq',          # Stooq (ポーランドの金融データ)
            'fred',           # Federal Reserve Economic Data
            'iex',            # IEX Cloud
            'av-daily',       # Alpha Vantage
            'tiingo',         # Tiingo
        ]
        
    def fetch_from_yahoo(self, symbol, start_date, end_date):
        """yfinanceを使用してYahoo Financeからデータ取得"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            if not df.empty:
                logger.info(f"✅ yfinance: {symbol} - {len(df)}日分取得")
                return df
            return None
        except Exception as e:
            logger.warning(f"⚠️ yfinance失敗 {symbol}: {e}")
            return None
    
    def fetch_from_stooq(self, symbol, start_date, end_date):
        """Stooqからデータ取得（主に国際市場データ）"""
        try:
            # Stooqは銘柄コードに市場コードが必要（例: AAPL.US）
            stooq_symbol = f"{symbol}.US" if not symbol.endswith('.US') else symbol
            df = web.DataReader(stooq_symbol, 'stooq', start_date, end_date)
            logger.info(f"✅ Stooq: {symbol} - {len(df)}日分取得")
            return df
        except Exception as e:
            logger.warning(f"⚠️ Stooq失敗 {symbol}: {e}")
            return None
    
    def fetch_from_fred(self, symbol):
        """FRED (Federal Reserve Economic Data)から経済指標取得"""
        try:
            # FREDは経済指標専用（例: DGS10=10年物国債利回り）
            economic_indicators = {
                'DGS10': '10年物米国債利回り',
                'DEXJPUS': 'USD/JPY為替レート',
                'DEXUSEU': 'USD/EUR為替レート',
                'DCOILWTICO': 'WTI原油価格',
                'GOLDAMGBD228NLBM': '金価格'
            }
            
            if symbol in economic_indicators:
                df = web.DataReader(symbol, 'fred', datetime.now() - timedelta(days=30))
                logger.info(f"✅ FRED: {economic_indicators[symbol]} - {len(df)}日分取得")
                return df
        except Exception as e:
            logger.warning(f"⚠️ FRED失敗 {symbol}: {e}")
            return None
    
    def fetch_from_multiple_sources(self, symbol, days_back=30):
        """複数のデータソースから順番に試行"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Stooqを最初に試行（pandas-datareader使用）
        df = self.fetch_from_stooq(symbol, start_date, end_date)
        if df is not None and not df.empty:
            return df, 'stooq'
        
        # yfinanceを試行（Yahoo Financeデータ）
        df = self.fetch_from_yahoo(symbol, start_date, end_date)
        if df is not None and not df.empty:
            return df, 'yfinance'
        
        # FREDを試行（経済指標の場合）
        df = self.fetch_from_fred(symbol)
        if df is not None and not df.empty:
            return df, 'fred'
        
        return None, None
    
    def collect_stock_data(self, batch_size=50):
        """株価データ収集のメイン処理"""
        connection = psycopg2.connect(**self.db_config)
        
        try:
            with connection.cursor() as cursor:
                logger.info("🚀 pandas-datareader データ収集開始")
                
                # アクティブな銘柄を取得
                cursor.execute("""
                    SELECT symbol, name, market, country 
                    FROM stock_master 
                    WHERE is_active = 1
                    ORDER BY 
                        CASE 
                            WHEN market = 'US' THEN 1
                            WHEN market = 'NASDAQ' THEN 2
                            WHEN market = 'NYSE' THEN 3
                            ELSE 4
                        END,
                        symbol
                    LIMIT %s
                """, (batch_size,))
                
                stocks = cursor.fetchall()
                logger.info(f"📊 対象: {len(stocks)}銘柄")
                
                successful_updates = 0
                failed_symbols = []
                
                for symbol, name, market, country in stocks:
                    try:
                        # 複数ソースからデータ取得を試行
                        df, source = self.fetch_from_multiple_sources(symbol)
                        
                        if df is not None and not df.empty:
                            # 最新のデータを処理
                            for date, row in df.tail(5).iterrows():
                                # データベースに保存
                                self.save_price_data(cursor, symbol, date, row, source)
                            
                            successful_updates += 1
                            
                            # 定期的にコミット
                            if successful_updates % 10 == 0:
                                connection.commit()
                                logger.info(f"📈 進捗: {successful_updates}件成功")
                        else:
                            failed_symbols.append(symbol)
                        
                        # API制限回避のための待機
                        time.sleep(0.2)
                        
                    except Exception as e:
                        logger.error(f"❌ {symbol}処理エラー: {e}")
                        failed_symbols.append(symbol)
                        continue
                
                # 最終コミット
                connection.commit()
                
                # 結果サマリー
                logger.info(f"""
                ✅ データ収集完了
                - 成功: {successful_updates}/{len(stocks)}件
                - 失敗: {len(failed_symbols)}件
                """)
                
                if failed_symbols:
                    logger.info(f"失敗銘柄: {', '.join(failed_symbols[:10])}")
                
                return successful_updates
                
        except Exception as e:
            logger.error(f"❌ データ収集エラー: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
    
    def save_price_data(self, cursor, symbol, date, row, source):
        """価格データをデータベースに保存"""
        try:
            # カラム名を正規化（大文字小文字両対応）
            open_price = float(row.get('Open', row.get('open', row.get('Open', 0))))
            high_price = float(row.get('High', row.get('high', row.get('High', 0))))
            low_price = float(row.get('Low', row.get('low', row.get('Low', 0))))
            close_price = float(row.get('Close', row.get('close', row.get('Close', 0))))
            volume = int(row.get('Volume', row.get('volume', row.get('Volume', 0))))
            adj_close = float(row.get('Adj Close', row.get('adj_close', row.get('Adj. Close', close_price))))
            
            cursor.execute("""
                INSERT INTO stock_price_history 
                (symbol, date, open_price, high_price, low_price, 
                 close_price, volume, adjusted_close, data_source, is_valid, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW(), NOW())
                ON DUPLICATE KEY UPDATE
                open_price = VALUES(open_price),
                high_price = VALUES(high_price),
                low_price = VALUES(low_price),
                close_price = VALUES(close_price),
                volume = VALUES(volume),
                adjusted_close = VALUES(adjusted_close),
                data_source = VALUES(data_source),
                updated_at = NOW()
            """, (
                symbol,
                date.date() if hasattr(date, 'date') else date,
                open_price,
                high_price,
                low_price,
                close_price,
                volume,
                adj_close,
                source
            ))
            
        except Exception as e:
            logger.error(f"❌ データ保存エラー {symbol}: {e}")
            raise
    
    def collect_economic_indicators(self):
        """経済指標データの収集"""
        connection = psycopg2.connect(**self.db_config)
        
        try:
            with connection.cursor() as cursor:
                logger.info("📊 経済指標データ収集開始")
                
                # FREDから主要経済指標を取得
                indicators = {
                    'DGS10': '10年物米国債利回り',
                    'DEXJPUS': 'USD/JPY',
                    'DEXUSEU': 'USD/EUR',
                    'DCOILWTICO': 'WTI原油',
                    'GOLDAMGBD228NLBM': '金価格'
                }
                
                for symbol, name in indicators.items():
                    try:
                        df = web.DataReader(symbol, 'fred', 
                                          datetime.now() - timedelta(days=30))
                        
                        if not df.empty:
                            latest_value = df.iloc[-1].values[0]
                            logger.info(f"✅ {name}: {latest_value:.2f}")
                            
                            # 経済指標テーブルに保存（必要に応じて作成）
                            cursor.execute("""
                                INSERT INTO economic_indicators 
                                (indicator_code, indicator_name, value, date, created_at)
                                VALUES (%s, %s, %s, %s, NOW())
                                ON DUPLICATE KEY UPDATE
                                value = VALUES(value),
                                updated_at = NOW()
                            """, (symbol, name, float(latest_value), df.index[-1].date()))
                            
                    except Exception as e:
                        logger.warning(f"⚠️ {name}取得失敗: {e}")
                        continue
                
                connection.commit()
                logger.info("✅ 経済指標データ収集完了")
                
        except Exception as e:
            logger.error(f"❌ 経済指標収集エラー: {e}")
            connection.rollback()
        finally:
            connection.close()

def main():
    """メイン実行関数"""
    worker_id = int(os.getenv("BATCH_TASK_INDEX", "0"))
    logger.info(f"🚀 DataReader Worker {worker_id} 開始")
    
    collector = DataReaderCollector()
    
    try:
        # 株価データ収集
        result = collector.collect_stock_data(batch_size=30)
        logger.info(f"✅ Worker {worker_id}: {result}件の株価データ収集完了")
        
        # Worker 0のみ経済指標も収集
        if worker_id == 0:
            collector.collect_economic_indicators()
        
    except Exception as e:
        logger.error(f"❌ Worker {worker_id} エラー: {e}")
        exit(1)

if __name__ == "__main__":
    main()