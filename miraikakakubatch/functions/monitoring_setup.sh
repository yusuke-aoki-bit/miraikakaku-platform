#!/bin/bash
# バッチジョブのモニタリングとアラート設定

PROJECT_ID="pricewise-huqkr"

echo "📊 バッチジョブ監視設定を開始..."

# 1. Monitoring APIを有効化
gcloud services enable monitoring.googleapis.com

# 2. 基本的なメトリクス表示コマンド
cat > monitor_batch_status.sh << 'EOF'
#!/bin/bash
echo "🔍 バッチジョブ監視レポート - $(date)"
echo "======================================"

# 最近のバッチジョブ状況
echo "📊 過去24時間のバッチジョブ:"
gcloud batch jobs list --location=us-central1 --filter="createTime>-P1D" --format="table(name.segment(-1):label=JOB_NAME,status.state:label=STATUS,createTime.date():label=CREATED)"

# データ収集統計をチェック
echo ""
echo "📈 データ収集統計:"
python3 -c "
import pymysql
import os
from datetime import datetime, timedelta

db_config = {
    'host': '34.58.103.36',
    'user': 'miraikakaku-user', 
    'password': 'miraikakaku-secure-pass-2024',
    'database': 'miraikakaku',
    'charset': 'utf8mb4'
}

connection = pymysql.connect(**db_config)
with connection.cursor() as cursor:
    # 過去1時間の統計
    cursor.execute('''
        SELECT COUNT(*) FROM stock_price_history 
        WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
    ''')
    hourly = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM unfetchable_stocks 
        WHERE attempted_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
    ''')
    hourly_unfetchable = cursor.fetchone()[0]
    
    # 全体統計
    cursor.execute('''
        SELECT 
            (SELECT COUNT(*) FROM stock_master WHERE is_active = 1) as total,
            (SELECT COUNT(DISTINCT sm.symbol) FROM stock_master sm JOIN stock_price_history sph ON sm.symbol = sph.symbol WHERE sm.is_active = 1) as covered,
            (SELECT COUNT(*) FROM unfetchable_stocks) as unfetchable
    ''')
    total, covered, unfetchable = cursor.fetchone()
    coverage = (covered / total * 100) if total > 0 else 0
    effective = ((covered + unfetchable) / total * 100) if total > 0 else 0
    
    print(f'  - 過去1時間: {hourly:,}件の新規データ')
    print(f'  - 過去1時間: {hourly_unfetchable:,}件のunfetchable')
    print(f'  - 実データカバー率: {coverage:.1f}%')
    print(f'  - 実質カバー率: {effective:.1f}%')
    print(f'  - 残り未処理: {total - covered - unfetchable:,}銘柄')

connection.close()
" 2>/dev/null || echo "データベース接続エラー"

echo ""
echo "⏰ 次回実行予定:"
gcloud scheduler jobs list --location=us-central1 --filter="name:miraikakaku-hourly" --format="table(name.segment(-1):label=SCHEDULER,schedule:label=CRON,nextRunTime:label=NEXT_RUN)"
EOF

chmod +x monitor_batch_status.sh

echo "✅ 監視スクリプト作成完了: ./monitor_batch_status.sh"

# 3. 簡易アラート設定（ログベース）
echo ""
echo "🚨 アラート設定："
echo "   以下のコマンドでバッチ失敗時にアラートを確認できます:"
echo "   gcloud logging read 'resource.type=batch.googleapis.com/Job AND severity=ERROR' --limit=10"

echo ""
echo "📅 定期監視の推奨設定:"
echo "   crontab -e で以下を追加:"
echo "   0 */2 * * * /path/to/monitor_batch_status.sh >> /var/log/batch_monitor.log"

echo ""
echo "✅ 監視設定完了！"