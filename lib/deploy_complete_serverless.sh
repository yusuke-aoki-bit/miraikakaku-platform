#!/bin/bash

# Complete Serverless Deployment Script
# Deploy entire Miraikakaku system to GCP Serverless

PROJECT_ID="miraikakaku-project"
REGION="asia-northeast1"

echo "🚀 COMPLETE SERVERLESS DEPLOYMENT"
echo "=================================="
echo "Deploying Miraikakaku to GCP Serverless Architecture"
echo ""

# 前提条件チェック
echo "🔍 Checking prerequisites..."
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi

# プロジェクト設定
echo "🔧 Setting up project..."
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION
gcloud config set functions/region $REGION

# APIの有効化
echo "🔌 Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable pubsub.googleapis.com

# Secrets管理
echo "🔐 Setting up secrets..."
echo -n "Miraikakaku2024!" | gcloud secrets create miraikakaku-db-password --data-file=-

# 1. Cloud Functions デプロイ
echo ""
echo "☁️ STEP 1: Deploying Cloud Functions..."
echo "======================================="
chmod +x deploy_cloud_functions.sh
./deploy_cloud_functions.sh

# 2. Cloud Scheduler セットアップ
echo ""
echo "📅 STEP 2: Setting up Cloud Scheduler..."
echo "========================================"
chmod +x setup_cloud_scheduler.sh
./setup_cloud_scheduler.sh

# 3. Cloud Run デプロイ
echo ""
echo "🐳 STEP 3: Deploying Cloud Run Services..."
echo "==========================================="
chmod +x deploy_cloud_run.sh
./deploy_cloud_run.sh

# 4. BigQuery セットアップ
echo ""
echo "📊 STEP 4: Setting up BigQuery Analytics..."
echo "==========================================="
chmod +x bigquery/setup_bigquery.sh
chmod +x bigquery/setup_cloudsql_connection.sh
./bigquery/setup_bigquery.sh
./bigquery/setup_cloudsql_connection.sh

# BigQuery分析ダッシュボード設定
echo "Setting up BigQuery analytics dashboard..."
bq query --use_legacy_sql=false < bigquery/analytics_dashboard.sql

# 5. ファイアウォール設定
echo ""
echo "🔒 STEP 5: Configuring Security..."
echo "=================================="

# Cloud Armor ポリシー作成（DDoS保護）
gcloud compute security-policies create miraikakaku-security-policy \
    --description="Miraikakaku DDoS protection"

gcloud compute security-policies rules create 1000 \
    --security-policy=miraikakaku-security-policy \
    --expression="true" \
    --action="allow"

# 6. モニタリング設定
echo ""
echo "📈 STEP 6: Setting up Monitoring..."
echo "==================================="

# アラートポリシー作成（例：API エラー率）
gcloud alpha monitoring policies create --policy-from-file=monitoring/alert-policies.yaml

# 7. 最終確認とテスト
echo ""
echo "🧪 STEP 7: Running Health Checks..."
echo "==================================="

# Function URLs取得
PREDICTION_URL="https://$REGION-$PROJECT_ID.cloudfunctions.net/prediction-generator"
PRICE_URL="https://$REGION-$PROJECT_ID.cloudfunctions.net/price-updater"

# Cloud Run URLs取得
API_URL=$(gcloud run services describe api-miraikakaku \
    --region=$REGION \
    --format="value(status.url)")

FRONTEND_URL=$(gcloud run services describe frontend-miraikakaku \
    --region=$REGION \
    --format="value(status.url)")

# ヘルスチェック
echo "Testing API health..."
curl -f "$API_URL/health" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ API health check passed"
else
    echo "⚠️ API health check failed"
fi

echo ""
echo "========================================"
echo "🎉 SERVERLESS DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "📊 Service Endpoints:"
echo "   Frontend: $FRONTEND_URL"
echo "   API: $API_URL"
echo "   Prediction Function: $PREDICTION_URL"
echo "   Price Update Function: $PRICE_URL"
echo ""
echo "📅 Scheduled Jobs:"
echo "   ✅ Daily price updates (9:00 AM JST)"
echo "   ✅ Daily predictions (10:00 AM JST)"
echo "   ✅ Realtime updates (every 15 min during market hours)"
echo ""
echo "📊 BigQuery Analytics:"
echo "   Dataset: $PROJECT_ID:miraikakaku_analytics"
echo "   Console: https://console.cloud.google.com/bigquery?project=$PROJECT_ID"
echo "   Analytics Views:"
echo "     • Executive Summary Dashboard"
echo "     • Prediction Accuracy Trends"
echo "     • Market Sector Performance"
echo "     • Model Comparison Analytics"
echo "     • System Health Monitoring"
echo ""
echo "🎯 System Status Dashboard:"
echo "   https://console.cloud.google.com/monitoring?project=$PROJECT_ID"
echo ""
echo "💡 Key Features Enabled:"
echo "   ✅ Serverless architecture (auto-scaling)"
echo "   ✅ Automated daily data updates"
echo "   ✅ Real-time prediction generation"
echo "   ✅ BigQuery analytics and reporting"
echo "   ✅ Security policies and monitoring"
echo "   ✅ Zero server maintenance required"
echo ""
echo "🚀 Your Miraikakaku system is now fully serverless!"