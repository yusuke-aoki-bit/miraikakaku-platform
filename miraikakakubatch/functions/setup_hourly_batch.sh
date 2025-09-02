#!/bin/bash
# 1時間ごとのバッチ実行を設定する簡易スクリプト

PROJECT_ID="pricewise-huqkr"
LOCATION="us-central1"

echo "🚀 1時間ごとのバッチ実行を設定中..."

# 1. Cloud Scheduler APIを有効化
echo "📌 Cloud Scheduler APIを有効化..."
gcloud services enable cloudscheduler.googleapis.com --project="${PROJECT_ID}"

# 2. 毎時実行のスケジューラーを作成（簡易版）
echo "⏰ 毎時実行のスケジューラーを作成..."

# バッチジョブを直接トリガーする簡易的な方法
gcloud scheduler jobs create http miraikakaku-hourly-batch \
    --location="${LOCATION}" \
    --schedule="0 * * * *" \
    --time-zone="Asia/Tokyo" \
    --uri="https://batch.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/jobs?job_id=scheduled-$(date +%s)" \
    --http-method="POST" \
    --headers="Content-Type=application/json,User-Agent=CloudScheduler" \
    --message-body-from-file="real-data-batch.yaml" \
    --description="毎時0分に実データ収集バッチを実行" \
    --attempt-deadline="30m" \
    2>/dev/null || echo "⚠️ スケジューラーが既に存在するか、権限が不足しています"

# 3. 既存のスケジューラーを確認
echo ""
echo "📊 現在のスケジューラー設定:"
gcloud scheduler jobs list --location="${LOCATION}" 2>/dev/null || echo "スケジューラーが設定されていません"

echo ""
echo "✅ 設定完了！"
echo ""
echo "📝 代替手段として、以下のコマンドをcronに登録することもできます:"
echo "   0 * * * * gcloud batch jobs submit hourly-\$(date +\\%Y\\%m\\%d-\\%H\\%M\\%S) --location=${LOCATION} --config=/path/to/real-data-batch.yaml"
echo ""
echo "🔧 手動実行コマンド:"
echo "   gcloud batch jobs submit manual-\$(date +%Y%m%d-%H%M%S) --location=${LOCATION} --config=real-data-batch.yaml"