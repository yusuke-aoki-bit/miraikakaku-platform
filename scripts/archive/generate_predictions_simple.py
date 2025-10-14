#!/usr/bin/env python3
"""
センチメント統合予測生成 - Cloud Run用シンプル版
APIエンドポイントから呼び出し可能
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import warnings
import os

warnings.filterwarnings('ignore')

def get_db_config():
    host = os.getenv('POSTGRES_HOST', 'localhost')
    config = {
        'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
    }
    if host.startswith('/cloudsql/'):
        config['host'] = host
    else:
        config['host'] = host
        config['port'] = int(os.getenv('POSTGRES_PORT', 5433))
    return config

def generate_for_symbols(symbols, conn):
    """指定された銘柄の予測を生成"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    results = []
    tomorrow = datetime.now().date() + timedelta(days=1)

    for symbol_info in symbols:
        symbol = symbol_info['symbol']

        try:
            # センチメントデータ取得
            cur.execute("""
                SELECT avg_sentiment, sentiment_strength, news_count
                FROM stock_sentiment_summary
                WHERE symbol = %s AND date = CURRENT_DATE
            """, (symbol,))
            sentiment_data = cur.fetchone()

            # 最新株価取得
            cur.execute("""
                SELECT close_price FROM stock_prices
                WHERE symbol = %s ORDER BY date DESC LIMIT 1
            """, (symbol,))
            latest = cur.fetchone()

            if not latest:
                continue

            current_price = float(latest['close_price'])

            # 過去株価取得
            cur.execute("""
                SELECT close_price FROM stock_prices
                WHERE symbol = %s ORDER BY date DESC LIMIT 60
            """, (symbol,))
            historical = cur.fetchall()

            if len(historical) < 30:
                continue

            prices = [float(h['close_price']) for h in reversed(historical)]

            # LSTM予測取得
            cur.execute("""
                SELECT predicted_price FROM stock_predictions
                WHERE symbol = %s AND prediction_date = %s AND prediction_days = 1
                AND model_type IN ('LSTM_Daily', 'LSTM_Improved')
                ORDER BY created_at DESC LIMIT 1
            """, (symbol, tomorrow))
            lstm_result = cur.fetchone()
            lstm_pred = float(lstm_result['predicted_price']) if lstm_result else None

            # ARIMA予測生成
            try:
                model = ARIMA(prices, order=(1, 1, 1))
                fitted = model.fit()
                forecast = fitted.forecast(steps=1)
                arima_pred = float(forecast[-1])
            except:
                arima_pred = None

            # MA予測生成
            try:
                ma = np.mean(prices[-5:])
                trend = (prices[-1] - prices[-5]) / 5
                ma_pred = float(ma + trend)
            except:
                ma_pred = None

            # アンサンブル計算
            preds = []
            weights = []
            if lstm_pred and lstm_pred > 0:
                preds.append(lstm_pred)
                weights.append(0.5)
            if arima_pred and arima_pred > 0:
                preds.append(arima_pred)
                weights.append(0.3)
            if ma_pred and ma_pred > 0:
                preds.append(ma_pred)
                weights.append(0.2)

            if not preds:
                continue

            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            ensemble_pred = sum(p * w for p, w in zip(preds, normalized_weights))
            confidence = len(preds) / 3.0

            # センチメント調整
            if sentiment_data and sentiment_data['news_count'] > 0:
                avg_sentiment = float(sentiment_data['avg_sentiment'])
                sentiment_strength = float(sentiment_data['sentiment_strength'])
                news_count = int(sentiment_data['news_count'])

                volume_factor = min(news_count / 20.0, 0.5)
                news_impact = sentiment_strength * volume_factor
                max_adjustment = 0.10
                price_adjustment_ratio = avg_sentiment * news_impact * max_adjustment

                sentiment_adjusted_pred = ensemble_pred * (1 + price_adjustment_ratio)

                min_price = current_price * 0.7
                max_price = current_price * 1.3
                sentiment_adjusted_pred = max(min_price, min(max_price, sentiment_adjusted_pred))

                news_sentiment = avg_sentiment
            else:
                sentiment_adjusted_pred = ensemble_pred
                news_sentiment = 0.0
                news_impact = 0.0

            # 保存
            cur.execute("""
                INSERT INTO ensemble_predictions (
                    symbol, prediction_date, prediction_days, current_price,
                    lstm_prediction, arima_prediction, ma_prediction,
                    ensemble_prediction, ensemble_confidence,
                    news_sentiment, news_impact, sentiment_adjusted_prediction,
                    created_at
                ) VALUES (%s, %s, 1, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (symbol, prediction_date, prediction_days)
                DO UPDATE SET
                    current_price = EXCLUDED.current_price,
                    lstm_prediction = EXCLUDED.lstm_prediction,
                    arima_prediction = EXCLUDED.arima_prediction,
                    ma_prediction = EXCLUDED.ma_prediction,
                    ensemble_prediction = EXCLUDED.ensemble_prediction,
                    ensemble_confidence = EXCLUDED.ensemble_confidence,
                    news_sentiment = EXCLUDED.news_sentiment,
                    news_impact = EXCLUDED.news_impact,
                    sentiment_adjusted_prediction = EXCLUDED.sentiment_adjusted_prediction,
                    created_at = NOW()
            """, (symbol, tomorrow, current_price, lstm_pred, arima_pred, ma_pred,
                  ensemble_pred, confidence, news_sentiment, news_impact, sentiment_adjusted_pred))

            conn.commit()

            results.append({
                "symbol": symbol,
                "company_name": symbol_info.get('company_name', symbol),
                "current_price": float(current_price),
                "ensemble_prediction": float(ensemble_pred),
                "sentiment_adjusted_prediction": float(sentiment_adjusted_pred),
                "news_sentiment": float(news_sentiment),
                "news_impact": float(news_impact),
                "adjustment_pct": float(((sentiment_adjusted_pred - ensemble_pred) / ensemble_pred * 100) if ensemble_pred > 0 else 0)
            })

        except Exception as e:
            results.append({
                "symbol": symbol,
                "company_name": symbol_info.get('company_name', symbol),
                "error": str(e)
            })

    cur.close()
    return results

if __name__ == "__main__":
    # テスト実行
    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT symbol, company_name FROM stock_master
        WHERE is_active = TRUE
          AND symbol NOT LIKE '%.KS'
          AND symbol NOT LIKE '%.HK'
          AND (symbol LIKE '%.T' OR (symbol NOT LIKE '%.%' AND LENGTH(symbol) <= 5))
        ORDER BY
            CASE
                WHEN symbol IN ('AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA') THEN 1
                WHEN symbol LIKE '%.T' THEN 2
                ELSE 3
            END,
            symbol
        LIMIT 5
    """)

    symbols = cur.fetchall()
    cur.close()

    results = generate_for_symbols(symbols, conn)
    conn.close()

    for r in results:
        if 'error' in r:
            print(f"{r['symbol']}: ERROR - {r['error']}")
        else:
            print(f"{r['symbol']}: {r['sentiment_adjusted_prediction']:.2f} (調整: {r['adjustment_pct']:+.2f}%)")
