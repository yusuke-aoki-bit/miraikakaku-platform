-- ============================================================
-- Phase 10: Price Alerts Database Schema
-- ============================================================

-- Drop existing objects if they exist
DROP TABLE IF EXISTS price_alerts CASCADE;

-- Create price_alerts table
CREATE TABLE IF NOT EXISTS price_alerts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    threshold DECIMAL(15, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint
    CONSTRAINT fk_alert_symbol
        FOREIGN KEY (symbol)
        REFERENCES stock_master(symbol)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    -- Check constraints
    CONSTRAINT chk_alert_type CHECK (
        alert_type IN (
            'price_above',
            'price_below',
            'price_change_percent_up',
            'price_change_percent_down',
            'prediction_up',
            'prediction_down'
        )
    ),
    CONSTRAINT chk_threshold_positive CHECK (threshold > 0)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_symbol ON price_alerts(symbol);
CREATE INDEX IF NOT EXISTS idx_price_alerts_is_active ON price_alerts(is_active);
CREATE INDEX IF NOT EXISTS idx_price_alerts_triggered_at ON price_alerts(triggered_at);
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_active ON price_alerts(user_id, is_active);

-- Verify schema application
SELECT 'Price alerts schema applied successfully!' as message;
