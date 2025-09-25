#!/usr/bin/env python3
"""
Continuous Data Enrichment Batch Job System
継続的データ充足バッチジョブシステム
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

class ContinuousDataEnrichmentJob:
    """継続的データ充足ジョブ"""

    def __init__(self, project_id="pricewise-huqkr", location="us-central1"):
        self.project_id = project_id
        self.location = location

    def create_comprehensive_job(self) -> Dict[str, Any]:
        """包括的データ収集・予測生成ジョブを作成"""

        script = """#!/bin/bash
set -e

echo "🚀 100%完璧miraikakakuシステム - 完全データ充足バッチ"
echo "開始時刻: $(date)"
echo "================================"

# 1. パッケージインストール
echo "📦 必要パッケージのインストール中..."
pip install -q psycopg2-binary>=2.9.9 yfinance>=0.2.18 pandas>=2.1.0 numpy>=1.24.0 requests>=2.31.0

# 2. 銘柄マスタの更新と拡張
echo "🔍 銘柄マスタの更新中..."
python3 -c "
import psycopg2
import yfinance as yf
from datetime import datetime, timedelta
import time

def update_stock_master():
    conn = psycopg2.connect(
        host='34.173.9.214',
        user='postgres',
        password='os.getenv('DB_PASSWORD', '')',
        database='miraikakaku'
    )
    cursor = conn.cursor()

    # 主要な銘柄リスト
    symbols = [
        # 米国株
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA',
        'JPM', 'V', 'JNJ', 'WMT', 'PG', 'UNH', 'HD', 'DIS',
        # 日本株
        '7203.T', '6758.T', '8306.T', '9984.T', '6861.T', '4063.T',
        '6501.T', '8058.T', '8031.T', '7267.T', '4502.T', '9433.T',
        # ETF
        'SPY', 'QQQ', 'DIA', 'VTI', 'VOO', 'IWM', 'EFA', 'EEM'
    ]

    added = 0
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            company_name = info.get('longName', info.get('shortName', symbol))
            exchange = info.get('exchange', 'UNKNOWN')

            cursor.execute('''
                INSERT INTO stock_master (symbol, company_name, exchange, is_active)
                VALUES (%s, %s, %s, true)
                ON CONFLICT (symbol) DO UPDATE SET
                    company_name = EXCLUDED.company_name,
                    exchange = EXCLUDED.exchange,
                    is_active = true
            ''', (symbol, company_name, exchange))

            added += 1
            if added % 10 == 0:
                conn.commit()
                print(f'✅ {added}銘柄を更新')

            time.sleep(0.5)  # API制限対策

        except Exception as e:
            print(f'⚠️ {symbol}のエラー: {e}')
            continue

    conn.commit()
    print(f'✅ 合計{added}銘柄を更新完了')
    conn.close()

update_stock_master()
"

# 3. 価格データの収集
echo "💹 価格データ収集中..."
python3 -c "
import psycopg2
import yfinance as yf
from datetime import datetime, timedelta
import time

def collect_price_data():
    conn = psycopg2.connect(
        host='34.173.9.214',
        user='postgres',
        password='os.getenv('DB_PASSWORD', '')',
        database='miraikakaku'
    )
    cursor = conn.cursor()

    # アクティブな銘柄を取得
    cursor.execute('''
        SELECT symbol FROM stock_master
        WHERE is_active = true
        ORDER BY RANDOM()
        LIMIT 100
    ''')
    symbols = [row[0] for row in cursor.fetchall()]

    prices_added = 0
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)

            if hist.empty:
                continue

            for date, row in hist.iterrows():
                cursor.execute('''
                    INSERT INTO stock_prices
                    (symbol, date, open_price, high_price, low_price, close_price, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, date) DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume
                ''', (
                    symbol,
                    date.date(),
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    int(row['Volume'])
                ))
                prices_added += 1

            if prices_added % 100 == 0:
                conn.commit()
                print(f'✅ {prices_added}件の価格データを保存')

            time.sleep(0.5)  # API制限対策

        except Exception as e:
            print(f'⚠️ {symbol}の価格取得エラー: {e}')
            continue

    conn.commit()
    print(f'✅ 合計{prices_added}件の価格データを収集完了')
    conn.close()

collect_price_data()
"

# 4. 予測データの生成
echo "🔮 予測データ生成中..."
python3 -c "
import psycopg2
import numpy as np
from datetime import datetime, timedelta
import random

