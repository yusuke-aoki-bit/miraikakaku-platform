#!/bin/bash
# Cloud SQL Proxyセットアップスクリプト
# ローカル環境からCloud SQLへの安全な接続を確立

PROJECT_ID="pricewise-huqkr"
INSTANCE_NAME="miraikakaku"
REGION="us-central1"
PORT="3306"

echo "🔧 Cloud SQL Proxyセットアップ"
echo "================================"

# 1. Cloud SQL Proxyのダウンロード（未インストールの場合）
if ! command -v cloud-sql-proxy &> /dev/null; then
    echo "📥 Cloud SQL Proxyをダウンロード中..."
    
    # OSを判定
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "linux" ]]; then
        curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.11.4/cloud-sql-proxy.linux.amd64
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.11.4/cloud-sql-proxy.darwin.amd64
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        curl -o cloud-sql-proxy.exe https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.11.4/cloud-sql-proxy.x64.exe
    fi
    
    chmod +x cloud-sql-proxy*
    echo "✅ Cloud SQL Proxyダウンロード完了"
fi

# 2. 認証確認
echo "🔐 認証状態を確認中..."
gcloud auth list --filter=status:ACTIVE --format="value(account)"

if [ $? -ne 0 ]; then
    echo "⚠️ gcloud認証が必要です"
    echo "実行: gcloud auth login"
    exit 1
fi

# 3. Cloud SQL Admin APIを有効化
echo "📡 Cloud SQL Admin APIを有効化..."
gcloud services enable sqladmin.googleapis.com --project="${PROJECT_ID}"

# 4. IAM権限の確認と設定
echo "🔑 IAM権限を確認中..."
CURRENT_USER=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
echo "現在のユーザー: ${CURRENT_USER}"

# Cloud SQL Client権限を付与
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="user:${CURRENT_USER}" \
    --role="roles/cloudsql.client" \
    --quiet 2>/dev/null

# 5. Cloud SQL Proxyを起動
echo ""
echo "🚀 Cloud SQL Proxyを起動します..."
echo "接続文字列: ${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"
echo ""

# 既存のプロキシプロセスを終了
pkill -f cloud-sql-proxy 2>/dev/null

# バックグラウンドで起動
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    ./cloud-sql-proxy.exe --port ${PORT} ${PROJECT_ID}:${REGION}:${INSTANCE_NAME} &
else
    ./cloud-sql-proxy --port ${PORT} ${PROJECT_ID}:${REGION}:${INSTANCE_NAME} &
fi

PROXY_PID=$!
echo "✅ Cloud SQL Proxy起動 (PID: ${PROXY_PID})"

# 6. 接続テスト用のPythonスクリプトを生成
cat > test_local_connection.py << 'EOF'
#!/usr/bin/env python3
import pymysql
import sys

db_config = {
    "host": "127.0.0.1",  # Proxy経由でローカル接続
    "port": 3306,
    "user": "miraikakaku-user",
    "password": "miraikakaku-secure-pass-2024",
    "database": "miraikakaku",
    "charset": "utf8mb4"
}

try:
    print("🔄 ローカルプロキシ経由で接続中...")
    connection = pymysql.connect(**db_config)
    
    with connection.cursor() as cursor:
        # 接続テスト
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"✅ 接続成功！ MySQL Version: {version}")
        
        # データ統計を取得
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM stock_master WHERE is_active = 1) as total_stocks,
                (SELECT COUNT(DISTINCT symbol) FROM stock_price_history) as stocks_with_data,
                (SELECT COUNT(*) FROM stock_predictions) as total_predictions,
                (SELECT COUNT(*) FROM unfetchable_stocks) as unfetchable_count
        """)
        
        total, with_data, predictions, unfetchable = cursor.fetchone()
        
        print("\n📊 データベース統計:")
        print(f"  - 総銘柄数: {total:,}")
        print(f"  - データあり: {with_data:,}")
        print(f"  - 予測データ: {predictions:,}")
        print(f"  - 取得不可: {unfetchable:,}")
        
        if total > 0:
            coverage = (with_data / total * 100)
            effective = ((with_data + unfetchable) / total * 100)
            print(f"  - カバー率: {coverage:.1f}%")
            print(f"  - 実質カバー率: {effective:.1f}%")
    
    connection.close()
    print("\n🎉 ローカル接続テスト成功！")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ 接続エラー: {e}")
    sys.exit(1)
EOF

# 7. 接続テスト実行
sleep 3  # Proxyの起動を待つ
echo ""
echo "🧪 接続テストを実行..."
python3 test_local_connection.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ セットアップ完了！"
    echo ""
    echo "📝 今後の使い方:"
    echo "  1. プロキシ起動: ./cloud-sql-proxy --port ${PORT} ${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"
    echo "  2. 接続設定:"
    echo "     - Host: 127.0.0.1"
    echo "     - Port: ${PORT}"
    echo "     - User: miraikakaku-user"
    echo "     - Password: miraikakaku-secure-pass-2024"
    echo "     - Database: miraikakaku"
    echo ""
    echo "⚠️ 注意: プロキシはバックグラウンドで実行中 (PID: ${PROXY_PID})"
    echo "  終了する場合: kill ${PROXY_PID}"
else
    echo ""
    echo "❌ 接続テスト失敗"
    echo "プロキシを終了します..."
    kill ${PROXY_PID} 2>/dev/null
    exit 1
fi