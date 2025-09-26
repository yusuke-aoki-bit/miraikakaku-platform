#!/bin/bash
# Production Deployment Script for MiraiKakaku
# Deploys optimized API and Frontend services to Cloud Run

set -e

PROJECT_ID="pricewise-huqkr"
REGION="us-central1"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "🚀 Starting MiraiKakaku production deployment..."
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Timestamp: $TIMESTAMP"

# Set project
gcloud config set project $PROJECT_ID

# Function to build and deploy API
deploy_api() {
    echo "🔧 Building and deploying API service..."

    cd /mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakuapi

    # Build the container image
    echo "   Building API container..."
    gcloud builds submit \
        --tag gcr.io/$PROJECT_ID/miraikakaku-api:$TIMESTAMP \
        --timeout=20m \
        .

    # Deploy to Cloud Run
    echo "   Deploying API to Cloud Run..."
    gcloud run deploy miraikakaku-api \
        --image gcr.io/$PROJECT_ID/miraikakaku-api:$TIMESTAMP \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 4Gi \
        --cpu 2 \
        --timeout 300 \
        --max-instances 10 \
        --min-instances 1 \
        --concurrency 80 \
        --port 8080 \
        --set-env-vars="PORT=8080" \
        --set-env-vars="NODE_ENV=production" \
        --set-env-vars="LOG_LEVEL=INFO"

    cd /mnt/c/Users/yuuku/cursor/miraikakaku
    echo "✅ API deployment completed"
}

# Function to build and deploy Frontend
deploy_frontend() {
    echo "🎨 Building and deploying Frontend service..."

    cd /mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakufront

    # Get API URL for frontend configuration
    API_URL=$(gcloud run services describe miraikakaku-api \
        --region=$REGION \
        --format="value(status.url)")

    echo "   API URL: $API_URL"

    # Build the container image
    echo "   Building Frontend container..."
    gcloud builds submit \
        --tag gcr.io/$PROJECT_ID/miraikakaku-front:$TIMESTAMP \
        --timeout=15m \
        .

    # Deploy to Cloud Run
    echo "   Deploying Frontend to Cloud Run..."
    gcloud run deploy miraikakaku-front \
        --image gcr.io/$PROJECT_ID/miraikakaku-front:$TIMESTAMP \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 1 \
        --timeout 60 \
        --max-instances 5 \
        --min-instances 1 \
        --concurrency 100 \
        --port 3000 \
        --set-env-vars="PORT=3000" \
        --set-env-vars="NODE_ENV=production" \
        --set-env-vars="NEXT_PUBLIC_API_URL=$API_URL"

    cd /mnt/c/Users/yuuku/cursor/miraikakaku
    echo "✅ Frontend deployment completed"
}

# Function to update DNS and custom domains
update_dns() {
    echo "🌐 Updating DNS and custom domains..."

    # Get service URLs
    API_URL=$(gcloud run services describe miraikakaku-api \
        --region=$REGION \
        --format="value(status.url)")

    FRONTEND_URL=$(gcloud run services describe miraikakaku-front \
        --region=$REGION \
        --format="value(status.url)")

    echo "   New service URLs:"
    echo "   API: $API_URL"
    echo "   Frontend: $FRONTEND_URL"

    # Map custom domains (if configured)
    echo "   Mapping custom domains..."

    # Map api.miraikakaku.com to API service
    gcloud run domain-mappings create \
        --service miraikakaku-api \
        --domain api.miraikakaku.com \
        --region $REGION \
        --quiet 2>/dev/null || echo "   API domain mapping already exists or failed"

    # Map miraikakaku.com to Frontend service
    gcloud run domain-mappings create \
        --service miraikakaku-front \
        --domain miraikakaku.com \
        --region $REGION \
        --quiet 2>/dev/null || echo "   Frontend domain mapping already exists or failed"

    echo "✅ DNS configuration completed"
}

