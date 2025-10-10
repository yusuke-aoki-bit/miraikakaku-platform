#!/usr/bin/env python3
"""
GCP Cloud Function for LSTM Daily Predictions - Improved Version
改善点:
1. 異常値検出と除外
2. 信頼度計算の改善
3. 予測範囲の制限
4. より長い学習期間
"""
import os
import functions_framework
from google.cloud import secretmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import numpy as np
import logging
import warnings

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('tensorflow').setLevel(logging.ERROR)

try:
    import tensorflow as tf
    tf.get_logger().setLevel('ERROR')
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    from sklearn.preprocessing import MinMaxScaler
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False
    logger.error("TensorFlow not available")

def get_secret(secret_id):
    """GCP Secret Managerからシークレットを取得"""
    try:
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv('GCP_PROJECT', 'pricewise-huqkr')
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode('UTF-8')
    except Exception as e:
        logger.warning(f"Secret Manager error: {e}. Using environment variable.")
        return os.getenv(secret_id)

def get_db_connection():
    """データベース接続を取得"""
    if os.getenv('CLOUD_SQL_CONNECTION_NAME'):
        try:
            return psycopg2.connect(
                host=f"/cloudsql/{os.getenv('CLOUD_SQL_CONNECTION_NAME')}",
                user=get_secret('POSTGRES_USER'),
                password=get_secret('POSTGRES_PASSWORD'),
                database=get_secret('POSTGRES_DB')
            )
        except Exception as e:
            logger.warning(f"Unix socket failed: {e}. Trying TCP...")
            return psycopg2.connect(
                host=get_secret('POSTGRES_HOST'),
                user=get_secret('POSTGRES_USER'),
                password=get_secret('POSTGRES_PASSWORD'),
                database=get_secret('POSTGRES_DB'),
                port=int(get_secret('POSTGRES_PORT') or '5432')
            )
    else:
        return psycopg2.connect(
            host=get_secret('POSTGRES_HOST'),
            user=get_secret('POSTGRES_USER'),
            password=get_secret('POSTGRES_PASSWORD'),
            database=get_secret('POSTGRES_DB'),
            port=int(get_secret('POSTGRES_PORT') or '5432')
        )

def detect_outliers(prices, threshold=3):
    """
    異常値を検出（Z-scoreベース）
    threshold: Z-scoreの閾値（デフォルト3）
    """
    prices_array = np.array(prices)
    mean = np.mean(prices_array)
    std = np.std(prices_array)

    if std == 0:
        return np.zeros(len(prices), dtype=bool)

    z_scores = np.abs((prices_array - mean) / std)
    return z_scores > threshold

def remove_outliers(prices, dates):
    """異常値を除外"""
    prices_array = np.array(prices)
    dates_array = np.array(dates)

    outliers = detect_outliers(prices_array)

    # 異常値を除外
    clean_prices = prices_array[~outliers]
    clean_dates = dates_array[~outliers]

    return clean_prices.tolist(), clean_dates.tolist(), np.sum(outliers)

def get_symbols_for_update(limit=50):
    """更新が必要な銘柄を取得"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT sm.symbol
            FROM stock_master sm
            JOIN (
                SELECT symbol
                FROM stock_prices
                WHERE date >= CURRENT_DATE - INTERVAL '120 days'
                GROUP BY symbol
                HAVING COUNT(*) >= 90
            ) sp ON sm.symbol = sp.symbol
            WHERE sm.is_active = TRUE
            ORDER BY sm.symbol
            LIMIT %s
        """, (limit,))
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()

def get_price_data(symbol, days=120):
    """価格データを取得"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT date, close_price
            FROM stock_prices
            WHERE symbol = %s
            ORDER BY date DESC
            LIMIT %s
        """, (symbol, days))
        return list(reversed(cursor.fetchall()))
    finally:
        conn.close()

def calculate_confidence(day, mse, volatility):
    """
    改善された信頼度計算

    Parameters:
    - day: 予測日数
    - mse: モデルの平均二乗誤差
    - volatility: 価格のボラティリティ
    """
    # 基本信頼度（予測日数に応じて減衰）
    base_confidence = 0.95 * np.exp(-day * 0.03)

    # MSEによる補正（低いほど信頼度が高い）
    mse_factor = 1.0 / (1.0 + mse * 10)

    # ボラティリティによる補正（低いほど信頼度が高い）
    volatility_factor = 1.0 / (1.0 + volatility)

    # 総合信頼度
    confidence = base_confidence * mse_factor * volatility_factor

    # 0.5-0.95の範囲に制限
    return float(np.clip(confidence, 0.5, 0.95))

