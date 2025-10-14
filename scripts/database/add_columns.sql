-- Add sector and industry columns to stock_master table

DO $$
BEGIN
    -- Add sector column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='stock_master' AND column_name='sector'
    ) THEN
        ALTER TABLE stock_master ADD COLUMN sector VARCHAR(100) DEFAULT NULL;
        RAISE NOTICE 'Added sector column';
    ELSE
        RAISE NOTICE 'Sector column already exists';
    END IF;

    -- Add industry column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='stock_master' AND column_name='industry'
    ) THEN
        ALTER TABLE stock_master ADD COLUMN industry VARCHAR(200) DEFAULT NULL;
        RAISE NOTICE 'Added industry column';
    ELSE
        RAISE NOTICE 'Industry column already exists';
    END IF;
END $$;

-- Show current statistics
SELECT
    COUNT(*) as total_stocks,
    COUNT(sector) as stocks_with_sector,
    COUNT(industry) as stocks_with_industry,
    ROUND(100.0 * COUNT(sector) / COUNT(*), 1) as sector_coverage_pct,
    ROUND(100.0 * COUNT(industry) / COUNT(*), 1) as industry_coverage_pct
FROM stock_master;
