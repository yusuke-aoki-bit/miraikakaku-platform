#!/usr/bin/env python3
"""
予測精度チェッカー
過去予測と未来予測の分析
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os

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

def check_past_accuracy(conn, days_back=30, limit=100):
    """過去予測の精度チェック"""
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        WITH past_predictions AS (
            SELECT
                ep.symbol,
                ep.prediction_date,
                ep.current_price as predicted_from_price,
                ep.ensemble_prediction,
                ep.sentiment_adjusted_prediction,
                ep.news_sentiment,
                ep.ensemble_confidence,
                sp.close_price as actual_price
            FROM ensemble_predictions ep
            JOIN stock_prices sp ON
                ep.symbol = sp.symbol
                AND sp.date = ep.prediction_date
            WHERE ep.prediction_date < CURRENT_DATE
              AND ep.prediction_date >= CURRENT_DATE - INTERVAL '%s days'
              AND ep.prediction_days = 1
              AND ep.ensemble_prediction IS NOT NULL
            ORDER BY ep.prediction_date DESC
            LIMIT %s
        )
        SELECT
            symbol,
            prediction_date,
            predicted_from_price,
            ensemble_prediction,
            sentiment_adjusted_prediction,
            actual_price,
            news_sentiment,
            ensemble_confidence,
            ABS(ensemble_prediction - actual_price) as ensemble_error,
            ABS((ensemble_prediction - actual_price) / actual_price * 100) as ensemble_error_pct,
            ABS(sentiment_adjusted_prediction - actual_price) as sentiment_error,
            ABS((sentiment_adjusted_prediction - actual_price) / actual_price * 100) as sentiment_error_pct,
            CASE
                WHEN (ensemble_prediction > predicted_from_price AND actual_price > predicted_from_price)
                     OR (ensemble_prediction < predicted_from_price AND actual_price < predicted_from_price)
                THEN TRUE
                ELSE FALSE
            END as ensemble_direction_correct,
            CASE
                WHEN (sentiment_adjusted_prediction > predicted_from_price AND actual_price > predicted_from_price)
                     OR (sentiment_adjusted_prediction < predicted_from_price AND actual_price < predicted_from_price)
                THEN TRUE
                ELSE FALSE
            END as sentiment_direction_correct
        FROM past_predictions
        ORDER BY prediction_date DESC
    """, (days_back, limit))

    predictions = cur.fetchall()
    cur.close()

    if not predictions:
        return {
            "total_predictions": 0,
            "message": "No past predictions found"
        }

    ensemble_errors = [float(p['ensemble_error_pct']) for p in predictions]
    sentiment_errors = [float(p['sentiment_error_pct']) for p in predictions if p['sentiment_adjusted_prediction']]

    ensemble_directions = [p['ensemble_direction_correct'] for p in predictions]
    sentiment_directions = [p['sentiment_direction_correct'] for p in predictions]

    return {
        "total_predictions": len(predictions),
        "ensemble_avg_error_pct": sum(ensemble_errors) / len(ensemble_errors) if ensemble_errors else 0,
        "ensemble_direction_accuracy": sum(ensemble_directions) / len(ensemble_directions) * 100 if ensemble_directions else 0,
        "sentiment_avg_error_pct": sum(sentiment_errors) / len(sentiment_errors) if sentiment_errors else 0,
        "sentiment_direction_accuracy": sum(sentiment_directions) / len(sentiment_directions) * 100 if sentiment_directions else 0,
        "predictions": [dict(p) for p in predictions]
    }

def check_future_predictions(conn, limit=100):
    """未来予測の状態チェック"""
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            ep.symbol,
            sm.company_name,
            ep.prediction_date,
            ep.prediction_days,
            ep.current_price,
            ep.ensemble_prediction,
            ep.sentiment_adjusted_prediction,
            ep.news_sentiment,
            ep.news_impact,
            ep.ensemble_confidence,
            (ep.ensemble_prediction - ep.current_price) / ep.current_price * 100 as ensemble_change_pct,
            (ep.sentiment_adjusted_prediction - ep.current_price) / ep.current_price * 100 as sentiment_change_pct,
            (ep.sentiment_adjusted_prediction - ep.ensemble_prediction) / ep.ensemble_prediction * 100 as sentiment_adjustment_pct
        FROM ensemble_predictions ep
        JOIN stock_master sm ON ep.symbol = sm.symbol
        WHERE ep.prediction_date >= CURRENT_DATE
          AND ep.prediction_days = 1
          AND ep.ensemble_prediction IS NOT NULL
        ORDER BY ep.prediction_date ASC, ep.symbol
        LIMIT %s
    """, (limit,))

    predictions = cur.fetchall()
    cur.close()

    if not predictions:
        return {
            "total_predictions": 0,
            "message": "No future predictions found"
        }

    with_sentiment = [p for p in predictions if p['news_sentiment'] is not None and p['news_sentiment'] != 0]

    return {
        "total_predictions": len(predictions),
        "with_sentiment_data": len(with_sentiment),
        "avg_confidence": sum(float(p['ensemble_confidence']) for p in predictions) / len(predictions),
        "avg_sentiment_adjustment_pct": sum(abs(float(p['sentiment_adjustment_pct'])) for p in with_sentiment) / len(with_sentiment) if with_sentiment else 0,
        "bullish_sentiment_count": len([p for p in with_sentiment if float(p['news_sentiment']) > 0.1]),
        "bearish_sentiment_count": len([p for p in with_sentiment if float(p['news_sentiment']) < -0.1]),
        "neutral_sentiment_count": len([p for p in with_sentiment if abs(float(p['news_sentiment'])) <= 0.1]),
        "predictions": [dict(p) for p in predictions]
    }
