-- Miraikakaku データ投入状況確認
USE miraikakaku_prod;

-- 1. マスターデータの投入状況
SELECT 
    'Master Data Status' as category,
    COUNT(*) as total_records,
    COUNT(DISTINCT country) as countries,
    COUNT(DISTINCT market) as markets
FROM stock_master;

-- 2. 国別・市場別の詳細
SELECT 
    country,
    market,
    COUNT(*) as count
FROM stock_master
GROUP BY country, market
ORDER BY country, count DESC;

-- 3. セクター別集計（ETF含む）
SELECT 
    sector,
    COUNT(*) as count
FROM stock_master
WHERE sector IN ('ETF', 'Equity', 'Bond', 'Commodity')
GROUP BY sector
ORDER BY count DESC;

-- 4. 価格データの投入状況確認
SELECT 
    'Price Data Status' as category,
    COUNT(DISTINCT symbol) as unique_symbols,
    COUNT(*) as total_price_records,
    MIN(date) as earliest_date,
    MAX(date) as latest_date
FROM stock_prices;

-- 5. 予測データの投入状況
SELECT 
    'Prediction Data Status' as category,
    COUNT(DISTINCT symbol) as symbols_with_predictions,
    COUNT(*) as total_predictions,
    MIN(prediction_date) as earliest_prediction,
    MAX(prediction_date) as latest_prediction
FROM stock_predictions;

-- 6. バッチログ確認
SELECT 
    batch_type,
    status,
    COUNT(*) as count,
    MAX(start_time) as last_run
FROM batch_logs
GROUP BY batch_type, status
ORDER BY last_run DESC;

-- 7. 分析レポート確認
SELECT 
    report_type,
    COUNT(*) as report_count,
    MAX(created_at) as latest_report
FROM analysis_reports
GROUP BY report_type;

-- 8. サンプルデータ確認（ETF）
SELECT 
    symbol,
    name,
    sector,
    market
FROM stock_master
WHERE sector IN ('ETF', 'Equity')
LIMIT 20;

-- 9. 価格データサンプル（存在する場合）
SELECT 
    symbol,
    date,
    close_price,
    volume
FROM stock_prices
ORDER BY date DESC
LIMIT 10;