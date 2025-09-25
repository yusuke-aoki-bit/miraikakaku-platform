#!/usr/bin/env python3
"""
Fixed Cloud Batch Strategy
マシンタイプとリソース要件を修正したCloud Batch戦略
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

class FixedCloudBatchStrategy:
    """修正版Cloud Batch戦略"""

    def __init__(self, project_id="pricewise-huqkr", location="us-central1"):
        self.project_id = project_id
        self.location = location

    def create_minimal_test_job(self) -> Dict[str, Any]:
        """最小テストジョブ"""

        script = '''#!/bin/bash
echo "🚀 Minimal Cloud Batch Test"
echo "Start: $(date)"
echo "✅ Cloud Batch is working!"
echo "End: $(date)"
'''

        return {
            "taskGroups": [{
                "taskSpec": {
                    "runnables": [{
                        "script": {"text": script.strip()}
                    }],
                    "computeResource": {
                        "cpuMilli": 500,   # 0.5 CPU
                        "memoryMib": 1024  # 1GB
                    },
                    "maxRetryCount": 1,
                    "maxRunDuration": "300s"
                },
                "taskCount": 1,
                "parallelism": 1
            }],
            "allocationPolicy": {
                "instances": [{
                    "policy": {
                        "machineType": "e2-small",  # e2-microより大きい
                        "provisioningModel": "STANDARD"
                    }
                }]
            },
            "logsPolicy": {
                "destination": "CLOUD_LOGGING"
            }
        }

    def create_symbol_addition_job(self) -> Dict[str, Any]:
        """修正版銘柄追加ジョブ"""

        script = '''#!/bin/bash
set -e

echo "🚀 Fixed Symbol Addition Job"
echo "Start: $(date)"

# 最小限インストール
apt-get update -q
apt-get install -y python3-pip -q
pip3 install psycopg2-binary --quiet

# 銘柄追加
python3 << 'PYEOF'
import psycopg2

print("🔌 Connecting to database...")
conn = psycopg2.connect(
    host='34.173.9.214',
    user='postgres',
    password='os.getenv('DB_PASSWORD', '')',
    database='miraikakaku'
)
cursor = conn.cursor()
print("✅ Database connected")

# テスト銘柄
symbols = ['AAPL', 'MSFT', 'GOOGL']

for symbol in symbols:
    try:
        cursor.execute("""
            INSERT INTO stock_master (symbol, name, company_name, exchange, is_active)
            VALUES (%s, %s, %s, 'NASDAQ', true)
            ON CONFLICT (symbol) DO UPDATE SET
                is_active = true,
                updated_at = NOW()
        """, (symbol, symbol, f"{symbol} Inc."))

        print(f"✅ Added/Updated: {symbol}")

    except Exception as e:
        print(f"❌ Error {symbol}: {e}")

conn.commit()
conn.close()
print("🎉 Symbol Addition Complete")
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
                        "cpuMilli": 1000,  # 1 CPU
                        "memoryMib": 2048  # 2GB
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
                        "machineType": "e2-standard-2",  # 2 CPU, 8GB
                        "provisioningModel": "STANDARD"
                    }
                }]
            },
            "logsPolicy": {
                "destination": "CLOUD_LOGGING"
            }
        }

    def create_price_data_job(self) -> Dict[str, Any]:
        """修正版価格データジョブ"""

        script = '''#!/bin/bash
set -e

echo "🚀 Fixed Price Data Collection"
echo "Start: $(date)"

# 依存関係インストール
apt-get update -q
apt-get install -y python3-pip -q
pip3 install psycopg2-binary yfinance pandas --quiet

python3 << 'PYEOF'
import yfinance as yf
import psycopg2
import pandas as pd
from datetime import datetime, timedelta

print("🔌 Connecting to database...")
conn = psycopg2.connect(
    host='34.173.9.214',
    user='postgres',
    password='os.getenv('DB_PASSWORD', '')',
    database='miraikakaku'
)
cursor = conn.cursor()
print("✅ Database connected")

symbols = ['AAPL', 'MSFT', 'GOOGL']
total_prices = 0

for symbol in symbols:
    try:
        print(f"📈 Processing {symbol}...")
        ticker = yf.Ticker(symbol)

        # 直近30日のデータ
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        hist = ticker.history(start=start_date, end=end_date)

        if not hist.empty:
            count = 0
            for date, row in hist.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO stock_prices
                        (symbol, date, open_price, high_price, low_price, close_price, volume, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (symbol, date) DO UPDATE SET
                            close_price = EXCLUDED.close_price,
                            volume = EXCLUDED.volume,
                            updated_at = NOW()
                    """, (
                        symbol, date.date(),
                        float(row['Open']), float(row['High']),
                        float(row['Low']), float(row['Close']),
                        int(row['Volume'])
                    ))
                    count += 1
                except Exception as e:
                    print(f"  ❌ Price error for {symbol} {date}: {e}")
                    continue

            total_prices += count
            print(f"  ✅ {symbol}: {count} prices added")

        conn.commit()

    except Exception as e:
        print(f"❌ Symbol error {symbol}: {e}")

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
                        "cpuMilli": 2000,  # 2 CPU
                        "memoryMib": 4096  # 4GB
                    },
                    "maxRetryCount": 2,
                    "maxRunDuration": "900s"  # 15分
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

    def create_simple_prediction_job(self) -> Dict[str, Any]:
        """修正版シンプル予測ジョブ"""

        script = '''#!/bin/bash
set -e

echo "🚀 Fixed Simple Prediction Job"
echo "Start: $(date)"

apt-get update -q
apt-get install -y python3-pip -q
pip3 install psycopg2-binary numpy --quiet

python3 << 'PYEOF'
import psycopg2
import numpy as np
from datetime import datetime, timedelta

print("🔌 Connecting to database...")
conn = psycopg2.connect(
    host='34.173.9.214',
    user='postgres',
    password='os.getenv('DB_PASSWORD', '')',
    database='miraikakaku'
)
cursor = conn.cursor()
print("✅ Database connected")

symbols = ['AAPL', 'MSFT', 'GOOGL']
total_predictions = 0

for symbol in symbols:
    try:
        print(f"🔮 Processing predictions for {symbol}...")

        # 最新10日の価格取得
        cursor.execute("""
            SELECT close_price FROM stock_prices
            WHERE symbol = %s AND close_price IS NOT NULL
            ORDER BY date DESC LIMIT 10
        """, (symbol,))

        rows = cursor.fetchall()
        prices = [float(row[0]) for row in rows]

        if len(prices) >= 5:
            # シンプルな移動平均予測
            recent_avg = sum(prices[:5]) / 5
            older_avg = sum(prices[-5:]) / min(5, len(prices[-5:]))
            trend = (recent_avg - older_avg) / 5 if len(prices) > 5 else 0

            predictions_made = 0

            for days in [1, 7, 30]:
                predicted_price = recent_avg + (trend * days)
                pred_date = datetime.now() + timedelta(days=days)
                confidence = max(0.5, 0.8 - (days * 0.01))

                cursor.execute("""
                    INSERT INTO stock_predictions
                    (symbol, prediction_date, prediction_days, current_price,
                     predicted_price, confidence_score, model_type, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (symbol, prediction_date, prediction_days)
                    DO UPDATE SET
                        predicted_price = EXCLUDED.predicted_price,
                        confidence_score = EXCLUDED.confidence_score,
                        model_type = EXCLUDED.model_type,
                        updated_at = NOW()
                """, (
                    symbol, pred_date.date(), days, prices[0],
                    predicted_price, confidence,
                    'CLOUD_BATCH_SIMPLE_PREDICTION_V1'
                ))

                predictions_made += 1
                total_predictions += 1

            print(f"  ✅ {symbol}: {predictions_made} predictions")

    except Exception as e:
        print(f"❌ Prediction error {symbol}: {e}")

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
                        "cpuMilli": 1000,  # 1 CPU
                        "memoryMib": 2048  # 2GB
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

    def submit_job(self, job_config: Dict[str, Any], job_name: str) -> bool:
        """ジョブ投入"""
        try:
            logger.info(f"🚀 Submitting: {job_name}")

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
                logger.info(f"✅ Success: {job_name}")
                return True

            finally:
                os.unlink(config_file)

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed {job_name}: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"❌ Error {job_name}: {e}")
            return False

    def execute_fixed_strategy(self):
        """修正版戦略実行"""
        logger.info("🎯 Executing Fixed Cloud Batch Strategy")
        logger.info("="*60)

        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

        # Step 1: テストジョブ
        logger.info("📊 Step 1: Minimal Test Job")
        test_job_name = f"test-minimal-{timestamp}"
        success1 = self.submit_job(self.create_minimal_test_job(), test_job_name)

        if success1:
            time.sleep(60)

            # Step 2: 銘柄追加
            logger.info("📊 Step 2: Symbol Addition")
            symbol_job_name = f"fixed-symbols-{timestamp}"
            success2 = self.submit_job(self.create_symbol_addition_job(), symbol_job_name)

            if success2:
                time.sleep(90)

                # Step 3: 価格データ
                logger.info("📊 Step 3: Price Data Collection")
                price_job_name = f"fixed-prices-{timestamp}"
                success3 = self.submit_job(self.create_price_data_job(), price_job_name)

                if success3:
                    time.sleep(90)

                    # Step 4: 予測
                    logger.info("📊 Step 4: Simple Predictions")
                    pred_job_name = f"fixed-predictions-{timestamp}"
                    success4 = self.submit_job(self.create_simple_prediction_job(), pred_job_name)

                    logger.info("="*60)
                    logger.info("🎉 Fixed Strategy Results:")
                    logger.info(f"  ✅ Test Job: {success1}")
                    logger.info(f"  ✅ Symbol Addition: {success2}")
                    logger.info(f"  ✅ Price Collection: {success3}")
                    logger.info(f"  ✅ Predictions: {success4}")
                    logger.info("="*60)

                    return success1 and success2 and success3 and success4

        logger.info("❌ Fixed strategy failed")
        return False

def main():
    strategy = FixedCloudBatchStrategy()
    strategy.execute_fixed_strategy()

if __name__ == "__main__":
    main()