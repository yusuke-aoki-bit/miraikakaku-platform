#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
センチメント強化アンサンブル予測生成スクリプト
LSTM、ARIMA、MA、ニュースセンチメントを統合した予測

処理フロー:
1. 従来のアンサンブル予測を生成（LSTM + ARIMA + MA）
2. ニュースセンチメントを取得
3. センチメントに基づいて予測を調整
4. sentiment_adjusted_predictionとして保存
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import io
from datetime import datetime, timedelta
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import warnings
import os
from dotenv import load_dotenv

warnings.filterwarnings('ignore')

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5433)),
    'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
}


def get_sentiment_for_symbol(cur, symbol):
    """
    銘柄のセンチメントサマリーを取得

    Returns:
        dict: {
            'avg_sentiment': float (-1.0 to 1.0),
            'sentiment_trend': str (bullish/bearish/neutral),
            'sentiment_strength': float (0.0 to 1.0),
            'news_count': int
        }
    """
    cur.execute("""
        SELECT
            avg_sentiment,
            sentiment_trend,
            sentiment_strength,
            news_count
        FROM stock_sentiment_summary
        WHERE symbol = %s
          AND date = CURRENT_DATE
    """, (symbol,))

    result = cur.fetchone()
    return dict(result) if result else None


def calculate_sentiment_adjustment(current_price, base_prediction, sentiment_data):
    """
    センチメントに基づいて予測価格を調整

    Args:
        current_price: 現在価格
        base_prediction: 基本予測価格（アンサンブル）
        sentiment_data: センチメントデータ

    Returns:
        tuple: (adjusted_prediction, news_sentiment, news_impact)
    """
    if not sentiment_data or sentiment_data['news_count'] == 0:
        return base_prediction, 0.0, 0.0

    avg_sentiment = float(sentiment_data['avg_sentiment'])
    sentiment_strength = float(sentiment_data['sentiment_strength'])
    news_count = int(sentiment_data['news_count'])

    # ニュース量に基づく影響度（多いほど影響大、上限0.5）
    volume_factor = min(news_count / 20.0, 0.5)

    # センチメント強度と量を組み合わせた影響度
    news_impact = sentiment_strength * volume_factor

    # 予測への影響を計算（最大±10%）
    max_adjustment = 0.10
    price_adjustment_ratio = avg_sentiment * news_impact * max_adjustment

    # 調整後の価格
    adjusted_prediction = base_prediction * (1 + price_adjustment_ratio)

    # 現実的な範囲にクリップ（現在価格から±30%）
    min_price = current_price * 0.7
    max_price = current_price * 1.3
    adjusted_prediction = max(min_price, min(max_price, adjusted_prediction))

    return float(adjusted_prediction), float(avg_sentiment), float(news_impact)


def get_active_symbols(cur):
    """アクティブな銘柄リストを取得"""
    cur.execute("""
        SELECT symbol, company_name
        FROM stock_master
        WHERE is_active = TRUE
        ORDER BY symbol
    """)
    return cur.fetchall()


def get_latest_price(cur, symbol):
    """最新株価を取得"""
    cur.execute("""
        SELECT close_price, date
        FROM stock_prices
        WHERE symbol = %s
        ORDER BY date DESC
        LIMIT 1
    """, (symbol,))
    return cur.fetchone()


def get_historical_prices(cur, symbol, days=60):
    """過去N日分の株価データを取得"""
    cur.execute("""
        SELECT date, close_price
        FROM stock_prices
        WHERE symbol = %s
        ORDER BY date DESC
        LIMIT %s
    """, (symbol, days))
    results = cur.fetchall()
    if not results:
        return []
    return sorted(results, key=lambda x: x['date'])


def get_lstm_prediction(cur, symbol, prediction_date, prediction_days):
    """LSTM予測を取得"""
    cur.execute("""
        SELECT predicted_price
        FROM stock_predictions
        WHERE symbol = %s
          AND prediction_date = %s
          AND prediction_days = %s
          AND model_type IN ('LSTM_Daily', 'LSTM_Improved')
        ORDER BY created_at DESC
        LIMIT 1
    """, (symbol, prediction_date, prediction_days))
    result = cur.fetchone()
    return float(result['predicted_price']) if result else None


def generate_arima_prediction(prices, forecast_days=1):
    """ARIMA予測を生成"""
    try:
        if len(prices) < 30:
            return None
        model = ARIMA(prices, order=(1, 1, 1))
        fitted = model.fit()
        forecast = fitted.forecast(steps=forecast_days)
        return float(forecast[-1])
    except Exception:
        return None


