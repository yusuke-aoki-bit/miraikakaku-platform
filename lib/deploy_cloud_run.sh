#!/bin/bash

# Cloud Run デプロイスクリプト
# Deploy API and Frontend to Cloud Run

PROJECT_ID="miraikakaku-project"
REGION="asia-northeast1"
ARTIFACT_REGISTRY="asia-northeast1-docker.pkg.dev/$PROJECT_ID/miraikakaku"

echo "🚀 Deploying to Cloud Run"
echo "========================="

# Artifact Registry作成（初回のみ）
echo "📦 Setting up Artifact Registry..."
gcloud artifacts repositories create miraikakaku \
    --repository-format=docker \
    --location=$REGION \
    --description="Miraikakaku Docker images" \
    --project=$PROJECT_ID || true

# Docker認証設定
gcloud auth configure-docker $REGION-docker.pkg.dev

# 1. API デプロイ
echo "🔧 Building and deploying API..."
cd miraikakakuapi

# Dockerイメージビルド
docker build -t $ARTIFACT_REGISTRY/api:latest -f Dockerfile.cloudrun .
docker push $ARTIFACT_REGISTRY/api:latest

# Cloud Runデプロイ
gcloud run deploy api-miraikakaku \
    --image=$ARTIFACT_REGISTRY/api:latest \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=1Gi \
    --cpu=2 \
    --timeout=60s \
    --concurrency=100 \
    --max-instances=10 \
    --set-env-vars="DB_HOST=34.173.9.214,DB_USER=postgres,DB_NAME=miraikakaku" \
    --set-secrets="DB_PASSWORD=miraikakaku-db-password:latest" \
    --project=$PROJECT_ID

# APIのURLを取得
API_URL=$(gcloud run services describe api-miraikakaku \
    --platform=managed \
    --region=$REGION \
    --format="value(status.url)" \
    --project=$PROJECT_ID)

echo "✅ API deployed at: $API_URL"

# 2. Frontend デプロイ
echo "🎨 Building and deploying Frontend..."
cd ../miraikakakufront

# 環境変数設定
echo "NEXT_PUBLIC_API_URL=$API_URL" > .env.production

# Dockerイメージビルド
docker build -t $ARTIFACT_REGISTRY/frontend:latest -f Dockerfile.cloudrun .
docker push $ARTIFACT_REGISTRY/frontend:latest

# Cloud Runデプロイ
gcloud run deploy frontend-miraikakaku \
    --image=$ARTIFACT_REGISTRY/frontend:latest \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1 \
    --timeout=60s \
    --concurrency=100 \
    --max-instances=10 \
    --set-env-vars="NEXT_PUBLIC_API_URL=$API_URL" \
    --project=$PROJECT_ID

# FrontendのURLを取得
FRONTEND_URL=$(gcloud run services describe frontend-miraikakaku \
    --platform=managed \
    --region=$REGION \
    --format="value(status.url)" \
    --project=$PROJECT_ID)

echo "✅ Frontend deployed at: $FRONTEND_URL"

# 3. Traffic Management設定（オプション）
echo "🔄 Setting up traffic management..."

# カスタムドメインマッピング（ドメインがある場合）
# gcloud run domain-mappings create \
#     --service=frontend-miraikakaku \
#     --domain=miraikakaku.com \
#     --region=$REGION \
#     --project=$PROJECT_ID

cd ..

echo ""
echo "======================================"
echo "✅ Cloud Run Deployment Complete!"
echo "======================================"
echo ""
echo "📊 Service URLs:"
echo "   API: $API_URL"
echo "   Frontend: $FRONTEND_URL"
echo ""
echo "📈 Monitoring:"
echo "   https://console.cloud.google.com/run?project=$PROJECT_ID"
echo ""
echo "💡 Next Steps:"
echo "   1. Configure custom domain (optional)"
echo "   2. Set up Cloud CDN for better performance"
echo "   3. Enable Cloud Armor for DDoS protection"