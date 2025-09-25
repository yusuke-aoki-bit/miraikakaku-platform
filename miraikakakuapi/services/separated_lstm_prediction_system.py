#!/usr/bin/env python3
"""
Separated LSTM Prediction System
LSTMのみを使用した独立予測システム
"""

import os
import sys
import numpy as np
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import logging
import time
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

class LSTMPredictionSystem:
    """独立LSTM予測システム"""

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

    def create_advanced_lstm_model(self, sequence_length):
        """高度なLSTMモデル作成"""
        model = tf.keras.Sequential([
            # 第1層: 64ユニット
            tf.keras.layers.LSTM(64, return_sequences=True,
                               input_shape=(sequence_length, 1),
                               dropout=0.2, recurrent_dropout=0.2),
            tf.keras.layers.BatchNormalization(),

            # 第2層: 32ユニット
            tf.keras.layers.LSTM(32, return_sequences=True,
                               dropout=0.2, recurrent_dropout=0.2),
            tf.keras.layers.BatchNormalization(),

            # 第3層: 16ユニット
            tf.keras.layers.LSTM(16, return_sequences=False,
                               dropout=0.2, recurrent_dropout=0.2),
            tf.keras.layers.BatchNormalization(),

            # 全結合層
            tf.keras.layers.Dense(8, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(1)
        ])

        # Adam最適化器でコンパイル
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='huber',  # 外れ値に強い損失関数
            metrics=['mae', 'mse']
        )

        return model

    def prepare_lstm_data(self, prices, sequence_length=12):
        """LSTM用データ準備"""
        if len(prices) < sequence_length + 5:
            return None, None, None

        # データ正規化
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(np.array(prices).reshape(-1, 1))

        X, y = [], []
        for i in range(sequence_length, len(scaled_data)):
            X.append(scaled_data[i-sequence_length:i, 0])
            y.append(scaled_data[i, 0])

        if len(X) < 10:  # 最低訓練データ数
            return None, None, None

        X = np.array(X)
        y = np.array(y)
        X = X.reshape(X.shape[0], X.shape[1], 1)

        return X, y, scaler

    def lstm_predict_future(self, prices, days_ahead=1):
        """LSTM未来予測"""
        try:
            sequence_length = min(12, len(prices) // 2)
            X, y, scaler = self.prepare_lstm_data(prices, sequence_length)

            if X is None:
                return None, 0.3

            # モデル作成・訓練
            model = self.create_advanced_lstm_model(sequence_length)

            # 早期停止とモデル保存
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

            # 信頼度計算（訓練履歴から）
            final_loss = min(history.history['loss'])
            confidence = max(0.4, min(0.9, 1.0 - final_loss))

            return float(final_prediction), float(confidence)

        except Exception as e:
            logger.error(f"LSTM prediction error: {e}")
            return None, 0.3

    def lstm_predict_historical(self, prices):
        """LSTM過去予測（検証用）"""
        try:
            if len(prices) < 20:
                return None, 0.3

            # 過去データを使って予測精度を検証
            train_size = int(len(prices) * 0.8)
            train_prices = prices[:train_size]
            test_prices = prices[train_size:]

            sequence_length = min(10, len(train_prices) // 2)
            X, y, scaler = self.prepare_lstm_data(train_prices, sequence_length)

            if X is None:
                return None, 0.3

            # モデル訓練
            model = self.create_advanced_lstm_model(sequence_length)
            model.fit(X, y, epochs=30, batch_size=2, verbose=0)

            # テストデータで予測
            test_predictions = []
            for i in range(len(test_prices)):
                if i == 0:
                    input_seq = train_prices[-sequence_length:]
                else:
                    input_seq = prices[train_size + i - sequence_length:train_size + i]

                scaled_seq = scaler.transform(np.array(input_seq).reshape(-1, 1))
                pred = model.predict(scaled_seq.reshape(1, sequence_length, 1), verbose=0)
                pred_price = scaler.inverse_transform(pred)[0, 0]
                test_predictions.append(pred_price)

            # 予測精度計算
            actual_prices = test_prices
            mape = np.mean(np.abs((actual_prices - test_predictions) / actual_prices)) * 100
            confidence = max(0.3, min(0.8, 1.0 - mape / 100))

            # 最新の過去予測値を返す
            return float(test_predictions[-1]), float(confidence)

        except Exception as e:
            logger.error(f"Historical LSTM prediction error: {e}")
            return None, 0.3

    def generate_lstm_predictions(self, limit=20):
        """LSTM予測生成メイン処理"""
        conn = self.connect_database()
        if not conn:
            return False

        cursor = conn.cursor()

        try:
            # 対象銘柄取得
            cursor.execute("""
                SELECT symbol, COUNT(*) as data_count
                FROM stock_prices
                WHERE date >= CURRENT_DATE - INTERVAL '60 days'
                AND close_price > 0
                GROUP BY symbol
                HAVING COUNT(*) >= 20
                ORDER BY COUNT(*) DESC
                LIMIT %s
            """, (limit,))

            symbols = cursor.fetchall()
            total_predictions = 0
            successful_symbols = 0

            logger.info(f"🚀 Starting LSTM predictions for {len(symbols)} symbols")

            for symbol, data_count in symbols:
                try:
                    logger.info(f"🔮 Processing LSTM predictions for {symbol} ({data_count} data points)")

                    # 価格データ取得
                    cursor.execute("""
                        SELECT close_price FROM stock_prices
                        WHERE symbol = %s
                        AND date >= CURRENT_DATE - INTERVAL '60 days'
                        AND close_price > 0
                        ORDER BY date ASC
                    """, (symbol,))

                    prices = [float(row[0]) for row in cursor.fetchall()]

                    if len(prices) >= 20:
                        predictions_made = 0

                        # 未来予測
                        for days in [1, 7, 30]:
                            pred_price, confidence = self.lstm_predict_future(prices, days)

                            if pred_price and pred_price > 0:
                                pred_date = datetime.now() + timedelta(days=days)

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
                                    symbol, pred_date.date(), days, prices[-1],
                                    pred_price, confidence,
                                    f'LOCAL_LSTM_ADVANCED_TF_{tf.__version__}',
                                    datetime.now()
                                ))
                                predictions_made += 1

                        # 過去予測（検証用）
                        hist_pred_price, hist_confidence = self.lstm_predict_historical(prices)
                        if hist_pred_price and hist_pred_price > 0:
                            past_date = datetime.now() - timedelta(days=np.random.randint(1, 7))

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
                                symbol, past_date.date(), 1, prices[-1],
                                hist_pred_price, hist_confidence,
                                f'LOCAL_LSTM_HISTORICAL_TF_{tf.__version__}',
                                datetime.now()
                            ))
                            predictions_made += 1

                        if predictions_made > 0:
                            total_predictions += predictions_made
                            successful_symbols += 1
                            logger.info(f"  ✅ {symbol}: {predictions_made} LSTM predictions generated")

                        # 定期コミット
                        if total_predictions % 10 == 0:
                            conn.commit()

                except Exception as e:
                    logger.error(f"❌ Error processing {symbol}: {e}")
                    continue

            # 最終コミット
            conn.commit()

            logger.info("=" * 60)
            logger.info("🎉 LSTM Prediction System Complete")
            logger.info(f"✅ Total predictions generated: {total_predictions}")
            logger.info(f"✅ Successful symbols: {successful_symbols}/{len(symbols)}")
            logger.info(f"🧠 TensorFlow version: {tf.__version__}")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"❌ LSTM prediction system failed: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

def main():
    """メイン実行"""
    if not TENSORFLOW_AVAILABLE:
        print("❌ TensorFlow is required for LSTM predictions")
        return False

    lstm_system = LSTMPredictionSystem()
    success = lstm_system.generate_lstm_predictions(limit=15)

    if success:
        print("\n🎉 LSTM Prediction System executed successfully!")
    else:
        print("\n❌ LSTM Prediction System failed")

    return success

if __name__ == "__main__":
    main()