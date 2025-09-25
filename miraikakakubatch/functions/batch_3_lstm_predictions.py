#!/usr/bin/env python3
"""
Batch 3: LSTM Predictions System
LSTM予測専用バッチシステム（過去・未来予測）
"""

import os
import sys
import numpy as np
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import logging
import warnings

# TensorFlow設定
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    import tensorflow as tf
    from sklearn.preprocessing import MinMaxScaler
    TENSORFLOW_AVAILABLE = True
    print(f"✅ TensorFlow {tf.__version__} loaded successfully")
except ImportError as e:
    TENSORFLOW_AVAILABLE = False
    print(f"❌ TensorFlow import failed: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LSTMPredictionBatch:
    """LSTM予測専用バッチ"""

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
            logger.info("✅ Database connected")
            return conn
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return None

    def get_symbols_for_prediction(self, cursor, min_data_points=20, limit=None):
        """予測対象銘柄取得"""
        try:
            query = """
                SELECT symbol, COUNT(*) as data_count
                FROM stock_prices
                WHERE date >= CURRENT_DATE - INTERVAL '60 days'
                AND close_price > 0
                GROUP BY symbol
                HAVING COUNT(*) >= %s
                ORDER BY COUNT(*) DESC
            """

            params = [min_data_points]
            if limit:
                query += " LIMIT %s"
                params.append(limit)

            cursor.execute(query, params)
            symbols = cursor.fetchall()
            logger.info(f"📊 Found {len(symbols)} symbols suitable for LSTM prediction")
            return symbols

        except Exception as e:
            logger.error(f"❌ Failed to get symbols for prediction: {e}")
            return []

    def get_price_data(self, cursor, symbol, days_back=60):
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

    def create_advanced_lstm_model(self, sequence_length):
        """高度なLSTMモデル作成"""
        try:
            model = tf.keras.Sequential([
                # 第1LSTM層
                tf.keras.layers.LSTM(64, return_sequences=True,
                                   input_shape=(sequence_length, 1),
                                   dropout=0.2, recurrent_dropout=0.2),
                tf.keras.layers.BatchNormalization(),

                # 第2LSTM層
                tf.keras.layers.LSTM(32, return_sequences=True,
                                   dropout=0.2, recurrent_dropout=0.2),
                tf.keras.layers.BatchNormalization(),

                # 第3LSTM層
                tf.keras.layers.LSTM(16, return_sequences=False,
                                   dropout=0.2, recurrent_dropout=0.2),
                tf.keras.layers.BatchNormalization(),

                # 全結合層
                tf.keras.layers.Dense(8, activation='relu'),
                tf.keras.layers.Dropout(0.3),
                tf.keras.layers.Dense(1)
            ])

            # 最適化設定
            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                loss='huber',  # 外れ値に強い損失関数
                metrics=['mae', 'mse']
            )

            return model

        except Exception as e:
            logger.error(f"❌ Failed to create LSTM model: {e}")
            return None

    def prepare_lstm_data(self, prices, sequence_length=12):
        """LSTM用データ準備"""
        try:
            if len(prices) < sequence_length + 5:
                return None, None, None

            # データ正規化
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(np.array(prices).reshape(-1, 1))

            X, y = [], []
            for i in range(sequence_length, len(scaled_data)):
                X.append(scaled_data[i-sequence_length:i, 0])
                y.append(scaled_data[i, 0])

            if len(X) < 10:
                return None, None, None

            X = np.array(X)
            y = np.array(y)
            X = X.reshape(X.shape[0], X.shape[1], 1)

            return X, y, scaler

        except Exception as e:
            logger.error(f"❌ Failed to prepare LSTM data: {e}")
            return None, None, None

    def lstm_predict_future(self, prices, days_ahead=1):
        """LSTM未来予測"""
        try:
            sequence_length = min(12, len(prices) // 2)
            X, y, scaler = self.prepare_lstm_data(prices, sequence_length)

            if X is None:
                return None, 0.3

            # モデル作成・訓練
            model = self.create_advanced_lstm_model(sequence_length)
            if not model:
                return None, 0.3

            # 早期停止コールバック
            callbacks = [
                tf.keras.callbacks.EarlyStopping(
                    monitor='loss', patience=5, restore_best_weights=True
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    monitor='loss', factor=0.5, patience=3, min_lr=0.0001
                )
            ]

            # モデル訓練
            history = model.fit(
                X, y, epochs=50, batch_size=4, verbose=0,
                validation_split=0.2, callbacks=callbacks
            )

            # 多ステップ予測
            predictions = []
            current_sequence = X[-1].copy()

            for _ in range(days_ahead):
                pred = model.predict(current_sequence.reshape(1, sequence_length, 1), verbose=0)
                predictions.append(pred[0, 0])

                # 次の予測のためにシーケンス更新
                current_sequence = np.roll(current_sequence, -1, axis=0)
                current_sequence[-1, 0] = pred[0, 0]

            # 最終予測値を逆変換
            final_prediction = scaler.inverse_transform([[predictions[-1]]])[0, 0]

            # 信頼度計算
            final_loss = min(history.history['loss']) if history.history['loss'] else 1.0
            confidence = max(0.4, min(0.9, 1.0 - final_loss))

            return float(final_prediction), float(confidence)

        except Exception as e:
            logger.error(f"❌ LSTM future prediction error: {e}")
            return None, 0.3

    def lstm_predict_historical(self, prices):
        """LSTM過去予測（検証用）"""
        try:
            if len(prices) < 25:
                return None, 0.3

            # 過去データを使って予測精度検証
            train_size = int(len(prices) * 0.8)
            train_prices = prices[:train_size]
            test_prices = prices[train_size:]

            sequence_length = min(10, len(train_prices) // 2)
            X, y, scaler = self.prepare_lstm_data(train_prices, sequence_length)

            if X is None:
                return None, 0.3

            # モデル訓練
            model = self.create_advanced_lstm_model(sequence_length)
            if not model:
                return None, 0.3

            model.fit(X, y, epochs=30, batch_size=2, verbose=0)

            # テストデータで予測
            test_predictions = []
            for i in range(len(test_prices)):
                if i == 0:
                    input_seq = train_prices[-sequence_length:]
                else:
                    input_seq = prices[train_size + i - sequence_length:train_size + i]

                if len(input_seq) < sequence_length:
                    continue

                scaled_seq = scaler.transform(np.array(input_seq).reshape(-1, 1))
                pred = model.predict(scaled_seq.reshape(1, sequence_length, 1), verbose=0)
                pred_price = scaler.inverse_transform(pred)[0, 0]
                test_predictions.append(pred_price)

            if not test_predictions:
                return None, 0.3

            # 予測精度計算
            actual_prices = test_prices[:len(test_predictions)]
            mape = np.mean(np.abs((np.array(actual_prices) - np.array(test_predictions)) / np.array(actual_prices))) * 100
            confidence = max(0.3, min(0.8, 1.0 - mape / 100))

            return float(test_predictions[-1]), float(confidence)

        except Exception as e:
            logger.error(f"❌ LSTM historical prediction error: {e}")
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

    def run_lstm_predictions(self, prediction_type="both", symbol_limit=None):
        """LSTM予測メイン処理"""
        if not TENSORFLOW_AVAILABLE:
            logger.error("❌ TensorFlow is required for LSTM predictions")
            return False

        conn = self.connect_database()
        if not conn:
            return False

        cursor = conn.cursor()

        try:
            # 予測対象銘柄取得
            symbols = self.get_symbols_for_prediction(cursor, limit=symbol_limit)
            if not symbols:
                logger.error("❌ No symbols found for prediction")
                return False

            total_symbols = len(symbols)
            successful_symbols = 0
            total_predictions = 0

            logger.info("🚀 Starting LSTM Prediction Batch")
            logger.info("=" * 60)
            logger.info(f"🧠 TensorFlow version: {tf.__version__}")
            logger.info(f"📊 Target symbols: {total_symbols}")
            logger.info(f"🔮 Prediction type: {prediction_type}")

            for i, (symbol, data_count) in enumerate(symbols, 1):
                try:
                    logger.info(f"🧠 [{i}/{total_symbols}] LSTM predictions for {symbol} ({data_count} data points)")

                    # 価格データ取得
                    prices = self.get_price_data(cursor, symbol)
                    if len(prices) < 20:
                        logger.warning(f"  ⚠️ {symbol}: Insufficient data ({len(prices)} points)")
                        continue

                    current_price = prices[-1]
                    predictions_made = 0

                    # 未来予測
                    if prediction_type in ["both", "future"]:
                        for days in [1, 7, 30]:
                            pred_price, confidence = self.lstm_predict_future(prices, days)

                            if pred_price and pred_price > 0:
                                pred_date = datetime.now() + timedelta(days=days)
                                model_type = f'BATCH_LSTM_FUTURE_TF_{tf.__version__}'

                                if self.insert_prediction(cursor, symbol, pred_date.date(), days,
                                                        current_price, pred_price, confidence, model_type):
                                    predictions_made += 1

                    # 過去予測（検証用）
                    if prediction_type in ["both", "historical"]:
                        hist_pred_price, hist_confidence = self.lstm_predict_historical(prices)
                        if hist_pred_price and hist_pred_price > 0:
                            past_date = datetime.now() - timedelta(days=np.random.randint(1, 7))
                            model_type = f'BATCH_LSTM_HISTORICAL_TF_{tf.__version__}'

                            if self.insert_prediction(cursor, symbol, past_date.date(), 1,
                                                    current_price, hist_pred_price, hist_confidence, model_type):
                                predictions_made += 1

                    if predictions_made > 0:
                        successful_symbols += 1
                        total_predictions += predictions_made
                        logger.info(f"  ✅ {symbol}: {predictions_made} LSTM predictions generated")

                    # 定期コミット（5銘柄ごと）
                    if i % 5 == 0:
                        conn.commit()
                        logger.info(f"  💾 Committed batch {i}")

                except Exception as e:
                    logger.error(f"❌ Error processing {symbol}: {e}")
                    continue

            # 最終コミット
            conn.commit()

            # 結果サマリー
            logger.info("=" * 60)
            logger.info("🎉 LSTM Prediction Batch Complete")
            logger.info(f"✅ Symbols processed: {total_symbols}")
            logger.info(f"✅ Successful predictions: {successful_symbols}")
            logger.info(f"🔮 Total predictions generated: {total_predictions}")
            logger.info(f"📊 Success rate: {successful_symbols/total_symbols*100:.1f}%")
            logger.info(f"🧠 TensorFlow version: {tf.__version__}")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"❌ LSTM prediction batch failed: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

def main():
    """メイン実行"""
    batch = LSTMPredictionBatch()

    prediction_type = "both"
    symbol_limit = None

    if len(sys.argv) > 1:
        if sys.argv[1] == "future":
            prediction_type = "future"
        elif sys.argv[1] == "historical":
            prediction_type = "historical"
        elif sys.argv[1] == "quick":
            symbol_limit = 10
        elif sys.argv[1].isdigit():
            symbol_limit = int(sys.argv[1])

    success = batch.run_lstm_predictions(prediction_type, symbol_limit)

    if success:
        print(f"\n🎉 LSTM Prediction Batch ({prediction_type}) completed successfully!")
    else:
        print(f"\n❌ LSTM Prediction Batch ({prediction_type}) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()