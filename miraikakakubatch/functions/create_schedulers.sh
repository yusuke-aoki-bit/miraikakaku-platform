#!/bin/bash
# Cloud Schedulerジョブを作成するスクリプト

PROJECT_ID="pricewise-huqkr"
LOCATION="us-central1"
SERVICE_ACCOUNT="miraikakaku-scheduler@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🔧 Cloud Schedulerジョブを設定中..."

# 1. 毎時0分 - メインデータ収集
gcloud scheduler jobs create http miraikakaku-hourly-main \
    --location="${LOCATION}" \
    --schedule="0 * * * *" \
    --time-zone="Asia/Tokyo" \
    --uri="https://batch.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/jobs" \
    --http-method="POST" \
    --headers="Content-Type=application/json" \
    --message-body='{
        "taskGroups": [{
            "taskSpec": {
                "runnables": [{
                    "container": {
                        "imageUri": "us-central1-docker.pkg.dev/pricewise-huqkr/miraikakaku-docker/batch-datareader:latest",
                        "entrypoint": "/bin/bash",
                        "commands": ["-c", "python3 /app/real_data_only_collector.py"]
                    }
                }],
                "computeResource": {
                    "cpuMilli": "4000",
                    "memoryMib": "8192"
                },
                "maxRetryCount": 1,
                "maxRunDuration": "3600s",
                "environment": {
                    "variables": {
                        "DB_HOST": "34.58.103.36",
                        "DB_USER": "miraikakaku-user",
                        "DB_PASSWORD": "miraikakaku-secure-pass-2024",
                        "DB_NAME": "miraikakaku",
                        "BATCH_MODE": "hourly_scheduled"
                    }
                }
            },
            "taskCount": "5",
            "parallelism": "3"
        }],
        "allocationPolicy": {
            "instances": [{
                "policy": {
                    "machineType": "e2-standard-4",
                    "provisioningModel": "STANDARD"
                }
            }],
            "location": {
                "allowedLocations": ["regions/us-central1"]
            }
        },
        "logsPolicy": {
            "destination": "CLOUD_LOGGING"
        },
        "labels": {
            "app": "miraikakaku",
            "type": "scheduled-hourly",
            "environment": "production"
        }
    }' \
    --oauth-service-account-email="${SERVICE_ACCOUNT}" \
    --description="毎時0分に実データ収集を実行" \
    --attempt-deadline="30m" \
    --max-retry-attempts=3 \
    --min-backoff="30s" \
    --max-backoff="10m" \
    || echo "ジョブが既に存在するか、作成に失敗しました"

echo "✅ メインデータ収集スケジューラー設定完了"

# 2. 毎時30分 - 追加データ収集
gcloud scheduler jobs create http miraikakaku-hourly-update \
    --location="${LOCATION}" \
    --schedule="30 * * * *" \
    --time-zone="Asia/Tokyo" \
    --uri="https://batch.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/jobs" \
    --http-method="POST" \
    --headers="Content-Type=application/json" \
    --message-body='{
        "taskGroups": [{
            "taskSpec": {
                "runnables": [{
                    "container": {
                        "imageUri": "us-central1-docker.pkg.dev/pricewise-huqkr/miraikakaku-docker/batch-datareader:latest",
                        "entrypoint": "/bin/bash",
                        "commands": ["-c", "python3 /app/datareader_collector.py"]
                    }
                }],
                "computeResource": {
                    "cpuMilli": "4000",
                    "memoryMib": "8192"
                },
                "maxRetryCount": 1,
                "maxRunDuration": "3600s",
                "environment": {
                    "variables": {
                        "DB_HOST": "34.58.103.36",
                        "DB_USER": "miraikakaku-user",
                        "DB_PASSWORD": "miraikakaku-secure-pass-2024",
                        "DB_NAME": "miraikakaku",
                        "BATCH_MODE": "hourly_update"
                    }
                }
            },
            "taskCount": "3",
            "parallelism": "2"
        }],
        "allocationPolicy": {
            "instances": [{
                "policy": {
                    "machineType": "e2-standard-4",
                    "provisioningModel": "STANDARD"
                }
            }],
            "location": {
                "allowedLocations": ["regions/us-central1"]
            }
        },
        "logsPolicy": {
            "destination": "CLOUD_LOGGING"
        },
        "labels": {
            "app": "miraikakaku",
            "type": "scheduled-update",
            "environment": "production"
        }
    }' \
    --oauth-service-account-email="${SERVICE_ACCOUNT}" \
    --description="毎時30分にデータ更新を実行" \
    --attempt-deadline="30m" \
    --max-retry-attempts=3 \
    --min-backoff="30s" \
    --max-backoff="10m" \
    || echo "ジョブが既に存在するか、作成に失敗しました"

echo "✅ データ更新スケジューラー設定完了"

