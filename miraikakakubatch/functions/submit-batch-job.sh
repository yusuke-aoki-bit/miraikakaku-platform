#!/bin/bash

# Google Cloud Batch設定
PROJECT_ID="pricewise-huqkr"
LOCATION="us-central1"
JOB_NAME="miraikakaku-data-collection-$(date +%Y%m%d-%H%M%S)"

echo "🚀 Google Cloud Batchジョブを投入します..."
echo "📊 プロジェクト: $PROJECT_ID"
echo "📍 ロケーション: $LOCATION"
echo "🏷️  ジョブ名: $JOB_NAME"

# バッチジョブの投入
gcloud batch jobs submit $JOB_NAME \
  --project=$PROJECT_ID \
  --location=$LOCATION \
  --config=batch-job-config.yaml

if [ $? -eq 0 ]; then
  echo "✅ バッチジョブが正常に投入されました"
  echo "📊 ジョブ状況確認:"
  echo "  gcloud batch jobs describe $JOB_NAME --location=$LOCATION"
  echo "📋 ログ確認:"
  echo "  gcloud batch jobs logs $JOB_NAME --location=$LOCATION"
else
  echo "❌ バッチジョブの投入に失敗しました"
  exit 1
fi