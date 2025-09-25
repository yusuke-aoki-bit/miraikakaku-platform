-- Miraikakaku Analytics Dashboard Queries
-- Comprehensive analytics queries for the BigQuery data warehouse

-- 1. Executive Summary Dashboard
CREATE OR REPLACE VIEW `miraikakaku-project.miraikakaku_analytics.executive_summary` AS
SELECT
  'System Overview' as section,
  CURRENT_DATE() as report_date,
  (SELECT COUNT(DISTINCT symbol) FROM `miraikakaku-project.miraikakaku_analytics.stock_prices` WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)) as active_symbols,
  (SELECT COUNT(*) FROM `miraikakaku-project.miraikakaku_analytics.stock_predictions` WHERE prediction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)) as weekly_predictions,
  (SELECT AVG(accuracy_score) FROM `miraikakaku-project.miraikakaku_analytics.prediction_accuracy` WHERE evaluation_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)) as avg_accuracy_30d,
  (SELECT COUNT(*) FROM `miraikakaku-project.miraikakaku_analytics.stock_prices` WHERE created_at >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)) as data_points_24h;

-- 2. Top Performing Predictions
CREATE OR REPLACE VIEW `miraikakaku-project.miraikakaku_analytics.top_predictions` AS
SELECT
  pa.symbol,
  sp.close_price as current_price,
  pa.predicted_price,
  pa.actual_price,
  pa.accuracy_score,
  pa.directional_accuracy,
  pa.evaluation_date,
  CASE
    WHEN pa.directional_accuracy THEN 'Correct Direction'
    ELSE 'Wrong Direction'
  END as direction_result,
  ABS(pa.predicted_change - pa.actual_change) as prediction_error
FROM `miraikakaku-project.miraikakaku_analytics.prediction_accuracy` pa
LEFT JOIN `miraikakaku-project.miraikakaku_analytics.stock_prices` sp
  ON pa.symbol = sp.symbol
  AND sp.date = pa.evaluation_date
WHERE pa.evaluation_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  AND pa.accuracy_score >= 0.7
ORDER BY pa.accuracy_score DESC, pa.evaluation_date DESC
LIMIT 50;

-- 3. Market Sector Performance Analysis
CREATE OR REPLACE VIEW `miraikakaku-project.miraikakaku_analytics.sector_performance` AS
SELECT
  CASE
    WHEN symbol LIKE '%.T' THEN 'Japan Stocks'
    WHEN symbol IN ('AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA') THEN 'Tech Giants'
    WHEN symbol LIKE '%USD' OR symbol LIKE '%JPY' THEN 'Forex'
    WHEN symbol LIKE 'BTC%' OR symbol LIKE 'ETH%' THEN 'Crypto'
    ELSE 'Other'
  END as sector,
  COUNT(DISTINCT symbol) as symbol_count,
  AVG(daily_return) as avg_daily_return,
  STDDEV(daily_return) as volatility,
  MAX(close_price/prev_close - 1) * 100 as max_daily_gain,
  MIN(close_price/prev_close - 1) * 100 as max_daily_loss
FROM `miraikakaku-project.miraikakaku_analytics.price_trends`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND prev_close IS NOT NULL
GROUP BY sector
ORDER BY avg_daily_return DESC;

-- 4. Prediction Model Comparison
CREATE OR REPLACE VIEW `miraikakaku-project.miraikakaku_analytics.model_comparison` AS
SELECT
  model_type,
  COUNT(*) as total_predictions,
  AVG(accuracy_score) as avg_accuracy,
  AVG(ABS(predicted_change - actual_change)) as mean_absolute_error,
  STDDEV(accuracy_score) as accuracy_std,
  SUM(CASE WHEN directional_accuracy THEN 1 ELSE 0 END) / COUNT(*) * 100 as directional_accuracy_pct,
  AVG(CASE WHEN evaluation_days = 1 THEN accuracy_score END) as accuracy_1day,
  AVG(CASE WHEN evaluation_days = 7 THEN accuracy_score END) as accuracy_7day,
  MAX(evaluation_date) as last_evaluation
FROM `miraikakaku-project.miraikakaku_analytics.prediction_accuracy`
WHERE evaluation_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY model_type
ORDER BY avg_accuracy DESC;

-- 5. Data Quality Metrics
CREATE OR REPLACE VIEW `miraikakaku-project.miraikakaku_analytics.data_quality` AS
SELECT
  'Price Data' as data_type,
  COUNT(*) as total_records,
  COUNT(CASE WHEN open_price IS NULL THEN 1 END) as missing_open,
  COUNT(CASE WHEN high_price IS NULL THEN 1 END) as missing_high,
  COUNT(CASE WHEN low_price IS NULL THEN 1 END) as missing_low,
  COUNT(CASE WHEN close_price IS NULL THEN 1 END) as missing_close,
  COUNT(CASE WHEN volume IS NULL THEN 1 END) as missing_volume,
  MAX(date) as latest_data_date,
  DATE_DIFF(CURRENT_DATE(), MAX(date), DAY) as days_since_update
