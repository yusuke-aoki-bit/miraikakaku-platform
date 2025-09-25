#!/usr/bin/env python3
"""
Add New Symbols to Stock Master
新銘柄追加システム
"""

import psycopg2
import yfinance as yf
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SymbolAdder:
    """銘柄追加システム"""

    def __init__(self):
        self.conn = psycopg2.connect(
            host='34.173.9.214',
            user='postgres',
            password='os.getenv('DB_PASSWORD', '')',
            database='miraikakaku'
        )
        self.cursor = self.conn.cursor()

    def add_symbols(self, symbols: list, fetch_price_data=True):
        """新銘柄を追加"""

        logger.info(f"🎯 Adding {len(symbols)} new symbols...")

        added_symbols = 0
        added_prices = 0

        for symbol in symbols:
            try:
                # Yahoo Finance から情報取得
                ticker = yf.Ticker(symbol)
                info = ticker.info

                company_name = info.get('longName', info.get('shortName', symbol))
                exchange = info.get('exchange', 'UNKNOWN')
                sector = info.get('sector', 'Unknown')

                # stock_master に追加
                self.cursor.execute("""
                    INSERT INTO stock_master (symbol, name, company_name, exchange, is_active)
                    VALUES (%s, %s, %s, %s, true)
                    ON CONFLICT (symbol) DO UPDATE SET
                        name = EXCLUDED.name,
                        company_name = EXCLUDED.company_name,
                        exchange = EXCLUDED.exchange,
                        is_active = true
                """, (symbol, company_name, company_name, exchange))

                added_symbols += 1
                logger.info(f"  ✅ {symbol}: {company_name} ({exchange})")

                # 価格データも取得する場合
                if fetch_price_data:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=180)  # 180日分

                    hist = ticker.history(start=start_date, end=end_date)

                    if not hist.empty:
                        price_count = 0
                        for date, row in hist.iterrows():
                            try:
                                self.cursor.execute("""
                                    INSERT INTO stock_prices
                                    (symbol, date, open_price, high_price, low_price, close_price, volume)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (symbol, date) DO UPDATE SET
                                        open_price = EXCLUDED.open_price,
                                        high_price = EXCLUDED.high_price,
                                        low_price = EXCLUDED.low_price,
                                        close_price = EXCLUDED.close_price,
                                        volume = EXCLUDED.volume
                                """, (
                                    symbol,
                                    date.date(),
                                    float(row['Open']) if not pd.isna(row['Open']) else None,
                                    float(row['High']) if not pd.isna(row['High']) else None,
                                    float(row['Low']) if not pd.isna(row['Low']) else None,
                                    float(row['Close']) if not pd.isna(row['Close']) else None,
                                    int(row['Volume']) if not pd.isna(row['Volume']) else 0
                                ))
                                price_count += 1
                            except Exception as price_error:
                                continue

                        added_prices += price_count
                        logger.info(f"    💰 {price_count}日分の価格データ追加")

                # 進捗コミット
                if added_symbols % 10 == 0:
                    self.conn.commit()

            except Exception as e:
                logger.warning(f"  ⚠️ {symbol}: {e}")
                continue

        self.conn.commit()

        logger.info("="*60)
        logger.info("🎉 銘柄追加完了")
        logger.info("="*60)
        logger.info(f"✅ 追加銘柄数: {added_symbols}")
        logger.info(f"💰 追加価格データ: {added_prices}件")
        logger.info("="*60)

        return added_symbols, added_prices

    def add_popular_stocks(self):
        """人気株式を追加"""
        popular_symbols = [
            # 米国テック株
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA',
            'NFLX', 'CRM', 'ADBE', 'INTC', 'AMD', 'ORCL', 'CSCO',

            # 米国大型株
            'BRK-B', 'UNH', 'JNJ', 'V', 'PG', 'JPM', 'XOM', 'HD',
            'CVX', 'LLY', 'PFE', 'ABBV', 'BAC', 'KO', 'AVGO',

            # 日本株
            '7203.T', '6758.T', '9984.T', '6861.T', '8306.T', '9433.T',
            '4063.T', '6501.T', '7267.T', '4502.T', '8031.T', '6954.T',

            # ETF
            'SPY', 'QQQ', 'DIA', 'VTI', 'VOO', 'IWM', 'EFA', 'EEM',
            'VEA', 'IEFA', 'VWO', 'IEMG'
        ]

        return self.add_symbols(popular_symbols, fetch_price_data=True)

    def add_crypto_pairs(self):
        """暗号通貨ペアを追加"""
        crypto_symbols = [
            # メジャー暗号通貨
            'BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD',
            'SOL-USD', 'DOGE-USD', 'AVAX-USD', 'TRX-USD', 'DOT-USD',
            'MATIC-USD', 'LTC-USD', 'SHIB-USD', 'BCH-USD', 'ATOM-USD',

            # 新興暗号通貨
            'LINK-USD', 'UNI-USD', 'ICP-USD', 'FIL-USD', 'VET-USD',
            'ALGO-USD', 'HBAR-USD', 'XLM-USD', 'MANA-USD', 'SAND-USD'
        ]

        return self.add_symbols(crypto_symbols, fetch_price_data=True)

    def check_current_symbols(self):
        """現在の銘柄数確認"""
        self.cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN is_active = true THEN 1 END) as active
            FROM stock_master
        """)

        total, active = self.cursor.fetchone()

        self.cursor.execute("""
            SELECT COUNT(DISTINCT symbol) as symbols_with_prices
            FROM stock_prices
            WHERE date >= CURRENT_DATE - INTERVAL '7 days'
        """)

        with_prices = self.cursor.fetchone()[0]

        logger.info("📊 現在の銘柄状況:")
        logger.info(f"  🎯 総銘柄数: {total}")
        logger.info(f"  ✅ アクティブ: {active}")
        logger.info(f"  💰 最新価格あり: {with_prices}")

        return total, active, with_prices

def main():
    """メイン実行"""
    adder = SymbolAdder()

    # 現在の状況確認
    adder.check_current_symbols()

    logger.info("\n🚀 新銘柄追加開始...")

    # 人気株式追加
    stocks_added, stocks_prices = adder.add_popular_stocks()

    # 暗号通貨追加
    crypto_added, crypto_prices = adder.add_crypto_pairs()

    # 最終結果
    total_added = stocks_added + crypto_added
    total_prices = stocks_prices + crypto_prices

    logger.info(f"\n🎉 合計追加結果:")
    logger.info(f"  📈 追加銘柄: {total_added}")
    logger.info(f"  💰 追加価格データ: {total_prices}件")

    # 追加後の状況確認
    adder.check_current_symbols()

if __name__ == "__main__":
    import pandas as pd  # yfinanceに必要
    main()