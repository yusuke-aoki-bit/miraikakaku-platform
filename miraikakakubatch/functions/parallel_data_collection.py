#!/usr/bin/env python3
"""
並列データ収集システム
既存のバッチ処理と並行してETF・為替・米国株データを収集
"""

import yfinance as yf
import psycopg2
import psycopg2.extras
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParallelDataCollection:
    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres", 
            "password": "miraikakaku-postgres-secure-2024",
            "database": "miraikakaku",
        }
        self.stats = {
            "us_stocks": {"processed": 0, "successful": 0, "failed": 0},
            "etfs": {"processed": 0, "successful": 0, "failed": 0},
            "forex": {"processed": 0, "successful": 0, "failed": 0}
        }
        self.lock = threading.Lock()

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def collect_major_us_stocks(self):
        """主要米国株収集"""
        major_us_stocks = [
            "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "META", "NVDA",
            "NFLX", "AMD", "CRM", "ORCL", "ADBE", "INTC", "CSCO", "IBM",
            "PYPL", "UBER", "LYFT", "ZOOM", "SHOP", "SQ", "TWTR", "SNAP",
            "BA", "GE", "F", "GM", "CAT", "DE", "MMM", "HON",
            "JPM", "BAC", "WFC", "C", "GS", "MS", "V", "MA",
            "KO", "PEP", "MCD", "SBUX", "NKE", "DIS", "WMT", "TGT"
        ]
        
        logger.info(f"🇺🇸 主要米国株収集開始: {len(major_us_stocks)}銘柄")
        
        for symbol in major_us_stocks:
            try:
                success = self.fetch_and_save_stock_data(symbol, "US Major Stock")
                with self.lock:
                    self.stats["us_stocks"]["processed"] += 1
                    if success:
                        self.stats["us_stocks"]["successful"] += 1
                        logger.info(f"✅ {symbol}: 米国株データ取得成功")
                    else:
                        self.stats["us_stocks"]["failed"] += 1
                
                time.sleep(0.5)  # レート制限
                
            except Exception as e:
                with self.lock:
                    self.stats["us_stocks"]["failed"] += 1
                logger.error(f"❌ {symbol}: {e}")

    def collect_major_etfs(self):
        """主要ETF収集"""
        major_etfs = [
            # 米国ETF
            "SPY", "QQQ", "IWM", "VTI", "VOO", "IVV", "VEA", "VWO",
            "AGG", "BND", "TLT", "GLD", "SLV", "USO", "UNG", "XLF",
            "XLK", "XLE", "XLV", "XLI", "XLB", "XLU", "XLP", "XLRE",
            # 日本ETF
            "1306.T", "1321.T", "1570.T", "1591.T", "2558.T", "1563.T"
        ]
        
        logger.info(f"📊 主要ETF収集開始: {len(major_etfs)}銘柄")
        
        for symbol in major_etfs:
            try:
                success = self.fetch_and_save_stock_data(symbol, "Major ETF")
                with self.lock:
                    self.stats["etfs"]["processed"] += 1
                    if success:
                        self.stats["etfs"]["successful"] += 1
                        logger.info(f"✅ {symbol}: ETFデータ取得成功")
                    else:
                        self.stats["etfs"]["failed"] += 1
                
                time.sleep(0.5)
                
            except Exception as e:
                with self.lock:
                    self.stats["etfs"]["failed"] += 1
                logger.error(f"❌ {symbol}: {e}")

    def collect_major_forex(self):
        """主要為替ペア収集"""
        major_forex = [
            "USDJPY=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "CHFJPY=X",
            "CADJPY=X", "NZDJPY=X", "ZARJPY=X", "EURUSD=X", "GBPUSD=X",
            "AUDUSD=X", "USDCHF=X", "USDCAD=X", "NZDUSD=X", "EURGBP=X",
            "EURAUD=X", "GBPAUD=X", "AUDCAD=X", "EURCHF=X", "GBPCHF=X"
        ]
        
        logger.info(f"💱 主要為替ペア収集開始: {len(major_forex)}ペア")
        
        for symbol in major_forex:
            try:
                success = self.collect_forex_data(symbol)
                with self.lock:
                    self.stats["forex"]["processed"] += 1
                    if success:
                        self.stats["forex"]["successful"] += 1
                        logger.info(f"✅ {symbol}: 為替データ取得成功")
                    else:
                        self.stats["forex"]["failed"] += 1
                
                time.sleep(0.3)
                
            except Exception as e:
                with self.lock:
                    self.stats["forex"]["failed"] += 1
                logger.error(f"❌ {symbol}: {e}")

    def fetch_and_save_stock_data(self, symbol, data_source):
        """株価・ETFデータ取得と保存"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return False
            
            latest_data = hist.iloc[-1]
            latest_date = hist.index[-1].strftime('%Y-%m-%d')
            
            connection = self.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO stock_price_history 
                        (symbol, date, open_price, high_price, low_price, close_price, volume, 
                         data_source, created_at, updated_at, is_valid, data_quality_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), 1, 0.95)
                        ON DUPLICATE KEY UPDATE
                        close_price = VALUES(close_price),
                        volume = VALUES(volume),
                        updated_at = NOW()
                    """, (
                        symbol, latest_date,
                        float(latest_data['Open']),
                        float(latest_data['High']),
                        float(latest_data['Low']),
                        float(latest_data['Close']),
                        int(latest_data['Volume']),
                        f"Parallel Collection - {data_source}"
                    ))
                    
                connection.commit()
                return True
                
            finally:
                connection.close()
                
        except Exception:
            return False

    def collect_forex_data(self, fx_symbol):
        """為替データ収集"""
        try:
            ticker = yf.Ticker(fx_symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return False
            
            latest_data = hist.iloc[-1]
            latest_date = hist.index[-1].strftime('%Y-%m-%d')
            
            # 為替データは別途ログ出力（DBへの保存は簡略化）
            logger.info(f"💱 {fx_symbol}: {latest_data['Close']:.4f} @ {latest_date}")
            return True
            
        except Exception:
            return False

    def run_parallel_collection(self):
        """並列データ収集実行"""
        start_time = datetime.now()
        logger.info(f"🚀 並列データ収集開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 3つのスレッドで並列実行
        with ThreadPoolExecutor(max_workers=3) as executor:
            # 米国株収集
            us_future = executor.submit(self.collect_major_us_stocks)
            
            # ETF収集
            etf_future = executor.submit(self.collect_major_etfs)
            
            # 為替収集
            fx_future = executor.submit(self.collect_major_forex)
            
            # すべての処理完了を待機
            us_future.result()
            etf_future.result() 
            fx_future.result()
        
        # 最終レポート
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("📊 並列データ収集完了レポート")
        logger.info(f"⏱️  実行時間: {duration:.1f}秒")
        
        total_processed = sum(cat["processed"] for cat in self.stats.values())
        total_successful = sum(cat["successful"] for cat in self.stats.values())
        total_failed = sum(cat["failed"] for cat in self.stats.values())
        
        logger.info(f"📈 総合結果:")
        logger.info(f"  🎯 総処理: {total_processed}件")
        logger.info(f"  ✅ 総成功: {total_successful}件")
        logger.info(f"  ❌ 総失敗: {total_failed}件")
        logger.info(f"  📊 成功率: {(total_successful/total_processed*100):.1f}%")
        
        logger.info(f"🇺🇸 米国株:")
        logger.info(f"  処理: {self.stats['us_stocks']['processed']}件")
        logger.info(f"  成功: {self.stats['us_stocks']['successful']}件")
        
        logger.info(f"📊 ETF:")
        logger.info(f"  処理: {self.stats['etfs']['processed']}件")
        logger.info(f"  成功: {self.stats['etfs']['successful']}件")
        
        logger.info(f"💱 為替:")
        logger.info(f"  処理: {self.stats['forex']['processed']}件")
        logger.info(f"  成功: {self.stats['forex']['successful']}件")
        
        logger.info("=" * 80)

if __name__ == "__main__":
    collector = ParallelDataCollection()
    
    try:
        collector.run_parallel_collection()
        
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ システムエラー: {e}")
        import traceback
        traceback.print_exc()