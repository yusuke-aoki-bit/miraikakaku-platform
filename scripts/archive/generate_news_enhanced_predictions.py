#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ニュースセンチメントを統合した予測生成スクリプト
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import numpy as np


# パスを追加
sys.path.insert(0, 'src/ml-models')
from news_feature_extractor import NewsFeatureExtractor


def get_db_connection():
    """データベース接続を取得"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/cloudsql/pricewise-huqkr:us-central1:miraikakaku-postgres'),
        database=os.getenv('POSTGRES_DB', 'miraikakaku'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', '')
    )


def generate_news_enhanced_prediction(symbol: str) -> dict:
    """
    ニュースセンチメントを統合した予測を生成

    Args:
        symbol: 銘柄コード

    Returns:
        dict: 予測結果
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 現在価格を取得
        cur.execute("""
            SELECT close_price, date
            FROM stock_prices
            WHERE symbol = %s
            ORDER BY date DESC
            LIMIT 1
        """, (symbol,))

        price_data = cur.fetchone()
        if not price_data:
            return {
                'status': 'error',
                'message': f'No price data for {symbol}'
            }

        current_price = float(price_data['close_price'])
        current_date = price_data['date']

        # 過去30日の価格データ取得
        cur.execute("""
            SELECT close_price, date
            FROM stock_prices
            WHERE symbol = %s
              AND date <= %s
            ORDER BY date DESC
            LIMIT 30
        """, (symbol, current_date))

        historical_prices = cur.fetchall()

        if len(historical_prices) < 30:
            return {
                'status': 'error',
                'message': f'Insufficient price history for {symbol}'
            }

        # ニュース特徴量を抽出
        db_config = {
            'host': os.getenv('POSTGRES_HOST', '/cloudsql/pricewise-huqkr:us-central1:miraikakaku-postgres'),
            'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', '')
        }

        extractor = NewsFeatureExtractor(db_config)
        news_features = extractor.get_latest_features(symbol)

        # 価格トレンド分析
        prices = [float(p['close_price']) for p in reversed(historical_prices)]
        ma_7 = np.mean(prices[-7:])
        ma_14 = np.mean(prices[-14:])
        ma_30 = np.mean(prices)

        # トレンド計算
        price_trend = (ma_7 - ma_30) / ma_30 if ma_30 > 0 else 0

        # ニュースセンチメントによる調整
        sentiment_adjustment = news_features['avg_sentiment'] * 0.02  # 最大±2%
        trend_adjustment = news_features['sentiment_trend'] * 0.01   # 最大±1%

        # 最終的な変化率予測
        predicted_change = price_trend + sentiment_adjustment + trend_adjustment

        # 変化率を制限（±15%）
        predicted_change = max(-0.15, min(0.15, predicted_change))

        # 予測価格計算
        predicted_price = current_price * (1 + predicted_change)

        # 信頼度計算
        # ニュース件数が多いほど信頼度が高い
        news_confidence = min(news_features['news_count'] / 10.0, 1.0) * 0.2

        # センチメントの一貫性（標準偏差が小さいほど高い）
        sentiment_consistency = max(0, 1.0 - news_features['sentiment_std']) * 0.2

        # 基本信頼度 + ニュースボーナス
        base_confidence = 0.60
        confidence = base_confidence + news_confidence + sentiment_consistency

        # 予測をデータベースに保存
        prediction_date = current_date + timedelta(days=7)

        cur.execute("""
            INSERT INTO ensemble_predictions (
                symbol,
                prediction_date,
                prediction_days,
                current_price,
                lstm_prediction,
                ensemble_prediction,
                ensemble_confidence,
                news_sentiment_score,
                news_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, prediction_date, prediction_days)
            DO UPDATE SET
                lstm_prediction = EXCLUDED.lstm_prediction,
                ensemble_prediction = EXCLUDED.ensemble_prediction,
                ensemble_confidence = EXCLUDED.ensemble_confidence,
                news_sentiment_score = EXCLUDED.news_sentiment_score,
                news_count = EXCLUDED.news_count
        """, (
            symbol,
            prediction_date,
            7,
            current_price,
            predicted_price,
            predicted_price,
            confidence,
            news_features['avg_sentiment'],
            news_features['news_count']
        ))

        conn.commit()

        return {
            'status': 'success',
            'symbol': symbol,
            'current_price': current_price,
            'predicted_price': predicted_price,
            'prediction_change_pct': predicted_change * 100,
            'confidence': confidence,
            'news_sentiment': news_features['avg_sentiment'],
            'news_count': news_features['news_count'],
            'sentiment_trend': news_features['sentiment_trend'],
            'bullish_ratio': news_features['bullish_ratio'],
            'bearish_ratio': news_features['bearish_ratio'],
            'prediction_date': prediction_date.isoformat()
        }

    except Exception as e:
        conn.rollback()
        return {
            'status': 'error',
            'symbol': symbol,
            'message': str(e)
        }
    finally:
        cur.close()
        conn.close()


def generate_batch_predictions(limit: int = 100) -> dict:
    """
    複数銘柄の予測を一括生成

    Args:
        limit: 処理する銘柄数

    Returns:
        dict: 実行結果
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # ニュースがある銘柄を優先的に選択
    cur.execute("""
        SELECT DISTINCT sm.symbol, sm.company_name
        FROM stock_master sm
        WHERE sm.is_active = TRUE
          AND EXISTS (
              SELECT 1 FROM stock_prices sp
              WHERE sp.symbol = sm.symbol
                AND sp.date >= CURRENT_DATE - INTERVAL '30 days'
          )
          AND EXISTS (
              SELECT 1 FROM stock_news sn
              WHERE sn.symbol = sm.symbol
                AND sn.published_at >= CURRENT_DATE - INTERVAL '7 days'
          )
        ORDER BY sm.symbol
        LIMIT %s
    """, (limit,))

    symbols = cur.fetchall()
    cur.close()
    conn.close()

    results = {
        'total_symbols': len(symbols),
        'successful': 0,
        'failed': 0,
        'predictions': []
    }

    for i, symbol_info in enumerate(symbols, 1):
        symbol = symbol_info['symbol']
        print(f"[{i}/{len(symbols)}] Generating prediction for {symbol}...")

        result = generate_news_enhanced_prediction(symbol)
        results['predictions'].append(result)

        if result['status'] == 'success':
            results['successful'] += 1
        else:
            results['failed'] += 1

    return results


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate news-enhanced predictions')
    parser.add_argument('--symbol', type=str, help='Single symbol to predict')
    parser.add_argument('--limit', type=int, default=100, help='Number of symbols for batch prediction')
    parser.add_argument('--batch', action='store_true', help='Batch mode')

    args = parser.parse_args()

    if args.symbol:
        # 単一銘柄
        result = generate_news_enhanced_prediction(args.symbol)
        print(f"\n=== Prediction for {args.symbol} ===")
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        # バッチモード
        results = generate_batch_predictions(args.limit)
        print(f"\n=== Batch Prediction Results ===")
        print(f"Total: {results['total_symbols']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