def generate_improved_lstm_prediction(symbol):
    """改善版LSTM予測を生成"""
    if not LSTM_AVAILABLE:
        return {'status': 'error', 'message': 'TensorFlow not available'}

    try:
        # データ取得
        price_data = get_price_data(symbol, days=120)
        if len(price_data) < 90:
            return {'status': 'skipped', 'reason': 'insufficient data'}

        prices = [float(row['close_price']) for row in price_data]
        dates = [row['date'] for row in price_data]

        # 異常値除外
        clean_prices, clean_dates, outliers_count = remove_outliers(prices, dates)

        if len(clean_prices) < 60:
            return {'status': 'skipped', 'reason': 'too many outliers'}

        logger.info(f"{symbol}: Removed {outliers_count} outliers")

        prices_array = np.array(clean_prices)

        # ボラティリティ計算
        returns = np.diff(prices_array) / prices_array[:-1]
        volatility = np.std(returns)

        # スケーリング
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(prices_array.reshape(-1, 1))

        # データ準備（lookback=30に増やす）
        lookback = 30
        X, y = [], []
        for i in range(lookback, len(scaled)):
            X.append(scaled[i-lookback:i, 0])
            y.append(scaled[i, 0])

        X = np.array(X).reshape(len(X), lookback, 1)
        y = np.array(y)

        if len(X) < 20:
            return {'status': 'skipped', 'reason': 'insufficient training data'}

        # 改善版モデル（Dropout追加）
        model = Sequential([
            LSTM(32, return_sequences=True, input_shape=(lookback, 1)),
            Dropout(0.2),
            LSTM(16),
            Dropout(0.2),
            Dense(1)
        ])

        model.compile(optimizer='adam', loss='mse')

        # Early Stopping
        early_stopping = EarlyStopping(
            monitor='loss',
            patience=3,
            restore_best_weights=True
        )

        # 学習
        history = model.fit(
            X, y,
            epochs=20,
            batch_size=16,
            verbose=0,
            callbacks=[early_stopping]
        )

        # 最終MSE
        final_mse = history.history['loss'][-1]

        # 予測生成（14日先に短縮）
        predictions = []
        last_seq = prices_array[-lookback:]

        for day in range(1, 15):
            scaled_seq = scaler.transform(last_seq.reshape(-1, 1))
            X_pred = scaled_seq.reshape(1, lookback, 1)
            pred_scaled = model.predict(X_pred, verbose=0)
            pred_price = scaler.inverse_transform(pred_scaled)[0][0]


            # 予測値の妥当性チェック（最小限のみ）
            current_price = float(prices_array[-1])

            # 負の値や0以下のみを防ぐ
            if pred_price <= 0:
                pred_price = current_price * 0.01
            # 改善された信頼度計算
            confidence = calculate_confidence(day, final_mse, volatility)

            pred_date = clean_dates[-1] + timedelta(days=day)

            predictions.append({
                'symbol': symbol,
                'prediction_date': pred_date,
                'predicted_price': float(pred_price),
                'current_price': current_price,
                'prediction_days': day,
                'confidence_score': confidence,
                'model_type': 'LSTM_Improved',
                'created_at': datetime.now()
            })

            # 次の予測用に更新
            last_seq = np.append(last_seq[1:], pred_price)

        # DB保存
        save_predictions(predictions)

        return {
            'status': 'success',
            'symbol': symbol,
            'predictions_generated': int(len(predictions)),
            'outliers_removed': int(outliers_count),
            'final_mse': float(final_mse),
            'volatility': float(volatility)
        }

    except Exception as e:
        logger.error(f"{symbol}: {e}")
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'message': str(e)}

def save_predictions(predictions):
    """予測をデータベースに保存"""
    if not predictions:
        return 0

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO stock_predictions
            (symbol, prediction_date, predicted_price, current_price, prediction_days,
             confidence_score, model_type, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, prediction_date, prediction_days)
            DO UPDATE SET
                predicted_price = EXCLUDED.predicted_price,
                current_price = EXCLUDED.current_price,
                confidence_score = EXCLUDED.confidence_score,
                model_type = EXCLUDED.model_type,
                created_at = EXCLUDED.created_at
        """

        for pred in predictions:
            cursor.execute(insert_query, (
                pred['symbol'],
                pred['prediction_date'],
                pred['predicted_price'],
                pred['current_price'],
                pred['prediction_days'],
                pred['confidence_score'],
                pred['model_type'],
                pred['created_at']
            ))

        conn.commit()
        return len(predictions)

    finally:
        conn.close()

@functions_framework.http
def generate_predictions(request):
    """Cloud Function エントリーポイント"""
    try:
        request_json = request.get_json(silent=True) or {}
        symbol = request_json.get('symbol')
        batch_size = request_json.get('batch_size', 50)

        if symbol:
            # 単一銘柄処理
            result = generate_improved_lstm_prediction(symbol)
            return result, 200
        else:
            # バッチ処理
            symbols = get_symbols_for_update(batch_size)
            logger.info(f"Processing {len(symbols)} symbols")

            results = []
            for sym in symbols:
                result = generate_improved_lstm_prediction(sym)
                results.append(result)

            successful = sum(1 for r in results if r.get('status') == 'success')

            return {
                'status': 'success',
                'symbols_processed': int(len(symbols)),
                'successful': int(successful),
                'failed': int(len(symbols) - successful),
                'results': results[:10]  # 最初の10件のみ返す
            }, 200

    except Exception as e:
        logger.error(f"Function error: {e}")
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'message': str(e)}, 500
