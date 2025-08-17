#!/bin/bash

# Miraikakaku 統一開発環境起動スクリプト

set -e

echo "🚀 Miraikakaku 統一開発環境を起動中..."

# 環境変数の確認
if [ ! -f "../miraikakakufront/.env" ]; then
    echo "⚠️  フロントエンドの.envファイルが見つかりません"
    echo "📝 .env.exampleをコピーして.envを作成してください"
fi

if [ ! -f "../miraikakakuapi/.env" ]; then
    echo "⚠️  APIサーバーの.envファイルが見つかりません" 
    echo "📝 .env.exampleをコピーして.envを作成してください"
fi

# Docker サービス起動（MySQL、Redis、監視システム）
echo "📦 インフラサービスを起動中..."
docker-compose up -d mysql redis prometheus grafana elasticsearch kibana

# データベース接続待機
echo "⏳ データベース接続を待機中..."
sleep 15

# 共有パッケージビルド
echo "📦 共有パッケージをビルド中..."
npm run build:shared

# APIサーバー起動
echo "🔌 APIサーバーを起動中..."
cd ../miraikakakuapi/functions
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# フロントエンド起動
echo "🎨 フロントエンドを起動中..."
cd ../../miraikakakufront
npm run dev &
FRONTEND_PID=$!

echo "✅ 統一開発環境が起動しました"
echo ""
echo "📍 アクセスURL:"
echo "   🎨 フロントエンド: http://localhost:3000"
echo "   🔌 API: http://localhost:8000"
echo "   📊 Grafana: http://localhost:3001 (admin/admin)"
echo "   🔍 Kibana: http://localhost:5601"
echo "   📈 Prometheus: http://localhost:9090"
echo ""
echo "🛑 停止するには Ctrl+C を押してください"

# シグナルハンドリング
trap 'echo "🛑 サービスを停止中..."; kill $API_PID $FRONTEND_PID; cd ../../miraikakakumonorepo; docker-compose down; exit 0' INT

# プロセスの監視
wait