-- 包括的データ投入確認
USE miraikakaku_prod;

-- 国別統計
SELECT 
    country,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM stock_master), 2) as percentage
FROM stock_master 
GROUP BY country
ORDER BY count DESC;

-- 通貨別統計  
SELECT 
    currency,
    COUNT(*) as count
FROM stock_master 
GROUP BY currency
ORDER BY count DESC;

-- 市場別統計（上位10）
SELECT 
    market,
    COUNT(*) as count
FROM stock_master 
GROUP BY market
ORDER BY count DESC
LIMIT 10;

-- 総数確認
SELECT 'Total Comprehensive Financial Database' as description, COUNT(*) as total_stocks FROM stock_master;

-- サンプルデータ確認
SELECT country, symbol, name, market, currency 
FROM stock_master 
WHERE country IN ('Japan', 'USA')
ORDER BY country, symbol
LIMIT 20;