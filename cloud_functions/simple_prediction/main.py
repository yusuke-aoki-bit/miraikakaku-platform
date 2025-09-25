import functions_framework
import psycopg2
import numpy as np
from datetime import datetime, timedelta
import os
import json

@functions_framework.http
def simple_prediction_handler(request):
    """シンプル予測ハンドラー"""

    try:
        # データベース接続
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', '34.173.9.214'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME', 'miraikakaku')
        )
        cursor = conn.cursor()

        # 対象銘柄取得
        cursor.execute("""
            SELECT symbol, COUNT(*) as cnt
            FROM stock_prices
            WHERE date >= CURRENT_DATE - INTERVAL '30 days'
            AND close_price > 0
            GROUP BY symbol
            HAVING COUNT(*) >= 10
            ORDER BY COUNT(*) DESC
            LIMIT 15
        """)

        symbols = cursor.fetchall()
        total_predictions = 0

        for symbol, cnt in symbols:
            try:
                # 価格データ取得
                cursor.execute("""
                    SELECT close_price FROM stock_prices
                    WHERE symbol = %s AND date >= CURRENT_DATE - INTERVAL '30 days'
                    AND close_price > 0
                    ORDER BY date ASC
                """, (symbol,))

                prices = [float(row[0]) for row in cursor.fetchall()]

                if len(prices) >= 10:
                    # シンプルな移動平均予測
                    recent_prices = prices[-5:]
                    avg_price = sum(recent_prices) / len(recent_prices)

                    # トレンド計算
                    if len(prices) >= 10:
                        older_avg = sum(prices[-10:-5]) / 5
                        trend = (avg_price - older_avg) / 5
                    else:
                        trend = 0

                    for days in [1, 7, 30]:
                        predicted_price = avg_price + (trend * days)
                        pred_date = datetime.now() + timedelta(days=days)
                        confidence = max(0.5, 0.8 - (days * 0.01))

                        cursor.execute("""
                            INSERT INTO stock_predictions
                            (symbol, prediction_date, prediction_days, current_price,
                             predicted_price, confidence_score, model_type, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (symbol, prediction_date, prediction_days)
                            DO UPDATE SET predicted_price = EXCLUDED.predicted_price,
                                         confidence_score = EXCLUDED.confidence_score,
                                         model_type = EXCLUDED.model_type,
                                         created_at = EXCLUDED.created_at
                        """, (
                            symbol, pred_date.date(), days, prices[-1],
                            predicted_price, confidence,
                            'CLOUD_FUNCTION_SIMPLE_PREDICTION_V1',
                            datetime.now()
                        ))

                        total_predictions += 1

                    # 進捗コミット
                    if total_predictions % 10 == 0:
                        conn.commit()

            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue

        conn.commit()
        conn.close()

        return {
            'status': 'success',
            'total_predictions': total_predictions,
            'symbols_processed': len(symbols),
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }