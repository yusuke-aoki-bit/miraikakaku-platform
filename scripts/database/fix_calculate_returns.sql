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
        SELECT total_value as value
        FROM v_daily_portfolio_value
        WHERE user_id = p_user_id
          AND date <= p_start_date
        ORDER BY date DESC
        LIMIT 1
    ),
    end_val AS (
        SELECT total_value as value
        FROM v_daily_portfolio_value
        WHERE user_id = p_user_id
          AND date <= p_end_date
        ORDER BY date DESC
        LIMIT 1
    )
    SELECT
        COALESCE((e.value - s.value), 0) as total_return,
        CASE
            WHEN COALESCE(s.value, 0) > 0 THEN ((COALESCE(e.value, 0) - COALESCE(s.value, 0)) / s.value * 100)
            ELSE 0
        END as return_pct,
        COALESCE(s.value, 0) as start_value,
        COALESCE(e.value, 0) as end_value,
        (p_end_date - p_start_date) as days_period
    FROM (SELECT 1) dummy
    LEFT JOIN start_val s ON true
    LEFT JOIN end_val e ON true;
END;
$$ LANGUAGE plpgsql;
