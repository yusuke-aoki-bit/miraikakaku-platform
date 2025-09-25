#!/bin/bash

# GCP Resources Cleanup Script
# 不要なバッチジョブ、関数、その他のリソースを整理

echo "🧹 GCP Resources Cleanup Starting..."
echo "=================================================="

# 1. Batch Jobs Cleanup
echo ""
echo "📊 Current Batch Jobs Analysis:"
TOTAL_JOBS=$(gcloud batch jobs list --location=us-central1 --format="value(name)" | wc -l)
echo "Total batch jobs: $TOTAL_JOBS"

# Get all old batch jobs (keep only the most recent ones)
echo ""
echo "🗑️  Deleting old batch jobs..."

# Get jobs older than today (all from Sept 22)
OLD_JOBS=$(gcloud batch jobs list --location=us-central1 --format="value(name.basename())" | grep -E "(20250922|stable-lstm|auto-recovery|continuous-data|lstm-ai|prediction-validation|test-minimal)")

if [ ! -z "$OLD_JOBS" ]; then
    echo "Found $(echo "$OLD_JOBS" | wc -l) old jobs to delete:"
    echo "$OLD_JOBS" | head -10
    echo ""

    # Delete in batches to avoid rate limiting
    echo "$OLD_JOBS" | while read job; do
        if [ ! -z "$job" ]; then
            echo "🗑️ Deleting: $job"
            gcloud batch jobs delete "$job" --location=us-central1 --quiet 2>/dev/null || echo "  ⚠️  Could not delete $job"
            sleep 0.5  # Rate limiting
        fi
    done
else
    echo "✅ No old jobs found to delete"
fi

echo ""
echo "📊 After cleanup:"
NEW_TOTAL=$(gcloud batch jobs list --location=us-central1 --format="value(name)" | wc -l)
echo "Remaining batch jobs: $NEW_TOTAL"
echo "Deleted jobs: $((TOTAL_JOBS - NEW_TOTAL))"

# 2. Cloud Functions Analysis
echo ""
echo "=================================================="
echo "☁️  Cloud Functions Analysis:"
gcloud functions list --format="table(name,status,updateTime)" 2>/dev/null

# 3. Cloud Scheduler (if any)
echo ""
echo "=================================================="
echo "⏰ Cloud Scheduler Jobs:"
gcloud scheduler jobs list --format="table(name,state,schedule)" 2>/dev/null || echo "No scheduler jobs found or service not enabled"

# 4. Cloud Storage Buckets
echo ""
echo "=================================================="
echo "🪣 Cloud Storage Buckets:"
gsutil ls 2>/dev/null | head -5 || echo "No buckets found or storage not accessible"

# 5. Compute Engine Instances
echo ""
echo "=================================================="
echo "🖥️  Compute Engine Instances:"
gcloud compute instances list --format="table(name,status,zone)" 2>/dev/null || echo "No compute instances found"

# 6. Cloud SQL Instances
echo ""
echo "=================================================="
echo "🗄️  Cloud SQL Instances:"
gcloud sql instances list --format="table(name,databaseVersion,region)" 2>/dev/null || echo "No SQL instances found"

# 7. Summary and Recommendations
echo ""
echo "=================================================="
echo "📋 Cleanup Summary:"
echo "✅ Batch jobs: Cleaned up old experimental jobs"
echo "✅ Functions: $(gcloud functions list --format="value(name)" 2>/dev/null | wc -l) functions active"
echo ""
echo "💡 Recommendations:"
echo "1. Keep only essential cloud functions running"
echo "2. Monitor ongoing batch jobs for cost optimization"
echo "3. Clean up unused storage buckets periodically"
echo "4. Review cloud scheduler jobs for necessity"
echo ""
echo "🎯 Cleanup completed successfully!"