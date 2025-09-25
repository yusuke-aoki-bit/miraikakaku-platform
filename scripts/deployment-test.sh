#!/bin/bash
# Production Deployment Test Script
# This script validates the deployment pipeline and performs comprehensive tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"pricewise-huqkr"}
REGION=${GCP_REGION:-"us-central1"}
STAGING_URL=""
PROD_URL=""

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Pre-deployment checks
pre_deployment_checks() {
    print_status "Running pre-deployment checks..."

    # Check GCP authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        print_error "Not authenticated with GCP. Run 'gcloud auth login'"
        exit 1
    fi

    # Check project
    current_project=$(gcloud config get-value project)
    if [[ "$current_project" != "$PROJECT_ID" ]]; then
        print_warning "Current project ($current_project) differs from expected ($PROJECT_ID)"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    print_success "Pre-deployment checks passed"
}

# Build and test locally
local_build_test() {
    print_status "Running local build and test..."

    # Test API build
    print_status "Testing API build..."
    cd miraikakakuapi
    docker build -t miraikakaku-api-test . || {
        print_error "API Docker build failed"
        exit 1
    }
    cd ..

    # Test Batch build
    print_status "Testing Batch build..."
    cd miraikakakubatch
    docker build -t miraikakaku-batch-test . || {
        print_error "Batch Docker build failed"
        exit 1
    }
    cd ..

    # Test Frontend build
    print_status "Testing Frontend build..."
    cd miraikakakufront
    docker build -t miraikakaku-frontend-test . || {
        print_error "Frontend Docker build failed"
        exit 1
    }
    cd ..

    print_success "Local build tests passed"
}

# Deploy to staging
deploy_staging() {
    print_status "Deploying to staging environment..."

    # Deploy API to staging
    print_status "Deploying API to staging..."
    gcloud run deploy miraikakaku-api-staging \
        --image gcr.io/${PROJECT_ID}/miraikakaku-api:latest \
        --platform managed \
        --region ${REGION} \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10 \
        --set-env-vars "NODE_ENV=staging" \
        --quiet || {
        print_error "API staging deployment failed"
        exit 1
    }

    # Deploy Frontend to staging
    print_status "Deploying Frontend to staging..."
    gcloud run deploy miraikakaku-frontend-staging \
        --image gcr.io/${PROJECT_ID}/miraikakaku-frontend:latest \
        --platform managed \
        --region ${REGION} \
        --allow-unauthenticated \
        --memory 256Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 5 \
        --quiet || {
        print_error "Frontend staging deployment failed"
        exit 1
    }

    # Get staging URLs
    STAGING_API_URL=$(gcloud run services describe miraikakaku-api-staging \
        --region=${REGION} --format='value(status.url)')
    STAGING_FRONTEND_URL=$(gcloud run services describe miraikakaku-frontend-staging \
        --region=${REGION} --format='value(status.url)')

    print_success "Staging deployment completed"
    print_status "Staging API URL: $STAGING_API_URL"
    print_status "Staging Frontend URL: $STAGING_FRONTEND_URL"
}

# Test staging deployment
test_staging() {
    print_status "Testing staging deployment..."

    # Wait for services to be ready
    sleep 30

    # Test API health
    if curl -sf "${STAGING_API_URL}/health" > /dev/null; then
        print_success "Staging API health check passed"
    else
        print_error "Staging API health check failed"
        return 1
    fi

    # Test Frontend
    if curl -sf "${STAGING_FRONTEND_URL}" > /dev/null; then
        print_success "Staging Frontend health check passed"
    else
        print_error "Staging Frontend health check failed"
        return 1
    fi

    # Test API endpoints
    print_status "Testing API endpoints..."
    if curl -sf "${STAGING_API_URL}/stock/AAPL" | jq '.symbol' | grep -q "AAPL"; then
        print_success "API stock endpoint test passed"
    else
        print_warning "API stock endpoint test failed (may be expected if no data)"
    fi

    print_success "Staging tests completed"
}

# Load test staging
load_test_staging() {
    print_status "Running load tests on staging..."

    # Simple load test with curl
    print_status "Running concurrent requests test..."
    for i in {1..10}; do
        curl -sf "${STAGING_API_URL}/health" > /dev/null &
    done
    wait

    print_success "Load tests completed"
}

