-- ============================================================
-- Phase 5-3: Performance Analysis Database Schema
-- ============================================================

-- Drop existing objects if they exist
DROP VIEW IF EXISTS v_portfolio_performance CASCADE;
DROP VIEW IF EXISTS v_portfolio_sector_allocation CASCADE;
DROP VIEW IF EXISTS v_daily_portfolio_value CASCADE;
DROP FUNCTION IF EXISTS calculate_portfolio_returns(VARCHAR, DATE, DATE) CASCADE;
DROP FUNCTION IF EXISTS calculate_sharpe_ratio(VARCHAR, DATE, DATE) CASCADE;

-- ============================================================
-- Portfolio Performance View
-- ============================================================
-- Calculates current performance metrics for each portfolio holding
CREATE OR REPLACE VIEW v_portfolio_performance AS
SELECT
    p.id,
    p.user_id,
    p.symbol,
    sm.company_name,
    sm.exchange,
    sm.sector,
    p.quantity,
    p.purchase_price,
    p.purchase_date,

    -- Current price from latest stock_prices
    COALESCE(sp.close_price, p.purchase_price) as current_price,
    sp.date as price_date,

    -- Cost basis and current value
    (p.quantity * p.purchase_price) as cost_basis,
    (p.quantity * COALESCE(sp.close_price, p.purchase_price)) as current_value,

    -- Profit/Loss calculations
    (p.quantity * COALESCE(sp.close_price, p.purchase_price)) - (p.quantity * p.purchase_price) as unrealized_pl,
    CASE
        WHEN p.purchase_price > 0 THEN
            ((COALESCE(sp.close_price, p.purchase_price) - p.purchase_price) / p.purchase_price * 100)
        ELSE 0
    END as return_pct,

    -- Holding period
    CURRENT_DATE - p.purchase_date as days_held,

    -- Annualized return
    CASE
        WHEN p.purchase_price > 0 AND (CURRENT_DATE - p.purchase_date) > 0 THEN
            ((COALESCE(sp.close_price, p.purchase_price) - p.purchase_price) / p.purchase_price * 365.0 / (CURRENT_DATE - p.purchase_date))
        ELSE 0
    END as annualized_return_pct,

    -- Prediction data
    ep.ensemble_prediction as predicted_price,
    ep.ensemble_confidence,
    CASE
        WHEN COALESCE(sp.close_price, p.purchase_price) > 0 AND ep.ensemble_prediction > 0 THEN
            ((ep.ensemble_prediction - COALESCE(sp.close_price, p.purchase_price)) / COALESCE(sp.close_price, p.purchase_price) * 100)
        ELSE 0
    END as predicted_change_pct,

    p.notes,
    p.created_at,
    p.updated_at

FROM portfolio_holdings p
LEFT JOIN stock_master sm ON p.symbol = sm.symbol

-- Latest price
LEFT JOIN LATERAL (
    SELECT close_price, date
    FROM stock_prices
    WHERE symbol = p.symbol
    ORDER BY date DESC
    LIMIT 1
) sp ON true

-- Latest prediction
LEFT JOIN LATERAL (
    SELECT ensemble_prediction, ensemble_confidence
    FROM ensemble_predictions
    WHERE symbol = p.symbol
      AND prediction_date >= CURRENT_DATE
    ORDER BY prediction_date ASC, prediction_days ASC
    LIMIT 1
) ep ON true;

-- ============================================================
-- Portfolio Sector Allocation View
-- ============================================================
-- Aggregates portfolio value by sector for allocation analysis
CREATE OR REPLACE VIEW v_portfolio_sector_allocation AS
SELECT
    user_id,
    COALESCE(sector, 'Unknown') as sector,
    COUNT(DISTINCT symbol) as holdings_count,
    SUM(cost_basis) as total_cost_basis,
    SUM(current_value) as total_current_value,
    SUM(unrealized_pl) as total_unrealized_pl,
    CASE
        WHEN SUM(cost_basis) > 0 THEN
            (SUM(unrealized_pl) / SUM(cost_basis) * 100)
        ELSE 0
    END as sector_return_pct,
    -- Allocation percentage (calculated per user)
    SUM(current_value) as sector_value
FROM v_portfolio_performance
GROUP BY user_id, sector;

