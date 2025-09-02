#!/bin/bash

# Configuration
PROJECT_ID="pricewise-huqkr"
LOCATION="us-central1" 
IMAGE_NAME="gcr.io/$PROJECT_ID/miraikakaku-batch:latest"
JOB_NAME="miraikakaku-data-collection-$(date +%Y%m%d-%H%M%S)"

echo "🚀 Google Cloud Batchコンテナベースジョブを準備中..."

# 1. Docker image build and push
echo "📦 Dockerイメージをビルド中..."
docker build -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    echo "✅ Dockerイメージビルド完了"
    echo "📤 Google Container Registryにプッシュ中..."
    docker push $IMAGE_NAME
    
    if [ $? -eq 0 ]; then
        echo "✅ イメージプッシュ完了"
    else
        echo "❌ イメージプッシュに失敗しました"
        exit 1
    fi
else
    echo "❌ Dockerイメージビルドに失敗しました"
    exit 1
fi

# 2. Submit batch job
echo "🚀 Google Cloud Batchジョブを投入中..."
echo "📊 プロジェクト: $PROJECT_ID"
echo "📍 ロケーション: $LOCATION"  
echo "🏷️  ジョブ名: $JOB_NAME"
echo "🐳 イメージ: $IMAGE_NAME"

gcloud batch jobs submit $JOB_NAME \
  --project=$PROJECT_ID \
  --location=$LOCATION \
  --config=batch-job-container-config.yaml

if [ $? -eq 0 ]; then
  echo "✅ バッチジョブが正常に投入されました"
  echo ""
  echo "📊 ジョブ状況確認コマンド:"
  echo "  gcloud batch jobs describe $JOB_NAME --location=$LOCATION --project=$PROJECT_ID"
  echo ""
  echo "📋 ログ確認コマンド:"
  echo "  gcloud logging read \"resource.type=gce_instance AND labels.job_name=$JOB_NAME\" --project=$PROJECT_ID"
  echo ""
  echo "🔍 ジョブ一覧確認:"
  echo "  gcloud batch jobs list --location=$LOCATION --project=$PROJECT_ID"
else
  echo "❌ バッチジョブの投入に失敗しました"
  exit 1
fi