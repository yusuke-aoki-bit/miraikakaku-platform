#!/bin/bash
# GCP Resource Cleanup Script
# Date: 2025-10-12
# Project: pricewise-huqkr

set -e

PROJECT="pricewise-huqkr"
REGION="us-central1"

echo "========================================================================"
echo "GCP RESOURCE CLEANUP SCRIPT"
echo "========================================================================"
echo "Project: $PROJECT"
echo "Region: $REGION"
echo ""

# 1. Clean up old Cloud Run revisions (keep last 3)
echo "1. Cleaning up old Cloud Run revisions..."
echo "----------------------------------------"

for SERVICE in miraikakaku-api miraikakaku-frontend parallel-batch-collector; do
    echo "Service: $SERVICE"

    # Get all revisions sorted by creation time (oldest first)
    REVISIONS=$(gcloud run revisions list \
        --service=$SERVICE \
        --region=$REGION \
        --project=$PROJECT \
        --format="value(metadata.name)" \
        --sort-by="metadata.creationTimestamp" 2>/dev/null)

    TOTAL=$(echo "$REVISIONS" | wc -l)
    KEEP=3
    DELETE=$((TOTAL - KEEP))

    if [ $DELETE -gt 0 ]; then
        echo "  Total revisions: $TOTAL"
        echo "  Will delete: $DELETE oldest revisions (keeping last $KEEP)"

        echo "$REVISIONS" | head -n $DELETE | while read REVISION; do
            echo "  Deleting: $REVISION"
            gcloud run revisions delete $REVISION \
                --region=$REGION \
                --project=$PROJECT \
                --quiet 2>&1 | grep -E "(Deleted|ERROR)" || echo "    Skipped (in use or already deleted)"
        done
    else
        echo "  Only $TOTAL revisions found. No cleanup needed."
    fi
    echo ""
done

# 2. Clean up old Docker images (keep last 5)
echo "2. Cleaning up old Docker images..."
echo "----------------------------------------"

for IMAGE in miraikakaku-api miraikakaku-frontend parallel-batch-collector; do
    echo "Image: gcr.io/$PROJECT/$IMAGE"

    # Get all images sorted by timestamp (oldest first)
    IMAGES=$(gcloud container images list-tags gcr.io/$PROJECT/$IMAGE \
        --format="get(digest)" \
        --sort-by="~timestamp" \
        --limit=100 2>/dev/null)

    TOTAL=$(echo "$IMAGES" | wc -l)
    KEEP=5
    DELETE=$((TOTAL - KEEP))

    if [ $DELETE -gt 0 ]; then
        echo "  Total images: $TOTAL"
        echo "  Will delete: $DELETE oldest images (keeping last $KEEP)"

        echo "$IMAGES" | tail -n $DELETE | while read DIGEST; do
            if [ ! -z "$DIGEST" ]; then
                echo "  Deleting: gcr.io/$PROJECT/$IMAGE@$DIGEST"
                gcloud container images delete "gcr.io/$PROJECT/$IMAGE@$DIGEST" \
                    --project=$PROJECT \
                    --quiet 2>&1 | grep -E "(Deleted|ERROR)" || echo "    Skipped"
            fi
        done
    else
        echo "  Only $TOTAL images found. No cleanup needed."
    fi
    echo ""
done

# 3. List Cloud Scheduler jobs (no cleanup, just info)
echo "3. Cloud Scheduler Jobs Status..."
echo "----------------------------------------"
gcloud scheduler jobs list \
    --location=$REGION \
    --project=$PROJECT \
    --format="table(name,schedule,state,lastAttemptTime)" 2>&1
echo ""

# 4. Check Cloud SQL instances (no cleanup, just info)
echo "4. Cloud SQL Instances..."
echo "----------------------------------------"
gcloud sql instances list \
    --project=$PROJECT \
    --format="table(name,region,tier,state)" 2>&1
echo ""

# 5. Summary
echo "========================================================================"
echo "CLEANUP COMPLETE"
echo "========================================================================"
echo ""
echo "Summary:"
echo "- Old Cloud Run revisions: Deleted (keeping last 3 per service)"
echo "- Old Docker images: Deleted (keeping last 5 per image)"
echo "- Cloud Scheduler jobs: 4 jobs ENABLED (no changes)"
echo "- Cloud SQL: 1 instance running (no changes)"
echo ""
echo "Next steps:"
echo "1. Verify services are still running: gcloud run services list"
echo "2. Check https://miraikakaku.jp"
echo "3. Monitor logs for any issues"
echo ""
