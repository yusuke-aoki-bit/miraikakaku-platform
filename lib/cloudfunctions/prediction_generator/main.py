"""
Google Cloud Functions - 予想生成サービス
Serverless Prediction Generator
"""

import functions_framework
import psycopg2
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List
import logging

# 環境変数から設定取得
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
def generate_predictions(request):
    """
    HTTPトリガー: 予想生成
    """
    # CORSヘッダー
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # OPTIONSリクエスト対応
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    try:
        # リクエストパラメータ
        request_json = request.get_json(silent=True)
        request_args = request.args

        symbol = None
        if request_json and 'symbol' in request_json:
            symbol = request_json['symbol']
        elif request_args and 'symbol' in request_args:
            symbol = request_args['symbol']

        # 予想生成実行
        if symbol:
            result = generate_prediction_for_symbol(symbol)
        else:
            result = generate_batch_predictions()

        return (json.dumps(result), 200, headers)

    except Exception as e:
        logger.error(f"Prediction generation error: {e}")
        error_response = {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        return (json.dumps(error_response), 500, headers)

def generate_prediction_for_symbol(symbol: str) -> Dict:
    """単一シンボルの予想生成"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 最新価格データ取得
            cursor.execute("""
                SELECT date, close_price, volume
                FROM stock_prices
                WHERE symbol = %s
                AND date >= CURRENT_DATE - INTERVAL '30 days'
                AND close_price > 0
                ORDER BY date DESC
                LIMIT 10
            """, (symbol,))

            price_data = cursor.fetchall()

            if len(price_data) < 3:
                return {
                    'success': False,
                    'symbol': symbol,
                    'error': 'Insufficient price data'
                }

            # 簡易予想計算
            latest_price = float(price_data[0][1])
            prices = [float(row[1]) for row in price_data[:5]]

            # トレンド計算
            if len(prices) >= 3:
                recent_trend = (prices[0] - prices[-1]) / prices[-1]
            else:
                recent_trend = 0

            # 予想価格
            trend_factor = 1.0 + (recent_trend * 0.5)
            predicted_price = latest_price * trend_factor * 1.01

            # 信頼度
            price_volatility = max(prices) / min(prices) if min(prices) > 0 else 1.0
            confidence = max(0.5, min(0.9, 1.0 - (price_volatility - 1.0)))

            # データベース保存
            cursor.execute("""
                INSERT INTO stock_predictions (
                    symbol, prediction_date, prediction_days, current_price,
                    predicted_price, confidence_score, model_version,
                    model_type, prediction_horizon, is_active
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                symbol,
                datetime.now().date(),
                7,
                latest_price,
                predicted_price,
                confidence,
                'CLOUD_FUNCTION_v1.0',
                'SERVERLESS_TREND',
                7,
                True
            ))

            conn.commit()

            return {
                'success': True,
                'symbol': symbol,
                'current_price': latest_price,
                'predicted_price': predicted_price,
                'confidence_score': confidence,
                'change_percent': ((predicted_price - latest_price) / latest_price) * 100,
                'timestamp': datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"Error generating prediction for {symbol}: {e}")
        return {
            'success': False,
            'symbol': symbol,
            'error': str(e)
        }

def generate_batch_predictions(limit: int = 50) -> Dict:
    """バッチ予想生成"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 予想が必要なシンボル取得
            cursor.execute("""
                SELECT DISTINCT sm.symbol
                FROM stock_master sm
                JOIN stock_prices sp ON sm.symbol = sp.symbol
                LEFT JOIN stock_predictions pred ON sm.symbol = pred.symbol
                    AND pred.prediction_date >= CURRENT_DATE - INTERVAL '7 days'
                WHERE sm.is_active = true
                AND sp.date >= CURRENT_DATE - INTERVAL '30 days'
                AND pred.id IS NULL
                ORDER BY sm.symbol
                LIMIT %s
            """, (limit,))

            symbols = [row[0] for row in cursor.fetchall()]

            results = {
                'total': len(symbols),
                'success': 0,
                'failed': 0,
                'predictions': []
            }

            for symbol in symbols:
                prediction = generate_prediction_for_symbol(symbol)
                if prediction['success']:
                    results['success'] += 1
                    results['predictions'].append(prediction)
                else:
                    results['failed'] += 1

            results['timestamp'] = datetime.now().isoformat()
            return results

    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@functions_framework.cloud_event
def scheduled_prediction_generation(cloud_event):
    """
    Cloud Scheduler トリガー: 定期実行用
    """
    logger.info(f"Scheduled prediction generation started at {datetime.now()}")

    result = generate_batch_predictions(limit=100)

    logger.info(f"Generated {result.get('success', 0)} predictions, {result.get('failed', 0)} failed")

    return result