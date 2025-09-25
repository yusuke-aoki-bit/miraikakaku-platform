#!/usr/bin/env python3
"""
Lightweight LSTM Batch System
軽量化LSTM予測バッチシステム（メモリ・CPU最適化）
"""

import os
import sys
import numpy as np
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import logging
import warnings

# 最適化設定
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# TensorFlow軽量化設定
try:
    import tensorflow as tf
    from sklearn.preprocessing import MinMaxScaler

    # メモリ最適化
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.threading.set_intra_op_parallelism_threads(1)

    # GPU無効化（CPUのみ使用）
    tf.config.set_visible_devices([], 'GPU')

    TENSORFLOW_AVAILABLE = True
    print(f"✅ Lightweight TensorFlow {tf.__version__} loaded")
except ImportError as e:
    TENSORFLOW_AVAILABLE = False
    print(f"❌ TensorFlow import failed: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightweightLSTMBatch:
    """軽量化LSTM予測バッチ"""

    def __init__(self):
        self.db_config = {
            'host': '34.173.9.214',
            'user': 'postgres',
            'password': 'os.getenv('DB_PASSWORD', '')',
            'database': 'miraikakaku'
        }

    def connect_database(self):
        """データベース接続"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return None

    def get_symbols_for_prediction(self, cursor, limit=10):
        """予測対象銘柄取得（軽量化）"""
        try:
            cursor.execute("""
                SELECT symbol, COUNT(*) as data_count
                FROM stock_prices
                WHERE date >= CURRENT_DATE - INTERVAL '30 days'
                AND close_price > 0
                GROUP BY symbol
                HAVING COUNT(*) >= 15
                ORDER BY COUNT(*) DESC
                LIMIT %s
            """, (limit,))

            symbols = cursor.fetchall()
            logger.info(f"📊 Found {len(symbols)} symbols for lightweight LSTM")
            return symbols
        except Exception as e:
            logger.error(f"❌ Failed to get symbols: {e}")
            return []

    def get_price_data(self, cursor, symbol, days_back=30):
        """価格データ取得"""
        try:
            cursor.execute("""
                SELECT close_price FROM stock_prices
                WHERE symbol = %s
                AND date >= CURRENT_DATE - INTERVAL '%s days'
                AND close_price > 0
                ORDER BY date ASC
            """, (symbol, days_back))

            prices = [float(row[0]) for row in cursor.fetchall()]
            return prices
        except Exception as e:
            logger.error(f"❌ Failed to get price data for {symbol}: {e}")
            return []

    def create_minimal_lstm_model(self, sequence_length):
        """最小限LSTMモデル"""
        try:
            model = tf.keras.Sequential([
                tf.keras.layers.LSTM(16, input_shape=(sequence_length, 1)),
                tf.keras.layers.Dense(1)
            ])

            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=0.1),
                loss='mse'
            )

            return model
        except Exception as e:
            logger.error(f"❌ Failed to create minimal LSTM: {e}")
            return None

    def minimal_lstm_predict(self, prices):
        """最小限LSTM予測"""
        try:
            if len(prices) < 10:
                return None, 0.3

            # 最小限のデータ準備
            scaler = MinMaxScaler()
            scaled = scaler.fit_transform(np.array(prices).reshape(-1, 1))

            sequence_length = min(5, len(scaled) - 2)
            X, y = [], []

            for i in range(sequence_length, len(scaled)):
                X.append(scaled[i-sequence_length:i, 0])
                y.append(scaled[i, 0])

            if len(X) < 3:
                return None, 0.3

            X = np.array(X).reshape(len(X), sequence_length, 1)
            y = np.array(y)

            # 最小限モデル訓練
            model = self.create_minimal_lstm_model(sequence_length)
            if not model:
                return None, 0.3

            model.fit(X, y, epochs=5, batch_size=1, verbose=0)

            # 予測
            last_seq = X[-1].reshape(1, sequence_length, 1)
            pred = model.predict(last_seq, verbose=0)

            # 逆変換
            pred_price = scaler.inverse_transform(pred)[0, 0]

            return float(pred_price), 0.7

        except Exception as e:
            logger.error(f"❌ Minimal LSTM prediction error: {e}")
            return None, 0.3

    def insert_prediction(self, cursor, symbol, pred_date, prediction_days, current_price,
                         predicted_price, confidence, model_type):
        """予測データ挿入"""
        try:
            cursor.execute("""
                INSERT INTO stock_predictions
                (symbol, prediction_date, prediction_days, current_price,
                 predicted_price, confidence_score, model_type, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, prediction_date, prediction_days)
                DO UPDATE SET
                    predicted_price = EXCLUDED.predicted_price,
                    confidence_score = EXCLUDED.confidence_score,
                    model_type = EXCLUDED.model_type,
                    updated_at = NOW()
            """, (
                symbol, pred_date, prediction_days, current_price,
                predicted_price, confidence, model_type, datetime.now()
            ))
            return True
        except Exception as e:
            logger.error(f"❌ Failed to insert prediction for {symbol}: {e}")
            return False

    def run_lightweight_predictions(self, symbol_limit=10):
        """軽量予測実行"""
        conn = self.connect_database()
        if not conn:
            return False

        cursor = conn.cursor()

        try:
            # 対象銘柄取得
            symbols = self.get_symbols_for_prediction(cursor, symbol_limit)
            if not symbols:
                logger.error("❌ No symbols found")
                return False

            total_predictions = 0
            successful_symbols = 0

            logger.info(f"🚀 Starting lightweight LSTM predictions for {len(symbols)} symbols")

            for symbol, data_count in symbols:
                try:
                    logger.info(f"🧠 Processing lightweight LSTM for {symbol}")

                    # 価格データ取得
                    prices = self.get_price_data(cursor, symbol)
                    if len(prices) < 10:
                        continue

                    current_price = prices[-1]
                    predictions_made = 0

                    # 軽量予測（1日、7日のみ）
                    for days in [1, 7]:
                        pred_price, confidence = self.minimal_lstm_predict(prices)

                        if pred_price and pred_price > 0:
                            pred_date = datetime.now() + timedelta(days=days)
                            model_type = f'LIGHTWEIGHT_LSTM_TF_{tf.__version__}'

                            if self.insert_prediction(cursor, symbol, pred_date.date(), days,
                                                    current_price, pred_price, confidence, model_type):
                                predictions_made += 1

                    if predictions_made > 0:
                        successful_symbols += 1
                        total_predictions += predictions_made

                    # 頻繁なコミット
                    if successful_symbols % 2 == 0:
                        conn.commit()

                except Exception as e:
                    logger.error(f"❌ Error processing {symbol}: {e}")
                    continue

            # 最終コミット
            conn.commit()

            logger.info("=" * 60)
            logger.info("🎉 Lightweight LSTM Prediction Complete")
            logger.info(f"✅ Symbols processed: {len(symbols)}")
            logger.info(f"✅ Successful predictions: {successful_symbols}")
            logger.info(f"🔮 Total predictions: {total_predictions}")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"❌ Lightweight LSTM batch failed: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

def main():
    """メイン実行"""
    batch = LightweightLSTMBatch()

    symbol_limit = 10
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        symbol_limit = int(sys.argv[1])

    success = batch.run_lightweight_predictions(symbol_limit)

    if success:
        print(f"\n🎉 Lightweight LSTM Batch completed successfully!")
    else:
        print(f"\n❌ Lightweight LSTM Batch failed")
        sys.exit(1)

if __name__ == "__main__":
    main()