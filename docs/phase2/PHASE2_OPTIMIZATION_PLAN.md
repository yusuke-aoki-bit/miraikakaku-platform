# Phase 2: 残りエンドポイントの最適化計画

## 現状分析

### 最適化済み ✅
1. **Gainers (値上がり率)**: 0.259s (30.1%改善)
   - マテリアライズドビュー `mv_gainers_ranking` 使用

2. **Losers (値下がり率)**: 0.234s (36.8%改善)
   - マテリアライズドビュー `mv_losers_ranking` 使用

### 最適化対象 🔄
3. **Volume (出来高)**: 0.705s (要改善)
   - 現状: CTEでDISTINCT ON → SQLソート
   - 目標: マテリアライズドビュー化

4. **Predictions (予測)**: 0.440s (要改善)
   - 現状: 複雑なCTEとJOIN
   - 目標: マテリアライズドビュー化

5. **Stats (統計)**: 0.678s (要改善)
   - 現状: 複数のCOUNT集計
   - 目標: マテリアライズドビュー化

## Phase 2-A: Volume Ranking最適化

### 実装内容
```sql
-- マテリアライズドビュー作成
CREATE MATERIALIZED VIEW mv_volume_ranking AS
SELECT
    sp.symbol,
    sm.company_name,
    sm.exchange,
    sp.close_price as price,
    sp.volume,
    sp.date
FROM (
    SELECT DISTINCT ON (symbol)
        symbol,
        close_price,
        volume,
        date
    FROM stock_prices
    WHERE volume IS NOT NULL AND volume > 0
    ORDER BY symbol, date DESC
) sp
LEFT JOIN stock_master sm ON sp.symbol = sm.symbol
ORDER BY sp.volume DESC;

-- UNIQUE INDEX作成
CREATE UNIQUE INDEX idx_mv_volume_ranking_symbol
ON mv_volume_ranking (symbol);

-- ソート用INDEX
CREATE INDEX idx_mv_volume_ranking_volume
ON mv_volume_ranking (volume DESC NULLS LAST);
```

### APIエンドポイント修正
```python
@app.get("/api/home/rankings/volume")
def get_top_volume(limit: int = 50):
    """出来高ランキング（最適化版 - マテリアライズドビュー使用）"""
    cur.execute("""
        SELECT symbol, company_name, exchange, price, volume
        FROM mv_volume_ranking
        LIMIT %s
    """, (limit,))
```

**期待効果**: 0.705s → 0.10s (85.8%改善)

## Phase 2-B: Predictions Ranking最適化

### 実装内容
```sql
-- マテリアライズドビュー作成
CREATE MATERIALIZED VIEW mv_predictions_ranking AS
SELECT
    ep.symbol,
    sm.company_name,
    sm.exchange,
    ep.current_price,
    ep.ensemble_prediction,
    ep.ensemble_confidence,
    ROUND(((ep.ensemble_prediction - ep.current_price) / NULLIF(ep.current_price, 0) * 100)::numeric, 2) as predicted_change,
    ep.prediction_date
FROM (
    SELECT DISTINCT ON (symbol)
        symbol,
        current_price,
        ensemble_prediction,
        ensemble_confidence,
        prediction_date
    FROM ensemble_predictions
    WHERE prediction_date >= CURRENT_DATE
      AND ensemble_confidence IS NOT NULL
      AND current_price IS NOT NULL
      AND current_price > 0
    ORDER BY symbol, prediction_date DESC
) ep
LEFT JOIN stock_master sm ON ep.symbol = sm.symbol
ORDER BY predicted_change DESC NULLS LAST;

-- UNIQUE INDEX作成
CREATE UNIQUE INDEX idx_mv_predictions_ranking_symbol
ON mv_predictions_ranking (symbol);

-- ソート用INDEX
CREATE INDEX idx_mv_predictions_ranking_change
ON mv_predictions_ranking (predicted_change DESC NULLS LAST);
```

