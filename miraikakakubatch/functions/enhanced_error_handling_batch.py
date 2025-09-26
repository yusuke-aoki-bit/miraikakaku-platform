#!/usr/bin/env python3
"""
Enhanced Error Handling Batch System
High-reliability data collection with comprehensive error handling and retry logic
"""

import os
import sys
import time
import logging
import traceback
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable
import json
import random
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager

# Add paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('/mnt/c/Users/yuuku/cursor/miraikakaku')

# Database imports with fallback
try:
    from shared.database.connection_pool import get_database_connection, execute_query, execute_update
    DATABASE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Database connection pool not available: {e}")
    DATABASE_AVAILABLE = False

# Try original database imports as fallback
if not DATABASE_AVAILABLE:
    try:
        from database.cloud_sql import db_manager, StockDataRepository
        from sqlalchemy import create_engine, text
        DATABASE_AVAILABLE = True
    except ImportError as e:
        logging.error(f"Database import failed: {e}")
        DATABASE_AVAILABLE = False

# Third-party imports with error handling
try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
except ImportError as e:
    logging.error(f"Required package import failed: {e}")
    sys.exit(1)

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/enhanced_batch.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

class EnhancedBatchProcessor:
    """エラーハンドリング強化済み高信頼性バッチ処理"""

    def __init__(self):
        self.max_retries = 5
        self.base_delay = 2  # seconds
        self.max_delay = 60  # seconds
        self.timeout = 30    # seconds

        # Statistics tracking
        self.stats = {
            'total_attempts': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'retries_used': 0,
            'symbols_processed': 0,
            'records_inserted': 0,
            'start_time': datetime.now()
        }

        # Initialize database connection
        self.db_repo = None
        self._init_database()

        # Initialize HTTP session with retry strategy
        self.session = self._create_robust_session()

    def _init_database(self):
        """データベース接続を初期化（エラーハンドリング強化）"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                if db_manager.is_connected():
                    self.db_repo = StockDataRepository()
                    logger.info("✅ Database connection established successfully")
                    return
                else:
                    logger.warning(f"Database not connected, attempt {attempt + 1}/{max_attempts}")
                    time.sleep(5)
            except Exception as e:
                logger.error(f"Database initialization failed (attempt {attempt + 1}): {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(10)

    def _create_robust_session(self) -> requests.Session:
        """堅牢なHTTPセッションを作成"""
        session = requests.Session()

        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Headers
        session.headers.update({
            'User-Agent': 'MiraiKakaku-DataCollector/2.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        })

        return session

    def exponential_backoff_retry(self, func, *args, **kwargs):
        """指数バックオフによるリトライ機構"""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                self.stats['total_attempts'] += 1
                result = func(*args, **kwargs)
                self.stats['successful_operations'] += 1

                if attempt > 0:
                    logger.info(f"✅ Operation succeeded after {attempt} retries")

                return result

            except Exception as e:
                last_exception = e
                self.stats['failed_operations'] += 1

                if attempt < self.max_retries - 1:
                    # Calculate delay with jitter
                    delay = min(
                        self.base_delay * (2 ** attempt) + random.uniform(0, 1),
                        self.max_delay
                    )

                    self.stats['retries_used'] += 1
                    logger.warning(f"⚠️ Attempt {attempt + 1} failed: {str(e)[:100]}... Retrying in {delay:.2f}s")
                    time.sleep(delay)
                else:
                    logger.error(f"❌ All {self.max_retries} attempts failed for {func.__name__}")

        # All retries exhausted
        raise last_exception

    def safe_yfinance_fetch(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """安全なyfinance データ取得"""
        def _fetch():
            try:
                ticker = yf.Ticker(symbol)

                # データ取得（タイムアウト付き）
                hist = ticker.history(
                    period=period,
                    timeout=self.timeout,
                    raise_errors=True,
                    repair=True  # データ修復オプション
                )

                if hist.empty:
                    raise ValueError(f"No data returned for symbol {symbol}")

                # データ品質チェック
                if len(hist) < 5:  # 最低5日分のデータは必要
                    raise ValueError(f"Insufficient data for {symbol}: {len(hist)} records")

                # 異常値チェック
                for col in ['Close', 'High', 'Low', 'Open']:
                    if col in hist.columns:
                        if (hist[col] <= 0).any():
                            logger.warning(f"Zero or negative prices found in {symbol} {col}")
                            hist = hist[hist[col] > 0]  # 異常値を除去

                logger.debug(f"✅ Fetched {len(hist)} records for {symbol}")
                return hist

            except Exception as e:
                if "404" in str(e) or "No data found" in str(e):
                    logger.info(f"📊 Symbol {symbol} not available (404 or no data)")
                    return None
                else:
                    raise

        try:
            return self.exponential_backoff_retry(_fetch)
        except Exception as e:
            logger.error(f"❌ Failed to fetch data for {symbol}: {e}")
            return None

    def safe_database_insert(self, symbol: str, price_data: pd.DataFrame) -> int:
        """安全なデータベース挿入"""
        def _insert():
            try:
                if self.db_repo is None:
                    self._init_database()

                records_inserted = self.db_repo.insert_stock_prices(symbol, price_data)
                logger.debug(f"✅ Inserted {records_inserted} records for {symbol}")
                return records_inserted

            except Exception as e:
                if "duplicate key" in str(e).lower():
                    logger.debug(f"📝 Data already exists for {symbol} (expected)")
                    return 0
                else:
                    raise

        try:
            result = self.exponential_backoff_retry(_insert)
            self.stats['records_inserted'] += result
            return result
        except Exception as e:
            logger.error(f"❌ Database insert failed for {symbol}: {e}")
            return 0

    def get_diversified_symbols(self, count: int = 50) -> List[str]:
        """多様化された銘柄リストを取得"""

        # カテゴリ別銘柄（エラー耐性を考慮した選択）
        symbol_categories = {
            'us_mega_cap': [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B',
                'JNJ', 'V', 'WMT', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'ADBE'
            ],
            'us_growth': [
                'NFLX', 'CRM', 'ZOOM', 'SQ', 'ROKU', 'TWLO', 'OKTA', 'ZM',
                'SHOP', 'SPOT', 'UBER', 'LYFT', 'SNAP', 'PINS'
            ],
            'us_value': [
                'JPM', 'BAC', 'C', 'WFC', 'GS', 'XOM', 'CVX', 'T', 'VZ',
                'KO', 'PEP', 'MCD', 'NKE', 'IBM', 'GE'
            ],
            'etfs': [
                'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'EFA',
                'GLD', 'SLV', 'TLT', 'HYG', 'LQD', 'XLF', 'XLK', 'XLE'
            ],
            'japanese': [
                '7203.T', '6758.T', '8058.T', '4063.T', '9984.T', '6861.T',
                '8035.T', '7974.T', '4452.T', '8306.T', '9432.T'
            ],
            'crypto': [
                'BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'LINK-USD',
                'LTC-USD', 'XRP-USD', 'SOL-USD', 'AVAX-USD'
            ],
            'forex': [
                'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCAD=X',
                'USDCHF=X', 'NZDUSD=X', 'EURGBP=X'
            ]
        }

        # カテゴリ別に均等に選択
        selected_symbols = []
        symbols_per_category = max(1, count // len(symbol_categories))

        for category, symbols in symbol_categories.items():
            # シャッフルして多様性を確保
            shuffled = random.sample(symbols, min(symbols_per_category, len(symbols)))
            selected_symbols.extend(shuffled)
            logger.debug(f"Selected {len(shuffled)} symbols from {category}")

        # 目標数に調整
        if len(selected_symbols) < count:
            # 不足分を補填
            all_symbols = [s for symbols in symbol_categories.values() for s in symbols]
            remaining = [s for s in all_symbols if s not in selected_symbols]
            additional = random.sample(remaining, min(count - len(selected_symbols), len(remaining)))
            selected_symbols.extend(additional)

        return selected_symbols[:count]

    def process_symbols_batch(self, symbols: List[str]) -> Dict[str, Any]:
        """銘柄バッチ処理（並列処理とエラー隔離）"""
        results = {
            'processed': [],
            'failed': [],
            'skipped': [],
            'total_records': 0
        }

        logger.info(f"🚀 Processing batch of {len(symbols)} symbols...")

        for i, symbol in enumerate(symbols, 1):
            try:
                logger.info(f"📊 Processing {symbol} ({i}/{len(symbols)})")

                # データ取得
                price_data = self.safe_yfinance_fetch(symbol, period="2y")  # 2年分

                if price_data is None or price_data.empty:
                    results['skipped'].append(symbol)
                    logger.info(f"⏭️ Skipped {symbol} (no data)")
                    continue

                # データベース挿入
                inserted_count = self.safe_database_insert(symbol, price_data)

                results['processed'].append({
                    'symbol': symbol,
                    'records': len(price_data),
                    'inserted': inserted_count,
                    'date_range': f"{price_data.index[0].date()} to {price_data.index[-1].date()}"
                })

                results['total_records'] += inserted_count
                self.stats['symbols_processed'] += 1

                # Rate limiting（API制限対策）
                time.sleep(random.uniform(0.1, 0.3))

            except Exception as e:
                results['failed'].append({
                    'symbol': symbol,
                    'error': str(e)[:200]  # エラーメッセージを短縮
                })
                logger.error(f"❌ Failed to process {symbol}: {e}")

                # エラー後の安全な継続
                time.sleep(1)

        return results

    def generate_execution_report(self, results: Dict[str, Any]) -> str:
        """実行レポート生成"""
        duration = (datetime.now() - self.stats['start_time']).total_seconds()

        report_lines = [
            "="*80,
            "📋 Enhanced Batch Processing Report",
            "="*80,
            f"⏱️ Execution Time: {duration:.2f} seconds",
            f"📊 Total Symbols: {len(results['processed']) + len(results['failed']) + len(results['skipped'])}",
            f"✅ Successfully Processed: {len(results['processed'])}",
            f"❌ Failed: {len(results['failed'])}",
            f"⏭️ Skipped: {len(results['skipped'])}",
            f"📝 Total Records Inserted: {results['total_records']}",
            "",
            "🔢 Operation Statistics:",
            f"  • Total Attempts: {self.stats['total_attempts']}",
            f"  • Successful Operations: {self.stats['successful_operations']}",
            f"  • Failed Operations: {self.stats['failed_operations']}",
            f"  • Retries Used: {self.stats['retries_used']}",
            f"  • Success Rate: {(self.stats['successful_operations'] / max(1, self.stats['total_attempts']) * 100):.2f}%",
            "",
            "📈 Performance Metrics:",
            f"  • Symbols/Second: {self.stats['symbols_processed'] / max(1, duration):.2f}",
            f"  • Records/Second: {results['total_records'] / max(1, duration):.2f}",
            f"  • Average Retries: {self.stats['retries_used'] / max(1, len(results['processed'])):.2f}",
        ]

        # Success examples
        if results['processed']:
            report_lines.extend([
                "",
                "✅ Successfully Processed Symbols (Top 10):"
            ])
            for item in results['processed'][:10]:
                report_lines.append(f"  • {item['symbol']}: {item['records']} records ({item['date_range']})")

        # Failure analysis
        if results['failed']:
            report_lines.extend([
                "",
                "❌ Failed Symbols:"
            ])
            for item in results['failed'][:10]:  # Show first 10 failures
                report_lines.append(f"  • {item['symbol']}: {item['error']}")

        report_lines.extend([
            "="*80,
            "✅ Batch Processing Complete"
        ])

        return "\n".join(report_lines)

def main():
    """メイン実行関数"""
    logger.info("🚀 Starting Enhanced Error-Handling Batch Processing")

    try:
        processor = EnhancedBatchProcessor()

        # 銘柄リスト取得
        target_count = int(os.getenv('SYMBOL_COUNT', '100'))  # 環境変数で調整可能
        symbols = processor.get_diversified_symbols(target_count)

        logger.info(f"📋 Selected {len(symbols)} diversified symbols for processing")

        # バッチ処理実行
        results = processor.process_symbols_batch(symbols)

        # レポート生成・出力
        report = processor.generate_execution_report(results)
        print(report)

        # 統計をログ出力
        logger.info(f"✅ Processing complete: {len(results['processed'])} successful, {len(results['failed'])} failed")

        # 成功率が低い場合は警告
        success_rate = len(results['processed']) / len(symbols) * 100
        if success_rate < 70:
            logger.warning(f"⚠️ Success rate ({success_rate:.1f}%) below optimal threshold (70%)")
            return 1
        else:
            logger.info(f"🎯 Excellent success rate: {success_rate:.1f}%")
            return 0

    except Exception as e:
        logger.error(f"💥 Fatal error in batch processing: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)