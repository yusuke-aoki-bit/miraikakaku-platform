#!/bin/bash
# 全バッチジョブ実行スクリプト
# システム全体の動作確認のため、すべてのジョブを手動実行

PROJECT_ID="pricewise-huqkr"
LOCATION="us-central1"

echo "🚀 全バッチジョブ実行開始"
echo "=========================="
echo "$(date)"
echo ""

# 実行するジョブの一覧
JOBS=(
    "データ収集バッチ:miraikakaku-hourly-batch"
    "スキーマ確認:miraikakaku-hourly-schema"
    "予測生成:miraikakaku-hourly-predictions"
)

echo "📋 実行予定ジョブ:"
for job in "${JOBS[@]}"; do
    name=$(echo "$job" | cut -d: -f1)
    scheduler=$(echo "$job" | cut -d: -f2)
    echo "  - $name ($scheduler)"
done
echo ""

# 各スケジューラーを手動実行
echo "⚡ 全スケジューラーを手動実行..."
echo ""

for job in "${JOBS[@]}"; do
    name=$(echo "$job" | cut -d: -f1)
    scheduler=$(echo "$job" | cut -d: -f2)
    
    echo "🔥 $name を実行中..."
    gcloud scheduler jobs run "$scheduler" --location="$LOCATION"
    
    if [ $? -eq 0 ]; then
        echo "✅ $name: スケジューラー起動成功"
    else
        echo "❌ $name: スケジューラー起動失敗"
    fi
    
    echo ""
    sleep 2  # API制限を避けるため少し待機
done

echo "⏰ 起動完了！バッチジョブが実行されています..."
echo ""

# 実行状況の確認
echo "📊 起動直後のバッチジョブ状況:"
sleep 10  # ジョブが作成されるまで待機
gcloud batch jobs list --location="$LOCATION" \
    --filter="createTime>-PT5M" \
    --format="table(name.segment(-1):label=JOB_NAME,status.state:label=STATUS,createTime:label=CREATED)" \
    --limit=10

echo ""
echo "🔍 継続監視コマンド:"
echo "  gcloud batch jobs list --location=$LOCATION --filter=\"createTime>-PT30M\" --limit=20"
echo ""
echo "📈 ログ確認コマンド:"
echo "  gcloud logging read 'resource.type=batch.googleapis.com/Job' --limit=20"
echo ""

# 監視スクリプトを実行
if [ -f "./monitor_batch_status.sh" ]; then
    echo "📋 現在のシステム状況:"
    ./monitor_batch_status.sh
fi

echo ""
echo "🎯 全ジョブ実行完了！"
echo "各バッチジョブは並行して実行されています。"
echo ""
echo "⏱️  予想実行時間:"
echo "  - データ収集: 15-30分"
echo "  - スキーマ確認: 2-5分"
echo "  - 予測生成: 10-20分"