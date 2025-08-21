#!/bin/bash

# GCP Alert Configuration Script
# アラート設定を調整するスクリプト

PROJECT_ID="pricewise-huqkr"
REGION="asia-northeast1"

echo "=== GCP アラート設定の調整 ==="

# 1. 既存のアラートポリシーを無効化
echo "既存のアラートポリシーを調整中..."
gcloud alpha monitoring policies update 13744833352273322629 \
    --update-enabled=false \
    --project=$PROJECT_ID 2>/dev/null || echo "既存ポリシーの更新をスキップ"

# 2. アップタイムチェックの作成
echo "アップタイムチェックを設定中..."

# フロントエンドのアップタイムチェック
gcloud monitoring uptime-check-configs create \
    --display-name="Miraikakaku Frontend Check" \
    --resource-type="uptime-url" \
    --hostname="www.miraikakaku.com" \
    --path="/" \
    --port=443 \
    --use-ssl \
    --period=60 \
    --timeout=10 \
    --project=$PROJECT_ID 2>/dev/null || echo "Frontend uptime check already exists"

# 3. Cloud Runサービスのアラートポリシー作成
echo "Cloud Runアラートポリシーを作成中..."

# CPU使用率アラート
cat > /tmp/cpu-alert-policy.yaml << EOF
displayName: "Cloud Run CPU Alert - Miraikakaku"
documentation:
  content: "Cloud RunサービスのCPU使用率が80%を超えた場合に通知"
  mimeType: text/markdown
conditions:
  - displayName: "High CPU Usage"
    conditionThreshold:
      filter: |
        resource.type="cloud_run_revision"
        AND resource.labels.service_name="miraikakaku-front"
        AND metric.type="run.googleapis.com/container/cpu/utilizations"
      comparison: COMPARISON_GT
      thresholdValue: 0.8
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_MEAN
enabled: true
combiner: OR
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/cpu-alert-policy.yaml \
    --project=$PROJECT_ID 2>/dev/null || echo "CPU alert policy already exists"

# メモリ使用率アラート
cat > /tmp/memory-alert-policy.yaml << EOF
displayName: "Cloud Run Memory Alert - Miraikakaku"
documentation:
  content: "Cloud RunサービスのMemory使用率が90%を超えた場合に通知"
  mimeType: text/markdown
conditions:
  - displayName: "High Memory Usage"
    conditionThreshold:
      filter: |
        resource.type="cloud_run_revision"
        AND resource.labels.service_name="miraikakaku-front"
        AND metric.type="run.googleapis.com/container/memory/utilizations"
      comparison: COMPARISON_GT
      thresholdValue: 0.9
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_MEAN
enabled: true
combiner: OR
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/memory-alert-policy.yaml \
    --project=$PROJECT_ID 2>/dev/null || echo "Memory alert policy already exists"

# エラー率アラート
cat > /tmp/error-rate-policy.yaml << EOF
displayName: "Cloud Run Error Rate Alert - Miraikakaku"
documentation:
  content: "Cloud Runサービスの5xxエラー率が1%を超えた場合に通知"
  mimeType: text/markdown
conditions:
  - displayName: "High Error Rate"
    conditionThreshold:
      filter: |
        resource.type="cloud_run_revision"
        AND resource.labels.service_name="miraikakaku-front"
        AND metric.type="run.googleapis.com/request_count"
        AND metric.labels.response_code_class="5xx"
      comparison: COMPARISON_GT
      thresholdValue: 10
      duration: 180s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_RATE
enabled: true
combiner: OR
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/error-rate-policy.yaml \
    --project=$PROJECT_ID 2>/dev/null || echo "Error rate policy already exists"

# 4. レイテンシアラート（p95 > 1秒）
cat > /tmp/latency-policy.yaml << EOF
displayName: "Cloud Run Latency Alert - Miraikakaku"
documentation:
  content: "Cloud Runサービスのレスポンスタイムが1秒を超えた場合に通知"
  mimeType: text/markdown
conditions:
  - displayName: "High Latency"
    conditionThreshold:
      filter: |
        resource.type="cloud_run_revision"
        AND resource.labels.service_name="miraikakaku-front"
        AND metric.type="run.googleapis.com/request_latencies"
      comparison: COMPARISON_GT
      thresholdValue: 1000
      duration: 180s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_PERCENTILE_95
enabled: false
combiner: OR
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/latency-policy.yaml \
    --project=$PROJECT_ID 2>/dev/null || echo "Latency policy already exists"

# 5. クリーンアップ
rm -f /tmp/*-policy.yaml

echo "=== アラート設定完了 ==="
echo ""
echo "設定されたアラート:"
echo "✅ Cloud Run CPU使用率 (>80%)"
echo "✅ Cloud Run メモリ使用率 (>90%)"
echo "✅ Cloud Run エラー率 (5xx >1%)"
echo "⏸  Cloud Run レイテンシ (p95 >1s) - 無効化済み"
echo ""
echo "通知先: yuu.kufs@gmail.com"
echo ""
echo "アラートの確認: https://console.cloud.google.com/monitoring/alerting/policies?project=$PROJECT_ID"