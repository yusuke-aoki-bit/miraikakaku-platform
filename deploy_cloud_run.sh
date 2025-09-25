#!/bin/bash
#
# Cloud Run完全デプロイメントスクリプト
# GCP Batchからの移行を自動化
#

set -e

PROJECT_ID="pricewise-huqkr"
REGION="us-central1"
SERVICE_ACCOUNT="cloud-run-sa@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🚀 Cloud Runデプロイメント開始"
echo "================================"

# 1. サービスアカウント作成
echo "📌 Step 1: サービスアカウント設定"
gcloud iam service-accounts create cloud-run-sa \
    --display-name="Cloud Run Service Account" 2>/dev/null || echo "サービスアカウント既存"

# 必要な権限を付与
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/cloudsql.client" --quiet

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" --quiet

# 2. Docker イメージビルド
echo "📌 Step 2: Dockerイメージビルド"

# Data Collector
echo "🔨 Building data-collector image..."
docker build -t gcr.io/${PROJECT_ID}/data-collector:latest \
    -f Dockerfile.data-collector .

# Prediction Generator
echo "🔨 Building prediction-generator image..."
docker build -t gcr.io/${PROJECT_ID}/prediction-generator:latest \
    -f Dockerfile.prediction-generator .

# 3. イメージをGCRにプッシュ
echo "📌 Step 3: GCRへイメージプッシュ"

docker push gcr.io/${PROJECT_ID}/data-collector:latest
docker push gcr.io/${PROJECT_ID}/prediction-generator:latest

# 4. Cloud Runサービスデプロイ
echo "📌 Step 4: Cloud Runサービスデプロイ"

# Data Collector Service
echo "🚀 Deploying data-collector service..."
gcloud run deploy miraikakaku-data-collector \
    --image=gcr.io/${PROJECT_ID}/data-collector:latest \
    --platform=managed \
    --region=${REGION} \
    --memory=2Gi \
    --cpu=1 \
    --timeout=600 \
    --min-instances=0 \
    --max-instances=10 \
    --concurrency=100 \
    --service-account=${SERVICE_ACCOUNT} \
    --set-env-vars="DATABASE_HOST=34.173.9.214,DATABASE_USER=postgres,DATABASE_NAME=miraikakaku" \
    --set-secrets="DATABASE_PASSWORD=projects/${PROJECT_ID}/secrets/db-password:latest" \
    --allow-unauthenticated

# Prediction Generator Service
echo "🚀 Deploying prediction-generator service..."
gcloud run deploy miraikakaku-prediction-generator \
    --image=gcr.io/${PROJECT_ID}/prediction-generator:latest \
    --platform=managed \
    --region=${REGION} \
    --memory=4Gi \
    --cpu=2 \
    --timeout=900 \
    --min-instances=1 \
    --max-instances=5 \
    --concurrency=50 \
    --service-account=${SERVICE_ACCOUNT} \
    --set-env-vars="DATABASE_HOST=34.173.9.214,DATABASE_USER=postgres,DATABASE_NAME=miraikakaku" \
    --set-secrets="DATABASE_PASSWORD=projects/${PROJECT_ID}/secrets/db-password:latest" \
    --allow-unauthenticated

# 5. Cloud Schedulerジョブ設定
echo "📌 Step 5: Cloud Schedulerジョブ設定"

# サービスURLを取得
DATA_COLLECTOR_URL=$(gcloud run services describe miraikakaku-data-collector \
    --region=${REGION} --format="value(status.url)")
PREDICTION_GENERATOR_URL=$(gcloud run services describe miraikakaku-prediction-generator \
    --region=${REGION} --format="value(status.url)")

# Hourly Data Collection
echo "⏰ Setting up hourly data collection..."
gcloud scheduler jobs create http hourly-data-collection \
    --location=${REGION} \
    --schedule="0 * * * *" \
    --uri="${DATA_COLLECTOR_URL}/collect" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"mode":"standard","symbols_limit":500,"days_back":7}' \
    --time-zone="Asia/Tokyo" 2>/dev/null || \
    gcloud scheduler jobs update http hourly-data-collection \
        --location=${REGION} \
        --schedule="0 * * * *" \
        --uri="${DATA_COLLECTOR_URL}/collect"