def generate_ma_prediction(prices, window=5):
    """移動平均予測を生成"""
    try:
        if len(prices) < window:
            return None
        ma = np.mean(prices[-window:])
        if len(prices) >= window + 5:
            trend = (prices[-1] - prices[-window]) / window
            return float(ma + trend)
        else:
            return float(ma)
    except Exception:
        return None


def calculate_ensemble_prediction(lstm_pred, arima_pred, ma_pred, current_price):
    """アンサンブル予測を計算"""
    predictions = []
    weights = []

    if lstm_pred and lstm_pred > 0:
        predictions.append(float(lstm_pred))
        weights.append(0.5)

    if arima_pred and arima_pred > 0:
        predictions.append(float(arima_pred))
        weights.append(0.3)

    if ma_pred and ma_pred > 0:
        predictions.append(float(ma_pred))
        weights.append(0.2)

    if not predictions:
        return None, 0.0

    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]
    ensemble = sum(p * w for p, w in zip(predictions, normalized_weights))

    # 信頼度計算
    confidence = len(predictions) / 3.0

    if len(predictions) > 1:
        std = float(np.std(predictions))
        mean = float(np.mean(predictions))
        cv = std / mean if mean > 0 else 1.0
        confidence *= (1.0 - min(cv, 0.5))

    if current_price > 0:
        change_pct = abs(ensemble - current_price) / current_price
        if change_pct > 0.2:
            confidence *= 0.5

    return float(ensemble), float(min(confidence, 1.0))


def save_prediction(cur, symbol, prediction_date, prediction_days,
                   current_price, lstm_pred, arima_pred, ma_pred,
                   ensemble_pred, confidence, news_sentiment, news_impact,
                   sentiment_adjusted_pred):
    """予測をデータベースに保存"""
    try:
        cur.execute("""
            INSERT INTO ensemble_predictions (
                symbol, prediction_date, prediction_days, current_price,
                lstm_prediction, arima_prediction, ma_prediction,
                ensemble_prediction, ensemble_confidence,
                news_sentiment, news_impact, sentiment_adjusted_prediction,
                created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
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
        """, (symbol, prediction_date, prediction_days, current_price,
              lstm_pred, arima_pred, ma_pred, ensemble_pred, confidence,
              news_sentiment, news_impact, sentiment_adjusted_pred))
        return True
    except Exception as e:
        print(f"保存エラー: {e}")
        return False


def process_symbol(cur, symbol, company_name, target_date, prediction_days, sentiment_data):
    """1銘柄の予測処理（センチメント統合）"""
    # 最新株価取得
    latest = get_latest_price(cur, symbol)
    if not latest:
        return None

    current_price = float(latest['close_price'])

    # 過去株価取得
    historical = get_historical_prices(cur, symbol, days=60)
    if len(historical) < 30:
        return None

    prices = [float(h['close_price']) for h in historical]

    # 各予測を取得/生成
    lstm_pred = get_lstm_prediction(cur, symbol, target_date, prediction_days)
    arima_pred = generate_arima_prediction(prices, forecast_days=prediction_days)
    ma_pred = generate_ma_prediction(prices, window=5)

    # アンサンブル予測計算
    ensemble_pred, confidence = calculate_ensemble_prediction(
        lstm_pred, arima_pred, ma_pred, current_price
    )

    if ensemble_pred is None:
        return None

    # センチメント調整
    sentiment_adjusted_pred, news_sentiment, news_impact = calculate_sentiment_adjustment(
        current_price, ensemble_pred, sentiment_data
    )

    # 保存
    success = save_prediction(
        cur, symbol, target_date, prediction_days, current_price,
        lstm_pred, arima_pred, ma_pred, ensemble_pred, confidence,
        news_sentiment, news_impact, sentiment_adjusted_pred
    )

    return {
        'symbol': symbol,
        'company_name': company_name,
        'current_price': current_price,
        'ensemble': ensemble_pred,
        'sentiment_adjusted': sentiment_adjusted_pred,
        'news_sentiment': news_sentiment,
        'news_impact': news_impact,
        'adjustment': sentiment_adjusted_pred - ensemble_pred,
        'adjustment_pct': ((sentiment_adjusted_pred - ensemble_pred) / ensemble_pred * 100) if ensemble_pred > 0 else 0,
        'success': success
    }


