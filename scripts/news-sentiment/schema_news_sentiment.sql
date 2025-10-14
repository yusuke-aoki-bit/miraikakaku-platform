-- ニュース分析機能のためのデータベーススキーマ拡張
-- 作成日: 2025-10-11

-- 1. ニューステーブル
CREATE TABLE IF NOT EXISTS stock_news (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    source VARCHAR(100),
    published_at TIMESTAMP NOT NULL,
    summary TEXT,
    sentiment_score NUMERIC(5, 4),  -- -1.0 to 1.0
    sentiment_label VARCHAR(20),     -- positive, negative, neutral
    relevance_score NUMERIC(5, 4),   -- 0.0 to 1.0
    topics TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_symbol FOREIGN KEY (symbol) REFERENCES stock_master(symbol) ON DELETE CASCADE
);

-- ユニーク制約 (同じURLは1回のみ保存)
CREATE UNIQUE INDEX IF NOT EXISTS idx_stock_news_unique_url ON stock_news(symbol, url);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_stock_news_symbol ON stock_news(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_news_published_at ON stock_news(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_stock_news_sentiment ON stock_news(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_stock_news_relevance ON stock_news(relevance_score);

-- 2. 銘柄別センチメント集計テーブル
CREATE TABLE IF NOT EXISTS stock_sentiment_summary (
    symbol VARCHAR(20) PRIMARY KEY,
    date DATE NOT NULL,
    news_count INTEGER DEFAULT 0,
    avg_sentiment NUMERIC(5, 4),         -- 平均センチメント
    positive_count INTEGER DEFAULT 0,
    negative_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    sentiment_trend VARCHAR(20),         -- bullish, bearish, neutral
    sentiment_strength NUMERIC(5, 4),    -- 0.0 to 1.0 (センチメントの強さ)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_symbol_sentiment FOREIGN KEY (symbol) REFERENCES stock_master(symbol) ON DELETE CASCADE
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_sentiment_summary_date ON stock_sentiment_summary(date DESC);
CREATE INDEX IF NOT EXISTS idx_sentiment_summary_trend ON stock_sentiment_summary(sentiment_trend);

-- 3. ensemble_predictions テーブルの拡張（既存テーブルに列を追加）
DO $$
BEGIN
    -- news_sentiment列を追加（まだ存在しない場合）
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ensemble_predictions' AND column_name = 'news_sentiment'
    ) THEN
        ALTER TABLE ensemble_predictions
        ADD COLUMN news_sentiment NUMERIC(5, 4);
    END IF;

    -- news_impact列を追加（まだ存在しない場合）
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ensemble_predictions' AND column_name = 'news_impact'
    ) THEN
        ALTER TABLE ensemble_predictions
        ADD COLUMN news_impact NUMERIC(5, 4);
    END IF;

    -- sentiment_adjusted_prediction列を追加（まだ存在しない場合）
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ensemble_predictions' AND column_name = 'sentiment_adjusted_prediction'
    ) THEN
        ALTER TABLE ensemble_predictions
        ADD COLUMN sentiment_adjusted_prediction NUMERIC(12, 2);
    END IF;
END $$;

-- 4. ニュース分析ログテーブル
CREATE TABLE IF NOT EXISTS news_analysis_log (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    analysis_date DATE NOT NULL,
    news_processed INTEGER DEFAULT 0,
    sentiment_calculated BOOLEAN DEFAULT FALSE,
    api_calls_made INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_news_log_date ON news_analysis_log(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_news_log_symbol ON news_analysis_log(symbol);

-- 5. ビュー: 最新のニュースセンチメント
CREATE OR REPLACE VIEW latest_news_sentiment AS
SELECT
    sn.symbol,
    sm.company_name,
    sn.title,
    sn.published_at,
    sn.sentiment_score,
    sn.sentiment_label,
    sn.relevance_score,
    sn.source
FROM stock_news sn
LEFT JOIN stock_master sm ON sn.symbol = sm.symbol
WHERE sn.published_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY sn.published_at DESC;

-- 6. ビュー: センチメント強化された予測
CREATE OR REPLACE VIEW sentiment_enhanced_predictions AS
SELECT
    ep.symbol,
    sm.company_name,
    ep.prediction_date,
    ep.prediction_days,
    ep.current_price,
    ep.ensemble_prediction,
    ep.sentiment_adjusted_prediction,
    ep.ensemble_confidence,
    ep.news_sentiment,
    ep.news_impact,
    ss.sentiment_trend,
    ss.news_count,
    CASE
        WHEN ep.sentiment_adjusted_prediction IS NOT NULL
        THEN ep.sentiment_adjusted_prediction
        ELSE ep.ensemble_prediction
    END as final_prediction,
    CASE
        WHEN ep.news_sentiment > 0.3 THEN 'strong_positive'
        WHEN ep.news_sentiment > 0.1 THEN 'positive'
        WHEN ep.news_sentiment < -0.3 THEN 'strong_negative'
        WHEN ep.news_sentiment < -0.1 THEN 'negative'
        ELSE 'neutral'
    END as sentiment_signal
FROM ensemble_predictions ep
LEFT JOIN stock_master sm ON ep.symbol = sm.symbol
LEFT JOIN stock_sentiment_summary ss ON ep.symbol = ss.symbol AND ss.date = CURRENT_DATE
WHERE ep.prediction_date >= CURRENT_DATE
ORDER BY ep.prediction_date, ep.symbol;

-- 7. 関数: センチメントスコアの計算
CREATE OR REPLACE FUNCTION calculate_sentiment_score(
    p_symbol VARCHAR(20),
    p_days INTEGER DEFAULT 7
)
RETURNS TABLE (
    avg_sentiment NUMERIC,
    sentiment_trend VARCHAR,
    news_count BIGINT,
    positive_ratio NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        AVG(sentiment_score)::NUMERIC(5,4) as avg_sentiment,
        CASE
            WHEN AVG(sentiment_score) > 0.3 THEN 'bullish'
            WHEN AVG(sentiment_score) < -0.3 THEN 'bearish'
            ELSE 'neutral'
        END::VARCHAR as sentiment_trend,
        COUNT(*)::BIGINT as news_count,
        (COUNT(*) FILTER (WHERE sentiment_score > 0)::NUMERIC / NULLIF(COUNT(*), 0))::NUMERIC(5,4) as positive_ratio
    FROM stock_news
    WHERE symbol = p_symbol
      AND published_at >= CURRENT_DATE - (p_days || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

-- 8. トリガー: sentiment_summaryの自動更新
CREATE OR REPLACE FUNCTION update_sentiment_summary()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO stock_sentiment_summary (
        symbol,
        date,
        news_count,
        avg_sentiment,
        positive_count,
        negative_count,
        neutral_count,
        sentiment_trend,
        sentiment_strength,
        updated_at
    )
    SELECT
        NEW.symbol,
        CURRENT_DATE,
        COUNT(*),
        AVG(sentiment_score),
        COUNT(*) FILTER (WHERE sentiment_label = 'positive'),
        COUNT(*) FILTER (WHERE sentiment_label = 'negative'),
        COUNT(*) FILTER (WHERE sentiment_label = 'neutral'),
        CASE
            WHEN AVG(sentiment_score) > 0.3 THEN 'bullish'
            WHEN AVG(sentiment_score) < -0.3 THEN 'bearish'
            ELSE 'neutral'
        END,
        ABS(AVG(sentiment_score)),
        NOW()
    FROM stock_news
    WHERE symbol = NEW.symbol
      AND published_at >= CURRENT_DATE - INTERVAL '7 days'
    ON CONFLICT (symbol)
    DO UPDATE SET
        news_count = EXCLUDED.news_count,
        avg_sentiment = EXCLUDED.avg_sentiment,
        positive_count = EXCLUDED.positive_count,
        negative_count = EXCLUDED.negative_count,
        neutral_count = EXCLUDED.neutral_count,
        sentiment_trend = EXCLUDED.sentiment_trend,
        sentiment_strength = EXCLUDED.sentiment_strength,
        updated_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_sentiment_summary
AFTER INSERT OR UPDATE ON stock_news
FOR EACH ROW
EXECUTE FUNCTION update_sentiment_summary();

-- コメント
COMMENT ON TABLE stock_news IS 'ニュース記事とセンチメント分析結果';
COMMENT ON TABLE stock_sentiment_summary IS '銘柄別のセンチメント集計（日次更新）';
COMMENT ON COLUMN ensemble_predictions.news_sentiment IS 'ニュースセンチメントスコア（-1.0～1.0）';
COMMENT ON COLUMN ensemble_predictions.news_impact IS 'ニュースの予測への影響度（0.0～1.0）';
COMMENT ON COLUMN ensemble_predictions.sentiment_adjusted_prediction IS 'センチメントで調整された最終予測価格';
