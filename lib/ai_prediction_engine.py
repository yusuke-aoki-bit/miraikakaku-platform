#!/usr/bin/env python3
"""
AI-Powered Prediction Engine with LSTM and VertexAI
LSTMとVertexAIを使ったAI予測エンジン
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIPredictionEngine:
    """AI予測エンジン（LSTM + VertexAI）"""

    def __init__(self, project_id="pricewise-huqkr", location="us-central1"):
        self.project_id = project_id
        self.location = location

    def create_ai_prediction_job(self) -> Dict[str, Any]:
        """AI予測ジョブを作成（過去予測と未来予測の整合性確認付き）"""

        script = """#!/bin/bash
set -e

echo "🤖 AI予測エンジン - LSTM & VertexAI予測システム"
echo "開始時刻: $(date)"
echo "=========================================="

# 1. AI/ML関連パッケージのインストール
echo "📦 AI/MLパッケージのインストール中..."
pip install -q psycopg2-binary>=2.9.9 yfinance>=0.2.18 pandas>=2.1.0 numpy>=1.24.0
pip install -q scikit-learn>=1.3.0 tensorflow>=2.13.0 google-cloud-aiplatform>=1.36.0
pip install -q requests>=2.31.0 matplotlib>=3.7.0 seaborn>=0.12.0

# 2. LSTM予測モデルの実装と実行
echo "🧠 LSTM予測モデルの実行中..."
python3 -c "
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

# TensorFlowのインポート（ログレベル調整）
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

def create_lstm_model(sequence_length, features):
    '''シンプルなLSTMモデルを作成'''
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(sequence_length, features)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(50, return_sequences=False),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(25),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
    return model

def prepare_lstm_data(prices, sequence_length=10):
    '''LSTM用のデータを準備'''
    if len(prices) < sequence_length + 1:
        return None, None, None

    # 正規化
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(np.array(prices).reshape(-1, 1))

    # シーケンスデータの作成
    X, y = [], []
    for i in range(sequence_length, len(scaled_data)):
        X.append(scaled_data[i-sequence_length:i, 0])
        y.append(scaled_data[i, 0])

    return np.array(X), np.array(y), scaler

