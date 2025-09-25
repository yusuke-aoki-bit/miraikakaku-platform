#!/usr/bin/env python3
"""
Cloud Batch Success Strategy
Cloud Batchでの確実実行のための戦略的アプローチ
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

class CloudBatchSuccessStrategy:
    """Cloud Batch確実実行戦略"""

    def __init__(self, project_id="pricewise-huqkr", location="us-central1"):
        self.project_id = project_id
        self.location = location

    def create_ultra_simple_symbol_job(self) -> Dict[str, Any]:
        """戦略1: 超シンプル銘柄追加ジョブ"""

        script = '''#!/bin/bash
set -e

echo "🚀 Ultra Simple Symbol Addition"
echo "Start: $(date)"

# 最小限インストール
apt-get update -q
apt-get install -y python3-pip -q
pip3 install psycopg2-binary --quiet

# 超シンプル銘柄追加
python3 << 'PYEOF'
import psycopg2

conn = psycopg2.connect(
    host='34.173.9.214',
    user='postgres',
    password='os.getenv('DB_PASSWORD', '')',
    database='miraikakaku'
)
cursor = conn.cursor()

# 基本銘柄のみ
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

for symbol in symbols:
    try:
        cursor.execute("""
            INSERT INTO stock_master (symbol, name, company_name, exchange, is_active)
            VALUES (%s, %s, %s, 'NASDAQ', true)
            ON CONFLICT (symbol) DO UPDATE SET is_active = true
        """, (symbol, symbol, symbol))
        print(f"✅ Added: {symbol}")
    except Exception as e:
        print(f"❌ Error {symbol}: {e}")

conn.commit()
conn.close()
print("🎉 Ultra Simple Addition Complete")
PYEOF

echo "End: $(date)"
'''

        return {
            "taskGroups": [{
                "taskSpec": {
                    "runnables": [{
                        "script": {"text": script.strip()}
                    }],
                    "computeResource": {
                        "cpuMilli": 1000,  # 最小リソース
                        "memoryMib": 2048
                    },
                    "maxRetryCount": 2,
                    "maxRunDuration": "300s"  # 5分
                },
                "taskCount": 1,
                "parallelism": 1
            }],
            "allocationPolicy": {
                "instances": [{
                    "policy": {
                        "machineType": "e2-micro",  # 最小マシン
                        "provisioningModel": "STANDARD"
                    }
                }]
            },
            "logsPolicy": {
                "destination": "CLOUD_LOGGING"
            }
        }

    def create_price_collection_job(self) -> Dict[str, Any]:
        """戦略2: 専用価格収集ジョブ"""

        script = '''#!/bin/bash
set -e

echo "🚀 Dedicated Price Collection"
echo "Start: $(date)"

# 価格データ専用
apt-get update -q
apt-get install -y python3-pip -q
pip3 install psycopg2-binary yfinance pandas --quiet

python3 << 'PYEOF'
import yfinance as yf
import psycopg2
import pandas as pd
from datetime import datetime, timedelta

conn = psycopg2.connect(
    host='34.173.9.214',
    user='postgres',
    password='os.getenv('DB_PASSWORD', '')',
    database='miraikakaku'
)
cursor = conn.cursor()

symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
total_prices = 0

for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        hist = ticker.history(start=start_date, end=end_date)

        for date, row in hist.iterrows():
            cursor.execute("""
                INSERT INTO stock_prices
                (symbol, date, close_price, volume)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (symbol, date) DO UPDATE SET
                    close_price = EXCLUDED.close_price
            """, (symbol, date.date(), float(row['Close']), int(row['Volume'])))
            total_prices += 1

        print(f"✅ {symbol}: {len(hist)} prices")
        conn.commit()

    except Exception as e:
        print(f"❌ {symbol}: {e}")

print(f"🎉 Total prices added: {total_prices}")
conn.close()
PYEOF

echo "End: $(date)"
'''

        return {
            "taskGroups": [{
                "taskSpec": {
                    "runnables": [{
                        "script": {"text": script.strip()}
                    }],
                    "computeResource": {
                        "cpuMilli": 2000,
                        "memoryMib": 4096
                    },
                    "maxRetryCount": 2,
                    "maxRunDuration": "600s"  # 10分
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

    def create_basic_prediction_job(self) -> Dict[str, Any]:
        """戦略3: 基本予測ジョブ（LSTM無し）"""

        script = '''#!/bin/bash
set -e

echo "🚀 Basic Prediction Job"
echo "Start: $(date)"

apt-get update -q
apt-get install -y python3-pip -q
pip3 install psycopg2-binary numpy --quiet

python3 << 'PYEOF'
import psycopg2
import numpy as np
from datetime import datetime, timedelta

conn = psycopg2.connect(
    host='34.173.9.214',
    user='postgres',
    password='os.getenv('DB_PASSWORD', '')',
    database='miraikakaku'
)
cursor = conn.cursor()

# 基本的な線形予測
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
total_predictions = 0

for symbol in symbols:
    try:
        cursor.execute("""
            SELECT close_price FROM stock_prices
            WHERE symbol = %s
            ORDER BY date DESC LIMIT 10
        """, (symbol,))

        prices = [float(row[0]) for row in cursor.fetchall()]

        if len(prices) >= 5:
            # シンプルな移動平均予測
            avg_price = sum(prices[:5]) / 5
            trend = (prices[0] - prices[4]) / 4 if len(prices) > 4 else 0

            for days in [1, 7, 30]:
                predicted_price = avg_price + (trend * days)
                pred_date = datetime.now() + timedelta(days=days)

                cursor.execute("""
                    INSERT INTO stock_predictions
                    (symbol, prediction_date, prediction_days, current_price,
                     predicted_price, confidence_score, model_type, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, prediction_date, prediction_days)
                    DO UPDATE SET predicted_price = EXCLUDED.predicted_price
                """, (symbol, pred_date.date(), days, prices[0],
                     predicted_price, 0.6, 'CLOUD_BATCH_BASIC_V1', datetime.now()))

                total_predictions += 1

            print(f"✅ {symbol}: 3 predictions")

    except Exception as e:
        print(f"❌ {symbol}: {e}")

conn.commit()
print(f"🎉 Total predictions: {total_predictions}")
conn.close()
PYEOF

echo "End: $(date)"
'''

        return {
            "taskGroups": [{
                "taskSpec": {
                    "runnables": [{
                        "script": {"text": script.strip()}
                    }],
                    "computeResource": {
                        "cpuMilli": 2000,
                        "memoryMib": 4096
                    },
                    "maxRetryCount": 2,
                    "maxRunDuration": "600s"
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

    def create_regional_failover_jobs(self) -> list:
        """戦略4: リージョン分散でフェイルオーバー"""

        regions = ["us-central1", "us-east1", "europe-west1"]
        jobs = []

        for region in regions:
            # 地域ごとの軽量ジョブ
            jobs.append({
                "region": region,
                "config": self.create_ultra_simple_symbol_job()
            })

        return jobs

    def submit_job(self, job_config: Dict[str, Any], job_name: str, location: str = None) -> bool:
        """ジョブ投入"""
        location = location or self.location

        try:
            logger.info(f"🚀 Submitting {job_name} to {location}")

            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(job_config, f, indent=2)
                config_file = f.name

            try:
                cmd = [
                    "gcloud", "batch", "jobs", "submit",
                    job_name,
                    f"--location={location}",
                    f"--config={config_file}"
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                logger.info(f"✅ Success: {job_name}")
                return True

            finally:
                os.unlink(config_file)

        except Exception as e:
            logger.error(f"❌ Failed {job_name}: {e}")
            return False

    def execute_progressive_strategy(self):
        """段階的戦略実行"""
        logger.info("🎯 Executing Progressive Cloud Batch Strategy")
        logger.info("="*60)

        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

        # Stage 1: 超シンプル銘柄追加
        logger.info("📊 Stage 1: Ultra Simple Symbol Addition")
        job1_name = f"ultra-simple-symbols-{timestamp}"
        success1 = self.submit_job(self.create_ultra_simple_symbol_job(), job1_name)

        if success1:
            time.sleep(60)  # 1分待機

            # Stage 2: 価格データ収集
            logger.info("📊 Stage 2: Dedicated Price Collection")
            job2_name = f"price-collection-{timestamp}"
            success2 = self.submit_job(self.create_price_collection_job(), job2_name)

            if success2:
                time.sleep(60)

                # Stage 3: 基本予測
                logger.info("📊 Stage 3: Basic Predictions")
                job3_name = f"basic-predictions-{timestamp}"
                success3 = self.submit_job(self.create_basic_prediction_job(), job3_name)

                logger.info("="*60)
                logger.info("🎉 Progressive Strategy Deployed")
                logger.info(f"  ✅ Stage 1: {success1}")
                logger.info(f"  ✅ Stage 2: {success2}")
                logger.info(f"  ✅ Stage 3: {success3}")
                logger.info("="*60)

                return True

        logger.info("❌ Progressive strategy failed at stage 1")
        return False

    def execute_regional_failover(self):
        """リージョン分散フェイルオーバー"""
        logger.info("🌍 Executing Regional Failover Strategy")

        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        regional_jobs = self.create_regional_failover_jobs()

        success_count = 0

        for job_info in regional_jobs:
            region = job_info["region"]
            config = job_info["config"]
            job_name = f"regional-{region}-{timestamp}"

            if self.submit_job(config, job_name, region):
                success_count += 1
                time.sleep(30)

        logger.info(f"🌍 Regional Deployment: {success_count}/{len(regional_jobs)} successful")
        return success_count > 0

def main():
    strategy = CloudBatchSuccessStrategy()

    logger.info("🎯 Cloud Batch Success Strategy Options:")
    logger.info("1. Progressive Strategy (Recommended)")
    logger.info("2. Regional Failover Strategy")
    logger.info("3. Both Strategies")

    # Execute progressive strategy
    success = strategy.execute_progressive_strategy()

    if not success:
        logger.info("🔄 Fallback to Regional Strategy")
        strategy.execute_regional_failover()

if __name__ == "__main__":
    main()