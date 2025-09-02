#!/bin/bash
# Batch Job Management Script

set -e

function show_help() {
    echo "🛠️  Batch Job Management Script"
    echo ""
    echo "使用方法:"
    echo "  $0 [コマンド]"
    echo ""
    echo "コマンド:"
    echo "  status          - 実行中/最近のバッチジョブ状況確認"
    echo "  latest          - 最新データ生成バッチジョブ実行"
    echo "  production      - Production バッチジョブ実行"
    echo "  weekly          - Weekly メガバッチジョブ実行" 
    echo "  scheduler       - スケジューラー状況確認"
    echo "  logs [JOB_NAME] - バッチジョブログ確認"
    echo "  stats           - データ生成統計確認"
    echo "  future          - 未来予測データ統計確認"
    echo "  cleanup         - 失敗したジョブのクリーンアップ"
    echo "  help            - このヘルプを表示"
}

function show_status() {
    echo "📊 バッチジョブ状況確認"
    echo "========================"
    gcloud batch jobs list --location=us-central1 --limit=10
}

function run_latest() {
    echo "🔥 最新データ生成バッチジョブ実行"
    JOB_NAME="latest-data-batch-$(date +%Y%m%d-%H%M%S)"
    
    gcloud batch jobs submit $JOB_NAME \
      --config=latest-data-batch.yaml \
      --location=us-central1
    
    echo "✅ 最新データバッチジョブ投入完了: $JOB_NAME"
    echo "💫 予想生成データ数: 135,000件 (4,500銘柄 × 30件/銘柄)"
    echo "🎯 予測対象: 今日以降の未来データ"
}

function run_production() {
    echo "🚀 Production バッチジョブ実行"
    ./run-production-batch.sh
}

function run_weekly() {
    echo "🔥 Weekly メガバッチジョブ実行"
    JOB_NAME="weekly-mega-batch-$(date +%Y%m%d-%H%M%S)"
    
    gcloud batch jobs submit $JOB_NAME \
      --config=weekly-batch-job.yaml \
      --location=us-central1
    
    echo "✅ Weekly バッチジョブ投入完了: $JOB_NAME"
    echo "💫 予想生成データ数: 300,000件 (6,000銘柄 × 50件/銘柄)"
}

function show_scheduler() {
    echo "⏰ スケジューラー状況確認"
    echo "========================"
    gcloud scheduler jobs list --location=us-central1
}

function show_logs() {
    if [ -z "$2" ]; then
        echo "❌ ジョブ名を指定してください"
        echo "使用例: $0 logs production-batch-20250830-135142"
        return 1
    fi
    
    echo "📋 バッチジョブログ: $2"
    echo "========================"
    gcloud logging read "resource.type=batch_task AND jsonPayload.job_id=\"$2\"" --limit=100
}

function show_stats() {
    echo "📊 データ生成統計"
    echo "=================="
    
    python3 << 'EOF'
import pymysql
from datetime import datetime, timedelta

conn = pymysql.connect(
    host='34.58.103.36', 
    user='miraikakaku-user', 
    password='miraikakaku-secure-pass-2024', 
    database='miraikakaku', 
    charset='utf8mb4'
)
cursor = conn.cursor()

print('=== 全体統計 ===')
cursor.execute('SELECT COUNT(*) FROM stock_predictions')
total = cursor.fetchone()[0]
print(f'総予測データ数: {total:,}件')

cursor.execute('SELECT COUNT(DISTINCT symbol) FROM stock_predictions')
symbols = cursor.fetchone()[0]
print(f'予測対象銘柄数: {symbols:,}銘柄')

print('\n=== 今日の生成データ ===')
cursor.execute('SELECT COUNT(*) FROM stock_predictions WHERE DATE(created_at) = CURDATE()')
today = cursor.fetchone()[0]
print(f'今日生成されたデータ: {today:,}件')

print('\n=== 最近7日間の生成データ ===')
for i in range(7):
    date = datetime.now() - timedelta(days=i)
    cursor.execute('SELECT COUNT(*) FROM stock_predictions WHERE DATE(created_at) = %s', (date.strftime('%Y-%m-%d'),))
    count = cursor.fetchone()[0]
    print(f'{date.strftime("%m/%d")}: {count:,}件')

print('\n=== モデル別統計 (今日) ===')
cursor.execute('''
    SELECT model_type, COUNT(*) as cnt 
    FROM stock_predictions 
    WHERE DATE(created_at) = CURDATE() 
    GROUP BY model_type 
    ORDER BY cnt DESC 
    LIMIT 10
''')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]:,}件')