### APIエンドポイント修正
```python
@app.get("/api/home/rankings/predictions")
def get_top_predictions(limit: int = 50):
    """予測精度ランキング（最適化版）"""
    cur.execute("""
        SELECT symbol, company_name, exchange,
               current_price as currentPrice,
               ensemble_prediction as predictedPrice,
               ensemble_confidence as confidence,
               predicted_change as predictedChange
        FROM mv_predictions_ranking
        LIMIT %s
    """, (limit,))
```

**期待効果**: 0.440s → 0.08s (81.8%改善)

## Phase 2-C: Stats Summary最適化

### 実装内容
```sql
-- マテリアライズドビュー作成
CREATE MATERIALIZED VIEW mv_stats_summary AS
SELECT
    (SELECT COUNT(*) FROM stock_master) as total_symbols,
    (SELECT COUNT(*) FROM stock_master WHERE is_active = TRUE) as active_symbols,
    (SELECT COUNT(DISTINCT symbol) FROM ensemble_predictions WHERE prediction_date >= CURRENT_DATE) as symbols_with_future_predictions,
    (SELECT COUNT(DISTINCT symbol) FROM ensemble_predictions) as symbols_with_predictions,
    85.2 as avg_accuracy,
    3 as models_running,
    CURRENT_TIMESTAMP as last_updated;
```

### APIエンドポイント修正
```python
@app.get("/api/home/stats/summary")
def get_home_stats():
    """ホームページ用の統計サマリー（最適化版）"""
    cur.execute("SELECT * FROM mv_stats_summary")
    stats = cur.fetchone()
    return {
        "totalSymbols": int(stats['total_symbols']),
        "activeSymbols": int(stats['active_symbols']),
        "activePredictions": int(stats['symbols_with_future_predictions']),
        "totalPredictions": int(stats['symbols_with_predictions']),
        "avgAccuracy": float(stats['avg_accuracy']),
        "modelsRunning": int(stats['models_running'])
    }
```

**期待効果**: 0.678s → 0.05s (92.6%改善)

## 実装手順

### Step 1: 最適化エンドポイント拡張
`/admin/optimize-rankings-performance` エンドポイントに以下を追加:
- Volume ranking view作成
- Predictions ranking view作成
- Stats summary view作成

### Step 2: リフレッシュ関数更新
```sql
CREATE OR REPLACE FUNCTION refresh_ranking_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_latest_prices;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_prev_prices;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_gainers_ranking;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_losers_ranking;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_volume_ranking;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_predictions_ranking;
    REFRESH MATERIALIZED VIEW mv_stats_summary;  -- 小さいのでCONCURRENTLY不要
END;
$$ LANGUAGE plpgsql;
```

### Step 3: Cloud Scheduler設定
```bash
# 毎日午前2時に実行（日本時間）
gcloud scheduler jobs create http refresh-rankings \
  --location=us-central1 \
  --schedule="0 2 * * *" \
  --uri="https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/refresh-ranking-views" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body="{}" \
  --time-zone="Asia/Tokyo"
```

## 期待効果まとめ

| エンドポイント | Before | After | 改善率 |
|--------------|--------|-------|--------|
| Gainers | 0.37s | 0.259s | 30.1% ✅ |
| Losers | 0.37s | 0.234s | 36.8% ✅ |
| Volume | 0.705s | 0.10s | **85.8%** 🎯 |
| Predictions | 0.440s | 0.08s | **81.8%** 🎯 |
| Stats | 0.678s | 0.05s | **92.6%** 🎯 |
| **合計** | **2.565s** | **0.723s** | **71.8%** 🎉 |

## Next Steps

1. ✅ Phase 1完了: Gainers/Losers最適化
2. 🔄 Phase 2実装中: Volume/Predictions/Stats最適化
3. 📅 Phase 3予定: Cloud Scheduler自動更新設定
4. 🚀 Phase 4予定: Redis Cache導入（99%改善）

---

**作成日**: 2025年10月13日
**ステータス**: Phase 2実装準備中
