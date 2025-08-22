-- Verify data loading
USE miraikakaku_prod;

-- Check total count
SELECT COUNT(*) as total_stocks FROM stock_master WHERE country = 'Japan';

-- Check by market
SELECT market, COUNT(*) as count FROM stock_master WHERE country = 'Japan' GROUP BY market;

-- Sample data
SELECT symbol, name, sector, market FROM stock_master WHERE country = 'Japan' LIMIT 10;