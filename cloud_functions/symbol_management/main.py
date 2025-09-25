import functions_framework
import psycopg2
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def symbol_management_handler(request):
    """銘柄管理ハンドラー"""

    try:
        # データベース接続
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', '34.173.9.214'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'os.getenv('DB_PASSWORD', '')'),
            database=os.environ.get('DB_NAME', 'miraikakaku')
        )
        cursor = conn.cursor()
        logger.info("✅ Database connected")

        # 拡張銘柄リスト
        symbols_to_add = [
            # 主要米国株
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'BRK-B',
            'UNH', 'JNJ', 'V', 'WMT', 'XOM', 'PG', 'JPM', 'HD', 'CVX', 'MA',
            'PFE', 'ABBV', 'BAC', 'KO', 'AVGO', 'PEP', 'TMO', 'COST', 'DIS',

            # 暗号通貨
            'BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'AVAX-USD', 'DOT-USD',
            'MATIC-USD', 'LINK-USD', 'UNI-USD', 'ATOM-USD',

            # ETF
            'SPY', 'QQQ', 'VTI', 'VOO', 'IWM', 'VEA', 'VWO', 'AGG', 'TLT',

            # 日本株
            '7203.T', '6758.T', '9984.T', '8306.T', '6861.T', '4519.T', '6502.T'
        ]

        added_symbols = 0
        added_prices = 0

        for symbol in symbols_to_add:
            try:
                logger.info(f"📈 Processing {symbol}")

                # Yahoo Finance から情報取得
                ticker = yf.Ticker(symbol)
                info = ticker.info

                company_name = info.get('longName', info.get('shortName', symbol))
                exchange = info.get('exchange', 'UNKNOWN')

                # 銘柄追加
                cursor.execute("""
                    INSERT INTO stock_master (symbol, name, company_name, exchange, is_active)
                    VALUES (%s, %s, %s, %s, true)
                    ON CONFLICT (symbol) DO UPDATE SET
                        name = EXCLUDED.name,
                        company_name = EXCLUDED.company_name,
                        exchange = EXCLUDED.exchange,
                        is_active = true,
                        updated_at = NOW()
                """, (symbol, company_name, company_name, exchange))

                added_symbols += 1
                logger.info(f"  ✅ Added: {symbol} - {company_name}")

                # 価格データ取得（90日分）
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)

                hist = ticker.history(start=start_date, end=end_date)

                if not hist.empty:
                    price_count = 0
                    for date, row in hist.iterrows():
                        try:
                            cursor.execute("""
                                INSERT INTO stock_prices
                                (symbol, date, open_price, high_price, low_price, close_price, volume, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                                ON CONFLICT (symbol, date) DO UPDATE SET
                                    open_price = EXCLUDED.open_price,
                                    high_price = EXCLUDED.high_price,
                                    low_price = EXCLUDED.low_price,
                                    close_price = EXCLUDED.close_price,
                                    volume = EXCLUDED.volume,
                                    updated_at = NOW()
                            """, (
                                symbol, date.date(),
                                float(row['Open']) if not pd.isna(row['Open']) else None,
                                float(row['High']) if not pd.isna(row['High']) else None,
                                float(row['Low']) if not pd.isna(row['Low']) else None,
                                float(row['Close']) if not pd.isna(row['Close']) else None,
                                int(row['Volume']) if not pd.isna(row['Volume']) else 0
                            ))
                            price_count += 1
                        except Exception:
                            continue

                    added_prices += price_count
                    logger.info(f"  💰 {price_count} price records added")

                # 定期コミット
                if added_symbols % 10 == 0:
                    conn.commit()

            except Exception as e:
                logger.warning(f"⚠️ Error processing {symbol}: {e}")
                continue

        conn.commit()
        conn.close()

        result = {
            'status': 'success',
            'added_symbols': added_symbols,
            'added_prices': added_prices,
            'total_attempted': len(symbols_to_add),
            'timestamp': datetime.now().isoformat()
        }

        logger.info("=" * 40)
        logger.info("🎉 Symbol Management Complete")
        logger.info(f"✅ Added symbols: {added_symbols}")
        logger.info(f"💰 Added prices: {added_prices}")
        logger.info("=" * 40)

        return result

    except Exception as e:
        logger.error(f"❌ Symbol management failed: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }
