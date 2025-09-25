#!/usr/bin/env python3
"""
Cloud Build LSTM System - Docker問題回避版
Google Cloud BuildでLSTM & VertexAIシステム構築
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudBuildLSTMSystem:
    """Cloud BuildでのLSTM & VertexAIシステム"""

    def __init__(self, project_id="pricewise-huqkr", location="us-central1"):
        self.project_id = project_id
        self.location = location

    def create_cloudbuild_config(self, image_tag: str) -> Dict[str, Any]:
        """Cloud Build設定を作成"""

        return {
            "steps": [
                {
                    "name": "gcr.io/cloud-builders/docker",
                    "args": [
                        "build",
                        "-t", f"gcr.io/{self.project_id}/miraikakaku-lstm:{image_tag}",
                        "-f", "Dockerfile.lstm",
                        "."
                    ]
                },
                {
                    "name": "gcr.io/cloud-builders/docker",
                    "args": [
                        "push",
                        f"gcr.io/{self.project_id}/miraikakaku-lstm:{image_tag}"
                    ]
                }
            ],
            "images": [f"gcr.io/{self.project_id}/miraikakaku-lstm:{image_tag}"],
            "options": {
                "logging": "CLOUD_LOGGING_ONLY",
                "machineType": "E2_HIGHCPU_8"
            }
        }

    def create_dockerfile_lstm(self) -> str:
        """LSTM専用Dockerfileを作成"""

        dockerfile_content = """FROM python:3.9-slim

