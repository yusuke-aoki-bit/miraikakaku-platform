#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アンサンブル予測統合スクリプト
LSTM、ARIMA、移動平均の予測を統合して ensemble_predictions テーブルに保存

処理フロー:
1. 最新の株価データを取得
2. LSTM予測を取得（stock_predictionsから）
3. ARIMA予測を生成
4. 移動平均予測を生成
5. 信頼度加重平均でアンサンブル予測を作成
6. ensemble_predictionsテーブルに保存
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
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Windows encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'miraikakaku',
    'user': 'postgres',
    'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
}

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.DatabaseError)),
    reraise=True
)
def get_active_symbols(cur):
    """アクティブな銘柄リストを取得"""
    logger.debug("Fetching active symbols from database")
    cur.execute("""
        SELECT symbol, company_name
        FROM stock_master
        WHERE is_active = TRUE
        ORDER BY symbol
    """)
    results = cur.fetchall()
    logger.info(f"Retrieved {len(results)} active symbols")
    return results

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
    """LSTM予測を取得（stock_predictionsから）"""
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

        # ARIMA(1,1,1)モデル
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

        # 単純移動平均
        ma = np.mean(prices[-window:])

        # トレンド計算（直近5日の傾向）
        if len(prices) >= window + 5:
            trend = (prices[-1] - prices[-window]) / window
            return float(ma + trend)
        else:
            return float(ma)
    except Exception:
        return None

def calculate_ensemble_prediction(lstm_pred, arima_pred, ma_pred, current_price):
    """信頼度加重平均でアンサンブル予測を計算"""
    predictions = []
    weights = []

    # LSTM予測（重み: 0.5）
    if lstm_pred and lstm_pred > 0:
        predictions.append(float(lstm_pred))
        weights.append(0.5)

    # ARIMA予測（重み: 0.3）
    if arima_pred and arima_pred > 0:
        predictions.append(float(arima_pred))
        weights.append(0.3)

    # 移動平均予測（重み: 0.2）
    if ma_pred and ma_pred > 0:
        predictions.append(float(ma_pred))
        weights.append(0.2)

    if not predictions:
        return None, 0.0

    # 重みを正規化
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]

    # 加重平均
    ensemble = sum(p * w for p, w in zip(predictions, normalized_weights))

    # 信頼度計算（予測数が多いほど高い、予測のばらつきが小さいほど高い）
    confidence = len(predictions) / 3.0  # 最大3つの予測

    # ばらつき係数（標準偏差/平均）
    if len(predictions) > 1:
        std = float(np.std(predictions))
        mean = float(np.mean(predictions))
        cv = std / mean if mean > 0 else 1.0
        confidence *= (1.0 - min(cv, 0.5))  # ばらつきが大きいと信頼度低下

    # 現在価格との乖離チェック（大きすぎる予測は信頼度を下げる）
    if current_price > 0:
        change_pct = abs(ensemble - current_price) / current_price
        if change_pct > 0.2:  # 20%以上の変動
            confidence *= 0.5

    return float(ensemble), float(min(confidence, 1.0))

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.DatabaseError)),
    reraise=True
)
def save_ensemble_prediction(cur, symbol, prediction_date, prediction_days,
                            current_price, lstm_pred, arima_pred, ma_pred,
                            ensemble_pred, confidence):
    """アンサンブル予測を ensemble_predictions テーブルに保存"""
    try:
        logger.debug(f"Saving prediction for {symbol} ({prediction_days} days ahead)")
        cur.execute("""
            INSERT INTO ensemble_predictions (
                symbol, prediction_date, prediction_days, current_price,
                lstm_prediction, arima_prediction, ma_prediction,
                ensemble_prediction, ensemble_confidence,
                created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
            ON CONFLICT (symbol, prediction_date, prediction_days)
            DO UPDATE SET
                current_price = EXCLUDED.current_price,
                lstm_prediction = EXCLUDED.lstm_prediction,
                arima_prediction = EXCLUDED.arima_prediction,
                ma_prediction = EXCLUDED.ma_prediction,
                ensemble_prediction = EXCLUDED.ensemble_prediction,
                ensemble_confidence = EXCLUDED.ensemble_confidence,
                created_at = NOW()
        """, (symbol, prediction_date, prediction_days, current_price,
              lstm_pred, arima_pred, ma_pred, ensemble_pred, confidence))
        return True
    except Exception as e:
        logger.error(f"Failed to save prediction for {symbol}: {e}")
        return False

def process_symbol(cur, symbol, company_name, target_date, prediction_days):
    """1銘柄の予測処理"""
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

    # 保存
    success = save_ensemble_prediction(
        cur, symbol, target_date, prediction_days, current_price,
        lstm_pred, arima_pred, ma_pred, ensemble_pred, confidence
    )

    return {
        'symbol': symbol,
        'company_name': company_name,
        'current_price': current_price,
        'lstm': lstm_pred,
        'arima': arima_pred,
        'ma': ma_pred,
        'ensemble': ensemble_pred,
        'confidence': confidence,
        'success': success
    }