def main():
    print("=" * 80)
    print("センチメント強化アンサンブル予測生成")
    print("=" * 80)
    print()

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # アクティブ銘柄取得
        print("-" * 80)
        print("1. アクティブ銘柄とセンチメント取得")
        print("-" * 80)

        symbols = get_active_symbols(cur)
        print(f"対象銘柄数: {len(symbols)}")

        # 各銘柄のセンチメントを事前取得
        sentiment_cache = {}
        for symbol_info in symbols:
            symbol = symbol_info['symbol']
            sentiment_data = get_sentiment_for_symbol(cur, symbol)
            if sentiment_data:
                sentiment_cache[symbol] = sentiment_data

        print(f"センチメントデータあり: {len(sentiment_cache)}銘柄")
        print()

        # 予測対象日
        prediction_configs = []
        tomorrow = datetime.now().date() + timedelta(days=1)

        for days_ahead in [1, 3, 7, 14]:
            target_date = tomorrow + timedelta(days=days_ahead - 1)
            prediction_configs.append((target_date, days_ahead))

        print("-" * 80)
        print("2. 予測生成（センチメント統合）")
        print("-" * 80)

        # 統計
        total_processed = 0
        total_with_sentiment = 0
        total_adjustments = []

        for i, symbol_info in enumerate(symbols, 1):
            symbol = symbol_info['symbol']
            company_name = symbol_info['company_name']
            sentiment_data = sentiment_cache.get(symbol)

            if i % 10 == 0:
                print(f"処理中: {i}/{len(symbols)} ({symbol})")

            for target_date, prediction_days in prediction_configs:
                try:
                    result = process_symbol(
                        cur, symbol, company_name, target_date, prediction_days, sentiment_data
                    )

                    if result and result['success']:
                        total_processed += 1
                        if sentiment_data:
                            total_with_sentiment += 1
                            total_adjustments.append(result['adjustment_pct'])

                except Exception as e:
                    conn.rollback()
                    if i <= 10:
                        print(f"  エラー ({symbol}): {e}")

            if i % 10 == 0:
                try:
                    conn.commit()
                except Exception:
                    conn.rollback()

        conn.commit()

        print()
        print("-" * 80)
        print("3. 処理結果")
        print("-" * 80)
        print(f"予測生成: {total_processed}件")
        print(f"センチメント調整あり: {total_with_sentiment}件")

        if total_adjustments:
            avg_adj = np.mean(total_adjustments)
            max_adj = max(total_adjustments)
            min_adj = min(total_adjustments)
            print(f"平均調整: {avg_adj:+.2f}%")
            print(f"最大調整: {max_adj:+.2f}%")
            print(f"最小調整: {min_adj:+.2f}%")

        # サンプル確認
        print()
        print("-" * 80)
        print("4. センチメント調整例")
        print("-" * 80)

        cur.execute("""
            SELECT
                ep.symbol,
                sm.company_name,
                ep.current_price,
                ep.ensemble_prediction,
                ep.sentiment_adjusted_prediction,
                ep.news_sentiment,
                ep.news_impact,
                ss.sentiment_trend,
                ss.news_count
            FROM ensemble_predictions ep
            LEFT JOIN stock_master sm ON ep.symbol = sm.symbol
            LEFT JOIN stock_sentiment_summary ss ON ep.symbol = ss.symbol
            WHERE ep.prediction_date >= CURRENT_DATE
              AND ep.news_sentiment IS NOT NULL
              AND ep.prediction_days = 1
            ORDER BY ABS(ep.news_sentiment) DESC
            LIMIT 10
        """)

        results = cur.fetchall()
        for r in results:
            adjustment = r['sentiment_adjusted_prediction'] - r['ensemble_prediction']
            adjustment_pct = (adjustment / r['ensemble_prediction'] * 100) if r['ensemble_prediction'] > 0 else 0

            print(f"\n{r['symbol']} - {r['company_name']}")
            print(f"  センチメント: {r['news_sentiment']:+.3f} ({r['sentiment_trend']}, {r['news_count']}件)")
            print(f"  基本予測: {r['ensemble_prediction']:,.0f}円")
            print(f"  調整後: {r['sentiment_adjusted_prediction']:,.0f}円 ({adjustment_pct:+.2f}%)")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"\nエラー: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()

    print()
    print("=" * 80)
    print("完了")
    print("=" * 80)


if __name__ == "__main__":
    main()
