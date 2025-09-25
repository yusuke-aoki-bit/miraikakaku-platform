#!/usr/bin/env python3
"""
Batch 1: Symbol Collection System
銘柄収集専用バッチシステム
"""

import os
import sys
import psycopg2
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SymbolCollectionBatch:
    """銘柄収集専用バッチ"""

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

    def get_symbol_lists(self):
        """銘柄リスト取得"""
        symbols = {
            'us_stocks': [
                # 主要テック株
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA',
                'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'UBER',

                # 金融・ヘルスケア
                'JPM', 'BAC', 'WFC', 'GS', 'MS', 'JNJ', 'PFE', 'UNH', 'ABBV',

                # 消費財・エネルギー
                'PG', 'KO', 'PEP', 'WMT', 'HD', 'DIS', 'MCD', 'NKE',
                'XOM', 'CVX', 'COP', 'SLB',

                # 通信・公益
                'VZ', 'T', 'TMUS', 'CMCSA', 'NEE', 'SO', 'DUK'
            ],

            'crypto': [
                'BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD',
                'SOL-USD', 'DOGE-USD', 'AVAX-USD', 'DOT-USD', 'MATIC-USD',
                'LTC-USD', 'LINK-USD', 'UNI-USD', 'ATOM-USD', 'VET-USD',
                'TRX-USD', 'FIL-USD', 'ICP-USD', 'NEAR-USD', 'ALGO-USD'
            ],

            'etfs': [
                'SPY', 'QQQ', 'VTI', 'VOO', 'IWM', 'VEA', 'VWO', 'EFA',
                'AGG', 'TLT', 'LQD', 'HYG', 'GLD', 'SLV', 'USO', 'XLF',
                'XLK', 'XLE', 'XLV', 'XLI', 'XLP', 'XLU', 'XLRE', 'XLY'
            ],

            'japanese_stocks': [
                '7203.T', '6758.T', '9984.T', '8306.T', '6861.T', '4519.T',
                '6502.T', '9432.T', '8035.T', '6954.T', '7974.T', '4063.T',
                '6981.T', '8316.T', '7267.T', '6501.T', '8766.T', '4568.T'
            ]
        }

        return symbols

    def collect_symbol_info(self, symbol):
        """個別銘柄情報収集"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # 基本情報取得
            symbol_data = {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'company_name': info.get('longName', info.get('shortName', symbol)),
                'exchange': info.get('exchange', info.get('market', 'UNKNOWN')),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', None),
                'currency': info.get('currency', 'USD'),
                'country': info.get('country', 'Unknown')
            }

            logger.info(f"  📊 {symbol}: {symbol_data['name']} ({symbol_data['exchange']})")
            return symbol_data

        except Exception as e:
            logger.warning(f"  ⚠️ {symbol}: Failed to fetch info - {e}")
            return {
                'symbol': symbol,
                'name': symbol,
                'company_name': symbol,
                'exchange': 'UNKNOWN',
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market_cap': None,
                'currency': 'USD',
                'country': 'Unknown'
            }

    def insert_or_update_symbol(self, cursor, symbol_data):
        """銘柄データ挿入・更新"""
        try:
            cursor.execute("""
                INSERT INTO stock_master
                (symbol, name, company_name, exchange, sector, industry,
                 market_cap, currency, country, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, true, NOW(), NOW())
                ON CONFLICT (symbol)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    company_name = EXCLUDED.company_name,
                    exchange = EXCLUDED.exchange,
                    sector = EXCLUDED.sector,
                    industry = EXCLUDED.industry,
                    market_cap = EXCLUDED.market_cap,
                    currency = EXCLUDED.currency,
                    country = EXCLUDED.country,
                    is_active = true,
                    updated_at = NOW()
            """, (
                symbol_data['symbol'], symbol_data['name'], symbol_data['company_name'],
                symbol_data['exchange'], symbol_data['sector'], symbol_data['industry'],
                symbol_data['market_cap'], symbol_data['currency'], symbol_data['country']
            ))
            return True
        except Exception as e:
            logger.error(f"❌ Failed to insert {symbol_data['symbol']}: {e}")
            return False

    def run_symbol_collection(self):
        """銘柄収集メイン処理"""
        conn = self.connect_database()
        if not conn:
            return False

        cursor = conn.cursor()

        try:
            symbol_lists = self.get_symbol_lists()
            total_symbols = 0
            successful_symbols = 0

            logger.info("🚀 Starting Symbol Collection Batch")
            logger.info("=" * 60)

            for category, symbols in symbol_lists.items():
                logger.info(f"📂 Processing {category.upper()} ({len(symbols)} symbols)")

                for symbol in symbols:
                    try:
                        # 銘柄情報収集
                        symbol_data = self.collect_symbol_info(symbol)

                        # データベース挿入
                        if self.insert_or_update_symbol(cursor, symbol_data):
                            successful_symbols += 1

                        total_symbols += 1

                        # 定期コミット（10件ごと）
                        if total_symbols % 10 == 0:
                            conn.commit()
                            logger.info(f"  💾 Committed {total_symbols} symbols")

                        # レート制限回避
                        time.sleep(0.5)

                    except Exception as e:
                        logger.error(f"❌ Error processing {symbol}: {e}")
                        continue

                logger.info(f"✅ {category.upper()} completed")

            # 最終コミット
            conn.commit()

            # 結果サマリー
            logger.info("=" * 60)
            logger.info("🎉 Symbol Collection Batch Complete")
            logger.info(f"✅ Total symbols processed: {total_symbols}")
            logger.info(f"✅ Successfully added/updated: {successful_symbols}")
            logger.info(f"📊 Success rate: {successful_symbols/total_symbols*100:.1f}%")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"❌ Symbol collection batch failed: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_symbol_statistics(self):
        """銘柄統計情報取得"""
        conn = self.connect_database()
        if not conn:
            return None

        cursor = conn.cursor()

        try:
            # 総銘柄数
            cursor.execute("SELECT COUNT(*) FROM stock_master WHERE is_active = true")
            total_symbols = cursor.fetchone()[0]

            # 取引所別統計
            cursor.execute("""
                SELECT exchange, COUNT(*)
                FROM stock_master
                WHERE is_active = true
                GROUP BY exchange
                ORDER BY COUNT(*) DESC
            """)
            exchange_stats = cursor.fetchall()

            # セクター別統計
            cursor.execute("""
                SELECT sector, COUNT(*)
                FROM stock_master
                WHERE is_active = true AND sector != 'Unknown'
                GROUP BY sector
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """)
            sector_stats = cursor.fetchall()

            # 最近追加された銘柄
            cursor.execute("""
                SELECT symbol, name, exchange, created_at
                FROM stock_master
                WHERE is_active = true
                ORDER BY created_at DESC
                LIMIT 10
            """)
            recent_symbols = cursor.fetchall()

            return {
                'total_symbols': total_symbols,
                'exchange_stats': exchange_stats,
                'sector_stats': sector_stats,
                'recent_symbols': recent_symbols
            }

        except Exception as e:
            logger.error(f"❌ Failed to get statistics: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

def main():
    """メイン実行"""
    batch = SymbolCollectionBatch()

    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        # 統計情報表示
        stats = batch.get_symbol_statistics()
        if stats:
            print("\n📊 Symbol Collection Statistics")
            print("=" * 50)
            print(f"Total Active Symbols: {stats['total_symbols']}")
            print("\nTop Exchanges:")
            for exchange, count in stats['exchange_stats'][:10]:
                print(f"  {exchange}: {count}")
            print("\nTop Sectors:")
            for sector, count in stats['sector_stats']:
                print(f"  {sector}: {count}")
            print("\nRecently Added:")
            for symbol, name, exchange, created_at in stats['recent_symbols']:
                print(f"  {symbol} ({exchange}) - {created_at.strftime('%Y-%m-%d')}")
    else:
        # 銘柄収集実行
        success = batch.run_symbol_collection()

        if success:
            print("\n🎉 Symbol Collection Batch completed successfully!")
        else:
            print("\n❌ Symbol Collection Batch failed")
            sys.exit(1)

if __name__ == "__main__":
    main()