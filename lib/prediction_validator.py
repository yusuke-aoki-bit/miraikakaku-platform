#!/usr/bin/env python3
"""
Prediction Consistency Validation System
予測整合性検証システム
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

class PredictionValidator:
    """予測整合性検証システム"""

    def __init__(self, project_id="pricewise-huqkr", location="us-central1"):
        self.project_id = project_id
        self.location = location

    def create_validation_job(self) -> Dict[str, Any]:
        """予測整合性検証ジョブを作成"""

        script = """#!/bin/bash
set -e

echo "🔍 予測整合性検証システム"
echo "開始時刻: $(date)"
echo "================================"

# パッケージインストール
echo "📦 パッケージのインストール中..."
pip install -q psycopg2-binary>=2.9.9 pandas>=2.1.0 numpy>=1.24.0 scikit-learn>=1.3.0

# 予測整合性検証の実行
echo "🔬 予測整合性検証中..."
python3 -c "
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.metrics import mean_absolute_error, mean_squared_error

def validate_prediction_consistency():
    '''予測整合性の検証'''
    conn = psycopg2.connect(
        host='34.173.9.214',
        user='postgres',
        password='os.getenv('DB_PASSWORD', '')',
        database='miraikakaku'
    )
    cursor = conn.cursor()

    print('🔍 予測整合性検証開始')

    # 1. 過去予測の精度評価
    cursor.execute('''
        SELECT
            symbol,
            model_type,
            prediction_days,
            predicted_price,
            actual_price,
            confidence_score,
            created_at
        FROM stock_predictions
        WHERE actual_price IS NOT NULL
        AND predicted_price IS NOT NULL
        AND model_type LIKE '%HISTORICAL%'
        ORDER BY symbol, prediction_days, created_at DESC
    ''')

    historical_data = cursor.fetchall()

    if historical_data:
        print(f'📊 過去予測データ: {len(historical_data)}件')

        # シンボル別・期間別精度分析
        symbol_accuracy = {}
        period_accuracy = {}

        for row in historical_data:
            symbol, model_type, pred_days, pred_price, actual_price, confidence, created_at = row

            if actual_price > 0:  # 有効な実価格のみ
                error_rate = abs(pred_price - actual_price) / actual_price * 100

                # シンボル別統計
                if symbol not in symbol_accuracy:
                    symbol_accuracy[symbol] = []
                symbol_accuracy[symbol].append(error_rate)

                # 期間別統計
                if pred_days not in period_accuracy:
                    period_accuracy[pred_days] = []
                period_accuracy[pred_days].append(error_rate)

        # 結果出力
        print('='*50)
        print('📈 シンボル別予測精度 (上位10)')
        symbol_avg = {k: np.mean(v) for k, v in symbol_accuracy.items() if len(v) >= 3}
        for symbol, avg_error in sorted(symbol_avg.items(), key=lambda x: x[1])[:10]:
            count = len(symbol_accuracy[symbol])
            print(f'  {symbol}: {avg_error:.2f}% (n={count})')

        print('\\n📅 期間別予測精度')
        for days, errors in sorted(period_accuracy.items()):
            avg_error = np.mean(errors)
            print(f'  {days}日先: {avg_error:.2f}% (n={len(errors)})')

    # 2. 未来予測の一貫性チェック
    print('\\n🔮 未来予測の一貫性チェック')
    cursor.execute('''
        SELECT
            symbol,
            prediction_days,
            predicted_price,
            confidence_score,
            model_type,
            created_at
        FROM stock_predictions
        WHERE prediction_date >= CURRENT_DATE
        AND model_type LIKE '%LSTM%'
        ORDER BY symbol, prediction_days, created_at DESC
    ''')

    future_data = cursor.fetchall()

    if future_data:
        print(f'📊 未来予測データ: {len(future_data)}件')

        # シンボル別の予測トレンド分析
        symbol_trends = {}
        for row in future_data:
            symbol, pred_days, pred_price, confidence, model_type, created_at = row

            if symbol not in symbol_trends:
                symbol_trends[symbol] = {}
            if pred_days not in symbol_trends[symbol]:
                symbol_trends[symbol][pred_days] = []

            symbol_trends[symbol][pred_days].append({
                'price': pred_price,
                'confidence': confidence,
                'created_at': created_at
            })

        # 一貫性スコアの計算
        consistency_scores = {}
        for symbol, periods in symbol_trends.items():
            if len(periods) >= 3:  # 複数期間の予測がある場合
                prices = []
                for days in sorted(periods.keys()):
                    if periods[days]:
                        latest_pred = sorted(periods[days], key=lambda x: x['created_at'])[-1]
                        prices.append(latest_pred['price'])

                if len(prices) >= 3:
                    # 価格変動の一貫性（単調性や変動幅の合理性）
                    price_changes = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
                    volatility = np.std(price_changes) / np.mean(prices) * 100
                    consistency_scores[symbol] = volatility

        print('\\n📊 予測一貫性スコア (低いほど一貫性が高い)')
        for symbol, score in sorted(consistency_scores.items(), key=lambda x: x[1])[:10]:
            print(f'  {symbol}: {score:.2f}%')

    # 3. モデル性能比較
    print('\\n🤖 モデル性能比較')
    cursor.execute('''
        SELECT
            model_type,
            COUNT(*) as prediction_count,
            AVG(confidence_score) as avg_confidence,
            AVG(CASE
                WHEN actual_price IS NOT NULL AND actual_price > 0
                THEN ABS(predicted_price - actual_price) / actual_price * 100
                ELSE NULL
            END) as avg_error_rate
        FROM stock_predictions
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY model_type
        HAVING COUNT(*) >= 10
        ORDER BY avg_error_rate ASC NULLS LAST
    ''')

    model_performance = cursor.fetchall()
    for row in model_performance:
        model_type, count, avg_conf, avg_error = row
        error_str = f'{avg_error:.2f}%' if avg_error else 'N/A'
        print(f'  {model_type}: 予測数={count}, 平均信頼度={avg_conf:.3f}, 平均誤差={error_str}')

    # 4. 予測品質スコアの更新
    print('\\n🎯 予測品質スコア更新中...')
    quality_updates = 0

    for symbol, accuracy_list in symbol_accuracy.items():
        if len(accuracy_list) >= 3:
            avg_accuracy = np.mean(accuracy_list)
            quality_score = max(0, min(1, (20 - avg_accuracy) / 20))  # 20%誤差で0, 0%誤差で1

            cursor.execute('''
                UPDATE stock_predictions
                SET accuracy_score = %s, is_validated = true, updated_at = NOW()
                WHERE symbol = %s
                AND prediction_date >= CURRENT_DATE
                AND accuracy_score IS NULL
            ''', (quality_score, symbol))

            quality_updates += cursor.rowcount

    conn.commit()
    print(f'✅ {quality_updates}件の予測品質スコアを更新')

    # 5. 異常予測の検出とフラグ設定
    print('\\n⚠️  異常予測の検出中...')
    cursor.execute('''
        UPDATE stock_predictions
        SET is_active = false, notes = 'Flagged as outlier - extreme price change'
        WHERE prediction_date >= CURRENT_DATE
        AND (
            predicted_price / current_price > 2.0  -- 2倍以上の上昇
            OR predicted_price / current_price < 0.5  -- 50%以上の下落
            OR confidence_score < 0.2  -- 信頼度が極めて低い
        )
        AND is_active = true
    ''')

    outlier_count = cursor.rowcount
    conn.commit()
    print(f'🚫 {outlier_count}件の異常予測をフラグ設定')

    print('='*50)
    print('✅ 予測整合性検証完了')
    print('='*50)

    conn.close()

validate_prediction_consistency()
"

echo "🎉 予測整合性検証完了"
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

    def submit_validation_job(self, job_name: str) -> bool:
        """検証ジョブを投入"""
        try:
            logger.info(f"Submitting validation job: {job_name}")

            job_config = self.create_validation_job()

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
                logger.info(f"Validation job submitted successfully: {job_name}")
                return True

            finally:
                os.unlink(config_file)

        except Exception as e:
            logger.error(f"Failed to submit validation job {job_name}: {e}")
            return False

    def deploy_validation_job(self) -> None:
        """検証ジョブをデプロイ"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        job_name = f"prediction-validation-{timestamp}"

        if self.submit_validation_job(job_name):
            logger.info(f"✅ Prediction validation job deployed: {job_name}")
        else:
            logger.error(f"❌ Failed to deploy validation job: {job_name}")

def main():
    """メイン関数"""
    validator = PredictionValidator()
    validator.deploy_validation_job()

if __name__ == "__main__":
    main()