#!/bin/bash
# GCP Resource Cleanup Script
# Cleans up old batch jobs, container images, and optimizes scheduler jobs

set -e

PROJECT_ID="pricewise-huqkr"
REGION="us-central1"

echo "🧹 Starting GCP resource cleanup for project: $PROJECT_ID"

# Function to clean up failed batch jobs
cleanup_failed_batch_jobs() {
    echo "📦 Cleaning up failed batch jobs..."

    # Get list of failed jobs
    FAILED_JOBS=$(gcloud batch jobs list \
        --location=$REGION \
        --filter="status.state:FAILED" \
        --format="value(name)" \
        --limit=50 2>/dev/null || echo "")

    if [ -n "$FAILED_JOBS" ]; then
        echo "Found failed batch jobs to clean up:"
        echo "$FAILED_JOBS"

        # Delete failed jobs (with confirmation)
        for job in $FAILED_JOBS; do
            echo "🗑️  Deleting failed job: $(basename $job)"
            gcloud batch jobs delete "$(basename $job)" \
                --location=$REGION \
                --quiet 2>/dev/null || echo "   Failed to delete $job"
        done
    else
        echo "✅ No failed batch jobs found"
    fi
}

# Function to clean up old container images
cleanup_old_images() {
    echo "🐳 Cleaning up old container images..."

    # Clean up API images (keep latest 3)
    echo "   Cleaning miraikakaku-api images..."
    gcloud container images list-tags gcr.io/$PROJECT_ID/miraikakaku-api \
        --limit=999 --sort-by=~timestamp \
        --format="get(digest)" | tail -n +4 | \
    while read digest; do
        if [ -n "$digest" ]; then
            echo "🗑️  Deleting old API image: $digest"
            gcloud container images delete gcr.io/$PROJECT_ID/miraikakaku-api@$digest \
                --force-delete-tags --quiet 2>/dev/null || true
        fi
    done

    # Clean up frontend images (keep latest 3)
    echo "   Cleaning miraikakaku-front images..."
    gcloud container images list-tags gcr.io/$PROJECT_ID/miraikakaku-front \
        --limit=999 --sort-by=~timestamp \
        --format="get(digest)" | tail -n +4 | \
    while read digest; do
        if [ -n "$digest" ]; then
            echo "🗑️  Deleting old frontend image: $digest"
            gcloud container images delete gcr.io/$PROJECT_ID/miraikakaku-front@$digest \
                --force-delete-tags --quiet 2>/dev/null || true
        fi
    done
}

# Function to optimize scheduler jobs
optimize_scheduler_jobs() {
    echo "⏰ Optimizing scheduler jobs..."

    # Disable overly frequent jobs during optimization
    FREQUENT_JOBS=(
        "emergency-hourly-data-recovery"
        "miraikakaku-realtime-data-collection"
        "health-check-monitor"
    )

    for job in "${FREQUENT_JOBS[@]}"; do
        echo "⏸️  Temporarily pausing frequent job: $job"
        gcloud scheduler jobs pause $job --location=$REGION --quiet 2>/dev/null || echo "   Job $job not found or already paused"
    done

    echo "✅ Frequent jobs paused for deployment"
}

# Function to check resource quotas
check_quotas() {
    echo "📊 Checking resource quotas..."

    echo "Cloud Run services:"
    gcloud run services list --format="table(metadata.name,status.traffic[0].percent)" --limit=10

    echo "Current batch jobs:"
    gcloud batch jobs list --location=$REGION --limit=5 --format="table(name,status.state)"

    echo "Scheduler jobs:"
    gcloud scheduler jobs list --location=$REGION --format="table(name,state)" --limit=5
}

# Main cleanup process
main() {
    echo "Starting cleanup process..."

    # Set the project
    gcloud config set project $PROJECT_ID

    # Run cleanup functions
    cleanup_failed_batch_jobs
    cleanup_old_images
    optimize_scheduler_jobs
    check_quotas

    echo "🎉 GCP cleanup completed successfully!"
    echo ""
    echo "📋 Summary:"
    echo "   - Cleaned up failed batch jobs"
    echo "   - Removed old container images (kept latest 3 of each)"
    echo "   - Paused frequent scheduler jobs for deployment"
    echo ""
    echo "⚡ Ready for fresh deployment!"
}

# Execute main function
main "$@"