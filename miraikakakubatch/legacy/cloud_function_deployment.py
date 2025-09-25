#!/usr/bin/env python3
"""
Cloud Functions Deployment Strategy
ローカルコードをCloud Functionsにデプロイしてスケジューラで実行
"""

import os
import sys
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudFunctionDeployment:
    """Cloud Functions デプロイメント戦略"""

    def __init__(self, project_id="pricewise-huqkr", region="us-central1"):
        self.project_id = project_id
        self.region = region

    def create_function_directory_structure(self):
        """Cloud Functions用ディレクトリ構造作成"""

        functions_dir = "cloud_functions"

        # ディレクトリ作成
        os.makedirs(f"{functions_dir}/lstm_predictions", exist_ok=True)
        os.makedirs(f"{functions_dir}/symbol_management", exist_ok=True)
        os.makedirs(f"{functions_dir}/price_collection", exist_ok=True)

        logger.info(f"✅ Created directory structure: {functions_dir}")
        return functions_dir

    def create_lstm_prediction_function(self):
        """LSTM予測Cloud Function"""

        main_py = '''import functions_framework
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# TensorFlow設定
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    import tensorflow as tf
    from sklearn.preprocessing import MinMaxScaler
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    from google.cloud import aiplatform
    aiplatform.init(project='pricewise-huqkr', location='us-central1')
    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False

@functions_framework.http
def lstm_predictions_handler(request):
    """LSTM予測メインハンドラー"""

    try:
        # データベース接続
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', '34.173.9.214'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'os.getenv('DB_PASSWORD', '')'),
            database=os.environ.get('DB_NAME', 'miraikakaku')
        )
        cursor = conn.cursor()

        # 対象銘柄取得
        cursor.execute("""
            SELECT symbol, COUNT(*) as cnt
            FROM stock_prices
            WHERE date >= CURRENT_DATE - INTERVAL '30 days'
            AND close_price > 0
            GROUP BY symbol
            HAVING COUNT(*) >= 15
            ORDER BY COUNT(*) DESC
            LIMIT 20
        """)

        symbols = cursor.fetchall()
        total_predictions = 0

        for symbol, cnt in symbols:
            try:
                # 価格データ取得
                cursor.execute("""
                    SELECT close_price FROM stock_prices
                    WHERE symbol = %s AND date >= CURRENT_DATE - INTERVAL '30 days'
                    AND close_price > 0
                    ORDER BY date ASC
                """, (symbol,))

                prices = [float(row[0]) for row in cursor.fetchall()]

                if len(prices) >= 15:
                    predictions_made = 0

                    if TENSORFLOW_AVAILABLE:
                        # LSTM予測
                        for days in [1, 7, 30]:
                            pred_price, confidence = lstm_predict(prices, days)

                            if pred_price:
                                pred_date = datetime.now() + timedelta(days=days)

                                cursor.execute("""
                                    INSERT INTO stock_predictions
                                    (symbol, prediction_date, prediction_days, current_price,
                                     predicted_price, confidence_score, model_type, created_at)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (symbol, prediction_date, prediction_days)
                                    DO UPDATE SET predicted_price = EXCLUDED.predicted_price,
                                                 confidence_score = EXCLUDED.confidence_score,
                                                 model_type = EXCLUDED.model_type,
                                                 created_at = EXCLUDED.created_at
                                """, (
                                    symbol, pred_date.date(), days, prices[-1],
                                    pred_price, confidence,
                                    'CLOUD_FUNCTION_LSTM_VERTEXAI_V1',
                                    datetime.now()
                                ))
                                predictions_made += 1
                                total_predictions += 1
                    else:
                        # フォールバック: シンプル予測
                        for days in [1, 7, 30]:
                            avg_price = sum(prices[-5:]) / 5
                            trend = (prices[-1] - prices[-5]) / 5
                            pred_price = avg_price + (trend * days)
                            confidence = 0.6

                            pred_date = datetime.now() + timedelta(days=days)

                            cursor.execute("""
                                INSERT INTO stock_predictions
                                (symbol, prediction_date, prediction_days, current_price,
                                 predicted_price, confidence_score, model_type, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (symbol, prediction_date, prediction_days)
                                DO UPDATE SET predicted_price = EXCLUDED.predicted_price
                            """, (
                                symbol, pred_date.date(), days, prices[-1],
                                pred_price, confidence,
                                'CLOUD_FUNCTION_SIMPLE_V1',
                                datetime.now()
                            ))
                            predictions_made += 1
                            total_predictions += 1

                    if predictions_made % 10 == 0:
                        conn.commit()

            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue

        conn.commit()
        conn.close()

        return {
            'status': 'success',
            'total_predictions': total_predictions,
            'symbols_processed': len(symbols),
            'tensorflow_available': TENSORFLOW_AVAILABLE,
            'vertexai_available': VERTEXAI_AVAILABLE
        }

    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def create_lstm_model(seq_len):
    """LSTM モデル作成"""
    if not TENSORFLOW_AVAILABLE:
        return None

    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(32, return_sequences=False, input_shape=(seq_len, 1)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(16),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

def lstm_predict(prices, days_ahead=1):
    """LSTM予測実行"""
    try:
        if not TENSORFLOW_AVAILABLE or len(prices) < 10:
            return None, 0.3

        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(np.array(prices).reshape(-1, 1))

        seq_len = min(8, len(scaled) - 1)
        X, y = [], []
        for i in range(seq_len, len(scaled)):
            X.append(scaled[i-seq_len:i, 0])
            y.append(scaled[i, 0])

        if len(X) < 3:
            return None, 0.3

        X, y = np.array(X), np.array(y)
        X = X.reshape(X.shape[0], X.shape[1], 1)

        model = create_lstm_model(seq_len)
        model.fit(X, y, epochs=10, batch_size=1, verbose=0)

        last_seq = X[-1].reshape(1, seq_len, 1)
        pred = model.predict(last_seq, verbose=0)[0, 0]
        final_pred = scaler.inverse_transform([[pred]])[0, 0]

        confidence = 0.8 if VERTEXAI_AVAILABLE else 0.7
        return float(final_pred), float(confidence)

    except Exception as e:
        print(f'LSTM prediction error: {e}')
        return None, 0.4
'''

        requirements_txt = '''functions-framework==3.*
psycopg2-binary==2.9.9
numpy==1.24.4
pandas==2.1.4
scikit-learn==1.3.0
tensorflow==2.13.0
google-cloud-aiplatform==1.36.0
'''

        return main_py, requirements_txt

    def create_symbol_management_function(self):
        """銘柄管理Cloud Function"""

        main_py = '''import functions_framework
import psycopg2
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

@functions_framework.http
def symbol_management_handler(request):
    """銘柄管理メインハンドラー"""

    try:
        # データベース接続
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', '34.173.9.214'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'os.getenv('DB_PASSWORD', '')'),
            database=os.environ.get('DB_NAME', 'miraikakaku')
        )
        cursor = conn.cursor()

        # 追加する銘柄リスト
        symbols_to_add = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA',
            'BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'AVAX-USD',
            'SPY', 'QQQ', 'VTI', 'VOO'
        ]

        added_symbols = 0
        added_prices = 0

        for symbol in symbols_to_add:
            try:
                # Yahoo Finance から情報取得
                ticker = yf.Ticker(symbol)
                info = ticker.info

                company_name = info.get('longName', info.get('shortName', symbol))
                exchange = info.get('exchange', 'UNKNOWN')

                # 銘柄追加
                cursor.execute("""
                    INSERT INTO stock_master (symbol, name, company_name, exchange, is_active)
                    VALUES (%s, %s, %s, %s, true)
                    ON CONFLICT (symbol) DO UPDATE SET
                        name = EXCLUDED.name,
                        company_name = EXCLUDED.company_name,
                        exchange = EXCLUDED.exchange,
                        is_active = true,
                        updated_at = NOW()
                """, (symbol, company_name, company_name, exchange))

                added_symbols += 1

                # 価格データ取得（30日分）
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)

                hist = ticker.history(start=start_date, end=end_date)

                if not hist.empty:
                    price_count = 0
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
                                float(row['Open']) if not pd.isna(row['Open']) else None,
                                float(row['High']) if not pd.isna(row['High']) else None,
                                float(row['Low']) if not pd.isna(row['Low']) else None,
                                float(row['Close']) if not pd.isna(row['Close']) else None,
                                int(row['Volume']) if not pd.isna(row['Volume']) else 0
                            ))
                            price_count += 1
                        except Exception:
                            continue

                    added_prices += price_count

                conn.commit()

            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue

        conn.close()

        return {
            'status': 'success',
            'added_symbols': added_symbols,
            'added_prices': added_prices
        }

    except Exception as e:
        return {'status': 'error', 'message': str(e)}
'''

        requirements_txt = '''functions-framework==3.*
psycopg2-binary==2.9.9
yfinance==0.2.18
pandas==2.1.4
'''

        return main_py, requirements_txt

    def write_function_files(self, func_name: str, main_py: str, requirements_txt: str):
        """Function ファイル書き込み"""

        func_dir = f"cloud_functions/{func_name}"

        with open(f"{func_dir}/main.py", 'w') as f:
            f.write(main_py)

        with open(f"{func_dir}/requirements.txt", 'w') as f:
            f.write(requirements_txt)

        logger.info(f"✅ Created function files: {func_dir}")

    def deploy_function(self, func_name: str, entry_point: str, timeout: int = 540):
        """Cloud Function デプロイ"""

        func_dir = f"cloud_functions/{func_name}"

        try:
            cmd = [
                "gcloud", "functions", "deploy", func_name,
                "--runtime", "python311",
                "--trigger-http",
                "--allow-unauthenticated",
                "--source", func_dir,
                "--entry-point", entry_point,
                "--timeout", str(timeout),
                "--memory", "2GB",
                "--region", self.region,
                "--set-env-vars", f"DB_HOST=34.173.9.214,DB_USER=postgres,DB_PASSWORD=os.getenv('DB_PASSWORD', ''),DB_NAME=miraikakaku"
            ]

            logger.info(f"🚀 Deploying function: {func_name}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            logger.info(f"✅ Function deployed: {func_name}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Deployment failed for {func_name}: {e.stderr}")
            return False

    def create_scheduler_jobs(self):
        """Cloud Scheduler ジョブ作成"""

        schedulers = [
            {
                "name": "lstm-predictions-scheduler",
                "schedule": "0 */2 * * *",  # 2時間ごと
                "url": f"https://{self.region}-{self.project_id}.cloudfunctions.net/lstm-predictions",
                "description": "LSTM predictions every 2 hours"
            },
            {
                "name": "symbol-management-scheduler",
                "schedule": "0 6 * * *",  # 毎日6時
                "url": f"https://{self.region}-{self.project_id}.cloudfunctions.net/symbol-management",
                "description": "Symbol management daily at 6 AM"
            }
        ]

        for scheduler in schedulers:
            try:
                cmd = [
                    "gcloud", "scheduler", "jobs", "create", "http",
                    scheduler["name"],
                    "--schedule", scheduler["schedule"],
                    "--uri", scheduler["url"],
                    "--http-method", "GET",
                    "--location", self.region,
                    "--description", scheduler["description"]
                ]

                logger.info(f"📅 Creating scheduler: {scheduler['name']}")
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    logger.info(f"✅ Scheduler created: {scheduler['name']}")
                else:
                    logger.warning(f"⚠️ Scheduler may already exist: {scheduler['name']}")

            except Exception as e:
                logger.error(f"❌ Scheduler creation failed: {e}")

    def deploy_all_functions(self):
        """全Function デプロイ"""

        logger.info("🚀 Cloud Functions Deployment Strategy")
        logger.info("="*60)

        # ディレクトリ構造作成
        self.create_function_directory_structure()

        # 1. LSTM予測Function
        logger.info("📊 Step 1: LSTM Predictions Function")
        lstm_main, lstm_req = self.create_lstm_prediction_function()
        self.write_function_files("lstm_predictions", lstm_main, lstm_req)
        lstm_success = self.deploy_function("lstm-predictions", "lstm_predictions_handler", 540)

        # 2. 銘柄管理Function
        logger.info("📊 Step 2: Symbol Management Function")
        symbol_main, symbol_req = self.create_symbol_management_function()
        self.write_function_files("symbol_management", symbol_main, symbol_req)
        symbol_success = self.deploy_function("symbol-management", "symbol_management_handler", 300)

        # 3. スケジューラー作成
        if lstm_success and symbol_success:
            logger.info("📊 Step 3: Cloud Scheduler Setup")
            self.create_scheduler_jobs()

        logger.info("="*60)
        logger.info("🎉 Cloud Functions Deployment Complete")
        logger.info(f"  ✅ LSTM Predictions: {lstm_success}")
        logger.info(f"  ✅ Symbol Management: {symbol_success}")
        logger.info("📅 Scheduler:")
        logger.info("  🔮 LSTM Predictions: Every 2 hours")
        logger.info("  📈 Symbol Management: Daily at 6 AM")
        logger.info("="*60)

        return lstm_success and symbol_success

def main():
    """メイン実行"""
    deployer = CloudFunctionDeployment()
    deployer.deploy_all_functions()

if __name__ == "__main__":
    main()