def main():
    print("=" * 80)
    print("アンサンブル予測統合スクリプト")
    print("=" * 80)
    print()

    # データベース接続
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # アクティブ銘柄取得
        print("-" * 80)
        print("1. アクティブ銘柄取得")
        print("-" * 80)

        symbols = get_active_symbols(cur)
        print(f"対象銘柄数: {len(symbols)}")
        print()

        # 予測対象日（明日から14日間）
        prediction_configs = []
        tomorrow = datetime.now().date() + timedelta(days=1)

        for days_ahead in [1, 3, 7, 14]:
            target_date = tomorrow + timedelta(days=days_ahead - 1)
            prediction_configs.append((target_date, days_ahead))

        print("-" * 80)
        print("2. 予測生成")
        print("-" * 80)
        print(f"予測パターン: {len(prediction_configs)}種類")
        for target_date, days in prediction_configs:
            print(f"  {days}日後予測 (予測日: {target_date})")
        print()

        # 統計
        total_processed = 0
        total_saved = 0
        total_skipped = 0

        for i, symbol_info in enumerate(symbols, 1):
            symbol = symbol_info['symbol']
            company_name = symbol_info['company_name']

            if i % 10 == 0:
                print(f"処理中: {i}/{len(symbols)} ({symbol})")

            for target_date, prediction_days in prediction_configs:
                try:
                    result = process_symbol(
                        cur, symbol, company_name, target_date, prediction_days
                    )

                    if result:
                        total_processed += 1
                        if result['success']:
                            total_saved += 1
                    else:
                        total_skipped += 1
                except Exception as e:
                    # エラーが発生した場合はロールバックして続行
                    conn.rollback()
                    total_skipped += 1
                    if i <= 10:
                        print(f"  エラー ({symbol}): {e}")

            # 10銘柄ごとにコミット
            if i % 10 == 0:
                try:
                    conn.commit()
                except Exception:
                    conn.rollback()

        # 最終コミット
        conn.commit()

        print()
        print("-" * 80)
        print("3. 処理結果")
        print("-" * 80)
        print(f"対象銘柄: {len(symbols)}")
        print(f"予測パターン: {len(prediction_configs)}")
        print(f"最大予測数: {len(symbols) * len(prediction_configs)}")
        print(f"処理成功: {total_processed}")
        print(f"保存成功: {total_saved}")
        print(f"スキップ: {total_skipped}")
        print()

        # サンプル確認
        print("-" * 80)
        print("4. サンプル確認")
        print("-" * 80)

        sample_symbols = ['9984.T', '7203.T', '6861.T', '7974.T', '6758.T']

        for symbol in sample_symbols:
            cur.execute("""
                SELECT
                    symbol,
                    prediction_date,
                    prediction_days,
                    current_price,
                    lstm_prediction,
                    arima_prediction,
                    ma_prediction,
                    ensemble_prediction,
                    ensemble_confidence
                FROM ensemble_predictions
                WHERE symbol = %s
                  AND prediction_date >= CURRENT_DATE
                ORDER BY prediction_date, prediction_days
                LIMIT 4
            """, (symbol,))

            results = cur.fetchall()
            if results:
                print(f"\n{symbol}:")
                for r in results:
                    lstm_str = f"{r['lstm_prediction']:,.0f}" if r['lstm_prediction'] else "なし"
                    arima_str = f"{r['arima_prediction']:,.0f}" if r['arima_prediction'] else "なし"
                    ma_str = f"{r['ma_prediction']:,.0f}" if r['ma_prediction'] else "なし"
                    print(f"  {r['prediction_days']}日後: 現在{r['current_price']:,.0f}円 -> "
                          f"予測{r['ensemble_prediction']:,.0f}円 "
                          f"(信頼度{r['ensemble_confidence']:.2f}) "
                          f"[LSTM:{lstm_str} ARIMA:{arima_str} MA:{ma_str}]")

        # 検証
        print()
        print("-" * 80)
        print("5. 検証")
        print("-" * 80)

        cur.execute("""
            SELECT COUNT(*) as total
            FROM ensemble_predictions
            WHERE prediction_date >= CURRENT_DATE
        """)
        result = cur.fetchone()
        print(f"未来予測の総数: {result['total']:,}件")

        cur.execute("""
            SELECT COUNT(DISTINCT symbol) as symbols
            FROM ensemble_predictions
            WHERE prediction_date >= CURRENT_DATE
        """)
        result = cur.fetchone()
        print(f"予測銘柄数: {result['symbols']:,}銘柄")

        cur.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(lstm_prediction) as with_lstm,
                COUNT(arima_prediction) as with_arima,
                COUNT(ma_prediction) as with_ma
            FROM ensemble_predictions
            WHERE prediction_date >= CURRENT_DATE
        """)
        result = cur.fetchone()
        print(f"LSTM予測あり: {result['with_lstm']:,}/{result['total']:,}件")
        print(f"ARIMA予測あり: {result['with_arima']:,}/{result['total']:,}件")
        print(f"MA予測あり: {result['with_ma']:,}/{result['total']:,}件")

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
