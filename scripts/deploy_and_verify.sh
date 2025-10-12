#!/bin/bash
#
# デプロイと検証の自動化スクリプト
# Usage: ./scripts/deploy_and_verify.sh [api|frontend]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="pricewise-huqkr"
REGION="us-central1"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Generate unique tag
generate_tag() {
    python -c "from datetime import datetime; print(f'v{datetime.now().strftime(\"%Y%m%d-%H%M%S\")}')"
}

# Deploy API
deploy_api() {
    local TAG=$(generate_tag)
    local IMAGE="gcr.io/${PROJECT_ID}/miraikakaku-api:${TAG}"

    log_info "Building API with tag: ${TAG}"
    gcloud builds submit --tag "${IMAGE}" --project="${PROJECT_ID}" --timeout=20m

    log_info "Deploying API to Cloud Run"
    gcloud run services update miraikakaku-api \
        --image "${IMAGE}" \
        --region "${REGION}" \
        --project="${PROJECT_ID}"

    log_info "Waiting for deployment to stabilize..."
    sleep 10

    # Verify
    log_info "Verifying API deployment..."
    local API_URL="https://miraikakaku-api-zbaru5v7za-uc.a.run.app"

    # Check stats endpoint
    local RESPONSE=$(curl -s "${API_URL}/api/home/stats/summary")
    local TOTAL_SYMBOLS=$(echo "${RESPONSE}" | python -m json.tool 2>/dev/null | grep totalSymbols | awk '{print $2}' | tr -d ',')

    if [ "${TOTAL_SYMBOLS}" == "3756" ]; then
        log_info "✅ API verification PASSED: totalSymbols = ${TOTAL_SYMBOLS}"
        echo "${IMAGE}" > .last_api_image
        return 0
    else
        log_error "❌ API verification FAILED: totalSymbols = ${TOTAL_SYMBOLS} (expected: 3756)"
        return 1
    fi
}

# Deploy Frontend
deploy_frontend() {
    local TAG=$(generate_tag)
    local IMAGE="gcr.io/${PROJECT_ID}/miraikakaku-frontend:${TAG}"

    log_info "Building Frontend with tag: ${TAG}"
    cd miraikakakufront
    gcloud builds submit --tag "${IMAGE}" --project="${PROJECT_ID}" --timeout=20m
    cd ..

    log_info "Deploying Frontend to Cloud Run"
    gcloud run services update miraikakaku-frontend \
        --image "${IMAGE}" \
        --region "${REGION}" \
        --project="${PROJECT_ID}"

    log_info "Waiting for deployment to stabilize..."
    sleep 10

    # Verify
    log_info "Verifying Frontend deployment..."
    local FRONTEND_URL="https://miraikakaku-frontend-zbaru5v7za-uc.a.run.app"

    local HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}")

    if [ "${HTTP_CODE}" == "200" ]; then
        log_info "✅ Frontend verification PASSED: HTTP ${HTTP_CODE}"
        echo "${IMAGE}" > .last_frontend_image
        return 0
    else
        log_error "❌ Frontend verification FAILED: HTTP ${HTTP_CODE}"
        return 1
    fi
}

# Main
main() {
    local SERVICE=$1

    if [ -z "${SERVICE}" ]; then
        log_error "Usage: $0 [api|frontend]"
        exit 1
    fi

    case "${SERVICE}" in
        api)
            deploy_api
            ;;
        frontend)
            deploy_frontend
            ;;
        *)
            log_error "Unknown service: ${SERVICE}"
            log_error "Usage: $0 [api|frontend]"
            exit 1
            ;;
    esac
}

main "$@"
