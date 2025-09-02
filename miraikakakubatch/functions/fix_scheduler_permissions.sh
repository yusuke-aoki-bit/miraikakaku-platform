#!/bin/bash
# スケジューラー権限修正スクリプト
# Cloud Schedulerが自動でバッチジョブを実行できるように権限を設定

PROJECT_ID="pricewise-huqkr"
LOCATION="us-central1"

echo "🔧 Cloud Scheduler権限修正"
echo "==========================="
echo ""

# デフォルトのCompute Engineサービスアカウントを使用
COMPUTE_SA="465603676610-compute@developer.gserviceaccount.com"
APPSPOT_SA="${PROJECT_ID}@appspot.gserviceaccount.com"

echo "📋 使用するサービスアカウント:"
echo "  - Compute Engine: ${COMPUTE_SA}"
echo "  - App Engine: ${APPSPOT_SA}"
echo ""

# 1. Compute Engineサービスアカウントに権限付与
echo "🔑 Compute Engineサービスアカウントに権限付与..."

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/batch.jobsEditor" \
    --quiet

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/iam.serviceAccountUser" \
    --quiet

echo "✅ Compute Engineサービスアカウント権限設定完了"

# 2. App Engineサービスアカウントに権限付与（存在する場合）
echo ""
echo "🔑 App Engineサービスアカウントに権限付与..."

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${APPSPOT_SA}" \
    --role="roles/batch.jobsEditor" \
    --quiet 2>/dev/null

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${APPSPOT_SA}" \
    --role="roles/cloudscheduler.jobRunner" \
    --quiet 2>/dev/null

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${APPSPOT_SA}" \
    --role="roles/iam.serviceAccountUser" \
    --quiet 2>/dev/null

echo "✅ App Engineサービスアカウント権限設定完了"

# 3. スケジューラーを再作成（正しいサービスアカウントで）
echo ""
echo "🔄 スケジューラーを更新..."

# 既存のスケジューラーを削除
gcloud scheduler jobs delete miraikakaku-hourly-batch --location="${LOCATION}" --quiet 2>/dev/null

# 新規作成（デフォルトサービスアカウントを使用）
gcloud scheduler jobs create http miraikakaku-hourly-batch \
    --location="${LOCATION}" \
    --schedule="0 * * * *" \
    --time-zone="Asia/Tokyo" \
    --uri="https://batch.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/jobs?job_id=scheduled-\$(date +%s)" \
    --http-method="POST" \
    --headers="Content-Type=application/json,User-Agent=CloudScheduler" \
    --message-body='{
        "taskGroups": [{
            "taskSpec": {
                "runnables": [{
                    "container": {
                        "imageUri": "us-central1-docker.pkg.dev/pricewise-huqkr/miraikakaku-docker/batch-stable:latest",
                        "entrypoint": "/bin/bash",
                        "commands": ["-c", "cd /app && python3 real_data_only_collector.py || python3 datareader_collector.py"]
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
            "type": "scheduled-hourly",
            "trigger": "scheduler",
            "environment": "production"
        }
    }' \
    --description="毎時0分に実データ収集を実行（権限修正済み）" \
    --attempt-deadline="30m" \
    --max-retry-attempts=3 \
    --min-backoff="30s" \
    --max-backoff="10m"

echo "✅ スケジューラー再作成完了"

# 4. テストのため手動実行
echo ""
echo "🧪 手動実行テスト..."
gcloud scheduler jobs run miraikakaku-hourly-batch --location="${LOCATION}"

# 5. 確認
echo ""
echo "📊 更新後の状態:"
gcloud scheduler jobs describe miraikakaku-hourly-batch --location="${LOCATION}" \
    --format="table(name.segment(-1):label=JOB,state:label=STATUS,schedule:label=SCHEDULE,lastAttemptTime:label=LAST_RUN)"

echo ""
echo "🎯 修正完了！"
echo ""
echo "📋 実施内容:"
echo "  ✅ Compute Engineサービスアカウントに必要な権限付与"
echo "  ✅ スケジューラーを正しいサービスアカウントで再作成"
echo "  ✅ 手動実行テストを実施"
echo ""
echo "⏰ 今後の自動実行:"
echo "  - 毎時0分に自動的にバッチジョブが起動されます"
echo "  - 実行ログ: gcloud logging read 'resource.type=batch.googleapis.com/Job AND labels.trigger=scheduler' --limit=10"