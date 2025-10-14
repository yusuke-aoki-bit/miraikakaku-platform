-- Add news sentiment columns to ensemble_predictions table

ALTER TABLE ensemble_predictions
ADD COLUMN IF NOT EXISTS news_sentiment_score DECIMAL(5,4),
ADD COLUMN IF NOT EXISTS news_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS sentiment_trend DECIMAL(5,4),
ADD COLUMN IF NOT EXISTS bullish_ratio DECIMAL(5,4),
ADD COLUMN IF NOT EXISTS bearish_ratio DECIMAL(5,4);

-- Verify columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'ensemble_predictions'
  AND (column_name LIKE '%news%' OR column_name LIKE '%sentiment%' OR column_name LIKE '%bullish%' OR column_name LIKE '%bearish%')
ORDER BY column_name;