# Function to run health checks
health_check() {
    echo "🏥 Running health checks..."

    # Get service URLs
    API_URL=$(gcloud run services describe miraikakaku-api \
        --region=$REGION \
        --format="value(status.url)")

    FRONTEND_URL=$(gcloud run services describe miraikakaku-front \
        --region=$REGION \
        --format="value(status.url)")

    # Test API health
    echo "   Testing API health..."
    if curl -f -s "$API_URL/health" > /dev/null; then
        echo "   ✅ API is healthy"
    else
        echo "   ⚠️  API health check failed"
    fi

    # Test Frontend
    echo "   Testing Frontend..."
    if curl -f -s "$FRONTEND_URL" > /dev/null; then
        echo "   ✅ Frontend is responding"
    else
        echo "   ⚠️  Frontend check failed"
    fi

    # Test custom domains
    echo "   Testing custom domains..."
    if curl -f -s "https://api.miraikakaku.com/health" > /dev/null 2>&1; then
        echo "   ✅ Custom API domain is working"
    else
        echo "   ⚠️  Custom API domain not ready (DNS propagation may take time)"
    fi

    if curl -f -s "https://miraikakaku.com" > /dev/null 2>&1; then
        echo "   ✅ Custom frontend domain is working"
    else
        echo "   ⚠️  Custom frontend domain not ready (DNS propagation may take time)"
    fi

    echo "✅ Health checks completed"
}

# Function to re-enable scheduler jobs
reenable_schedulers() {
    echo "⏰ Re-enabling scheduler jobs..."

    JOBS_TO_RESUME=(
        "emergency-hourly-data-recovery"
        "miraikakaku-realtime-data-collection"
        "health-check-monitor"
    )

    for job in "${JOBS_TO_RESUME[@]}"; do
        echo "▶️  Resuming job: $job"
        gcloud scheduler jobs resume $job --location=$REGION --quiet 2>/dev/null || echo "   Job $job not found"
    done

    echo "✅ Scheduler jobs resumed"
}

# Function to generate deployment report
generate_report() {
    echo "📋 Generating deployment report..."

    API_URL=$(gcloud run services describe miraikakaku-api \
        --region=$REGION \
        --format="value(status.url)")

    FRONTEND_URL=$(gcloud run services describe miraikakaku-front \
        --region=$REGION \
        --format="value(status.url)")

    cat > deployment_report_$TIMESTAMP.md << EOF
# MiraiKakaku Deployment Report
**Date:** $(date)
**Timestamp:** $TIMESTAMP

## Services Deployed

### API Service
- **URL:** $API_URL
- **Custom Domain:** https://api.miraikakaku.com
- **Image:** gcr.io/$PROJECT_ID/miraikakaku-api:$TIMESTAMP
- **Resources:** 4GB RAM, 2 CPUs
- **Auto-scaling:** 1-10 instances

### Frontend Service
- **URL:** $FRONTEND_URL
- **Custom Domain:** https://miraikakaku.com
- **Image:** gcr.io/$PROJECT_ID/miraikakaku-front:$TIMESTAMP
- **Resources:** 2GB RAM, 1 CPU
- **Auto-scaling:** 1-5 instances

## Configuration
- **Region:** $REGION
- **Environment:** Production
- **Security:** HTTPS enabled, unauthenticated access
- **Monitoring:** Cloud Run metrics enabled

## Next Steps
1. Monitor service health and performance
2. Verify custom domain DNS propagation
3. Check batch job execution
4. Monitor database connection pool performance

## Verification Links
- API Health: $API_URL/health
- Frontend: $FRONTEND_URL
- Custom API: https://api.miraikakaku.com/health
- Custom Frontend: https://miraikakaku.com
EOF

    echo "✅ Deployment report saved: deployment_report_$TIMESTAMP.md"
}

# Main deployment process
main() {
    echo "🔄 Starting deployment pipeline..."

    # Check prerequisites
    if ! command -v gcloud &> /dev/null; then
        echo "❌ gcloud CLI not found. Please install it first."
        exit 1
    fi

    # Authenticate
    echo "🔐 Checking authentication..."
    gcloud auth application-default print-access-token > /dev/null 2>&1 || {
        echo "❌ Not authenticated. Please run 'gcloud auth login' first."
        exit 1
    }

    # Deploy services
    deploy_api
    sleep 30  # Wait for API to stabilize
    deploy_frontend
    sleep 30  # Wait for frontend to stabilize

    # Configure domains and run checks
    update_dns
    health_check
    reenable_schedulers
    generate_report

    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "📊 Service URLs:"
    echo "   API: https://api.miraikakaku.com"
    echo "   Frontend: https://miraikakaku.com"
    echo ""
    echo "💡 Next steps:"
    echo "   1. Monitor logs: gcloud logs tail --service=miraikakaku-api"
    echo "   2. Check metrics in Cloud Console"
    echo "   3. Verify all functionality is working"
}

# Execute main function
main "$@"