# システム依存関係
RUN apt-get update && apt-get install -y \\
    gcc g++ curl wget && \\
    rm -rf /var/lib/apt/lists/*

# Python環境（最適化済み）
RUN pip install --no-cache-dir \\
    psycopg2-binary==2.9.9 \\
    pandas==2.1.4 \\
    numpy==1.24.4 \\
    scikit-learn==1.3.0 \\
    tensorflow-cpu==2.13.0 \\
    google-cloud-aiplatform==1.36.0

WORKDIR /app
ENTRYPOINT ["/bin/bash"]
"""

        dockerfile_path = "Dockerfile.lstm"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content.strip())

        return dockerfile_path

    def submit_cloud_build(self, image_tag: str) -> bool:
        """Cloud Buildを実行"""
        try:
            # Dockerfileを作成
            self.create_dockerfile_lstm()

            # Cloud Build設定を作成
            build_config = self.create_cloudbuild_config(image_tag)

            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(build_config, f, indent=2)
                config_file = f.name

            try:
                # Cloud Build実行
                cmd = [
                    "gcloud", "builds", "submit",
                    "--config", config_file,
                    "."
                ]

                logger.info(f"🏗️ Cloud Build開始: {image_tag}")
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    logger.info(f"✅ Cloud Build成功: {image_tag}")
                    return True
                else:
                    logger.error(f"❌ Cloud Build失敗: {result.stderr}")
                    return False

            finally:
                os.unlink(config_file)

        except Exception as e:
            logger.error(f"Cloud Build実行エラー: {e}")
            return False

    def create_lstm_batch_job(self, image_tag: str) -> Dict[str, Any]:
        """LSTMバッチジョブを作成"""

        image_uri = f"gcr.io/{self.project_id}/miraikakaku-lstm:{image_tag}"

        # 高度なLSTM予測スクリプト
        lstm_script = """
echo "🧠 高度LSTM予測システム開始"
echo "TensorFlow Version: $(python3 -c 'import tensorflow as tf; print(tf.__version__)')"

python3 -c "
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

print('🚀 TensorFlow LSTM予測システム')
print(f'TensorFlow Version: {tf.__version__}')

def create_lstm_model(seq_len):
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(seq_len, 1)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(50, return_sequences=False),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(25),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

def lstm_predict(prices, days_ahead=1):
    try:
        if len(prices) < 10:
            return None, 0.3

        # データ準備
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(np.array(prices).reshape(-1, 1))

        seq_len = min(10, len(scaled) - 1)
        X, y = [], []
        for i in range(seq_len, len(scaled)):
            X.append(scaled[i-seq_len:i, 0])
            y.append(scaled[i, 0])

        if len(X) < 3:
            return None, 0.3

        X, y = np.array(X), np.array(y)
        X = X.reshape(X.shape[0], X.shape[1], 1)

        # モデル訓練
        model = create_lstm_model(seq_len)
        model.fit(X, y, epochs=20, batch_size=1, verbose=0)

        # 予測
        last_seq = X[-1].reshape(1, seq_len, 1)
        predictions = []
        current_seq = last_seq.copy()

        for _ in range(days_ahead):
            pred = model.predict(current_seq, verbose=0)[0, 0]
            predictions.append(pred)
            current_seq = np.roll(current_seq, -1, axis=1)
            current_seq[0, -1, 0] = pred

        final_pred = scaler.inverse_transform([[predictions[-1]]])[0, 0]
        confidence = max(0.4, 0.8 - (days_ahead * 0.02))

        return float(final_pred), float(confidence)

    except Exception as e:
        print(f'LSTM エラー: {e}')
        return None, 0.3

def generate_lstm_predictions():
    conn = psycopg2.connect(
        host='34.173.9.214',
        user='postgres',
        password='os.getenv('DB_PASSWORD', '')',
        database='miraikakaku'
    )
    cursor = conn.cursor()

    # 対象銘柄取得
    cursor.execute('''
        SELECT symbol, COUNT(*) as cnt
        FROM stock_prices
        WHERE date >= CURRENT_DATE - INTERVAL '30 days'
        AND close_price > 0
        GROUP BY symbol
        HAVING COUNT(*) >= 15
        ORDER BY COUNT(*) DESC
        LIMIT 30
    ''')

    symbols = cursor.fetchall()
    total_predictions = 0

    for symbol, cnt in symbols:
        try:
            # 価格データ取得
            cursor.execute('''
                SELECT close_price FROM stock_prices
                WHERE symbol = %s AND date >= CURRENT_DATE - INTERVAL '30 days'
                AND close_price > 0
                ORDER BY date ASC
            ''', (symbol,))

            prices = [float(row[0]) for row in cursor.fetchall()]

            if len(prices) >= 15:
                print(f'🔮 {symbol}: LSTM予測生成 ({len(prices)}日分)')

                # 各期間の予測
                for days in [1, 3, 7, 14, 30]:
                    pred_price, confidence = lstm_predict(prices, days)

                    if pred_price:
                        pred_date = datetime.now() + timedelta(days=days)

                        cursor.execute('''
                            INSERT INTO stock_predictions
                            (symbol, prediction_date, prediction_days, current_price,
                             predicted_price, confidence_score, model_type, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (symbol, prediction_date, prediction_days)
                            DO UPDATE SET predicted_price = EXCLUDED.predicted_price,
                                         confidence_score = EXCLUDED.confidence_score,
                                         model_type = EXCLUDED.model_type,
                                         created_at = EXCLUDED.created_at
                        ''', (
                            symbol, pred_date.date(), days, prices[-1],
                            pred_price, confidence, 'CLOUD_BUILD_LSTM_V1', datetime.now()
                        ))
                        total_predictions += 1

        except Exception as e:
            print(f'⚠️ {symbol}: {e}')

    conn.commit()
    print(f'✅ 総予測生成数: {total_predictions}件')
    conn.close()

generate_lstm_predictions()
"

echo "🎉 LSTM予測システム完了"
"""

        return {
            "taskGroups": [{
                "taskSpec": {
                    "runnables": [{
                        "container": {
                            "imageUri": image_uri,
                            "commands": ["/bin/bash", "-c", lstm_script.strip()]
                        }
                    }],
                    "computeResource": {
                        "cpuMilli": 4000,
                        "memoryMib": 8192
                    },
                    "maxRetryCount": 2,
                    "maxRunDuration": "3600s"
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

    def deploy_lstm_system(self) -> None:
        """完全なLSTMシステムをデプロイ"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        image_tag = f"v{timestamp}"

        logger.info("🚀 Cloud Build LSTM システムデプロイ開始")

        # 1. Cloud BuildでDockerイメージ作成
        if not self.submit_cloud_build(image_tag):
            logger.error("❌ Cloud Build失敗")
            return

        # 2. バッチジョブ投入
        job_name = f"cloud-build-lstm-{timestamp}"

        try:
            job_config = self.create_lstm_batch_job(image_tag)

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
                logger.info(f"✅ LSTM バッチジョブ投入成功: {job_name}")

            finally:
                os.unlink(config_file)

        except Exception as e:
            logger.error(f"❌ バッチジョブ投入失敗: {e}")

def main():
    """メイン関数"""
    system = CloudBuildLSTMSystem()
    system.deploy_lstm_system()

if __name__ == "__main__":
    main()