FROM `miraikakaku-project.miraikakaku_analytics.stock_prices`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)

UNION ALL

SELECT
  'Prediction Data' as data_type,
  COUNT(*) as total_records,
  COUNT(CASE WHEN current_price IS NULL THEN 1 END) as missing_current_price,
  COUNT(CASE WHEN predicted_price IS NULL THEN 1 END) as missing_predicted_price,
  COUNT(CASE WHEN confidence_score IS NULL THEN 1 END) as missing_confidence,
  COUNT(CASE WHEN model_type IS NULL THEN 1 END) as missing_model_type,
  COUNT(CASE WHEN is_active IS NULL THEN 1 END) as missing_active_flag,
  MAX(prediction_date) as latest_prediction_date,
  DATE_DIFF(CURRENT_DATE(), MAX(prediction_date), DAY) as days_since_prediction
FROM `miraikakaku-project.miraikakaku_analytics.stock_predictions`
WHERE prediction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY);

-- 6. Alert Conditions
CREATE OR REPLACE VIEW `miraikakaku-project.miraikakaku_analytics.system_alerts` AS
SELECT
  'Data Freshness' as alert_type,
  'WARNING' as severity,
  CONCAT('Price data is ', DATE_DIFF(CURRENT_DATE(), MAX(date), DAY), ' days old') as message,
  MAX(date) as last_update
FROM `miraikakaku-project.miraikakaku_analytics.stock_prices`
WHERE DATE_DIFF(CURRENT_DATE(), MAX(date), DAY) > 1

UNION ALL

SELECT
  'Prediction Coverage' as alert_type,
  'INFO' as severity,
  CONCAT('Coverage: ', ROUND(COUNT(DISTINCT symbol) * 100.0 / (SELECT COUNT(DISTINCT symbol) FROM `miraikakaku-project.miraikakaku_analytics.stock_prices`), 1), '%') as message,
  MAX(prediction_date) as last_update
FROM `miraikakaku-project.miraikakaku_analytics.stock_predictions`
WHERE prediction_date >= CURRENT_DATE()

UNION ALL

SELECT
  'Model Accuracy' as alert_type,
  CASE
    WHEN AVG(accuracy_score) < 0.5 THEN 'CRITICAL'
    WHEN AVG(accuracy_score) < 0.6 THEN 'WARNING'
    ELSE 'GOOD'
  END as severity,
  CONCAT('7-day accuracy: ', ROUND(AVG(accuracy_score) * 100, 1), '%') as message,
  MAX(evaluation_date) as last_update
FROM `miraikakaku-project.miraikakaku_analytics.prediction_accuracy`
WHERE evaluation_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY);

-- 7. Performance Trending
CREATE OR REPLACE VIEW `miraikakaku-project.miraikakaku_analytics.performance_trends` AS
SELECT
  DATE_TRUNC(metric_date, WEEK) as week,
  AVG(CASE WHEN metric_name = 'prediction_accuracy' THEN metric_value END) as avg_accuracy,
  AVG(CASE WHEN metric_name = 'api_response_time' THEN metric_value END) as avg_response_time,
  AVG(CASE WHEN metric_name = 'system_uptime' THEN metric_value END) as avg_uptime,
  AVG(CASE WHEN metric_name = 'prediction_coverage' THEN metric_value END) as avg_coverage,
  COUNT(DISTINCT metric_date) as active_days
FROM `miraikakaku-project.miraikakaku_analytics.performance_metrics`
WHERE metric_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY week
ORDER BY week DESC;

-- 8. Symbol Ranking by Performance
CREATE OR REPLACE VIEW `miraikakaku-project.miraikakaku_analytics.symbol_rankings` AS
WITH symbol_stats AS (
  SELECT
    pt.symbol,
    AVG(pt.daily_return) as avg_return,
    STDDEV(pt.daily_return) as volatility,
    COUNT(*) as trading_days,
    AVG(pa.accuracy_score) as prediction_accuracy,
    COUNT(pa.symbol) as prediction_count
  FROM `miraikakaku-project.miraikakaku_analytics.price_trends` pt
  LEFT JOIN `miraikakaku-project.miraikakaku_analytics.prediction_accuracy` pa
    ON pt.symbol = pa.symbol
    AND pt.date = pa.evaluation_date
  WHERE pt.date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY pt.symbol
)
SELECT
  symbol,
  avg_return,
  volatility,
  CASE
    WHEN volatility > 0 THEN avg_return / volatility
    ELSE 0
  END as sharpe_ratio,
  prediction_accuracy,
  prediction_count,
  trading_days,
  RANK() OVER (ORDER BY avg_return DESC) as return_rank,
  RANK() OVER (ORDER BY prediction_accuracy DESC) as accuracy_rank
FROM symbol_stats
WHERE trading_days >= 20
  AND prediction_count >= 5
ORDER BY sharpe_ratio DESC;