conn.close()
EOF
}

function show_future_stats() {
    echo "🔮 未来予測データ統計"
    echo "===================="
    
    python3 << 'EOF'
import pymysql
from datetime import datetime, timedelta

conn = pymysql.connect(
    host='34.58.103.36', 
    user='miraikakaku-user', 
    password='miraikakaku-secure-pass-2024', 
    database='miraikakaku', 
    charset='utf8mb4'
)
cursor = conn.cursor()

print('=== 未来予測データ統計 ===')
cursor.execute('SELECT COUNT(*) FROM stock_predictions WHERE prediction_date >= CURDATE()')
future_total = cursor.fetchone()[0]
print(f'未来予測データ総数: {future_total:,}件')

cursor.execute('SELECT COUNT(DISTINCT symbol) FROM stock_predictions WHERE prediction_date >= CURDATE()')
future_symbols = cursor.fetchone()[0]
print(f'未来予測対象銘柄数: {future_symbols:,}銘柄')

print('\n=== 今日生成の未来予測 ===')
today = datetime.now().strftime('%Y%m%d')
cursor.execute('SELECT COUNT(*) FROM stock_predictions WHERE notes LIKE %s AND prediction_date >= CURDATE()', (f'LatestBatch_{today}_%',))
today_future = cursor.fetchone()[0]
print(f'今日生成の未来予測: {today_future:,}件')

print('\n=== 予測期間別統計 (未来データ) ===')
for days in [1, 3, 7, 14, 30, 60, 90]:
    future_date = datetime.now() + timedelta(days=days)
    cursor.execute('SELECT COUNT(*) FROM stock_predictions WHERE DATE(prediction_date) = %s', (future_date.strftime('%Y-%m-%d'),))
    count = cursor.fetchone()[0]
    print(f'{days}日後 ({future_date.strftime("%m/%d")}): {count:,}件')

print('\n=== 最新モデル性能統計 ===')
cursor.execute('''
    SELECT model_type, AVG(confidence_score), COUNT(*) as cnt 
    FROM stock_predictions 
    WHERE prediction_date >= CURDATE() AND notes LIKE %s
    GROUP BY model_type 
    ORDER BY AVG(confidence_score) DESC
''', (f'LatestBatch_{today}_%',))
for row in cursor.fetchall():
    print(f'{row[0]}: 平均信頼度 {row[1]:.3f} ({row[2]:,}件)')

conn.close()
EOF
}

function cleanup_jobs() {
    echo "🧹 失敗ジョブクリーンアップ"
    echo "=========================="
    
    # 失敗したジョブの一覧取得
    FAILED_JOBS=$(gcloud batch jobs list --location=us-central1 --filter="status.state:FAILED" --format="value(name)")
    
    if [ -z "$FAILED_JOBS" ]; then
        echo "✅ クリーンアップが必要な失敗ジョブはありません"
        return 0
    fi
    
    echo "以下の失敗ジョブを削除します:"
    echo "$FAILED_JOBS"
    
    read -p "削除を続行しますか？ (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for job in $FAILED_JOBS; do
            echo "削除中: $job"
            gcloud batch jobs delete "$job" --location=us-central1 --quiet
        done
        echo "✅ クリーンアップ完了"
    else
        echo "❌ クリーンアップをキャンセルしました"
    fi
}

# メインロジック
case "${1:-help}" in
    status)
        show_status
        ;;
    latest)
        run_latest
        ;;
    production)
        run_production
        ;;
    weekly)
        run_weekly
        ;;
    scheduler)
        show_scheduler
        ;;
    logs)
        show_logs "$@"
        ;;
    stats)
        show_stats
        ;;
    future)
        show_future_stats
        ;;
    cleanup)
        cleanup_jobs
        ;;
    help|*)
        show_help
        ;;
esac