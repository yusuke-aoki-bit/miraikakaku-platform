#!/bin/bash

# BigQuery セットアップスクリプト
# Setup BigQuery for data analytics

PROJECT_ID="miraikakaku-project"
DATASET="miraikakaku_analytics"
REGION="asia-northeast1"

echo "📊 Setting up BigQuery Analytics"
echo "================================"

# 1. BigQueryデータセット作成
echo "Creating BigQuery dataset..."
bq mk --dataset \
    --location=$REGION \
    --description="Miraikakaku analytics dataset" \
    $PROJECT_ID:$DATASET

# 2. テーブル作成
echo "Creating tables..."

# 価格データテーブル
bq mk --table \
    $PROJECT_ID:$DATASET.stock_prices \
    bigquery/schemas/stock_prices.json

# 予想データテーブル
bq mk --table \
    $PROJECT_ID:$DATASET.stock_predictions \
    bigquery/schemas/stock_predictions.json

# 精度追跡テーブル
bq mk --table \
    $PROJECT_ID:$DATASET.prediction_accuracy \
    bigquery/schemas/prediction_accuracy.json

# パフォーマンスメトリクステーブル
bq mk --table \
    $PROJECT_ID:$DATASET.performance_metrics \
    bigquery/schemas/performance_metrics.json

# 3. CloudSQL → BigQuery データ転送設定
echo "Setting up data transfer from CloudSQL..."
bq mk --transfer_config \
    --project_id=$PROJECT_ID \
    --data_source=scheduled_query \
    --display_name="Daily Stock Price Sync" \
    --target_dataset=$DATASET \
    --schedule="every day 02:00" \
    --params='{
        "query": "SELECT * FROM EXTERNAL_QUERY(\"projects/'$PROJECT_ID'/locations/asia-northeast1/connections/cloudsql-connection\", \"SELECT * FROM stock_prices WHERE date >= CURRENT_DATE - 1\")",
        "destination_table_name_template": "stock_prices",
        "write_disposition": "WRITE_APPEND"
    }'

# 4. ビュー作成
echo "Creating analytical views..."

# 日次パフォーマンスビュー
bq mk --use_legacy_sql=false --view \
    "SELECT
        DATE(prediction_date) as date,
        COUNT(DISTINCT symbol) as symbols_predicted,
        AVG(confidence_score) as avg_confidence,
        AVG((predicted_price - current_price) / current_price) as avg_predicted_change
    FROM \`$PROJECT_ID.$DATASET.stock_predictions\`
    GROUP BY DATE(prediction_date)
    ORDER BY date DESC" \
    $PROJECT_ID:$DATASET.daily_performance

# トップパフォーマービュー
bq mk --use_legacy_sql=false --view \
    "SELECT
        symbol,
        COUNT(*) as prediction_count,
        AVG(accuracy_score) as avg_accuracy,
        AVG(ABS(predicted_change - actual_change)) as avg_error
    FROM \`$PROJECT_ID.$DATASET.prediction_accuracy\`
    WHERE evaluation_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    GROUP BY symbol
    HAVING prediction_count >= 5
    ORDER BY avg_accuracy DESC
    LIMIT 20" \
    $PROJECT_ID:$DATASET.top_performers

# 価格トレンド分析ビュー
bq mk --use_legacy_sql=false --view \
    "SELECT
        symbol,
        date,
        close_price,
        LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date) as prev_close,
        (close_price - LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date)) / LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date) * 100 as daily_return,
        AVG(close_price) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as ma_20,
        AVG(close_price) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) as ma_50
    FROM \`$PROJECT_ID.$DATASET.stock_prices\`
    WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
    ORDER BY symbol, date DESC" \
    $PROJECT_ID:$DATASET.price_trends

# 予測精度分析ビュー
bq mk --use_legacy_sql=false --view \
    "SELECT
        DATE_TRUNC(evaluation_date, WEEK) as week,
        model_type,
        COUNT(*) as total_predictions,
        AVG(accuracy_score) as avg_accuracy,
        AVG(ABS(predicted_change - actual_change)) as avg_absolute_error,
        SUM(CASE WHEN directional_accuracy THEN 1 ELSE 0 END) / COUNT(*) * 100 as directional_accuracy_pct,
        AVG(CASE WHEN evaluation_days = 1 THEN accuracy_score END) as accuracy_1d,
        AVG(CASE WHEN evaluation_days = 7 THEN accuracy_score END) as accuracy_7d
    FROM \`$PROJECT_ID.$DATASET.prediction_accuracy\`
    WHERE evaluation_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
    GROUP BY week, model_type
    ORDER BY week DESC, avg_accuracy DESC" \
    $PROJECT_ID:$DATASET.accuracy_trends

# システム健全性ダッシュボードビュー
bq mk --use_legacy_sql=false --view \
    "SELECT
        metric_date,
        MAX(CASE WHEN metric_name = 'prediction_coverage' THEN metric_value END) as prediction_coverage_pct,
        MAX(CASE WHEN metric_name = 'data_freshness' THEN metric_value END) as data_freshness_hours,
        MAX(CASE WHEN metric_name = 'api_response_time' THEN metric_value END) as api_response_ms,
        MAX(CASE WHEN metric_name = 'prediction_accuracy' THEN metric_value END) as avg_accuracy_pct,
        MAX(CASE WHEN metric_name = 'system_uptime' THEN metric_value END) as uptime_pct
    FROM \`$PROJECT_ID.$DATASET.performance_metrics\`
    WHERE metric_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    GROUP BY metric_date
    ORDER BY metric_date DESC" \
    $PROJECT_ID:$DATASET.system_health

echo ""
echo "✅ BigQuery setup completed!"
echo ""
echo "📊 Dataset: $PROJECT_ID:$DATASET"
echo "📈 Analytics Console: https://console.cloud.google.com/bigquery?project=$PROJECT_ID"