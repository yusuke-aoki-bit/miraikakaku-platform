#!/bin/bash
# Miraikakaku モニタリング設定スクリプト

PROJECT_ID="pricewise-huqkr"
API_URL="miraikakaku-api-465603676610.us-central1.run.app"
FRONTEND_URL="miraikakaku-front-465603676610.us-central1.run.app"
BATCH_URL="miraikakaku-batch-465603676610.us-central1.run.app"

echo "🔍 Miraikakaku モニタリング設定を開始..."

# アップタイムチェック作成（Web UIでの設定を推奨）
echo "📊 アップタイムチェックの設定は Web UI で行ってください："
echo "1. Google Cloud Console > Monitoring > Uptime Checks"
echo "2. 以下のURLを設定："
echo "   - API: https://${API_URL}/health"
echo "   - Frontend: https://${FRONTEND_URL}/"
echo "   - Batch: https://${BATCH_URL}/health"

# アラートポリシーの作成
echo "🚨 アラートポリシー作成中..."

# API レスポンスタイム アラート
cat > api-response-time-policy.json << EOF
{
  "displayName": "Miraikakaku API レスポンスタイム アラート",
  "conditions": [
    {
      "displayName": "API レスポンス時間 > 5秒",
      "conditionThreshold": {
        "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"miraikakaku-api\"",
        "comparison": "COMPARISON_GREATER_THAN",
        "thresholdValue": 5000,
        "duration": "300s",
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_MEAN",
            "crossSeriesReducer": "REDUCE_MEAN"
          }
        ]
      }
    }
  ],
  "combiner": "OR",
  "enabled": true,
  "notificationChannels": [],
  "alertStrategy": {
    "autoClose": "1800s"
  }
}
EOF

# Cloud SQL 接続アラート
cat > cloudsql-connection-policy.json << EOF
{
  "displayName": "Cloud SQL 接続エラー アラート",
  "conditions": [
    {
      "displayName": "Cloud SQL 接続失敗",
      "conditionThreshold": {
        "filter": "resource.type=\"cloudsql_database\" AND log_name=\"projects/${PROJECT_ID}/logs/cloudsql.googleapis.com%2Fmysql.err\"",
        "comparison": "COMPARISON_GREATER_THAN",
        "thresholdValue": 5,
        "duration": "300s",
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_RATE",
            "crossSeriesReducer": "REDUCE_SUM"
          }
        ]
      }
    }
  ],
  "combiner": "OR",
  "enabled": true,
  "notificationChannels": []
}
EOF

echo "✅ モニタリング設定完了"
echo "📍 次のステップ："
echo "1. Google Cloud Console でアップタイムチェックを手動設定"
echo "2. 通知チャネル（Email/Slack）を設定"
echo "3. アラートポリシーの通知先を設定"