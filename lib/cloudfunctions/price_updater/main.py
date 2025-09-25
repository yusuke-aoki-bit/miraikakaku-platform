"""
Google Cloud Functions - 価格データ更新サービス
Serverless Price Data Updater
"""

import functions_framework
import psycopg2
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import logging

# 環境変数
DB_HOST = os.environ.get('DB_HOST', '34.173.9.214')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'os.getenv('DB_PASSWORD', '')')
DB_NAME = os.environ.get('DB_NAME', 'miraikakaku')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """データベース接続"""
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=5432
    )

@functions_framework.http
def update_prices(request):
    """
    HTTPトリガー: 価格データ更新
    """
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    if request.method == 'OPTIONS':
        return ('', 204, headers)

    try:
        request_json = request.get_json(silent=True)
        request_args = request.args

        symbol = None
        if request_json and 'symbol' in request_json:
            symbol = request_json['symbol']
        elif request_args and 'symbol' in request_args:
            symbol = request_args['symbol']

        # 価格更新実行
        if symbol:
            result = update_symbol_price(symbol)
        else:
            result = update_batch_prices()

        return (json.dumps(result), 200, headers)

    except Exception as e:
        logger.error(f"Price update error: {e}")
        error_response = {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        return (json.dumps(error_response), 500, headers)

def update_symbol_price(symbol: str) -> dict:
    """単一シンボルの価格更新"""
    try:
        # yfinanceでデータ取得
        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        hist = ticker.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            auto_adjust=True
        )

        if hist.empty:
            return {
                'success': False,
                'symbol': symbol,
                'error': 'No price data available'
            }

        # データ整形
        hist.reset_index(inplace=True)
        records_added = 0

        with get_db_connection() as conn:
            cursor = conn.cursor()

            for _, row in hist.iterrows():
                try:
                    # 既存チェック
                    cursor.execute("""
                        SELECT 1 FROM stock_prices
                        WHERE symbol = %s AND date = %s
                    """, (symbol, row['Date']))

                    if cursor.fetchone() is None:
                        # 新規挿入
                        cursor.execute("""
                            INSERT INTO stock_prices (
                                symbol, date, open_price, high_price,
                                low_price, close_price, volume, created_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            symbol,
                            row['Date'],
                            float(row['Open']),
                            float(row['High']),
                            float(row['Low']),
                            float(row['Close']),
                            int(row['Volume']),
                            datetime.now()
                        ))
                        records_added += 1

                except Exception as e:
                    logger.debug(f"Skip record: {e}")
                    continue

            conn.commit()

        return {
            'success': True,
            'symbol': symbol,
            'records_added': records_added,
            'latest_price': float(hist['Close'].iloc[-1]),
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error updating {symbol}: {e}")
        return {
            'success': False,
            'symbol': symbol,
            'error': str(e)
        }

def update_batch_prices(limit: int = 20) -> dict:
    """バッチ価格更新"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 更新が必要なシンボル取得
            cursor.execute("""
                SELECT DISTINCT sm.symbol
                FROM stock_master sm
                LEFT JOIN stock_prices sp ON sm.symbol = sp.symbol
                    AND sp.date >= CURRENT_DATE - INTERVAL '1 day'
                WHERE sm.is_active = true
                AND sp.symbol IS NULL
                AND sm.symbol ~ '^[A-Z]{1,5}$'
                ORDER BY sm.symbol
                LIMIT %s
            """, (limit,))

            symbols = [row[0] for row in cursor.fetchall()]

        results = {
            'total': len(symbols),
            'success': 0,
            'failed': 0,
            'updates': []
        }

        for symbol in symbols:
            update = update_symbol_price(symbol)
            if update['success']:
                results['success'] += 1
                results['updates'].append({
                    'symbol': symbol,
                    'records': update['records_added']
                })
            else:
                results['failed'] += 1

        results['timestamp'] = datetime.now().isoformat()
        return results

    except Exception as e:
        logger.error(f"Batch update error: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@functions_framework.cloud_event
def scheduled_price_update(cloud_event):
    """
    Cloud Scheduler トリガー: 定期価格更新
    """
    logger.info(f"Scheduled price update started at {datetime.now()}")

    result = update_batch_prices(limit=50)

    logger.info(f"Updated {result.get('success', 0)} symbols, {result.get('failed', 0)} failed")

    return result