def predict_with_lstm(prices, days_ahead=1):
    '''LSTMで価格予測'''
    try:
        sequence_length = min(10, len(prices) - 1)
        if sequence_length < 3:
            return None, 0.3

        X, y, scaler = prepare_lstm_data(prices, sequence_length)
        if X is None:
            return None, 0.3

        # モデル作成と学習
        model = create_lstm_model(sequence_length, 1)

        # データが少ない場合は簡単な学習
        epochs = min(20, max(5, len(X) // 2))
        model.fit(X.reshape(X.shape[0], X.shape[1], 1), y,
                 epochs=epochs, batch_size=1, verbose=0)

        # 予測実行
        last_sequence = X[-1].reshape(1, sequence_length, 1)

        predictions = []
        current_sequence = last_sequence.copy()

        for _ in range(days_ahead):
            pred = model.predict(current_sequence, verbose=0)[0, 0]
            predictions.append(pred)

            # 次の予測のためにシーケンスを更新
            current_sequence = np.roll(current_sequence, -1, axis=1)
            current_sequence[0, -1, 0] = pred

        # 正規化を元に戻す
        final_prediction = scaler.inverse_transform([[predictions[-1]]])[0, 0]

        # 信頼度スコア（データ量と学習エポック数に基づく）
        confidence = min(0.9, 0.5 + (len(X) * epochs) / 1000)

        return float(final_prediction), float(confidence)

    except Exception as e:
        print(f'LSTM予測エラー: {e}')
        return None, 0.3

def generate_ai_predictions():
    '''AI予測の生成（過去予測と未来予測）'''
    conn = psycopg2.connect(
        host='34.173.9.214',
        user='postgres',
        password='os.getenv('DB_PASSWORD', '')',
        database='miraikakaku'
    )
    cursor = conn.cursor()

    # 価格データが十分にある銘柄を取得
    cursor.execute('''
        SELECT symbol, COUNT(*) as price_count
        FROM stock_prices
        WHERE date >= CURRENT_DATE - INTERVAL '60 days'
        AND close_price IS NOT NULL
        GROUP BY symbol
        HAVING COUNT(*) >= 15
        ORDER BY COUNT(*) DESC
        LIMIT 30
    ''')

    symbols_data = cursor.fetchall()

    total_predictions = 0
    historical_predictions = 0
    future_predictions = 0

    for symbol, price_count in symbols_data:
        try:
            # 過去60日の価格データを取得
            cursor.execute('''
                SELECT date, close_price
                FROM stock_prices
                WHERE symbol = %s
                AND date >= CURRENT_DATE - INTERVAL '60 days'
                AND close_price IS NOT NULL
                ORDER BY date ASC
            ''', (symbol,))

            price_data = cursor.fetchall()
            if len(price_data) < 15:
                continue

            dates = [row[0] for row in price_data]
            prices = [float(row[1]) for row in price_data]

            # 1. 未来予測の生成
            print(f'🔮 {symbol}: 未来予測生成中...')
            for days_ahead in [1, 3, 7, 14, 30]:
                prediction_date = datetime.now() + timedelta(days=days_ahead)
                predicted_price, confidence = predict_with_lstm(prices, days_ahead)

                if predicted_price is not None:
                    cursor.execute('''
                        INSERT INTO stock_predictions
                        (symbol, prediction_date, prediction_days, current_price,
                         predicted_price, confidence_score, model_type, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, prediction_date, prediction_days) DO UPDATE SET
                            predicted_price = EXCLUDED.predicted_price,
                            confidence_score = EXCLUDED.confidence_score,
                            model_type = EXCLUDED.model_type,
                            created_at = EXCLUDED.created_at
                    ''', (
                        symbol,
                        prediction_date.date(),
                        days_ahead,
                        prices[-1],  # 最新価格
                        predicted_price,
                        confidence,
                        'LSTM_AI_V1',
                        datetime.now()
                    ))
                    future_predictions += 1

            # 2. 過去予測の生成（整合性確認のため）
            print(f'📊 {symbol}: 過去予測生成中（整合性確認用）...')

            # 過去の異なる時点でのデータを使って予測
            for back_days in [7, 14, 30]:
                if len(prices) > back_days + 10:
                    # back_days前の時点でのデータを使用
                    historical_data = prices[:-back_days]
                    actual_price = prices[-back_days]
                    prediction_date = dates[-back_days]

                    # その時点での予測を生成
                    predicted_price, confidence = predict_with_lstm(historical_data, back_days)

                    if predicted_price is not None:
                        # 過去予測として保存（実際の値との比較用）
                        cursor.execute('''
                            INSERT INTO stock_predictions
                            (symbol, prediction_date, prediction_days, current_price,
                             predicted_price, confidence_score, model_type, created_at, actual_price)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (symbol, prediction_date, prediction_days) DO UPDATE SET
                                predicted_price = EXCLUDED.predicted_price,
                                confidence_score = EXCLUDED.confidence_score,
                                model_type = EXCLUDED.model_type,
                                actual_price = EXCLUDED.actual_price,
                                created_at = EXCLUDED.created_at
                        ''', (
                            symbol,
                            prediction_date,
                            back_days,
                            historical_data[-1],  # その時点での最新価格
                            predicted_price,
                            confidence,
                            'LSTM_HISTORICAL_V1',
                            datetime.now(),
                            actual_price  # 実際の価格
                        ))
                        historical_predictions += 1

        except Exception as e:
            print(f'⚠️ {symbol}のAI予測エラー: {e}')
            continue

        total_predictions = future_predictions + historical_predictions

        if total_predictions % 20 == 0:
            conn.commit()
            print(f'✅ 進捗: 未来予測{future_predictions}件, 過去予測{historical_predictions}件')

    conn.commit()

    print('='*60)
    print('🤖 AI予測生成レポート')
    print(f'✅ 処理銘柄数: {len(symbols_data)}')
    print(f'✅ 未来予測生成: {future_predictions}件')
    print(f'✅ 過去予測生成: {historical_predictions}件')
    print(f'✅ 総予測数: {total_predictions}件')
    print('='*60)

    conn.close()

generate_ai_predictions()
"

# 3. 予測精度の評価
echo "📈 予測精度評価中..."
python3 -c "
import psycopg2
import numpy as np

def evaluate_prediction_accuracy():
    '''予測精度の評価'''
    conn = psycopg2.connect(
        host='34.173.9.214',
        user='postgres',
        password='os.getenv('DB_PASSWORD', '')',
        database='miraikakaku'
    )
    cursor = conn.cursor()

    # 過去予測の精度を評価
    cursor.execute('''
        SELECT
            symbol,
            model_type,
            prediction_days,
            predicted_price,
            actual_price,
            ABS(predicted_price - actual_price) / actual_price * 100 as error_percentage
        FROM stock_predictions
        WHERE actual_price IS NOT NULL
        AND model_type LIKE '%HISTORICAL%'
        AND created_at >= NOW() - INTERVAL '1 hour'
    ''')

    accuracy_data = cursor.fetchall()

    if accuracy_data:
        total_predictions = len(accuracy_data)
        avg_error = np.mean([row[5] for row in accuracy_data])

        # モデル別精度
        model_accuracy = {}
        for row in accuracy_data:
            model = row[1]
            error = row[5]
            if model not in model_accuracy:
                model_accuracy[model] = []
            model_accuracy[model].append(error)

        print('='*50)
        print('📊 AI予測精度レポート')
        print(f'✅ 評価対象予測数: {total_predictions}')
        print(f'✅ 平均誤差率: {avg_error:.2f}%')

        for model, errors in model_accuracy.items():
            avg_model_error = np.mean(errors)
            print(f'✅ {model}: {avg_model_error:.2f}%')

        print('='*50)
    else:
        print('⚠️ 評価可能な過去予測データがありません')

    conn.close()

evaluate_prediction_accuracy()
"

echo "🎉 AI予測エンジン実行完了"
echo "終了時刻: $(date)"
"""

        return {
            "taskGroups": [{
                "taskSpec": {
                    "runnables": [{
                        "script": {
                            "text": script.strip()
                        }
                    }],
                    "computeResource": {
                        "cpuMilli": 4000,
                        "memoryMib": 8192
                    },
                    "maxRetryCount": 2,
                    "maxRunDuration": "5400s"  # 90分
                },
                "taskCount": 1,
                "parallelism": 1
            }],
            "allocationPolicy": {
                "instances": [{
                    "policy": {
                        "machineType": "e2-standard-4",
                        "provisioningModel": "STANDARD"
                    }
                }]
            },
            "logsPolicy": {
                "destination": "CLOUD_LOGGING"
            }
        }

    def submit_ai_job(self, job_name: str) -> bool:
        """AI予測ジョブを投入"""
        try:
            logger.info(f"Submitting AI prediction job: {job_name}")

            job_config = self.create_ai_prediction_job()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(job_config, f, indent=2)
                config_file = f.name

            try:
                cmd = [
                    "gcloud", "batch", "jobs", "submit",
                    job_name,
                    f"--location={self.location}",
                    f"--config={config_file}"
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                logger.info(f"AI prediction job submitted successfully: {job_name}")
                return True

            finally:
                os.unlink(config_file)

        except Exception as e:
            logger.error(f"Failed to submit AI job {job_name}: {e}")
            return False

    def deploy_ai_prediction_job(self) -> None:
        """AI予測ジョブをデプロイ"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        job_name = f"lstm-ai-predictions-{timestamp}"

        if self.submit_ai_job(job_name):
            logger.info(f"✅ AI prediction job deployed: {job_name}")
        else:
            logger.error(f"❌ Failed to deploy AI job: {job_name}")

def main():
    """メイン関数"""
    engine = AIPredictionEngine()
    engine.deploy_ai_prediction_job()

if __name__ == "__main__":
    main()