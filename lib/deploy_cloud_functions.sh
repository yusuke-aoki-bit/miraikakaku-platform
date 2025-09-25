#!/bin/bash

# Google Cloud Functions デプロイスクリプト
# Deploy all serverless functions

PROJECT_ID="miraikakaku-project"
REGION="asia-northeast1"

echo "🚀 Deploying Cloud Functions to GCP"
echo "=================================="

# 1. 予想生成Function
echo "📊 Deploying Prediction Generator..."
gcloud functions deploy prediction-generator \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=./cloudfunctions/prediction_generator \
    --entry-point=generate_predictions \
    --trigger-http \
    --allow-unauthenticated \
    --memory=512MB \
    --timeout=300s \
    --max-instances=100 \
    --set-env-vars="DB_HOST=34.173.9.214,DB_USER=postgres,DB_NAME=miraikakaku" \
    --set-secrets="DB_PASSWORD=miraikakaku-db-password:latest"

# 2. 価格更新Function
echo "💹 Deploying Price Updater..."
gcloud functions deploy price-updater \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=./cloudfunctions/price_updater \
    --entry-point=update_prices \
    --trigger-http \
    --allow-unauthenticated \
    --memory=1GB \
    --timeout=540s \
    --max-instances=50 \
    --set-env-vars="DB_HOST=34.173.9.214,DB_USER=postgres,DB_NAME=miraikakaku" \
    --set-secrets="DB_PASSWORD=miraikakaku-db-password:latest"

# 3. スケジュール予想生成Function
echo "⏰ Deploying Scheduled Prediction Generator..."
gcloud functions deploy scheduled-prediction-generator \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=./cloudfunctions/prediction_generator \
    --entry-point=scheduled_prediction_generation \
    --trigger-topic=prediction-schedule \
    --memory=1GB \
    --timeout=540s \
    --max-instances=10 \
    --set-env-vars="DB_HOST=34.173.9.214,DB_USER=postgres,DB_NAME=miraikakaku" \
    --set-secrets="DB_PASSWORD=miraikakaku-db-password:latest"

# 4. スケジュール価格更新Function
echo "⏰ Deploying Scheduled Price Updater..."
gcloud functions deploy scheduled-price-updater \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=./cloudfunctions/price_updater \
    --entry-point=scheduled_price_update \
    --trigger-topic=price-update-schedule \
    --memory=2GB \
    --timeout=540s \
    --max-instances=10 \
    --set-env-vars="DB_HOST=34.173.9.214,DB_USER=postgres,DB_NAME=miraikakaku" \
    --set-secrets="DB_PASSWORD=miraikakaku-db-password:latest"

echo ""
echo "✅ Cloud Functions deployment completed!"
echo ""
echo "Function URLs:"
echo "- Prediction Generator: https://$REGION-$PROJECT_ID.cloudfunctions.net/prediction-generator"
echo "- Price Updater: https://$REGION-$PROJECT_ID.cloudfunctions.net/price-updater"