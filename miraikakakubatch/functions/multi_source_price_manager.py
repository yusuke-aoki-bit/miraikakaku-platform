"""
Multi-Source Price Data Manager - 複数データソース対応版
Yahoo Finance + Alpha Vantage + pandas-datareader + その他API対応
PostgreSQL対応版
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
import yfinance as yf
import pandas as pd
import pandas_datareader as pdr
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiSourcePriceManager:
    """複数データソース対応価格データの管理クラス"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', '34.173.9.214'),
            'database': os.getenv('DB_NAME', 'miraikakaku'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'miraikakaku-secure-pass-2024'),
            'port': os.getenv('DB_PORT', '5432')
        }
        self.connection = None
        self.cursor = None

        # API設定
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.polygon_key = os.getenv('POLYGON_API_KEY', '')
        self.fmp_key = os.getenv('FMP_API_KEY', '')

        # データソース優先順位
        self.data_sources = [
            'yfinance',
            'alpha_vantage',
            'pandas_datareader_stooq',
            'pandas_datareader_tiingo',
            'polygon',
            'fmp'
        ]

    def connect(self):
        """データベース接続"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("✅ PostgreSQL接続成功")
            return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL接続エラー: {e}")
            return False

    def disconnect(self):
        """データベース切断"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def fetch_yfinance_data(self, symbol: str, days: int = 180) -> Optional[pd.DataFrame]:
        """Yahoo Financeからデータ取得"""
        try:
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            df = ticker.history(start=start_date, end=end_date)

            if df.empty:
                return None

            df.reset_index(inplace=True)
            df.columns = [col.lower() for col in df.columns]
            df['source'] = 'yfinance'

            # datetime列をdateに変換
            if df['date'].dtype.name.startswith('datetime'):
                df['date'] = df['date'].dt.date

            return df[['date', 'open', 'high', 'low', 'close', 'volume', 'source']]

        except Exception as e:
            logger.debug(f"Yahoo Finance error for {symbol}: {e}")
            return None

    def fetch_alpha_vantage_data(self, symbol: str, days: int = 180) -> Optional[pd.DataFrame]:
        """Alpha Vantageからデータ取得"""
        try:
            if self.alpha_vantage_key == 'demo':
                return None

            # 為替の場合
            if '=X' in symbol or 'USD' in symbol:
                from_currency = symbol.replace('USD=X', '').replace('=X', '')
                to_currency = 'USD'
                url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={from_currency}&to_symbol={to_currency}&apikey={self.alpha_vantage_key}"
            else:
                # 株式の場合
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={self.alpha_vantage_key}"

            response = requests.get(url)
            data = response.json()

            if 'Error Message' in data or 'Note' in data:
                return None

            # データ解析
            time_series_key = None
            for key in data.keys():
                if 'Time Series' in key or 'FX' in key:
                    time_series_key = key
                    break

            if not time_series_key:
                return None

            time_series = data[time_series_key]

            # DataFrameに変換
            rows = []
            for date_str, values in time_series.items():
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

                # キー名の調整（Alpha Vantageは異なるキー名を使用）
                if 'FX' in time_series_key:
                    row = {
                        'date': date_obj,
                        'open': float(values.get('1. open', values.get('1a. open (EUR)', 0))),
                        'high': float(values.get('2. high', values.get('2a. high (EUR)', 0))),
                        'low': float(values.get('3. low', values.get('3a. low (EUR)', 0))),
                        'close': float(values.get('4. close', values.get('4a. close (EUR)', 0))),
                        'volume': 0,  # 為替にはボリュームなし
                        'source': 'alpha_vantage'
                    }
                else:
                    row = {
                        'date': date_obj,
                        'open': float(values.get('1. open', 0)),
                        'high': float(values.get('2. high', 0)),
                        'low': float(values.get('3. low', 0)),
                        'close': float(values.get('4. close', 0)),
                        'volume': int(float(values.get('5. volume', 0))),
                        'source': 'alpha_vantage'
                    }
                rows.append(row)

            df = pd.DataFrame(rows)
            df = df[df['date'] >= (datetime.now().date() - timedelta(days=days))]

            return df if not df.empty else None

        except Exception as e:
            logger.debug(f"Alpha Vantage error for {symbol}: {e}")
            return None

    def fetch_pandas_datareader_data(self, symbol: str, source: str, days: int = 180) -> Optional[pd.DataFrame]:
        """pandas-datareaderからデータ取得"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # ソース別の設定
            if source == 'pandas_datareader_stooq':
                df = pdr.get_data_stooq(symbol, start=start_date, end=end_date)
            elif source == 'pandas_datareader_tiingo':
                df = pdr.get_data_tiingo(symbol, start=start_date, end=end_date)
            else:
                return None

            if df.empty:
                return None

            df.reset_index(inplace=True)
            df.columns = [col.lower() for col in df.columns]
            df['source'] = source

            # カラム名の統一
            if 'date' not in df.columns and 'timestamp' in df.columns:
                df['date'] = df['timestamp']

            required_cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'source']
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                for col in missing_cols:
                    if col == 'volume':
                        df[col] = 0
                    elif col != 'source':
                        return None

            return df[required_cols]

        except Exception as e:
            logger.debug(f"pandas-datareader {source} error for {symbol}: {e}")
            return None

    def fetch_polygon_data(self, symbol: str, days: int = 180) -> Optional[pd.DataFrame]:
        """Polygon.ioからデータ取得"""
        try:
            if not self.polygon_key:
                return None

            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)

            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}?apikey={self.polygon_key}"

            response = requests.get(url)
            data = response.json()

            if data.get('status') != 'OK' or not data.get('results'):
                return None

            rows = []
            for result in data['results']:
                date_obj = datetime.fromtimestamp(result['t'] / 1000).date()
                row = {
                    'date': date_obj,
                    'open': float(result['o']),
                    'high': float(result['h']),
                    'low': float(result['l']),
                    'close': float(result['c']),
                    'volume': int(result['v']),
                    'source': 'polygon'
                }
                rows.append(row)

            df = pd.DataFrame(rows)
            return df if not df.empty else None

        except Exception as e:
            logger.debug(f"Polygon error for {symbol}: {e}")
            return None

    def fetch_fmp_data(self, symbol: str, days: int = 180) -> Optional[pd.DataFrame]:
        """Financial Modeling Prepからデータ取得"""
        try:
            if not self.fmp_key:
                return None

            url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?apikey={self.fmp_key}"

            response = requests.get(url)
            data = response.json()

            if 'historical' not in data:
                return None

            rows = []
            cutoff_date = datetime.now().date() - timedelta(days=days)

            for record in data['historical']:
                date_obj = datetime.strptime(record['date'], '%Y-%m-%d').date()

                if date_obj < cutoff_date:
                    continue

                row = {
                    'date': date_obj,
                    'open': float(record['open']),
                    'high': float(record['high']),
                    'low': float(record['low']),
                    'close': float(record['close']),
                    'volume': int(record['volume']),
                    'source': 'fmp'
                }
                rows.append(row)

            df = pd.DataFrame(rows)
            return df if not df.empty else None

        except Exception as e:
            logger.debug(f"FMP error for {symbol}: {e}")
            return None

    def fetch_multi_source_data(self, symbol: str, days: int = 180) -> Tuple[Optional[pd.DataFrame], str]:
        """複数ソースからデータ取得（フォールバック機能付き）"""

        for source in self.data_sources:
            try:
                logger.debug(f"Trying {source} for {symbol}")

                if source == 'yfinance':
                    df = self.fetch_yfinance_data(symbol, days)
                elif source == 'alpha_vantage':
                    df = self.fetch_alpha_vantage_data(symbol, days)
                elif source.startswith('pandas_datareader'):
                    df = self.fetch_pandas_datareader_data(symbol, source, days)
                elif source == 'polygon':
                    df = self.fetch_polygon_data(symbol, days)
                elif source == 'fmp':
                    df = self.fetch_fmp_data(symbol, days)
                else:
                    continue

                if df is not None and not df.empty:
                    logger.info(f"✅ {symbol}: データ取得成功 ({source}) - {len(df)}レコード")
                    return df, source

                # API制限を考慮して少し待機
                if source in ['alpha_vantage', 'polygon', 'fmp']:
                    time.sleep(0.2)

            except Exception as e:
                logger.debug(f"Error with {source} for {symbol}: {e}")
                continue

        logger.warning(f"❌ {symbol}: 全ソースでデータ取得失敗")
        return None, 'none'

    def update_multi_source_price_data(self, symbols: Optional[List[str]] = None, max_workers: int = 5) -> Dict:
        """マルチソース価格データの更新（並列処理対応）"""
        if not symbols:
            # アクティブな銘柄を取得
            self.cursor.execute("""
                SELECT symbol FROM stock_master
                WHERE is_active = true
                ORDER BY symbol
                LIMIT 100
            """)
            symbols = [row['symbol'] for row in self.cursor.fetchall()]

        updated = []
        failed = []
        records_added = 0
        source_stats = {}

        def process_symbol(symbol):
            """個別銘柄の処理"""
            try:
                # 最新の価格日付を取得
                with psycopg2.connect(**self.db_config) as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("""
                            SELECT MAX(date) as last_date
                            FROM stock_prices
                            WHERE symbol = %s
                        """, (symbol,))

                        result = cur.fetchone()
                        last_date = result['last_date'] if result and result['last_date'] else None

                        # 取得期間の決定
                        if last_date:
                            days_needed = (datetime.now().date() - last_date).days + 1
                            if days_needed <= 1:
                                return symbol, 'skipped', 0, 'up_to_date'
                        else:
                            days_needed = 180

                        # マルチソースからデータ取得
                        df, source_used = self.fetch_multi_source_data(symbol, days_needed)

                        if df is None or df.empty:
                            return symbol, 'failed', 0, 'no_data'

                        # 既存データとの重複を除外
                        if last_date:
                            # datetime列をdateに変換
                            if df['date'].dtype.name.startswith('datetime'):
                                df['date'] = df['date'].dt.date
                            df = df[df['date'] > last_date]

                        if df.empty:
                            return symbol, 'skipped', 0, 'no_new_data'

                        # データベースに保存
                        records = []
                        for _, row in df.iterrows():
                            records.append((
                                symbol,
                                row['date'],
                                float(row['open']),
                                float(row['high']),
                                float(row['low']),
                                float(row['close']),
                                int(row['volume']) if pd.notna(row['volume']) else 0,
                                datetime.now(),
                                row.get('source', source_used)
                            ))

                        if records:
                            execute_batch(cur, """
                                INSERT INTO stock_prices
                                (symbol, date, open_price, high_price, low_price, close_price, volume, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (symbol, date) DO UPDATE
                                SET open_price = EXCLUDED.open_price,
                                    high_price = EXCLUDED.high_price,
                                    low_price = EXCLUDED.low_price,
                                    close_price = EXCLUDED.close_price,
                                    volume = EXCLUDED.volume
                            """, [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]) for r in records])

                            conn.commit()
                            return symbol, 'success', len(records), source_used

                        return symbol, 'skipped', 0, 'no_records'

            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                return symbol, 'failed', 0, 'error'

        # 並列処理で実行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {executor.submit(process_symbol, symbol): symbol for symbol in symbols}

            for future in as_completed(future_to_symbol):
                symbol, status, record_count, source_used = future.result()

                if status == 'success':
                    updated.append(symbol)
                    records_added += record_count
                    source_stats[source_used] = source_stats.get(source_used, 0) + 1
                    logger.info(f"✅ {symbol}: {record_count}レコード追加 ({source_used})")
                elif status == 'failed':
                    failed.append(symbol)

        return {
            'updated': updated,
            'failed': failed,
            'source_stats': source_stats,
            'summary': {
                'updated_count': len(updated),
                'failed_count': len(failed),
                'records_added': records_added,
                'sources_used': len(source_stats)
            }
        }

    def verify_multi_source_coverage(self) -> Dict:
        """マルチソース価格データカバレッジの確認"""
        try:
            # データソース別統計（注: この情報を保存する場合はスキーマ拡張が必要）
            self.cursor.execute("""
                SELECT
                    COUNT(DISTINCT symbol) as symbols_with_prices,
                    COUNT(*) as total_price_records,
                    MIN(date) as earliest_date,
                    MAX(date) as latest_date,
                    AVG(volume) as avg_volume
                FROM stock_prices
            """)
            overall_stats = dict(self.cursor.fetchone())

            # 最新データの鮮度確認
            self.cursor.execute("""
                SELECT
                    symbol,
                    MAX(date) as last_update,
                    COUNT(*) as record_count,
                    CURRENT_DATE - MAX(date) as days_since_update
                FROM stock_prices
                GROUP BY symbol
                HAVING CURRENT_DATE - MAX(date) <= 30
                ORDER BY days_since_update
                LIMIT 20
            """)
            recent_updates = self.cursor.fetchall()

            # データギャップの確認
            self.cursor.execute("""
                SELECT
                    symbol,
                    CURRENT_DATE - MAX(date) as days_behind
                FROM stock_prices
                GROUP BY symbol
                HAVING CURRENT_DATE - MAX(date) > 7
                ORDER BY days_behind DESC
                LIMIT 20
            """)
            data_gaps = self.cursor.fetchall()

            logger.info(f"📊 マルチソース価格データ統計:")
            logger.info(f"  - 価格データがある銘柄: {overall_stats['symbols_with_prices']}")
            logger.info(f"  - 総レコード数: {overall_stats['total_price_records']:,}")
            logger.info(f"  - データ期間: {overall_stats['earliest_date']} ~ {overall_stats['latest_date']}")

            return {
                'overall': overall_stats,
                'recent_updates': recent_updates,
                'data_gaps': data_gaps
            }

        except Exception as e:
            logger.error(f"❌ マルチソースカバレッジ確認エラー: {e}")
            return None


def main():
    """メイン処理"""
    logger.info("🚀 Multi-Source Price Data Manager開始")

    # バッチモードの取得
    mode = os.getenv('BATCH_MODE', 'verify')
    max_workers = int(os.getenv('MAX_WORKERS', '5'))

    manager = MultiSourcePriceManager()

    if not manager.connect():
        logger.error("データベース接続失敗")
        sys.exit(1)

    try:
        if mode == 'verify':
            # マルチソース価格データカバレッジの確認
            result = manager.verify_multi_source_coverage()
            if result:
                logger.info(f"✅ マルチソースカバレッジ確認完了")

        elif mode == 'update':
            # マルチソース価格データの更新
            symbols_str = os.getenv('SYMBOLS_TO_UPDATE', '')
            symbols = None

            if symbols_str:
                symbols = [s.strip() for s in symbols_str.split(',')]

            result = manager.update_multi_source_price_data(symbols, max_workers)
            logger.info(f"✅ マルチソース更新結果: {result['summary']}")
            logger.info(f"📊 使用データソース: {result['source_stats']}")

        elif mode == 'massive_update':
            # 大規模価格データ更新
            max_symbols = int(os.getenv('MAX_SYMBOLS', '1000'))
            days_back = int(os.getenv('DAYS_BACK', '365'))

            logger.info(f"🚀 大規模価格データ更新開始: 最大{max_symbols}銘柄、{days_back}日分")

            # 全銘柄から価格データが少ない順にソート
            manager.cursor.execute("""
                SELECT sm.symbol
                FROM stock_master sm
                LEFT JOIN (
                    SELECT symbol, COUNT(*) as price_count
                    FROM stock_prices
                    GROUP BY symbol
                ) sp ON sm.symbol = sp.symbol
                WHERE sm.is_active = true
                ORDER BY COALESCE(sp.price_count, 0) ASC, sm.symbol
                LIMIT %s
            """, (max_symbols,))

            symbols = [row[0] for row in manager.cursor.fetchall()]
            logger.info(f"📊 対象銘柄: {len(symbols)}銘柄")

            if symbols:
                result = manager.update_multi_source_price_data(symbols, max_workers)
                logger.info(f"✅ 大規模更新結果: {result['summary']}")
                logger.info(f"📊 使用データソース: {result['source_stats']}")
            else:
                logger.warning("対象銘柄が見つかりませんでした")

        else:
            logger.warning(f"不明なモード: {mode}")

    except Exception as e:
        logger.error(f"❌ 処理エラー: {e}")
        sys.exit(1)

    finally:
        manager.disconnect()
        logger.info("✅ Multi-Source Price Data Manager完了")


if __name__ == "__main__":
    main()