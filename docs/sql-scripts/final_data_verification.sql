-- 最終データ投入確認
USE miraikakaku_prod;

-- 1. 全体データサマリー
SELECT 
    'Master Data' as category,
    COUNT(*) as total_records,
    COUNT(DISTINCT country) as countries,
    COUNT(DISTINCT market) as markets,
    COUNT(DISTINCT sector) as sectors
FROM stock_master

UNION ALL

SELECT 
    'Price Data',
    COUNT(*),
    COUNT(DISTINCT symbol),
    DATEDIFF(MAX(date), MIN(date)),
    NULL
FROM stock_prices

UNION ALL

SELECT 
    'Prediction Data',
    COUNT(*),
    COUNT(DISTINCT symbol),
    DATEDIFF(MAX(prediction_date), MIN(prediction_date)),
    NULL
FROM stock_predictions;

-- 2. 国・市場別マスターデータ
SELECT 
    country,
    COUNT(*) as stocks,
    GROUP_CONCAT(DISTINCT market ORDER BY market) as markets
FROM stock_master 
GROUP BY country
ORDER BY stocks DESC;

-- 3. ETF確認
SELECT 
    sector,
    COUNT(*) as count
FROM stock_master
WHERE sector IN ('ETF', 'Equity', 'Bond', 'Commodity')
GROUP BY sector;

-- 4. 価格データサンプル
SELECT 
    symbol,
    COUNT(*) as price_records,
    MIN(date) as earliest,
    MAX(date) as latest,
    AVG(close_price) as avg_price
FROM stock_prices
GROUP BY symbol
ORDER BY price_records DESC;

-- 5. 予測データサンプル
SELECT 
    symbol,
    COUNT(*) as predictions,
    MIN(prediction_date) as start_date,
    MAX(prediction_date) as end_date,
    AVG(confidence_score) as avg_confidence
FROM stock_predictions
GROUP BY symbol
ORDER BY predictions DESC;

-- 6. バッチログ確認
SELECT * FROM batch_logs ORDER BY start_time DESC;

-- 7. システム全体統計
SELECT 
    'Miraikakaku Database Status' as system_status,
    (SELECT COUNT(*) FROM stock_master) as total_stocks,
    (SELECT COUNT(*) FROM stock_prices) as price_records,
    (SELECT COUNT(*) FROM stock_predictions) as prediction_records,
    CONCAT(
        (SELECT COUNT(*) FROM stock_master WHERE country = 'Japan'), ' JP + ',
        (SELECT COUNT(*) FROM stock_master WHERE country = 'USA'), ' US + ',
        (SELECT COUNT(*) FROM stock_master WHERE country = 'US'), ' ETF'
    ) as breakdown;