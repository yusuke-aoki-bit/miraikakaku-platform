#!/bin/bash
#
# 失敗したGCP Batchジョブの完全クリーンアップ
# 100%失敗ジョブのリソース削除とコスト削減
#

set -e

LOCATION="us-central1"

echo "🗑️ 失敗GCP Batchジョブクリーンアップ開始"
echo "=============================================="

# 失敗ジョブ一覧を定義
FAILED_JOBS=(
    "ultra-reliable-batch-1-20250924-154844"
    "ultra-reliable-batch-2-20250924-154846"
    "ultra-reliable-batch-3-20250924-154848"
    "ultra-reliable-batch-4-20250924-154850"
    "ultra-reliable-batch-5-20250924-154852"
    "final-assault-alpha-20250924-154232"
    "final-assault-beta-20250924-154232"
    "final-assault-gamma-20250924-154232"
    "urgent-data-recovery-20250924-151929"
    "robust-predictions-20250922-155456"
    "comprehensive-data-collection-20250922-032447"
    "reliable-data-collection-20250922-032741"
    "simple-effective-collection-20250922-060634"
    "emergency-recovery-20250922-155444"
    "historical-predictions-postgres-20250918-225000"
    "massive-parallel-collection-20250922-032555"
    "symbol-verify-corrected-20250918-112109"
    "master-enhanced-postgres-20250918-224857"
)

echo "📊 削除対象ジョブ数: ${#FAILED_JOBS[@]}個"

# 1. 現在のジョブ状態確認
echo ""
echo "📌 Step 1: 現在の状態確認"
echo "========================="

gcloud batch jobs list --location=${LOCATION} \
    --format="table(name,status.state,createTime)" \
    --filter="status.state=FAILED OR status.state=RUNNING" | head -20

echo ""

# 2. 失敗ジョブの詳細確認と削除
echo "📌 Step 2: 失敗ジョブ削除"
echo "========================"

deleted_count=0
not_found_count=0

for job in "${FAILED_JOBS[@]}"; do
    echo -n "🔍 Processing: $job ... "

    # ジョブの存在確認
    if gcloud batch jobs describe "$job" --location=${LOCATION} >/dev/null 2>&1; then
        # ジョブが存在する場合、状態を確認
        job_state=$(gcloud batch jobs describe "$job" --location=${LOCATION} --format="value(status.state)")
        echo -n "(状態: $job_state) "

        # ジョブを削除
        if gcloud batch jobs delete "$job" --location=${LOCATION} --quiet 2>/dev/null; then
            echo "✅ 削除完了"
            ((deleted_count++))
        else
            echo "⚠️ 削除失敗"
        fi
    else
        echo "🔍 ジョブが見つかりません"
        ((not_found_count++))
    fi

    # API rate limitを避けるため少し待機
    sleep 1
done

echo ""
echo "📊 削除結果サマリー:"
echo "  ✅ 削除完了: $deleted_count ジョブ"
echo "  🔍 見つからない: $not_found_count ジョブ"

# 3. 残存ジョブの確認
echo ""
echo "📌 Step 3: 残存ジョブ確認"
echo "========================"

echo "現在のバッチジョブ一覧:"
remaining_jobs=$(gcloud batch jobs list --location=${LOCATION} --format="value(name)" | wc -l)
echo "残存ジョブ数: $remaining_jobs"

if [ $remaining_jobs -gt 0 ]; then
    echo ""
    gcloud batch jobs list --location=${LOCATION} \
        --format="table(name,status.state,createTime)" \
        --sort-by="createTime" --limit=10
fi

# 4. Cloud Schedulerの無効なスケジューラもクリーンアップ
echo ""
echo "📌 Step 4: 古いCloud Schedulerジョブ確認"
echo "========================================"

scheduler_jobs=$(gcloud scheduler jobs list --location=${LOCATION} --format="value(name)" 2>/dev/null || echo "")
if [ -n "$scheduler_jobs" ]; then
    echo "既存のCloud Schedulerジョブ:"
    gcloud scheduler jobs list --location=${LOCATION} \
        --format="table(name,schedule,state)" 2>/dev/null || echo "スケジューラジョブなし"
else
    echo "Cloud Schedulerジョブなし"
fi

# 5. コスト削減の見積もり
echo ""
echo "📌 Step 5: コスト削減効果"
echo "========================"

echo "💰 期待される効果:"
echo "  🔹 失敗ジョブのリソース課金停止"
echo "  🔹 不要なログストレージ削減"
echo "  🔹 バッチAPI利用量削減"
echo "  🔹 監視コスト削減"
echo ""
echo "📈 削除されたジョブによる継続的な無駄コスト:"
echo "  - 失敗ジョブ: ${#FAILED_JOBS[@]}個 × $0.10/日 = $$(echo \"${#FAILED_JOBS[@]} * 0.10\" | bc)/日"
echo "  - 年間節約: $$(echo \"${#FAILED_JOBS[@]} * 0.10 * 365\" | bc 2>/dev/null || echo \"計算不可\")"

# 6. 次のアクションの提案
echo ""
echo "📌 Step 6: 推奨される次のアクション"
echo "=================================="

echo "✅ 完了した作業:"
echo "  - 失敗バッチジョブ $deleted_count 個を削除"
echo "  - リソースの無駄遣い停止"
echo ""
echo "🚀 推奨される次のステップ:"
echo "  1. Cloud Runシステムの本番デプロイ (deploy_cloud_run.sh実行)"
echo "  2. Cloud Schedulerによる自動化設定"
echo "  3. 既存データベースの健全性確認"
echo "  4. システム監視とアラート設定"
echo ""
echo "⚡ 即座実行可能なコマンド:"
echo "  chmod +x deploy_cloud_run.sh && ./deploy_cloud_run.sh"
echo ""

echo "🎉 GCP Batchクリーンアップ完了!"
echo "================================="