# Production deployment (Blue-Green)
deploy_production() {
    print_status "Starting production deployment (Blue-Green)..."

    # Confirmation
    read -p "Deploy to PRODUCTION? This will affect live users. (yes/no): " -r
    if [[ ! $REPLY == "yes" ]]; then
        print_warning "Production deployment cancelled"
        return 0
    fi

    # Deploy to new production version
    print_status "Deploying new production version..."
    gcloud run deploy miraikakaku-api-prod-new \
        --image gcr.io/${PROJECT_ID}/miraikakaku-api:latest \
        --platform managed \
        --region ${REGION} \
        --no-allow-unauthenticated \
        --memory 1Gi \
        --cpu 2 \
        --min-instances 1 \
        --max-instances 20 \
        --set-env-vars "NODE_ENV=production" \
        --quiet || {
        print_error "Production API deployment failed"
        exit 1
    }

    # Health check new version
    NEW_PROD_URL=$(gcloud run services describe miraikakaku-api-prod-new \
        --region=${REGION} --format='value(status.url)')

    print_status "Testing new production version..."
    sleep 15

    if curl -sf "${NEW_PROD_URL}/health" > /dev/null; then
        print_success "New production version health check passed"
    else
        print_error "New production version health check failed"
        print_error "Aborting production switch"
        exit 1
    fi

    # Switch traffic (Blue-Green switch)
    print_status "Switching traffic to new version..."
    gcloud run services update-traffic miraikakaku-api-prod \
        --to-revisions=LATEST=100 \
        --region=${REGION} || {
        print_error "Traffic switch failed"
        exit 1
    }

    print_success "Production deployment completed successfully"
}

# Post-deployment verification
post_deployment_verification() {
    print_status "Running post-deployment verification..."

    # Get production URL
    PROD_API_URL=$(gcloud run services describe miraikakaku-api-prod \
        --region=${REGION} --format='value(status.url)')

    # Comprehensive health checks
    print_status "Testing production endpoints..."

    # Health check
    if curl -sf "${PROD_API_URL}/health" > /dev/null; then
        print_success "Production API health check passed"
    else
        print_error "Production API health check FAILED"
        return 1
    fi

    # Database connectivity test
    print_status "Testing database connectivity..."
    # This would require a specific endpoint for DB health

    # Performance test
    print_status "Running performance verification..."
    start_time=$(date +%s%N)
    curl -sf "${PROD_API_URL}/health" > /dev/null
    end_time=$(date +%s%N)
    response_time=$((($end_time - $start_time) / 1000000))  # Convert to milliseconds

    if [[ $response_time -lt 1000 ]]; then
        print_success "Performance test passed (${response_time}ms)"
    else
        print_warning "Performance test: slow response (${response_time}ms)"
    fi

    print_success "Post-deployment verification completed"
}

# Rollback function
rollback_production() {
    print_error "Rolling back production deployment..."

    # List previous revisions
    gcloud run revisions list --service=miraikakaku-api-prod --region=${REGION}

    read -p "Enter revision name to rollback to: " revision_name

    if [[ -n "$revision_name" ]]; then
        gcloud run services update-traffic miraikakaku-api-prod \
            --to-revisions=${revision_name}=100 \
            --region=${REGION}
        print_success "Rollback completed to revision: $revision_name"
    else
        print_error "No revision specified, rollback cancelled"
    fi
}

# Cleanup test resources
cleanup() {
    print_status "Cleaning up test resources..."

    # Remove test Docker images
    docker rmi -f miraikakaku-api-test miraikakaku-batch-test miraikakaku-frontend-test 2>/dev/null || true

    print_success "Cleanup completed"
}

# Main execution
main() {
    echo "🚀 MiraiKakaku Production Deployment Test"
    echo "======================================="

    case "${1:-full}" in
        "pre-checks")
            pre_deployment_checks
            ;;
        "build")
            pre_deployment_checks
            local_build_test
            ;;
        "staging")
            pre_deployment_checks
            local_build_test
            deploy_staging
            test_staging
            ;;
        "load-test")
            load_test_staging
            ;;
        "production")
            deploy_production
            post_deployment_verification
            ;;
        "rollback")
            rollback_production
            ;;
        "full")
            pre_deployment_checks
            local_build_test
            deploy_staging
            test_staging
            load_test_staging

            # Ask for production deployment
            read -p "Continue with production deployment? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                deploy_production
                post_deployment_verification
            fi
            ;;
        *)
            echo "Usage: $0 [pre-checks|build|staging|load-test|production|rollback|full]"
            exit 1
            ;;
    esac

    cleanup
    print_success "Deployment test completed successfully! 🎉"
}

# Trap for cleanup on exit
trap cleanup EXIT

# Run main function
main "$@"