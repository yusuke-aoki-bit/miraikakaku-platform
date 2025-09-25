#!/bin/bash

# Cloud Scheduler セットアップスクリプト
# Setup automated schedules for serverless functions

PROJECT_ID="miraikakaku-project"
REGION="asia-northeast1"

echo "📅 Setting up Cloud Scheduler"
echo "============================="

# Pub/Subトピック作成
echo "Creating Pub/Sub topics..."
gcloud pubsub topics create prediction-schedule --project=$PROJECT_ID
gcloud pubsub topics create price-update-schedule --project=$PROJECT_ID

# 1. 価格データ更新スケジュール（毎日午前9時 JST）
echo "⏰ Creating price update schedule..."
gcloud scheduler jobs create pubsub daily-price-update \
    --location=$REGION \
    --schedule="0 9 * * *" \
    --time-zone="Asia/Tokyo" \
    --topic=price-update-schedule \
    --message-body='{"action":"update_prices","source":"scheduler"}' \
    --description="Daily price data update at 9:00 AM JST"

# 2. 予想生成スケジュール（毎日午前10時 JST）
echo "🔮 Creating prediction generation schedule..."
gcloud scheduler jobs create pubsub daily-prediction-generation \
    --location=$REGION \
    --schedule="0 10 * * *" \
    --time-zone="Asia/Tokyo" \
    --topic=prediction-schedule \
    --message-body='{"action":"generate_predictions","source":"scheduler"}' \
    --description="Daily prediction generation at 10:00 AM JST"

# 3. リアルタイム価格更新（15分ごと、市場時間中）
echo "📊 Creating realtime price update schedule..."
gcloud scheduler jobs create pubsub realtime-price-update \
    --location=$REGION \
    --schedule="*/15 9-15 * * 1-5" \
    --time-zone="Asia/Tokyo" \
    --topic=price-update-schedule \
    --message-body='{"action":"realtime_update","source":"scheduler"}' \
    --description="Realtime price updates every 15 minutes during market hours"

# 4. 週次予想精度評価（毎週月曜日午前6時 JST）
echo "📈 Creating weekly accuracy evaluation schedule..."
gcloud scheduler jobs create http weekly-accuracy-evaluation \
    --location=$REGION \
    --schedule="0 6 * * 1" \
    --time-zone="Asia/Tokyo" \
    --uri="https://$REGION-$PROJECT_ID.cloudfunctions.net/prediction-accuracy-tracker" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"action":"evaluate_accuracy","period":"weekly"}' \
    --description="Weekly prediction accuracy evaluation"

echo ""
echo "📋 Scheduler Status:"
gcloud scheduler jobs list --location=$REGION

echo ""
echo "✅ Cloud Scheduler setup completed!"
echo ""
echo "Scheduled Jobs:"
echo "1. Daily Price Update: 9:00 AM JST"
echo "2. Daily Prediction Generation: 10:00 AM JST"
echo "3. Realtime Updates: Every 15 min (9 AM - 3 PM weekdays)"
echo "4. Weekly Accuracy Check: Mondays 6:00 AM JST"