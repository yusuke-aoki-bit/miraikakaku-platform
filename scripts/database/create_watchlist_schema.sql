-- ============================================================
-- Phase 5-2: Watchlist Feature Database Schema
-- ============================================================

-- Drop existing objects if they exist
DROP VIEW IF EXISTS v_watchlist_current_price CASCADE;
DROP FUNCTION IF EXISTS get_watchlist_with_predictions(VARCHAR) CASCADE;
DROP TABLE IF EXISTS watchlist CASCADE;

-- Create watchlist table
CREATE TABLE IF NOT EXISTS watchlist (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    notes TEXT,
    alert_price_high DECIMAL(15, 2),  -- 上限アラート価格
    alert_price_low DECIMAL(15, 2),   -- 下限アラート価格
    alert_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_watchlist_symbol
        FOREIGN KEY (symbol)
        REFERENCES stock_master(symbol)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_watchlist_user_symbol UNIQUE(user_id, symbol),
    CONSTRAINT chk_alert_price_valid CHECK (
        (alert_price_high IS NULL OR alert_price_low IS NULL) OR
        (alert_price_high > alert_price_low)
    )
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_watchlist_user_id ON watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_symbol ON watchlist(symbol);
CREATE INDEX IF NOT EXISTS idx_watchlist_user_symbol ON watchlist(user_id, symbol);
CREATE INDEX IF NOT EXISTS idx_watchlist_alert_enabled ON watchlist(alert_enabled) WHERE alert_enabled = true;

-- Create view: v_watchlist_current_price
CREATE OR REPLACE VIEW v_watchlist_current_price AS
SELECT
    w.id,
    w.user_id,
    w.symbol,
    sm.company_name,
    sm.exchange,
    sm.sector,

    -- 現在価格情報
    COALESCE(sp.close_price, 0) as current_price,
    sp.date as price_date,
    sp.open_price,
    sp.high_price,
    sp.low_price,
    sp.volume,

    -- 価格変動
    COALESCE(sp.close_price - sp_prev.close_price, 0) as price_change,
    CASE
        WHEN sp_prev.close_price > 0 THEN
            ((sp.close_price - sp_prev.close_price) / sp_prev.close_price * 100)
        ELSE 0
    END as price_change_pct,

    -- 予測情報
    ep.prediction_date,
    ep.prediction_days,
    ep.ensemble_prediction,
    ep.ensemble_confidence,
    CASE
        WHEN sp.close_price > 0 AND ep.ensemble_prediction > 0 THEN
            ((ep.ensemble_prediction - sp.close_price) / sp.close_price * 100)
        ELSE 0
    END as predicted_change_pct,

    -- アラート設定
    w.alert_price_high,
    w.alert_price_low,
    w.alert_enabled,
    CASE
        WHEN w.alert_enabled AND w.alert_price_high IS NOT NULL AND sp.close_price >= w.alert_price_high THEN true
        WHEN w.alert_enabled AND w.alert_price_low IS NOT NULL AND sp.close_price <= w.alert_price_low THEN true
        ELSE false
    END as alert_triggered,

    w.notes,
    w.created_at,
    w.updated_at

FROM watchlist w
LEFT JOIN stock_master sm ON w.symbol = sm.symbol

-- 最新価格
LEFT JOIN LATERAL (
    SELECT close_price, date, open_price, high_price, low_price, volume
    FROM stock_prices
    WHERE symbol = w.symbol
    ORDER BY date DESC
    LIMIT 1
) sp ON true

-- 前日価格（価格変動計算用）
LEFT JOIN LATERAL (
    SELECT close_price
    FROM stock_prices
    WHERE symbol = w.symbol
      AND date < COALESCE(sp.date, CURRENT_DATE)
    ORDER BY date DESC
    LIMIT 1
) sp_prev ON true

-- 最新予測
LEFT JOIN LATERAL (
    SELECT prediction_date, prediction_days,
           ensemble_prediction, ensemble_confidence
    FROM ensemble_predictions
    WHERE symbol = w.symbol
      AND prediction_date >= CURRENT_DATE
    ORDER BY prediction_date ASC, prediction_days ASC
    LIMIT 1
) ep ON true;

-- Create function: get_watchlist_with_predictions
CREATE OR REPLACE FUNCTION get_watchlist_with_predictions(p_user_id VARCHAR)
RETURNS TABLE (
    id INTEGER,
    symbol VARCHAR(20),
    company_name VARCHAR(500),
    exchange VARCHAR(10),
    sector VARCHAR(200),
    current_price DECIMAL(15, 2),
    price_change DECIMAL(15, 2),
    price_change_pct DECIMAL(10, 2),
    ensemble_prediction DECIMAL(15, 2),
    ensemble_confidence DECIMAL(5, 2),
    predicted_change_pct DECIMAL(10, 2),
    alert_triggered BOOLEAN,
    notes TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.id,
        v.symbol,
        v.company_name,
        v.exchange,
        v.sector,
        v.current_price,
        v.price_change,
        v.price_change_pct,
        v.ensemble_prediction,
        v.ensemble_confidence,
        v.predicted_change_pct,
        v.alert_triggered,
        v.notes
    FROM v_watchlist_current_price v
    WHERE v.user_id = p_user_id
    ORDER BY v.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic timestamp updates
DROP TRIGGER IF EXISTS update_watchlist_timestamp ON watchlist;
CREATE TRIGGER update_watchlist_timestamp
    BEFORE UPDATE ON watchlist
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Verify schema application
SELECT 'Watchlist schema applied successfully!' as message;
