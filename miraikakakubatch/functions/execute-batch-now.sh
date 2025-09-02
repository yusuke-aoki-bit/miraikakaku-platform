#!/bin/bash
# Google Cloud Batchジョブ即座実行スクリプト

set -e

echo "🚀 訓練データ生成バッチジョブ実行開始: $(date)"

# プロジェクト設定確認
echo "📋 プロジェクト設定確認..."
gcloud config get-value project

# Batchジョブ実行
echo "🔥 バッチジョブ投入中..."
JOB_NAME="training-data-batch-$(date +%Y%m%d-%H%M%S)"

gcloud batch jobs submit $JOB_NAME \
  --config=gcloud-batch-job.yaml \
  --location=us-central1

echo "✅ バッチジョブ投入完了: $JOB_NAME"
echo "📊 ジョブ状況確認..."

# 実行状況監視
gcloud batch jobs list --location=us-central1 --limit=5

echo "🔗 ジョブ詳細確認コマンド:"
echo "gcloud batch jobs describe $JOB_NAME --location=us-central1"

echo "📈 ログ確認コマンド:"
echo "gcloud logging read \"resource.type=batch_job AND resource.labels.job_uid=$(gcloud batch jobs describe $JOB_NAME --location=us-central1 --format='value(uid)')\" --limit=50 --format='table(timestamp,textPayload)'"

echo "🎯 推定完了時間: $(date -d '+30 minutes' '+%H:%M')"