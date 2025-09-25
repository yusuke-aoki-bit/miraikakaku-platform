#!/usr/bin/env python3
"""
Fixed Batch Job Deployer - pip installation issue resolver
修正版バッチジョブデプロイヤー - pip インストール問題解決
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FixedBatchDeployer:
    """修正版バッチジョブデプロイヤー"""

    def __init__(self, project_id="pricewise-huqkr", location="us-central1"):
        self.project_id = project_id
        self.location = location

    def create_fixed_data_job(self) -> Dict[str, Any]:
        """修正版データ収集・予測生成ジョブを作成"""

        script = """#!/bin/bash
set -e

echo "🔧 修正版バッチジョブ実行開始"
echo "開始時刻: $(date)"
echo "=================================="

# 1. システム準備とpipインストール
echo "🔧 システム準備中..."
apt-get update -qq
apt-get install -y python3-pip curl wget -qq

# 2. Python環境確認
echo "🐍 Python環境確認..."
python3 --version
pip3 --version

# 3. 必要パッケージのインストール
echo "📦 パッケージインストール中..."
pip3 install --upgrade pip
pip3 install psycopg2-binary==2.9.9 yfinance==0.2.18 pandas==2.1.4 numpy==1.24.4 requests==2.31.0

# 4. データベース接続確認
echo "🔌 データベース接続確認..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='34.173.9.214',
        user='postgres',
        password='os.getenv('DB_PASSWORD', '')',
        database='miraikakaku',
        connect_timeout=10
    )
    print('✅ データベース接続成功')
    conn.close()
except Exception as e:
    print(f'❌ データベース接続失敗: {e}')
    exit(1)
"

# 5. シンプル予測データ生成
echo "🔮 シンプル予測データ生成中..."
python3 -c "
import psycopg2
import numpy as np
from datetime import datetime, timedelta
import random

def generate_simple_predictions():
    print('🚀 シンプル予測データ生成開始')

    conn = psycopg2.connect(
        host='34.173.9.214',
        user='postgres',
        password='os.getenv('DB_PASSWORD', '')',
        database='miraikakaku'
    )
    cursor = conn.cursor()

    # 最新の価格データがある銘柄を取得
    cursor.execute('''
        SELECT sp.symbol, sp.close_price, sm.company_name
        FROM stock_prices sp
        JOIN stock_master sm ON sp.symbol = sm.symbol
        WHERE sp.date >= CURRENT_DATE - INTERVAL '7 days'
        AND sp.close_price IS NOT NULL
        AND sm.is_active = true
        ORDER BY RANDOM()
        LIMIT 100
    ''')

    symbols_data = cursor.fetchall()
    predictions_created = 0

    print(f'🎯 対象銘柄数: {len(symbols_data)}')

    for symbol, current_price, company_name in symbols_data:
        try:
            # 過去10日の価格データを取得
            cursor.execute('''
                SELECT close_price FROM stock_prices
                WHERE symbol = %s
                AND date >= CURRENT_DATE - INTERVAL '10 days'
                AND close_price IS NOT NULL
                ORDER BY date DESC
                LIMIT 10
            ''', (symbol,))

            price_history = [row[0] for row in cursor.fetchall()]

            if len(price_history) >= 3:
                # シンプルな統計ベース予測
                avg_price = np.mean(price_history)
                price_std = np.std(price_history)
                trend = (price_history[0] - price_history[-1]) / len(price_history)

                # 複数期間の予測を生成
                for days_ahead in [1, 3, 7, 14, 30]:
                    prediction_date = datetime.now() + timedelta(days=days_ahead)

                    # トレンド + ランダム変動
                    trend_component = trend * days_ahead
                    random_component = random.gauss(0, max(price_std * 0.1, current_price * 0.02))
                    predicted_price = float(current_price + trend_component + random_component)

                    # 妥当性チェック
                    predicted_price = max(predicted_price, current_price * 0.8)
                    predicted_price = min(predicted_price, current_price * 1.2)

                    # 信頼度（期間が長いほど低下）
                    confidence = max(0.4, 0.8 - (days_ahead * 0.015))

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
                        float(current_price),
                        predicted_price,
                        confidence,
                        'FIXED_SIMPLE_V1',
                        datetime.now()
                    ))

                    predictions_created += 1

        except Exception as e:
            print(f'⚠️ {symbol} エラー: {e}')
            continue

        # 進捗表示
        if predictions_created % 100 == 0:
            conn.commit()
            print(f'✅ 進捗: {predictions_created}件の予測を生成')

    conn.commit()
    print(f'✅ 合計 {predictions_created}件の予測データを生成完了')

    # 結果確認
    cursor.execute('''
        SELECT COUNT(*) FROM stock_predictions
        WHERE created_at >= NOW() - INTERVAL '10 minutes'
    ''')
    recent_count = cursor.fetchone()[0]
    print(f'📊 今回生成された予測数: {recent_count}')

    conn.close()

generate_simple_predictions()
"

echo "🎉 修正版バッチジョブ実行完了"
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
                        "cpuMilli": 2000,
                        "memoryMib": 4096
                    },
                    "maxRetryCount": 2,
                    "maxRunDuration": "1800s"
                },
                "taskCount": 1,
                "parallelism": 1
            }],
            "allocationPolicy": {
                "instances": [{
                    "policy": {
                        "machineType": "e2-standard-2",
                        "provisioningModel": "STANDARD"
                    }
                }]
            },
            "logsPolicy": {
                "destination": "CLOUD_LOGGING"
            }
        }

    def submit_fixed_job(self, job_name: str) -> bool:
        """修正版ジョブを投入"""
        try:
            logger.info(f"Submitting fixed job: {job_name}")

            job_config = self.create_fixed_data_job()

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
                logger.info(f"Fixed job submitted successfully: {job_name}")
                return True

            finally:
                os.unlink(config_file)

        except Exception as e:
            logger.error(f"Failed to submit fixed job {job_name}: {e}")
            return False

    def deploy_fixed_job(self) -> None:
        """修正版ジョブをデプロイ"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        job_name = f"fixed-prediction-job-{timestamp}"

        if self.submit_fixed_job(job_name):
            logger.info(f"✅ Fixed prediction job deployed: {job_name}")
        else:
            logger.error(f"❌ Failed to deploy fixed job: {job_name}")

def main():
    """メイン関数"""
    deployer = FixedBatchDeployer()
    deployer.deploy_fixed_job()

if __name__ == "__main__":
    main()