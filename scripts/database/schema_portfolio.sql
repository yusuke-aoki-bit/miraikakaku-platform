-- ============================================================
-- Phase 5-1: Portfolio Management Database Schema Application
-- ============================================================

-- Drop existing objects if they exist (using CASCADE for safety)
DROP VIEW IF EXISTS v_portfolio_current_value CASCADE;
DROP VIEW IF EXISTS v_portfolio_summary CASCADE;
DROP VIEW IF EXISTS v_portfolio_sector_allocation CASCADE;
DROP FUNCTION IF EXISTS calculate_portfolio_value(VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS update_timestamp() CASCADE;

-- Create or recreate tables with IF NOT EXISTS
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(15, 4) NOT NULL,
    purchase_price DECIMAL(15, 2) NOT NULL,
    purchase_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_portfolio_symbol
        FOREIGN KEY (symbol)
        REFERENCES stock_master(symbol)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_quantity_positive CHECK (quantity > 0),
    CONSTRAINT chk_purchase_price_positive CHECK (purchase_price > 0)
);

CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    snapshot_date DATE NOT NULL,
    total_value DECIMAL(20, 2) NOT NULL,
    total_cost DECIMAL(20, 2) NOT NULL,
    unrealized_gain DECIMAL(20, 2) NOT NULL,
    unrealized_gain_pct DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_portfolio_snapshot UNIQUE(user_id, snapshot_date)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_portfolio_user_id ON portfolio_holdings(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_symbol ON portfolio_holdings(symbol);
CREATE INDEX IF NOT EXISTS idx_portfolio_user_symbol ON portfolio_holdings(user_id, symbol);
CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_user_date ON portfolio_snapshots(user_id, snapshot_date);

-- Create view: v_portfolio_current_value
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

    -- Cost basis and valuation
    (ph.quantity * ph.purchase_price) as cost_basis,
    (ph.quantity * COALESCE(sp.close_price, ph.purchase_price)) as current_value,
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
) sp ON true;

-- Create view: v_portfolio_summary
CREATE OR REPLACE VIEW v_portfolio_summary AS
SELECT
    user_id,
    COUNT(*) as total_holdings,
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

-- Create view: v_portfolio_sector_allocation
CREATE OR REPLACE VIEW v_portfolio_sector_allocation AS
SELECT
    user_id,
    sector,
    COUNT(*) as holdings_count,
    SUM(current_value) as sector_value,
    (SUM(current_value) / NULLIF(
        SUM(SUM(current_value)) OVER (PARTITION BY user_id), 0
    ) * 100) as sector_percentage
FROM v_portfolio_current_value
WHERE sector IS NOT NULL
GROUP BY user_id, sector;

-- Create function: calculate_portfolio_value
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
        SUM(v.cost_basis)::DECIMAL(20, 2) as total_cost,
        SUM(v.current_value)::DECIMAL(20, 2) as total_value,
        SUM(v.unrealized_gain)::DECIMAL(20, 2) as unrealized_gain,
        CASE
            WHEN SUM(v.cost_basis) > 0 THEN
                (SUM(v.unrealized_gain) / SUM(v.cost_basis) * 100)::DECIMAL(10, 2)
            ELSE 0
        END as unrealized_gain_pct
    FROM v_portfolio_current_value v
    WHERE v.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Create function: update_timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic timestamp updates
DROP TRIGGER IF EXISTS update_portfolio_holdings_timestamp ON portfolio_holdings;
CREATE TRIGGER update_portfolio_holdings_timestamp
    BEFORE UPDATE ON portfolio_holdings
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Verify schema application
SELECT 'Portfolio schema applied successfully!' as message;
