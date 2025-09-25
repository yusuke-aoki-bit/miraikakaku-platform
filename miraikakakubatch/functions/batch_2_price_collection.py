#!/usr/bin/env python3
"""
Batch 2: Price Collection System
価格収集専用バッチシステム
"""

import os
import sys
import psycopg2
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceCollectionBatch:
    """価格収集専用バッチ"""

    def __init__(self):
        self.db_config = {
            'host': '34.173.9.214',
            'user': 'postgres',
            'password': 'os.getenv('DB_PASSWORD', '')',
            'database': 'miraikakaku'
        }

    def connect_database(self):
        """データベース接続"""
        try:
            conn = psycopg2.connect(**self.db_config)
            logger.info("✅ Database connected")
            return conn
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return None

    def get_active_symbols(self, cursor, limit=None):
        """アクティブ銘柄取得"""
        try:
            query = """
                SELECT symbol, name, exchange
                FROM stock_master
                WHERE is_active = true
                ORDER BY
                    CASE
                        WHEN exchange LIKE '%NASDAQ%' THEN 1
                        WHEN exchange LIKE '%NYSE%' THEN 2
                        WHEN symbol LIKE '%-USD' THEN 3
                        WHEN symbol LIKE '%.T' THEN 4
                        ELSE 5
                    END,
                    symbol
            """

            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            symbols = cursor.fetchall()
            logger.info(f"📊 Found {len(symbols)} active symbols")
            return symbols

        except Exception as e:
            logger.error(f"❌ Failed to get active symbols: {e}")
            return []

    def get_last_price_date(self, cursor, symbol):
        """最終価格データ日付取得"""
        try:
            cursor.execute("""
                SELECT MAX(date) FROM stock_prices
                WHERE symbol = %s
            """, (symbol,))

            result = cursor.fetchone()
            return result[0] if result[0] else None

        except Exception as e:
            logger.warning(f"⚠️ Failed to get last price date for {symbol}: {e}")
            return None

    def collect_historical_prices(self, symbol, start_date, end_date):
        """過去価格データ収集"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date, auto_adjust=True)

            if hist.empty:
                logger.warning(f"  ⚠️ {symbol}: No price data available")
                return []

            price_data = []
            for date, row in hist.iterrows():
                try:
                    # データ検証
                    open_price = float(row['Open']) if not pd.isna(row['Open']) else None
                    high_price = float(row['High']) if not pd.isna(row['High']) else None
                    low_price = float(row['Low']) if not pd.isna(row['Low']) else None
                    close_price = float(row['Close']) if not pd.isna(row['Close']) else None
                    volume = int(row['Volume']) if not pd.isna(row['Volume']) else 0

                    # 価格データの合理性チェック
                    if close_price and close_price > 0:
                        price_data.append({
                            'date': date.date(),
                            'open_price': open_price,
                            'high_price': high_price,
                            'low_price': low_price,
                            'close_price': close_price,
                            'volume': volume
                        })

                except Exception as e:
                    logger.warning(f"  ⚠️ {symbol}: Invalid data for {date}: {e}")
                    continue

            logger.info(f"  📈 {symbol}: Collected {len(price_data)} price records")
            return price_data

        except Exception as e:
            logger.error(f"  ❌ {symbol}: Failed to collect prices - {e}")
            return []

    def insert_price_data(self, cursor, symbol, price_data):
        """価格データ挿入"""
        inserted_count = 0

        try:
            for data in price_data:
                cursor.execute("""
                    INSERT INTO stock_prices
                    (symbol, date, open_price, high_price, low_price, close_price, volume, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (symbol, date)
                    DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume,
                        updated_at = NOW()
                """, (
                    symbol, data['date'], data['open_price'], data['high_price'],
                    data['low_price'], data['close_price'], data['volume']
                ))
                inserted_count += 1

            return inserted_count

        except Exception as e:
            logger.error(f"❌ Failed to insert price data for {symbol}: {e}")
            return 0

    def run_price_collection(self, days_back=90, symbol_limit=None):
        """価格収集メイン処理"""
        conn = self.connect_database()
        if not conn:
            return False

        cursor = conn.cursor()

        try:
            # アクティブ銘柄取得
            symbols = self.get_active_symbols(cursor, symbol_limit)
            if not symbols:
                logger.error("❌ No active symbols found")
                return False

            total_symbols = len(symbols)
            successful_symbols = 0
            total_prices = 0

            # 収集期間設定
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            logger.info("🚀 Starting Price Collection Batch")
            logger.info("=" * 60)
            logger.info(f"📅 Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            logger.info(f"📊 Target symbols: {total_symbols}")

            for i, (symbol, name, exchange) in enumerate(symbols, 1):
                try:
                    logger.info(f"📈 [{i}/{total_symbols}] Processing {symbol} ({exchange})")

                    # 最終価格データ日付確認
                    last_date = self.get_last_price_date(cursor, symbol)

                    # 収集開始日調整
                    if last_date:
                        collection_start = max(start_date.date(), last_date - timedelta(days=7))
                        logger.info(f"  📅 Last data: {last_date}, collecting from {collection_start}")
                    else:
                        collection_start = start_date.date()
                        logger.info(f"  📅 No existing data, collecting from {collection_start}")

                    # 価格データ収集
                    price_data = self.collect_historical_prices(
                        symbol, collection_start, end_date.date()
                    )

                    if price_data:
                        # データベース挿入
                        inserted_count = self.insert_price_data(cursor, symbol, price_data)

                        if inserted_count > 0:
                            successful_symbols += 1
                            total_prices += inserted_count
                            logger.info(f"  ✅ {symbol}: {inserted_count} prices inserted/updated")

                        # 定期コミット（10銘柄ごと）
                        if i % 10 == 0:
                            conn.commit()
                            logger.info(f"  💾 Committed batch {i}")

                    else:
                        logger.warning(f"  ⚠️ {symbol}: No price data collected")

                    # レート制限回避
                    time.sleep(0.3)

                except Exception as e:
                    logger.error(f"❌ Error processing {symbol}: {e}")
                    continue

            # 最終コミット
            conn.commit()

            # 結果サマリー
            logger.info("=" * 60)
            logger.info("🎉 Price Collection Batch Complete")
            logger.info(f"✅ Symbols processed: {total_symbols}")
            logger.info(f"✅ Successful collections: {successful_symbols}")
            logger.info(f"📊 Total prices collected: {total_prices}")
            logger.info(f"📈 Success rate: {successful_symbols/total_symbols*100:.1f}%")
            logger.info(f"📊 Avg prices per symbol: {total_prices/max(1,successful_symbols):.1f}")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"❌ Price collection batch failed: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_price_statistics(self):
        """価格データ統計情報取得"""
        conn = self.connect_database()
        if not conn:
            return None

        cursor = conn.cursor()

        try:
            # 総価格データ数
            cursor.execute("SELECT COUNT(*) FROM stock_prices")
            total_prices = cursor.fetchone()[0]

            # 銘柄別価格データ数
            cursor.execute("""
                SELECT symbol, COUNT(*) as price_count,
                       MIN(date) as first_date,
                       MAX(date) as last_date
                FROM stock_prices
                GROUP BY symbol
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """)
            symbol_stats = cursor.fetchall()

            # 最近のデータ更新
            cursor.execute("""
                SELECT symbol, date, close_price
                FROM stock_prices
                WHERE date >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY date DESC, symbol
                LIMIT 20
            """)
            recent_updates = cursor.fetchall()

            # データ欠損チェック
            cursor.execute("""
                SELECT symbol, COUNT(*) as days_count
                FROM stock_prices
                WHERE date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY symbol
                HAVING COUNT(*) < 20
                ORDER BY COUNT(*)
                LIMIT 10
            """)
            missing_data = cursor.fetchall()

            return {
                'total_prices': total_prices,
                'symbol_stats': symbol_stats,
                'recent_updates': recent_updates,
                'missing_data': missing_data
            }

        except Exception as e:
            logger.error(f"❌ Failed to get statistics: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

def main():
    """メイン実行"""
    batch = PriceCollectionBatch()

    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            # 統計情報表示
            stats = batch.get_price_statistics()
            if stats:
                print("\n📊 Price Collection Statistics")
                print("=" * 50)
                print(f"Total Price Records: {stats['total_prices']:,}")
                print("\nTop Symbols by Data Count:")
                for symbol, count, first, last in stats['symbol_stats']:
                    print(f"  {symbol}: {count} records ({first} to {last})")
                print("\nRecent Updates:")
                for symbol, date, price in stats['recent_updates'][:10]:
                    print(f"  {symbol}: ${price:.2f} on {date}")
                if stats['missing_data']:
                    print("\nSymbols with Missing Data (last 30 days):")
                    for symbol, count in stats['missing_data']:
                        print(f"  {symbol}: only {count} days")

        elif sys.argv[1] == "quick":
            # クイック実行（最近30日、30銘柄限定）
            success = batch.run_price_collection(days_back=30, symbol_limit=30)

        elif sys.argv[1].isdigit():
            # 指定銘柄数で実行
            limit = int(sys.argv[1])
            success = batch.run_price_collection(symbol_limit=limit)

        else:
            print("Usage: python batch_2_price_collection.py [stats|quick|<number>]")
            sys.exit(1)
    else:
        # 通常実行（全銘柄、90日）
        success = batch.run_price_collection()

    if 'success' in locals():
        if success:
            print("\n🎉 Price Collection Batch completed successfully!")
        else:
            print("\n❌ Price Collection Batch failed")
            sys.exit(1)

if __name__ == "__main__":
    main()