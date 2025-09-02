#!/bin/bash
# API修正デプロイスクリプト
# stock_predictions エンドポイントのデータベース接続修正

PROJECT_ID="pricewise-huqkr"
SERVICE_NAME="miraikakaku-api"
REGION="us-central1"

echo "🚀 API修正をデプロイ中..."
echo "修正内容:"
echo "  - get_predictions_from_db: データベースセッション管理修正"
echo "  - /api/ai/predictions: stock_predictionsテーブルからのデータ取得"
echo ""

# 1. Docker イメージのビルド
echo "📦 Dockerイメージをビルド中..."
cd /mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakuapi

gcloud builds submit \
    --tag "gcr.io/${PROJECT_ID}/${SERVICE_NAME}:fixed-predictions" \
    --project="${PROJECT_ID}" \
    --timeout=30m

if [ $? -ne 0 ]; then
    echo "❌ ビルドに失敗しました"
    exit 1
fi

# 2. Cloud Runへのデプロイ
echo "🌐 Cloud Runにデプロイ中..."
gcloud run deploy ${SERVICE_NAME} \
    --image "gcr.io/${PROJECT_ID}/${SERVICE_NAME}:fixed-predictions" \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 60 \
    --max-instances 10 \
    --set-env-vars="DATABASE_URL=mysql+pymysql://miraikakaku-user:miraikakaku-secure-pass-2024@34.58.103.36/miraikakaku" \
    --set-env-vars="CLOUD_SQL_CONNECTION_NAME=${PROJECT_ID}:${REGION}:miraikakaku" \
    --add-cloudsql-instances="${PROJECT_ID}:${REGION}:miraikakaku" \
    --project="${PROJECT_ID}"

if [ $? -ne 0 ]; then
    echo "❌ デプロイに失敗しました"
    exit 1
fi

# 3. デプロイ結果確認
echo ""
echo "✅ デプロイ完了！"
echo ""
echo "📊 APIエンドポイント確認:"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)" --project="${PROJECT_ID}")
echo "  URL: ${SERVICE_URL}"
echo ""
echo "🧪 テストコマンド:"
echo "  # 予測データ取得（データベース）"
echo "  curl '${SERVICE_URL}/api/ai/predictions?limit=10'"
echo ""
echo "  # 株価予測取得"
echo "  curl '${SERVICE_URL}/api/finance/stocks/AAPL/predictions?days=7'"
echo ""
echo "  # ヘルスチェック"
echo "  curl '${SERVICE_URL}/api/health'"
echo ""
echo "📝 修正内容:"
echo "  1. get_predictions_from_db関数:"
echo "     - db_manager.get_session()でセッション取得"
echo "     - StockDataRepositoryにセッション渡す"
echo "     - finally節でセッションクローズ"
echo ""
echo "  2. /api/ai/predictionsエンドポイント:"
echo "     - stock_predictionsテーブルから直接クエリ"
echo "     - データベース接続失敗時はモックデータにフォールバック"
echo "     - data_sourceフィールドでデータ元を表示"
echo ""
echo "🎯 完了!"