-- Cloud SQL データ状況確認
USE miraikakaku_prod;

-- 1. 全体データサマリー
SELECT 
    'Cloud SQL Status' as database_type,
    COUNT(*) as total_stocks,
    COUNT(DISTINCT country) as countries,
    COUNT(DISTINCT market) as markets,
    COUNT(DISTINCT sector) as sectors
FROM stock_master;

-- 2. 国別詳細
SELECT 
    'Country Breakdown' as type,
    country,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM stock_master), 2) as percentage
FROM stock_master 
GROUP BY country
ORDER BY count DESC;

-- 3. 価格データ状況
SELECT 
    'Price Data Status' as type,
    COUNT(*) as total_records,
    COUNT(DISTINCT symbol) as unique_symbols,
    MIN(date) as earliest_date,
    MAX(date) as latest_date
FROM stock_prices;

-- 4. 予測データ状況
SELECT 
    'Prediction Data Status' as type,
    COUNT(*) as total_records,
    COUNT(DISTINCT symbol) as unique_symbols,
    MIN(prediction_date) as earliest_prediction,
    MAX(prediction_date) as latest_prediction
FROM stock_predictions;

-- 5. SQLite重複チェック（Cloud SQLにSQLite銘柄があるか）
SELECT 
    'SQLite Symbol Check' as check_type,
    symbol,
    name,
    country
FROM stock_master 
WHERE symbol IN ('AAPL', 'GOOGL', 'MSFT', 'NVDA', 'TSLA')
ORDER BY symbol;

-- 6. データ品質確認
SELECT 
    'Data Quality' as check_type,
    COUNT(CASE WHEN symbol IS NULL OR symbol = '' THEN 1 END) as null_symbols,
    COUNT(CASE WHEN name IS NULL OR name = '' THEN 1 END) as null_names,
    COUNT(CASE WHEN country IS NULL OR country = '' THEN 1 END) as null_countries,
    COUNT(CASE WHEN sector IS NULL OR sector = '' THEN 1 END) as null_sectors
FROM stock_master;

-- 7. 重複銘柄チェック
SELECT 
    'Duplicate Symbols' as check_type,
    symbol,
    COUNT(*) as count
FROM stock_master 
GROUP BY symbol 
HAVING COUNT(*) > 1
LIMIT 10;

-- 8. 最新のバッチログ
SELECT 
    'Latest Batch Logs' as type,
    batch_type,
    status,
    records_processed,
    start_time
FROM batch_logs 
ORDER BY start_time DESC
LIMIT 5;