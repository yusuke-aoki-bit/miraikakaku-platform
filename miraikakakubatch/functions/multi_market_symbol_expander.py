#!/usr/bin/env python3
"""
Multi-Market Symbol Expander for Miraikakaku
米国・日本・ETF・為替の多様な銘柄を拡張収集
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Set
from datetime import datetime
import yfinance as yf
import time

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from miraikakakuapi.functions.database.cloud_sql import db_manager
except ImportError:
    print("⚠️ Database module not available, using mock database")
    db_manager = None

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiMarketSymbolExpander:
    """多市場銘柄拡張システム"""

    def __init__(self):
        self.db_manager = db_manager
        self.processed_symbols = set()
        self.successful_symbols = set()
        self.failed_symbols = set()

        # 対象市場の銘柄カテゴリ
        self.symbol_categories = {
            'us_mega_cap': [
                'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META',
                'BRK-A', 'BRK-B', 'UNH', 'JNJ', 'JPM', 'V', 'PG', 'HD', 'MA',
                'ASML', 'LLY', 'AVGO', 'XOM', 'ABBV', 'NVO', 'PFE', 'TMO',
                'BAC', 'CVX', 'KO', 'ORCL', 'PEP', 'COST', 'DIS', 'ADBE',
                'WMT', 'CSCO', 'ACN', 'DHR', 'VZ', 'MCD', 'ABT', 'LIN',
                'CRM', 'TXN', 'NFLX', 'AMD', 'WFC', 'PM', 'RTX', 'QCOM',
                'CAT', 'INTU', 'IBM', 'GS', 'HON', 'SPGI', 'LOW', 'T'
            ],
            'us_growth': [
                'SHOP', 'SQ', 'ROKU', 'ZOOM', 'DOCU', 'ZM', 'PTON', 'PLTR',
                'SNAP', 'UBER', 'LYFT', 'TWTR', 'PINS', 'SPOT', 'SE', 'BABA',
                'JD', 'PDD', 'BILI', 'NIO', 'XPEV', 'LI', 'DIDI', 'GRAB'
            ],
            'us_tech': [
                'CRM', 'NOW', 'SNOW', 'DDOG', 'OKTA', 'ZS', 'CRWD', 'FTNT',
                'PANW', 'NET', 'TEAM', 'WDAY', 'SPLK', 'VEEV', 'ZI', 'ESTC'
            ],
            'japan_nikkei': [
                '7203.T', '9984.T', '6758.T', '9433.T', '8306.T', '6861.T',
                '6501.T', '7267.T', '6594.T', '4519.T', '8316.T', '6752.T',
                '4568.T', '7974.T', '8035.T', '6367.T', '9020.T', '6178.T',
                '6981.T', '4523.T', '9432.T', '4704.T', '7751.T', '6098.T',
                '8001.T', '8031.T', '8002.T', '7182.T', '7270.T', '6326.T'
            ],
            'japan_growth': [
                '4755.T', '3659.T', '4385.T', '4689.T', '2432.T', '3825.T',
                '4477.T', '6619.T', '4751.T', '3962.T', '4178.T', '3691.T',
                '6079.T', '4490.T', '6094.T', '4776.T', '3900.T', '4880.T'
            ],
            'etf_us': [
                'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'BND',
                'AGG', 'LQD', 'HYG', 'TIP', 'GLD', 'SLV', 'USO', 'UNG',
                'XLK', 'XLF', 'XLE', 'XLV', 'XLI', 'XLY', 'XLP', 'XLU',
                'ARKK', 'ARKG', 'ARKQ', 'ARKW', 'ARKF', 'ICLN', 'MOON',
                'SOXX', 'SMH', 'IBB', 'XBI', 'BOTZ', 'ROBO', 'JETS', 'HACK'
            ],
            'etf_japan': [
                '1321.T', '1306.T', '1570.T', '1343.T', '1364.T', '1472.T',
                '1348.T', '1349.T', '1475.T', '1346.T', '1577.T', '1579.T'
            ],
            'forex_major': [
                'USDJPY=X', 'EURUSD=X', 'GBPUSD=X', 'AUDUSD=X', 'USDCAD=X',
                'USDCHF=X', 'EURJPY=X', 'GBPJPY=X', 'AUDJPY=X', 'NZDUSD=X'
            ],
            'crypto_major': [
                'BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD',
                'SOL-USD', 'DOT-USD', 'DOGE-USD', 'AVAX-USD', 'SHIB-USD'
            ],
            'commodities': [
                'GC=F', 'SI=F', 'CL=F', 'NG=F', 'ZC=F', 'ZS=F', 'ZW=F',
                'KC=F', 'CC=F', 'CT=F', 'LBS=F', 'HG=F', 'PA=F', 'PL=F'
            ]
        }

    def get_all_target_symbols(self) -> List[str]:
        """すべての対象銘柄リストを取得"""
        all_symbols = []
        for category, symbols in self.symbol_categories.items():
            all_symbols.extend(symbols)
            logger.info(f"📊 {category}: {len(symbols)} symbols")

        logger.info(f"🎯 Total target symbols: {len(all_symbols)}")
        return all_symbols

    def validate_symbol(self, symbol: str) -> bool:
        """銘柄の有効性を検証"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # 基本情報の存在確認
            if not info or 'symbol' not in info:
                return False

            # 最近の価格データ確認
            hist = ticker.history(period="5d")
            if hist.empty:
                return False

            logger.debug(f"✅ {symbol} validated successfully")
            return True

        except Exception as e:
            logger.warning(f"❌ {symbol} validation failed: {e}")
            return False

    def get_symbol_info(self, symbol: str) -> Dict:
        """銘柄の詳細情報を取得"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'country': info.get('country', 'Unknown'),
                'currency': info.get('currency', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'exchange': info.get('exchange', 'Unknown'),
                'updated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get info for {symbol}: {e}")
            return None

    async def register_symbol_to_db(self, symbol_info: Dict) -> bool:
        """銘柄をデータベースに登録"""
        if not self.db_manager:
            logger.warning("Database manager not available")
            return False

        try:
            # Check if symbol already exists
            cursor = self.db_manager.get_cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM stock_master WHERE symbol = %s",
                (symbol_info['symbol'],)
            )
            exists = cursor.fetchone()[0] > 0

            if exists:
                logger.debug(f"📝 {symbol_info['symbol']} already exists in database")
                return True

            # Insert new symbol
            cursor.execute("""
                INSERT INTO stock_master
                (symbol, name, sector, industry, country, currency, market_cap, exchange, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol) DO UPDATE SET
                name = EXCLUDED.name,
                sector = EXCLUDED.sector,
                industry = EXCLUDED.industry,
                country = EXCLUDED.country,
                currency = EXCLUDED.currency,
                market_cap = EXCLUDED.market_cap,
                exchange = EXCLUDED.exchange,
                updated_at = EXCLUDED.updated_at
            """, (
                symbol_info['symbol'],
                symbol_info['name'],
                symbol_info['sector'],
                symbol_info['industry'],
                symbol_info['country'],
                symbol_info['currency'],
                symbol_info['market_cap'],
                symbol_info['exchange'],
                symbol_info['updated_at']
            ))

            self.db_manager.commit()
            logger.info(f"💾 Registered {symbol_info['symbol']} to database")
            return True

        except Exception as e:
            logger.error(f"Database registration failed for {symbol_info['symbol']}: {e}")
            return False

    async def expand_symbol_coverage(self, target_count: int = 500) -> Dict:
        """銘柄カバレッジを拡張"""
        logger.info(f"🚀 Starting multi-market symbol expansion (target: {target_count})")

        start_time = time.time()
        all_symbols = self.get_all_target_symbols()

        # Process symbols in batches
        batch_size = 50
        processed = 0

        for i in range(0, min(len(all_symbols), target_count), batch_size):
            batch = all_symbols[i:i+batch_size]
            logger.info(f"📦 Processing batch {i//batch_size + 1}: symbols {i+1}-{min(i+batch_size, target_count)}")

            for symbol in batch:
                if processed >= target_count:
                    break

                try:
                    # Validate symbol
                    if not self.validate_symbol(symbol):
                        self.failed_symbols.add(symbol)
                        logger.warning(f"❌ {symbol} validation failed")
                        continue

                    # Get symbol information
                    symbol_info = self.get_symbol_info(symbol)
                    if not symbol_info:
                        self.failed_symbols.add(symbol)
                        continue

                    # Register to database
                    if await self.register_symbol_to_db(symbol_info):
                        self.successful_symbols.add(symbol)
                        logger.info(f"✅ {symbol} ({symbol_info['name']}) added successfully")
                    else:
                        self.failed_symbols.add(symbol)

                    self.processed_symbols.add(symbol)
                    processed += 1

                    # Rate limiting
                    await asyncio.sleep(0.1)

                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    self.failed_symbols.add(symbol)

            # Progress update
            logger.info(f"📊 Progress: {processed}/{target_count} symbols processed")

        end_time = time.time()
        duration = end_time - start_time

        results = {
            'processed_count': len(self.processed_symbols),
            'successful_count': len(self.successful_symbols),
            'failed_count': len(self.failed_symbols),
            'duration_seconds': duration,
            'successful_symbols': list(self.successful_symbols),
            'failed_symbols': list(self.failed_symbols),
            'categories_processed': list(self.symbol_categories.keys())
        }

        logger.info(f"🎉 Symbol expansion completed!")
        logger.info(f"✅ Successful: {results['successful_count']}")
        logger.info(f"❌ Failed: {results['failed_count']}")
        logger.info(f"⏱️ Duration: {duration:.2f} seconds")

        return results

def main():
    """メイン実行関数"""
    print("🌍 Multi-Market Symbol Expander Starting...")
    print("Target markets: US, Japan, ETF, Forex, Crypto, Commodities")

    expander = MultiMarketSymbolExpander()

    # Run expansion
    target_count = int(input("Enter target symbol count (default 500): ") or "500")

    try:
        results = asyncio.run(expander.expand_symbol_coverage(target_count))

        print("\n" + "="*60)
        print("📊 EXPANSION RESULTS")
        print("="*60)
        print(f"🎯 Target symbols: {target_count}")
        print(f"✅ Successfully added: {results['successful_count']}")
        print(f"❌ Failed: {results['failed_count']}")
        print(f"⏱️ Duration: {results['duration_seconds']:.2f} seconds")

        if results['successful_symbols']:
            print(f"\n🎉 Sample successful symbols:")
            for symbol in results['successful_symbols'][:10]:
                print(f"  - {symbol}")

        if results['failed_symbols']:
            print(f"\n⚠️ Sample failed symbols:")
            for symbol in results['failed_symbols'][:5]:
                print(f"  - {symbol}")

        print(f"\n📈 Categories processed:")
        for category in results['categories_processed']:
            print(f"  - {category}")

    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")

if __name__ == "__main__":
    main()