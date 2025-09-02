#!/bin/bash
set -e

echo "🚀 Starting batch job deployment process..."

# Configuration
PROJECT_ID="pricewise-huqkr"
REGION="us-central1"
REPOSITORY="miraikakaku-docker"
IMAGE_NAME="batch-production"
TAG="latest"

# Full image path
IMAGE_URI="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$TAG"

echo "📦 Building Docker image..."
docker build -f Dockerfile.production -t $IMAGE_URI .

echo "🔄 Pushing to Artifact Registry..."
docker push $IMAGE_URI

echo "✅ Image pushed successfully: $IMAGE_URI"

echo "📝 Submitting batch job..."
gcloud batch jobs submit miraikakaku-production-$(date +%Y%m%d-%H%M%S) \
    --location=$REGION \
    --config=production-batch.yaml

echo "✅ Batch job submitted successfully!"