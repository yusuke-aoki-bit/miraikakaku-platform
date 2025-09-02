#!/bin/bash
# Production Batch Job実行スクリプト

set -e

echo "🚀 Production バッチジョブ実行開始: $(date)"

# プロジェクト設定確認
echo "📋 プロジェクト設定確認..."
PROJECT_ID=$(gcloud config get-value project)
echo "Project ID: $PROJECT_ID"

# バッチジョブ実行
echo "🔥 Production バッチジョブ投入中..."
JOB_NAME="production-batch-$(date +%Y%m%d-%H%M%S)"

gcloud batch jobs submit $JOB_NAME \
  --config=production-batch-job.yaml \
  --location=us-central1

echo "✅ Production バッチジョブ投入完了: $JOB_NAME"
echo "📊 ジョブ状況確認..."

# 実行状況監視
gcloud batch jobs list --location=us-central1 --limit=3

echo ""
echo "🔗 ジョブ詳細確認コマンド:"
echo "gcloud batch jobs describe $JOB_NAME --location=us-central1"

echo ""
echo "📈 ログ確認コマンド:"
echo "gcloud logging read \"resource.type=batch_task AND jsonPayload.job_id=\\\"$JOB_NAME\\\"\" --limit=50"

echo ""
echo "🎯 予想完了時間: $(date -d '+30 minutes' '+%H:%M')"
echo "💫 予想生成データ数: 50,000件 (2,000銘柄 × 25件/銘柄)"

# 結果確認用関数
echo ""
echo "📋 結果確認用コマンド:"
echo "python3 -c \"
import pymysql
conn = pymysql.connect(host='34.58.103.36', user='miraikakaku-user', password='miraikakaku-secure-pass-2024', database='miraikakaku', charset='utf8mb4')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM stock_predictions WHERE notes LIKE \\\"ProductionBatch_$(date +%Y%m%d)_%\\\"')
count = cursor.fetchone()[0]
print(f'今日の生成データ: {count:,}件')
conn.close()
\""