#!/bin/bash

set -e

echo "🚀 Miraikakaku GCP デプロイスクリプト"
echo "プロジェクト: pricewise-huqkr"
echo "=================================="

# 環境変数チェック
if [ ! -f ".env" ]; then
    echo "❌ .env ファイルが見つかりません"
    exit 1
fi

source .env

echo "📦 Docker イメージをビルド中..."

# API イメージビルド
echo "  - API イメージビルド"
docker build -t gcr.io/pricewise-huqkr/miraikakaku-api:latest ./miraikakakuapi

# Frontend イメージビルド
echo "  - Frontend イメージビルド"
docker build -t gcr.io/pricewise-huqkr/miraikakaku-frontend:latest ./miraikakakufront

# Batch イメージビルド
echo "  - Batch イメージビルド"
docker build -t gcr.io/pricewise-huqkr/miraikakaku-batch:latest ./miraikakakubatch

echo "🔄 Docker イメージを Container Registry にプッシュ中..."

# Container Registry にプッシュ
docker push gcr.io/pricewise-huqkr/miraikakaku-api:latest
docker push gcr.io/pricewise-huqkr/miraikakaku-frontend:latest
docker push gcr.io/pricewise-huqkr/miraikakaku-batch:latest

echo "☁️  Cloud Run サービスにデプロイ中..."

# API サービスをデプロイ
echo "  - API サービスデプロイ"
gcloud run deploy miraikakaku-api \
    --image gcr.io/pricewise-huqkr/miraikakaku-api:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --set-env-vars="DATABASE_URL=${DATABASE_URL},JWT_SECRET_KEY=${JWT_SECRET_KEY},VERTEX_AI_PROJECT_ID=${VERTEX_AI_PROJECT_ID},GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-service-account.json" \
    --service-account miraikakaku-service@pricewise-huqkr.iam.gserviceaccount.com

# Frontend サービスをデプロイ
echo "  - Frontend サービスデプロイ"
API_URL=$(gcloud run services describe miraikakaku-api --region=us-central1 --format="value(status.url)")

gcloud run deploy miraikakaku-frontend \
    --image gcr.io/pricewise-huqkr/miraikakaku-frontend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 5 \
    --set-env-vars="NEXT_PUBLIC_API_BASE_URL=${API_URL},NEXT_PUBLIC_WS_URL=${API_URL/https/wss}/ws"

echo "🔄 Cloud Functions バッチ処理をデプロイ中..."

# バッチ処理を Cloud Functions にデプロイ
gcloud functions deploy miraikakaku-batch \
    --gen2 \
    --runtime python311 \
    --region us-central1 \
    --source ./miraikakakubatch/functions \
    --entry-point main \
    --trigger-http \
    --memory 2Gi \
    --timeout 540s \
    --set-env-vars="DATABASE_URL=${DATABASE_URL},VERTEX_AI_PROJECT_ID=${VERTEX_AI_PROJECT_ID}" \
    --service-account miraikakaku-service@pricewise-huqkr.iam.gserviceaccount.com

echo "✅ デプロイ完了!"
echo ""
echo "🌐 サービス URL:"
echo "  - Frontend: $(gcloud run services describe miraikakaku-frontend --region=us-central1 --format="value(status.url)")"
echo "  - API: $(gcloud run services describe miraikakaku-api --region=us-central1 --format="value(status.url)")"
echo "  - Functions: https://us-central1-pricewise-huqkr.cloudfunctions.net/miraikakaku-batch"
echo ""
echo "📊 監視:"
echo "  - Cloud Console: https://console.cloud.google.com/home/dashboard?project=pricewise-huqkr"
echo "  - Cloud Run: https://console.cloud.google.com/run?project=pricewise-huqkr"