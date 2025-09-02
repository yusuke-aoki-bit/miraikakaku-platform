#!/bin/bash
# スケジューラー自動実行確認スクリプト

PROJECT_ID="pricewise-huqkr"
LOCATION="us-central1"

echo "🕐 Cloud Schedulerの自動実行状況を確認"
echo "========================================"
echo ""

# 1. スケジューラーの詳細情報
echo "📊 設定済みスケジューラー:"
gcloud scheduler jobs list --location="${LOCATION}" --filter="name:miraikakaku-hourly" \
    --format="table(name.segment(-1):label=JOB_NAME,schedule:label=SCHEDULE,state:label=STATUS,lastAttemptTime.date():label=LAST_RUN,nextRunTime.date():label=NEXT_RUN)"

echo ""
echo "📈 実行履歴の確認:"

# 2. 最近のバッチジョブ（スケジューラーから起動されたもの）
echo ""
echo "🔍 過去24時間のバッチジョブ:"
gcloud batch jobs list --location="${LOCATION}" \
    --filter="createTime>-P1D" \
    --format="table(name.segment(-1):label=JOB_NAME,status.state:label=STATUS,createTime.date():label=CREATED,labels.trigger:label=TRIGGER)" \
    --limit=20

# 3. スケジューラーの実行ログ確認
echo ""
echo "📝 スケジューラー実行ログ (最新5件):"
gcloud logging read "resource.type=cloudscheduler.googleapis.com/Job AND (resource.labels.job_id=miraikakaku-hourly-batch OR resource.labels.job_id=miraikakaku-hourly-schema)" \
    --limit=5 \
    --format="table(timestamp.date():label=TIME,resource.labels.job_id:label=SCHEDULER,severity:label=LEVEL,textPayload:label=MESSAGE)" \
    --project="${PROJECT_ID}" 2>/dev/null || echo "ログが見つかりません"

# 4. 次回実行予定の確認
echo ""
echo "⏰ 次回実行予定:"
for job in miraikakaku-hourly-batch miraikakaku-hourly-schema; do
    echo -n "  ${job}: "
    gcloud scheduler jobs describe ${job} --location="${LOCATION}" --format="value(nextRunTime)" 2>/dev/null || echo "Not found"
done

# 5. 自動実行を確実にするための推奨事項
echo ""
echo "🔧 自動実行を確実にするための確認事項:"
echo "  ✓ スケジューラーのステータスがENABLEDであること"
echo "  ✓ サービスアカウントに適切な権限があること"
echo "  ✓ Batch APIが有効であること"
echo "  ✓ Cloud Scheduler APIが有効であること"

# 6. サービスアカウントの権限確認
echo ""
echo "🔑 サービスアカウント権限確認:"
SA_EMAIL="${PROJECT_ID}@appspot.gserviceaccount.com"
echo "  サービスアカウント: ${SA_EMAIL}"

# 必要な役割の確認
REQUIRED_ROLES=(
    "roles/batch.jobsEditor"
    "roles/cloudscheduler.jobRunner"
    "roles/iam.serviceAccountUser"
)

for role in "${REQUIRED_ROLES[@]}"; do
    echo -n "  ${role}: "
    gcloud projects get-iam-policy ${PROJECT_ID} \
        --flatten="bindings[].members" \
        --filter="bindings.role:${role} AND bindings.members:serviceAccount:${SA_EMAIL}" \
        --format="value(bindings.role)" 2>/dev/null | grep -q "${role}" && echo "✓" || echo "✗ (要設定)"
done

# 7. APIの有効化状態確認
echo ""
echo "🌐 必要なAPIの有効化状態:"
REQUIRED_APIS=(
    "batch.googleapis.com"
    "cloudscheduler.googleapis.com"
    "compute.googleapis.com"
    "logging.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    echo -n "  ${api}: "
    gcloud services list --enabled --filter="name:${api}" --format="value(name)" --project="${PROJECT_ID}" | grep -q "${api}" && echo "✓" || echo "✗"
done

echo ""
echo "✅ 確認完了！"
echo ""
echo "💡 ヒント:"
echo "  - スケジューラーが実行されない場合は、手動でトリガー:"
echo "    gcloud scheduler jobs run miraikakaku-hourly-batch --location=${LOCATION}"
echo ""
echo "  - ログの詳細確認:"
echo "    gcloud logging read 'resource.type=batch.googleapis.com/Job' --limit=20"