-- ============================================================
-- Daily Portfolio Value Tracking
-- ============================================================
-- Historical view of total portfolio value over time
CREATE OR REPLACE VIEW v_daily_portfolio_value AS
SELECT
    p.user_id,
    sp.date,
    SUM(p.quantity * sp.close_price) as total_value,
    SUM(p.quantity * p.purchase_price) as total_cost_basis,
    SUM(p.quantity * sp.close_price) - SUM(p.quantity * p.purchase_price) as unrealized_pl,
    CASE
        WHEN SUM(p.quantity * p.purchase_price) > 0 THEN
            ((SUM(p.quantity * sp.close_price) - SUM(p.quantity * p.purchase_price)) / SUM(p.quantity * p.purchase_price) * 100)
        ELSE 0
    END as total_return_pct
FROM portfolio_holdings p
INNER JOIN stock_prices sp ON p.symbol = sp.symbol
WHERE sp.date >= p.purchase_date
GROUP BY p.user_id, sp.date
ORDER BY p.user_id, sp.date;

-- ============================================================
-- Function: Calculate Portfolio Returns
-- ============================================================
-- Calculates returns over a specific period
CREATE OR REPLACE FUNCTION calculate_portfolio_returns(
    p_user_id VARCHAR,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    total_return DECIMAL(15, 2),
    return_pct DECIMAL(10, 4),
    start_value DECIMAL(15, 2),
    end_value DECIMAL(15, 2),
    days_period INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH start_val AS (
        SELECT COALESCE(SUM(total_value), 0) as value
        FROM v_daily_portfolio_value
        WHERE user_id = p_user_id
          AND date <= p_start_date
        ORDER BY date DESC
        LIMIT 1
    ),
    end_val AS (
        SELECT COALESCE(SUM(total_value), 0) as value
        FROM v_daily_portfolio_value
        WHERE user_id = p_user_id
          AND date <= p_end_date
        ORDER BY date DESC
        LIMIT 1
    )
    SELECT
        (e.value - s.value) as total_return,
        CASE
            WHEN s.value > 0 THEN ((e.value - s.value) / s.value * 100)
            ELSE 0
        END as return_pct,
        s.value as start_value,
        e.value as end_value,
        (p_end_date - p_start_date) as days_period
    FROM start_val s, end_val e;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- Function: Calculate Sharpe Ratio
-- ============================================================
-- Risk-adjusted return metric (simplified version)
CREATE OR REPLACE FUNCTION calculate_sharpe_ratio(
    p_user_id VARCHAR,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS DECIMAL(10, 4) AS $$
DECLARE
    daily_returns DECIMAL[];
    avg_return DECIMAL;
    std_dev DECIMAL;
    sharpe DECIMAL;
    risk_free_rate DECIMAL := 0.02; -- 2% annual risk-free rate
BEGIN
    -- Calculate daily returns
    WITH daily_values AS (
        SELECT date, total_value,
               LAG(total_value) OVER (ORDER BY date) as prev_value
        FROM v_daily_portfolio_value
        WHERE user_id = p_user_id
          AND date BETWEEN p_start_date AND p_end_date
    ),
    daily_return_calc AS (
        SELECT
            CASE
                WHEN prev_value > 0 THEN (total_value - prev_value) / prev_value
                ELSE 0
            END as daily_return
        FROM daily_values
        WHERE prev_value IS NOT NULL
    )
    SELECT
        AVG(daily_return),
        STDDEV(daily_return)
    INTO avg_return, std_dev
    FROM daily_return_calc;

    -- Calculate Sharpe ratio (annualized)
    IF std_dev > 0 THEN
        sharpe := ((avg_return * 252) - risk_free_rate) / (std_dev * SQRT(252));
    ELSE
        sharpe := 0;
    END IF;

    RETURN sharpe;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- Indexes for Performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date ON stock_prices(symbol, date DESC);
CREATE INDEX IF NOT EXISTS idx_portfolio_user_purchase_date ON portfolio_holdings(user_id, purchase_date);
CREATE INDEX IF NOT EXISTS idx_ensemble_predictions_symbol_date ON ensemble_predictions(symbol, prediction_date, prediction_days);

-- ============================================================
-- Verify Schema Application
-- ============================================================
SELECT 'Performance analysis schema applied successfully!' as message;