# Daily Predictions
echo "⏰ Setting up daily predictions..."
gcloud scheduler jobs create http daily-predictions \
    --location=${REGION} \
    --schedule="0 6 * * *" \
    --uri="${PREDICTION_GENERATOR_URL}/predict" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"mode":"priority","prediction_days":[1,3,7,14,30]}' \
    --time-zone="Asia/Tokyo" 2>/dev/null || \
    gcloud scheduler jobs update http daily-predictions \
        --location=${REGION} \
        --schedule="0 6 * * *" \
        --uri="${PREDICTION_GENERATOR_URL}/predict"

# Priority Collection (3x daily on weekdays)
echo "⏰ Setting up priority collection..."
gcloud scheduler jobs create http priority-collection \
    --location=${REGION} \
    --schedule="0 9,15,21 * * 1-5" \
    --uri="${DATA_COLLECTOR_URL}/collect" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"mode":"priority","symbols_limit":100,"days_back":1}' \
    --time-zone="Asia/Tokyo" 2>/dev/null || \
    gcloud scheduler jobs update http priority-collection \
        --location=${REGION} \
        --schedule="0 9,15,21 * * 1-5" \
        --uri="${DATA_COLLECTOR_URL}/collect"

# Weekly Full Collection
echo "⏰ Setting up weekly full collection..."
gcloud scheduler jobs create http weekly-full-collection \
    --location=${REGION} \
    --schedule="0 2 * * 0" \
    --uri="${DATA_COLLECTOR_URL}/collect" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"mode":"full","symbols_limit":2000,"days_back":30}' \
    --time-zone="Asia/Tokyo" 2>/dev/null || \
    gcloud scheduler jobs update http weekly-full-collection \
        --location=${REGION} \
        --schedule="0 2 * * 0" \
        --uri="${DATA_COLLECTOR_URL}/collect"

# Health Check (every 15 minutes)
echo "⏰ Setting up health monitoring..."
gcloud scheduler jobs create http health-check \
    --location=${REGION} \
    --schedule="*/15 * * * *" \
    --uri="${DATA_COLLECTOR_URL}/health" \
    --http-method=GET \
    --time-zone="Asia/Tokyo" 2>/dev/null || \
    gcloud scheduler jobs update http health-check \
        --location=${REGION} \
        --schedule="*/15 * * * *" \
        --uri="${DATA_COLLECTOR_URL}/health"

# 6. アラート設定
echo "📌 Step 6: アラート設定"

# Uptime Checks
gcloud monitoring uptime-checks create data-collector-uptime \
    --display-name="Data Collector Health Check" \
    --resource-type=uptime-url \
    --monitored-resource="{'host': '${DATA_COLLECTOR_URL#https://}'}" \
    --http-check="{'path': '/health', 'port': 443, 'use_ssl': true}" \
    --period=5m 2>/dev/null || echo "Uptime check既存"

gcloud monitoring uptime-checks create prediction-generator-uptime \
    --display-name="Prediction Generator Health Check" \
    --resource-type=uptime-url \
    --monitored-resource="{'host': '${PREDICTION_GENERATOR_URL#https://}'}" \
    --http-check="{'path': '/health', 'port': 443, 'use_ssl': true}" \
    --period=5m 2>/dev/null || echo "Uptime check既存"

# 7. 最終確認
echo "📌 Step 7: デプロイメント確認"
echo "================================"

echo "✅ Data Collector URL: ${DATA_COLLECTOR_URL}"
echo "✅ Prediction Generator URL: ${PREDICTION_GENERATOR_URL}"

# サービス状態確認
echo ""
echo "📊 サービス状態:"
gcloud run services list --platform=managed --region=${REGION} \
    --filter="metadata.name:miraikakaku" --format="table(metadata.name,status.url,status.conditions[0].message)"

echo ""
echo "⏰ スケジューラジョブ:"
gcloud scheduler jobs list --location=${REGION} \
    --format="table(name,schedule,state)"

echo ""
echo "🎉 Cloud Runデプロイメント完了!"
echo "================================"
echo ""
echo "📝 次のステップ:"
echo "1. サービスURLでヘルスチェック確認"
echo "2. Cloud Schedulerジョブの手動実行でテスト"
echo "3. Cloud Monitoringでメトリクス監視"
echo "4. 古いGCP Batchジョブのクリーンアップ実行"