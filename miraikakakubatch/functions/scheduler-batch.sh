#!/bin/bash
set -e

PROJECT_ID="miraikakaku-430816"
REGION="us-central1"
JOB_NAME="miraikakaku-scheduled-$(date +%Y%m%d-%H%M%S)"

echo "📅 スケジュール実行バッチジョブ開始"
echo "📋 プロジェクト: $PROJECT_ID"
echo "🌍 リージョン: $REGION"
echo "🏷️ ジョブ名: $JOB_NAME"

# バッチジョブ送信
gcloud batch jobs submit $JOB_NAME \
    --location=$REGION \
    --config=gcloud-stable-batch.yaml

if [ $? -eq 0 ]; then
    echo "✅ スケジュールバッチジョブ送信成功: $JOB_NAME"
else
    echo "❌ スケジュールバッチジョブ送信失敗"
    exit 1
fi

echo "🎯 スケジュール実行完了"