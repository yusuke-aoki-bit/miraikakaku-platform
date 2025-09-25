#!/bin/bash
# API Prediction Endpoint Fix Deployment Script
# Fixes database connection issue in prediction endpoints

PROJECT_ID="pricewise-huqkr"
SERVICE_NAME="miraikakaku-api"
REGION="us-central1"

echo "🚀 Deploying API prediction endpoint fix..."
echo "Fix Details:"
echo "  - Fixed get_ai_predictions function to use Cloud SQL Manager instead of localhost"
echo "  - Fixed undefined 'today' variable in prediction metadata"
echo "  - Updated database queries to use proper PostgreSQL connection"
echo ""

# Change to the correct directory
cd /mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakuapi

# 1. Build Docker image
echo "📦 Building Docker image..."
gcloud builds submit \
    --tag "gcr.io/${PROJECT_ID}/${SERVICE_NAME}:prediction-fix-$(date +%Y%m%d-%H%M)" \
    --project="${PROJECT_ID}" \
    --timeout=30m

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

# 2. Deploy to Cloud Run keeping existing configuration
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image "gcr.io/${PROJECT_ID}/${SERVICE_NAME}:prediction-fix-$(date +%Y%m%d-%H%M)" \
    --platform managed \
    --region ${REGION} \
    --project="${PROJECT_ID}"

if [ $? -ne 0 ]; then
    echo "❌ Deployment failed"
    exit 1
fi

# 3. Verify deployment
echo ""
echo "✅ Deployment completed!"
echo ""
echo "📊 API Endpoint Check:"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)" --project="${PROJECT_ID}")
echo "  URL: ${SERVICE_URL}"
echo ""
echo "🧪 Test Commands:"
echo "  # Health check (should show database: connected)"
echo "  curl '${SERVICE_URL}/health'"
echo ""
echo "  # Stock price (should work - uses different connection)"
echo "  curl '${SERVICE_URL}/api/finance/stocks/AAPL/price?period=1d'"
echo ""
echo "  # Predictions (should now work with Cloud SQL)"
echo "  curl '${SERVICE_URL}/api/finance/stocks/AAPL/predictions'"
echo ""
echo "  # AI predictions endpoint"
echo "  curl -X POST '${SERVICE_URL}/api/ai/predictions/generic' -H 'Content-Type: application/json' -d '{\"symbol\":\"AAPL\"}'"
echo ""
echo "📝 Changes Made:"
echo "  1. get_ai_predictions function now uses db_manager.engine.connect()"
echo "  2. Database queries converted from ? to %s format for PostgreSQL"
echo "  3. Fixed undefined 'today' variable in prediction metadata"
echo "  4. Updated row access from dict-style to attribute-style"
echo ""
echo "🎯 The prediction endpoints should now connect to Cloud SQL instead of localhost!"