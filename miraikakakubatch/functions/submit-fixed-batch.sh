#!/bin/bash
set -e

PROJECT_ID="miraikakaku-430816"
REGION="us-central1"
JOB_NAME="miraikakaku-fixed-$(date +%Y%m%d-%H%M%S)"

echo "🚀 固定バッチジョブ送信開始"
echo "📋 プロジェクト: $PROJECT_ID"
echo "🌍 リージョン: $REGION"
echo "🏷️ ジョブ名: $JOB_NAME"

# 1. Dockerfile.fixedをビルド
echo "🔨 固定コンテナイメージビルド開始"
cp Dockerfile.fixed Dockerfile
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/miraikakaku-docker/batch-fixed:latest \
    . \
    --timeout=20m \
    --machine-type=e2-highcpu-8

if [ $? -eq 0 ]; then
    echo "✅ コンテナイメージビルド成功"
else
    echo "❌ コンテナイメージビルド失敗"
    exit 1
fi

# 2. バッチ設定（Artifact Registry使用）
echo "📝 バッチ設定確認"
cp improved-batch-config.yaml temp-batch-config.yaml

# 3. バッチジョブ送信
echo "🚁 バッチジョブ送信"
gcloud batch jobs submit $JOB_NAME \
    --location=$REGION \
    --config=temp-batch-config.yaml

if [ $? -eq 0 ]; then
    echo "✅ バッチジョブ送信成功: $JOB_NAME"
    echo "🔍 ジョブ確認コマンド:"
    echo "   gcloud batch jobs describe $JOB_NAME --location=$REGION"
    echo "   gcloud logging read \"resource.type=batch_task AND labels.job_id=\\\"$JOB_NAME\\\"\" --limit=50 --format=\"value(timestamp,severity,textPayload)\""
else
    echo "❌ バッチジョブ送信失敗"
    exit 1
fi

# 4. 一時ファイル削除
rm -f temp-batch-config.yaml

echo "🎯 固定バッチジョブ送信完了"