#!/bin/bash

# CloudSQL to BigQuery Connection Setup Script
# Setup federated queries and data transfer from CloudSQL

PROJECT_ID="miraikakaku-project"
REGION="asia-northeast1"
CONNECTION_ID="cloudsql-connection"
DATASET="miraikakaku_analytics"

echo "🔗 Setting up CloudSQL to BigQuery Connection"
echo "============================================="

# 1. Cloud Resource Manager API有効化
echo "Enabling required APIs..."
gcloud services enable bigqueryconnection.googleapis.com
gcloud services enable bigquerydatatransfer.googleapis.com

# 2. BigQuery Connection作成
echo "Creating BigQuery connection to CloudSQL..."
bq mk --connection \
    --display_name="Miraikakaku CloudSQL Connection" \
    --connection_type=CLOUD_SQL \
    --properties='{"instanceId":"'"$PROJECT_ID:$REGION:postgres-main"'","database":"miraikakaku","type":"POSTGRES"}' \
    --connection_credential='{"username":"postgres"}' \
    --project_id=$PROJECT_ID \
    --location=$REGION \
    $CONNECTION_ID

# 3. Connection Service Accountに権限付与
echo "Granting permissions to connection service account..."
CONNECTION_SA=$(bq show --connection --project_id=$PROJECT_ID --location=$REGION $CONNECTION_ID | grep serviceAccountId | cut -d'"' -f4)

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CONNECTION_SA" \
    --role="roles/cloudsql.client"

# 4. CloudSQL Proxyセットアップ用のサービスアカウント作成
echo "Creating service account for CloudSQL Proxy..."
gcloud iam service-accounts create cloudsql-proxy \
    --display-name="CloudSQL Proxy Service Account" \
    --project=$PROJECT_ID

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloudsql-proxy@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# 5. BigQuery External Data Source設定
echo "Setting up external data source..."
bq mk --external_data_source \
    --source_format=CLOUD_SQL \
    --connection_id=$PROJECT_ID.$REGION.$CONNECTION_ID \
    $PROJECT_ID:$DATASET.ext_stock_prices

# 6. Scheduled Query作成（日次データ同期）
echo "Creating scheduled queries for data synchronization..."

# Stock Prices同期
bq mk --transfer_config \
    --project_id=$PROJECT_ID \
    --data_source=scheduled_query \
    --display_name="Daily Stock Prices Sync" \
    --target_dataset=$DATASET \
    --schedule="every day 02:00" \
    --params='{
        "query": "INSERT INTO `'"$PROJECT_ID.$DATASET"'.stock_prices` (symbol, date, open_price, high_price, low_price, close_price, volume, created_at) SELECT symbol, date, open_price, high_price, low_price, close_price, volume, created_at FROM EXTERNAL_QUERY(\"'"$PROJECT_ID.$REGION.$CONNECTION_ID"'\", \"SELECT symbol, date, open_price, high_price, low_price, close_price, volume, created_at FROM stock_prices WHERE date >= CURRENT_DATE - 1\");",
        "use_legacy_sql": false,
        "write_disposition": "WRITE_APPEND"
    }'

# Stock Predictions同期
bq mk --transfer_config \
    --project_id=$PROJECT_ID \
    --data_source=scheduled_query \
    --display_name="Daily Stock Predictions Sync" \
    --target_dataset=$DATASET \
    --schedule="every day 02:30" \
    --params='{
        "query": "INSERT INTO `'"$PROJECT_ID.$DATASET"'.stock_predictions` (symbol, prediction_date, prediction_days, current_price, predicted_price, confidence_score, model_version, model_type, prediction_horizon, features_used, is_active, created_at) SELECT symbol, prediction_date, prediction_days, current_price, predicted_price, confidence_score, model_version, model_type, prediction_horizon, features_used, is_active, created_at FROM EXTERNAL_QUERY(\"'"$PROJECT_ID.$REGION.$CONNECTION_ID"'\", \"SELECT symbol, prediction_date, prediction_days, current_price, predicted_price, confidence_score, model_version, model_type, prediction_horizon, features_used, is_active, created_at FROM stock_predictions WHERE prediction_date >= CURRENT_DATE - 1\");",
        "use_legacy_sql": false,
        "write_disposition": "WRITE_APPEND"
    }'

# 7. 初回データ移行（履歴データ）
echo "Performing initial data migration..."
bq query --use_legacy_sql=false \
    "INSERT INTO \`$PROJECT_ID.$DATASET.stock_prices\` (symbol, date, open_price, high_price, low_price, close_price, volume, created_at)
    SELECT symbol, date, open_price, high_price, low_price, close_price, volume, created_at
    FROM EXTERNAL_QUERY('$PROJECT_ID.$REGION.$CONNECTION_ID',
        'SELECT symbol, date, open_price, high_price, low_price, close_price, volume, created_at
         FROM stock_prices
         WHERE date >= CURRENT_DATE - 90
         ORDER BY date DESC')"

bq query --use_legacy_sql=false \
    "INSERT INTO \`$PROJECT_ID.$DATASET.stock_predictions\` (symbol, prediction_date, prediction_days, current_price, predicted_price, confidence_score, model_version, model_type, prediction_horizon, features_used, is_active, created_at)
    SELECT symbol, prediction_date, prediction_days, current_price, predicted_price, confidence_score, model_version, model_type, prediction_horizon, features_used, is_active, created_at
    FROM EXTERNAL_QUERY('$PROJECT_ID.$REGION.$CONNECTION_ID',
        'SELECT symbol, prediction_date, prediction_days, current_price, predicted_price, confidence_score, model_version, model_type, prediction_horizon, features_used, is_active, created_at
         FROM stock_predictions
         WHERE prediction_date >= CURRENT_DATE - 30
         ORDER BY prediction_date DESC')"

echo ""
echo "✅ CloudSQL to BigQuery connection setup completed!"
echo ""
echo "🔗 Connection ID: $CONNECTION_ID"
echo "📊 Dataset: $PROJECT_ID:$DATASET"
echo "🔄 Scheduled transfers: Daily at 02:00 and 02:30 JST"
echo ""
echo "📈 Monitoring:"
echo "   Data Transfer Jobs: https://console.cloud.google.com/bigquery/transfers?project=$PROJECT_ID"
echo "   Connection Status: https://console.cloud.google.com/bigquery/connections?project=$PROJECT_ID"