# 3. 毎時15分 - テーブル構造チェック・作成
gcloud scheduler jobs create http miraikakaku-hourly-schema \
    --location="${LOCATION}" \
    --schedule="15 * * * *" \
    --time-zone="Asia/Tokyo" \
    --uri="https://batch.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/jobs" \
    --http-method="POST" \
    --headers="Content-Type=application/json" \
    --message-body='{
        "taskGroups": [{
            "taskSpec": {
                "runnables": [{
                    "container": {
                        "imageUri": "us-central1-docker.pkg.dev/pricewise-huqkr/miraikakaku-docker/batch-stable:latest",
                        "entrypoint": "/bin/bash",
                        "commands": ["-c", "python3 -c \"import pymysql; db_config = {'\''host'\'': '\''34.58.103.36'\'', '\''user'\'': '\''miraikakaku-user'\'', '\''password'\'': '\''miraikakaku-secure-pass-2024'\'', '\''database'\'': '\''miraikakaku'\'', '\''charset'\'': '\''utf8mb4'\''}; connection = pymysql.connect(**db_config); cursor = connection.cursor(); cursor.execute('\''CREATE TABLE IF NOT EXISTS stock_predictions (id BIGINT AUTO_INCREMENT PRIMARY KEY, symbol VARCHAR(20) NOT NULL, prediction_date DATE NOT NULL, target_date DATE NOT NULL, prediction_horizon_days INT NOT NULL, predicted_open DECIMAL(10,3), predicted_high DECIMAL(10,3), predicted_low DECIMAL(10,3), predicted_close DECIMAL(10,3), predicted_volume BIGINT, actual_open DECIMAL(10,3), actual_high DECIMAL(10,3), actual_low DECIMAL(10,3), actual_close DECIMAL(10,3), actual_volume BIGINT, accuracy_score DECIMAL(5,4), mse_score DECIMAL(10,6), mae_score DECIMAL(10,6), direction_accuracy DECIMAL(5,4), model_name VARCHAR(50) NOT NULL, model_version VARCHAR(20), confidence_score DECIMAL(5,4), features_used TEXT, training_data_start DATE, training_data_end DATE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, INDEX idx_symbol_date (symbol, prediction_date), INDEX idx_target_date (target_date), INDEX idx_model (model_name, model_version), INDEX idx_accuracy (accuracy_score), UNIQUE KEY unique_prediction (symbol, prediction_date, target_date, model_name)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci'\''); cursor.execute('\''CREATE OR REPLACE VIEW prediction_accuracy_summary AS SELECT model_name, model_version, COUNT(*) as total_predictions, AVG(accuracy_score) as avg_accuracy, AVG(direction_accuracy) as avg_direction_accuracy, AVG(confidence_score) as avg_confidence, MIN(prediction_date) as first_prediction, MAX(prediction_date) as last_prediction FROM stock_predictions WHERE accuracy_score IS NOT NULL GROUP BY model_name, model_version ORDER BY avg_accuracy DESC'\''); connection.commit(); print('\''✅ テーブル・ビュー確認完了'\''); connection.close()\""]
                    }
                }],
                "computeResource": {
                    "cpuMilli": "1000",
                    "memoryMib": "2048"
                },
                "maxRetryCount": 2,
                "maxRunDuration": "600s",
                "environment": {
                    "variables": {
                        "DB_HOST": "34.58.103.36",
                        "DB_USER": "miraikakaku-user",
                        "DB_PASSWORD": "miraikakaku-secure-pass-2024",
                        "DB_NAME": "miraikakaku",
                        "BATCH_MODE": "schema_maintenance"
                    }
                }
            },
            "taskCount": "1",
            "parallelism": "1"
        }],
        "allocationPolicy": {
            "instances": [{
                "policy": {
                    "machineType": "e2-standard-2",
                    "provisioningModel": "STANDARD"
                }
            }],
            "location": {
                "allowedLocations": ["regions/us-central1"]
            }
        },
        "logsPolicy": {
            "destination": "CLOUD_LOGGING"
        },
        "labels": {
            "app": "miraikakaku",
            "type": "scheduled-schema",
            "environment": "production"
        }
    }' \
    --oauth-service-account-email="${SERVICE_ACCOUNT}" \
    --description="毎時15分にテーブル構造チェック・作成を実行" \
    --attempt-deadline="10m" \
    --max-retry-attempts=2 \
    --min-backoff="30s" \
    --max-backoff="5m" \
    || echo "ジョブが既に存在するか、作成に失敗しました"

echo "✅ テーブル構造管理スケジューラー設定完了"

# スケジューラーの状態を確認
echo ""
echo "📊 設定されたスケジューラー:"
gcloud scheduler jobs list --location="${LOCATION}" --filter="name:miraikakaku-hourly"

echo ""
echo "🎯 完了！1時間ごとの自動実行が設定されました。"
echo "   - 毎時0分: メインデータ収集（5並列タスク）"
echo "   - 毎時15分: テーブル構造チェック・作成（1タスク）"
echo "   - 毎時30分: データ更新（3並列タスク）"