def generate_predictions():
    conn = psycopg2.connect(
        host='34.173.9.214',
        user='postgres',
        password='os.getenv('DB_PASSWORD', '')',
        database='miraikakaku'
    )
    cursor = conn.cursor()

    # 最近価格データがある銘柄を取得
    cursor.execute('''
        SELECT DISTINCT sp.symbol, sp.close_price
        FROM stock_prices sp
        WHERE sp.date >= CURRENT_DATE - INTERVAL '7 days'
        AND sp.close_price IS NOT NULL
        ORDER BY RANDOM()
        LIMIT 50
    ''')

    symbols_with_price = cursor.fetchall()
    predictions_added = 0

    for symbol, current_price in symbols_with_price:
        try:
            # 過去の価格データを取得
            cursor.execute('''
                SELECT close_price FROM stock_prices
                WHERE symbol = %s AND date >= CURRENT_DATE - INTERVAL '30 days'
                AND close_price IS NOT NULL
                ORDER BY date DESC
                LIMIT 10
            ''', (symbol,))

            prices = [row[0] for row in cursor.fetchall()]

            if len(prices) < 2:
                continue

            # シンプルな予測ロジック
            avg_price = np.mean(prices)
            std_price = np.std(prices) if len(prices) > 1 else avg_price * 0.05
            trend = (prices[0] - prices[-1]) / len(prices) if len(prices) > 1 else 0

            # 複数日の予測を生成
            for days_ahead in [1, 3, 7, 14, 30]:
                prediction_date = datetime.now() + timedelta(days=days_ahead)

                # トレンドと変動を考慮した予測
                trend_adjustment = trend * days_ahead
                random_variation = random.gauss(0, std_price * 0.1)
                predicted_price = float(avg_price + trend_adjustment + random_variation)

                # 価格が負にならないように調整
                predicted_price = max(predicted_price, current_price * 0.5)

                # 信頼度スコア（日数が長いほど低下）
                confidence = max(0.3, 0.9 - (days_ahead * 0.02))

                cursor.execute('''
                    INSERT INTO stock_predictions
                    (symbol, prediction_date, prediction_days, current_price,
                     predicted_price, confidence_score, model_type, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, prediction_date, prediction_days) DO UPDATE SET
                        predicted_price = EXCLUDED.predicted_price,
                        confidence_score = EXCLUDED.confidence_score,
                        created_at = EXCLUDED.created_at
                ''', (
                    symbol,
                    prediction_date.date(),
                    days_ahead,
                    float(current_price),
                    predicted_price,
                    confidence,
                    'CONTINUOUS_ENRICHMENT_V1',
                    datetime.now()
                ))

                predictions_added += 1

        except Exception as e:
            print(f'⚠️ {symbol}の予測生成エラー: {e}')
            continue

        if predictions_added % 50 == 0:
            conn.commit()
            print(f'✅ {predictions_added}件の予測を生成')

    conn.commit()
    print(f'✅ 合計{predictions_added}件の予測データを生成完了')
    conn.close()

generate_predictions()
"

# 5. データ充足状況の確認
echo "📊 データ充足状況確認中..."
python3 -c "
import psycopg2

conn = psycopg2.connect(
    host='34.173.9.214',
    user='postgres',
    password='os.getenv('DB_PASSWORD', '')',
    database='miraikakaku'
)
cursor = conn.cursor()

# 統計情報を取得
cursor.execute('SELECT COUNT(*) FROM stock_master WHERE is_active = true')
active_symbols = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(DISTINCT symbol) FROM stock_prices WHERE date >= CURRENT_DATE - INTERVAL \\'7 days\\'')
symbols_with_recent_prices = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM stock_predictions WHERE created_at >= NOW() - INTERVAL \\'1 hour\\'')
recent_predictions = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(DISTINCT symbol) FROM stock_predictions WHERE prediction_date >= CURRENT_DATE')
symbols_with_predictions = cursor.fetchone()[0]

print('='*50)
print('📈 データ充足レポート')
print(f'✅ アクティブ銘柄数: {active_symbols:,}')
print(f'✅ 最近の価格データがある銘柄: {symbols_with_recent_prices:,}')
print(f'✅ 予測データがある銘柄: {symbols_with_predictions:,}')
print(f'✅ 今回生成した予測: {recent_predictions:,}')
print('='*50)

conn.close()
"

echo "🎉 データ充足バッチ完了"
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
                    "maxRunDuration": "3600s"
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

    def submit_job(self, job_name: str) -> bool:
        """ジョブを投入"""
        try:
            logger.info(f"Submitting job: {job_name}")

            job_config = self.create_comprehensive_job()

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
                logger.info(f"Job submitted successfully: {job_name}")
                return True

            finally:
                os.unlink(config_file)

        except Exception as e:
            logger.error(f"Failed to submit job {job_name}: {e}")
            return False

    def deploy_continuous_jobs(self) -> None:
        """継続的なジョブをデプロイ"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        job_name = f"continuous-data-enrichment-{timestamp}"

        if self.submit_job(job_name):
            logger.info(f"✅ Continuous data enrichment job deployed: {job_name}")
        else:
            logger.error(f"❌ Failed to deploy job: {job_name}")

def main():
    """メイン関数"""
    deployer = ContinuousDataEnrichmentJob()
    deployer.deploy_continuous_jobs()

if __name__ == "__main__":
    main()