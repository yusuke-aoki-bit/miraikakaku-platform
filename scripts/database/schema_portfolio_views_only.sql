-- ============================================================
-- Phase 5-1: Portfolio Management - Views and Functions Only
-- ============================================================
-- This creates only the views and functions, assuming tables already exist
-- ============================================================

-- Drop existing views and functions if they exist
DROP VIEW IF EXISTS v_portfolio_current_value CASCADE;
DROP VIEW IF EXISTS v_portfolio_summary CASCADE;
DROP VIEW IF EXISTS v_portfolio_sector_allocation CASCADE;
DROP FUNCTION IF EXISTS calculate_portfolio_value(VARCHAR) CASCADE;

-- ============================================================
-- 1. View: v_portfolio_current_value
-- ============================================================
CREATE OR REPLACE VIEW v_portfolio_current_value AS
SELECT
    ph.id,
    ph.user_id,
    ph.symbol,
    sm.company_name,
    sm.exchange,
    sm.sector,
    ph.quantity,
    ph.purchase_price,
    ph.purchase_date,
    COALESCE(sp.close_price, ph.purchase_price) as current_price,
    sp.date as price_date,

    -- Cost basis and valuation
    (ph.quantity * ph.purchase_price) as cost_basis,
    (ph.quantity * COALESCE(sp.close_price, ph.purchase_price)) as current_value,

    -- Profit/Loss calculation
    (ph.quantity * COALESCE(sp.close_price, ph.purchase_price)) -
    (ph.quantity * ph.purchase_price) as unrealized_gain,

    CASE
        WHEN ph.purchase_price > 0 THEN
            ((COALESCE(sp.close_price, ph.purchase_price) - ph.purchase_price) / ph.purchase_price * 100)
        ELSE 0
    END as unrealized_gain_pct,

    ph.notes,
    ph.created_at,
    ph.updated_at
FROM portfolio_holdings ph
LEFT JOIN stock_master sm ON ph.symbol = sm.symbol
LEFT JOIN LATERAL (
    SELECT close_price, date
    FROM stock_prices
    WHERE symbol = ph.symbol
    ORDER BY date DESC
    LIMIT 1
) sp ON true
ORDER BY ph.user_id, ph.symbol;

-- ============================================================
-- 2. View: v_portfolio_summary
-- ============================================================
CREATE OR REPLACE VIEW v_portfolio_summary AS
SELECT
    user_id,
    COUNT(DISTINCT symbol) as total_holdings,
    SUM(cost_basis) as total_cost,
    SUM(current_value) as total_value,
    SUM(unrealized_gain) as total_unrealized_gain,
    CASE
        WHEN SUM(cost_basis) > 0 THEN
            (SUM(unrealized_gain) / SUM(cost_basis) * 100)
        ELSE 0
    END as total_unrealized_gain_pct
FROM v_portfolio_current_value
GROUP BY user_id;

-- ============================================================
-- 3. View: v_portfolio_sector_allocation
-- ============================================================
CREATE OR REPLACE VIEW v_portfolio_sector_allocation AS
SELECT
    user_id,
    COALESCE(sector, 'Unknown') as sector,
    COUNT(DISTINCT symbol) as holdings_count,
    SUM(current_value) as sector_value,
    SUM(unrealized_gain) as sector_gain
FROM v_portfolio_current_value
GROUP BY user_id, sector
ORDER BY user_id, sector_value DESC;

-- ============================================================
-- 4. Function: calculate_portfolio_value
-- ============================================================
CREATE OR REPLACE FUNCTION calculate_portfolio_value(p_user_id VARCHAR)
RETURNS TABLE (
    total_cost DECIMAL(20, 2),
    total_value DECIMAL(20, 2),
    unrealized_gain DECIMAL(20, 2),
    unrealized_gain_pct DECIMAL(10, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        SUM(cost_basis)::DECIMAL(20, 2) as total_cost,
        SUM(current_value)::DECIMAL(20, 2) as total_value,
        SUM(unrealized_gain)::DECIMAL(20, 2) as unrealized_gain,
        CASE
            WHEN SUM(cost_basis) > 0 THEN
                (SUM(unrealized_gain) / SUM(cost_basis) * 100)::DECIMAL(10, 2)
            ELSE 0
        END as unrealized_gain_pct
    FROM v_portfolio_current_value
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

SELECT 'Portfolio views and functions created successfully!' as message;
