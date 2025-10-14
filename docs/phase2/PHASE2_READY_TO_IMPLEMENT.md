# Phase 2実装準備完了 - 詳細ガイド

## 📊 現在の状況

### ✅ Phase 1完了 (稼働中)
- **Gainers endpoint**: 30.1%改善 (0.37s → 0.259s)
- **Losers endpoint**: 36.8%改善 (0.37s → 0.234s)
- Cloud Scheduler: 毎日午前2時自動更新
- デプロイ済み: miraikakaku-api-00098-d9x

### 🎯 Phase 2目標
Volume/Predictions/Stats エンドポイントを最適化して、TOP画面全体を**71.8%改善** (2.565s → 0.723s)

## 🛠️ Phase 2実装手順

### Step 1: api_predictions.pyにマテリアライズドビュー追加

`/admin/optimize-rankings-performance` エンドポイント（Line 1833-1991）に以下を追加：

#### 1-A. Volume Ranking View
```python
# Step 2-5: 出来高ランキングビュー
try:
    cur.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_volume_ranking AS
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
        ORDER BY sp.volume DESC
    """)
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_volume_ranking_symbol ON mv_volume_ranking (symbol)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_volume_ranking_volume ON mv_volume_ranking (volume DESC NULLS LAST)")
    results["views_created"].append("mv_volume_ranking")
except Exception as e:
    results["errors"].append(f"mv_volume_ranking: {str(e)}")
```

#### 1-B. Predictions Ranking View
```python
# Step 2-6: 予測ランキングビュー
try:
    cur.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_predictions_ranking AS
        SELECT
            ep.symbol,
            sm.company_name,
            sm.exchange,
            ep.current_price,
            ep.ensemble_prediction,
            ep.ensemble_confidence,
            ROUND(((ep.ensemble_prediction - ep.current_price) /
                   NULLIF(ep.current_price, 0) * 100)::numeric, 2) as predicted_change,
            ep.prediction_date
        FROM (
            SELECT DISTINCT ON (symbol)
                symbol,
                current_price,
                ensemble_prediction,
                ensemble_confidence,
                prediction_date
            FROM ensemble_predictions
            WHERE prediction_date >= CURRENT_DATE - INTERVAL '1 day'
              AND ensemble_confidence IS NOT NULL
              AND current_price IS NOT NULL
              AND current_price > 0
            ORDER BY symbol, prediction_date DESC
        ) ep
        LEFT JOIN stock_master sm ON ep.symbol = sm.symbol
        ORDER BY predicted_change DESC NULLS LAST
    """)
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_predictions_ranking_symbol ON mv_predictions_ranking (symbol)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_predictions_ranking_change ON mv_predictions_ranking (predicted_change DESC NULLS LAST)")
    results["views_created"].append("mv_predictions_ranking")
except Exception as e:
    results["errors"].append(f"mv_predictions_ranking: {str(e)}")
```

#### 1-C. Stats Summary View
```python
# Step 2-7: 統計サマリービュー
try:
    cur.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_stats_summary AS
        SELECT
            (SELECT COUNT(*) FROM stock_master) as total_symbols,
            (SELECT COUNT(*) FROM stock_master WHERE is_active = TRUE) as active_symbols,
            (SELECT COUNT(DISTINCT symbol) FROM ensemble_predictions
             WHERE prediction_date >= CURRENT_DATE - INTERVAL '1 day') as symbols_with_future_predictions,
            (SELECT COUNT(DISTINCT symbol) FROM ensemble_predictions) as symbols_with_predictions,
            85.2 as avg_accuracy,
            3 as models_running,
            CURRENT_TIMESTAMP as last_updated
    """)
    results["views_created"].append("mv_stats_summary")
except Exception as e:
    results["errors"].append(f"mv_stats_summary: {str(e)}")
```

#### 1-D. リフレッシュ関数更新
```python
# Step 3: リフレッシュ関数更新（Line 1917-1933を置き換え）
try:
    cur.execute("""
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
    """)
    results["views_created"].append("refresh_ranking_views (function) - updated")
except Exception as e:
    results["errors"].append(f"refresh_ranking_views: {str(e)}")
```

### Step 2: APIエンドポイント更新

#### 2-A. Volume Endpoint (Line 738-785)
```python
@app.get("/api/home/rankings/volume")
def get_top_volume(limit: int = 50):
    """出来高ランキング（Phase 2最適化版 - マテリアライズドビュー使用）"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # マテリアライズドビューから直接取得
        cur.execute("""
            SELECT
                symbol,
                company_name,
                exchange,
                price,
                volume
            FROM mv_volume_ranking
            LIMIT %s
        """, (limit,))

        results = cur.fetchall()
        return [
            {
                "symbol": row['symbol'],
                "name": row['company_name'] or row['symbol'],
                "exchange": row['exchange'] or '',
                "price": float(row['price']),
                "volume": int(row['volume'])
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
```

#### 2-B. Predictions Endpoint (Line 787以降)
```python
@app.get("/api/home/rankings/predictions")
def get_top_predictions(limit: int = 50):
    """予測精度ランキング（Phase 2最適化版 - マテリアライズドビュー使用）"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # マテリアライズドビューから直接取得
        cur.execute("""
            SELECT
                symbol,
                company_name,
                exchange,
                current_price,
                ensemble_prediction,
                ensemble_confidence,
                predicted_change
            FROM mv_predictions_ranking
            LIMIT %s
        """, (limit,))

        results = cur.fetchall()
        return [
            {
                "symbol": row['symbol'],
                "name": row['company_name'] or row['symbol'],
                "exchange": row['exchange'] or '',
                "currentPrice": float(row['current_price']),
                "predictedPrice": float(row['ensemble_prediction']),
                "confidence": float(row['ensemble_confidence']) if row['ensemble_confidence'] else 0.0,
                "predictedChange": float(row['predicted_change'])
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
```

#### 2-C. Stats Endpoint
```python
@app.get("/api/home/stats/summary")
def get_home_stats():
    """ホームページ用の統計サマリー（Phase 2最適化版 - マテリアライズドビュー使用）"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # マテリアライズドビューから直接取得
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
```

### Step 3: デプロイ

```bash
# ビルド
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api \
  --project=pricewise-huqkr --timeout=20m

# デプロイ
gcloud run services update miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api:latest \
  --region us-central1 \
  --project=pricewise-huqkr
```

### Step 4: 最適化実行

```bash
# Phase 2マテリアライズドビュー作成
curl -X POST \
  "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/optimize-rankings-performance" \
  -H "Content-Type: application/json" \
  -H "Content-Length: 0"
```

**期待される結果:**
```json
{
  "status": "success",
  "views_created": [
    "mv_latest_prices",
    "mv_prev_prices",
    "mv_gainers_ranking",
    "mv_losers_ranking",
    "mv_volume_ranking",
    "mv_predictions_ranking",
    "mv_stats_summary",
    "refresh_ranking_views (function) - updated"
  ]
}
```

### Step 5: パフォーマンステスト

```bash
echo "=== Phase 2 Performance Test ===" && \
curl -s -w "Gainers: %{time_total}s\n" -o /dev/null \
  "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/rankings/gainers?limit=50" && \
curl -s -w "Losers: %{time_total}s\n" -o /dev/null \
  "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/rankings/losers?limit=50" && \
curl -s -w "Volume: %{time_total}s\n" -o /dev/null \
  "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/rankings/volume?limit=50" && \
curl -s -w "Predictions: %{time_total}s\n" -o /dev/null \
  "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/rankings/predictions?limit=50" && \
curl -s -w "Stats: %{time_total}s\n" -o /dev/null \
  "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/stats/summary"
```

**期待される結果:**
```
Gainers: 0.259s (既存)
Losers: 0.234s (既存)
Volume: 0.10s (改善: 85.8%)
Predictions: 0.08s (改善: 81.8%)
Stats: 0.05s (改善: 92.6%)
合計: ~0.723s (改善: 71.8%)
```

## 📊 改善効果予測

### Before (Phase 1完了時点)
| エンドポイント | レスポンス時間 |
|--------------|---------------|
| Gainers | 0.259s ✅ |
| Losers | 0.234s ✅ |
| Volume | 0.705s ❌ |
| Predictions | 0.440s ❌ |
| Stats | 0.678s ❌ |
| **合計** | **2.316s** |

### After (Phase 2完了時点)
| エンドポイント | レスポンス時間 | 改善率 |
|--------------|---------------|--------|
| Gainers | 0.259s | - |
| Losers | 0.234s | - |
| Volume | 0.10s | **85.8%** |
| Predictions | 0.08s | **81.8%** |
| Stats | 0.05s | **92.6%** |
| **合計** | **0.723s** | **68.8%** |

## 🔍 注意事項

### 1. CURRENT_DATEの扱い
ensemble_predictionsテーブルのWHERE句で`CURRENT_DATE`を使用すると、マテリアライズドビューの更新時にエラーが発生する可能性があります。

**解決策:**
```sql
-- ❌ 問題のあるコード
WHERE prediction_date >= CURRENT_DATE

-- ✅ 修正版
WHERE prediction_date >= CURRENT_DATE - INTERVAL '1 day'
```

### 2. UNIQUE INDEXの重要性
CONCURRENT REFRESHを使用するには、各マテリアライズドビューにUNIQUE INDEXが必要です。

```sql
CREATE UNIQUE INDEX idx_mv_volume_ranking_symbol ON mv_volume_ranking (symbol);
CREATE UNIQUE INDEX idx_mv_predictions_ranking_symbol ON mv_predictions_ranking (symbol);
-- mv_stats_summaryはUNIQUE INDEXなし（1行のみのため）
```

### 3. データ型の確認
APIレスポンスで使用するデータ型を確認：
- `float()` → price, prediction, confidence
- `int()` → volume, counts

## 🚀 実装チェックリスト

- [ ] api_predictions.py修正
  - [ ] Volume ranking view追加
  - [ ] Predictions ranking view追加
  - [ ] Stats summary view追加
  - [ ] リフレッシュ関数更新
- [ ] APIエンドポイント更新
  - [ ] Volume endpoint修正
  - [ ] Predictions endpoint修正
  - [ ] Stats endpoint修正
- [ ] ビルド＆デプロイ
  - [ ] gcloud builds submit実行
  - [ ] gcloud run services update実行
- [ ] 最適化実行
  - [ ] /admin/optimize-rankings-performance実行
- [ ] パフォーマンステスト
  - [ ] 全エンドポイントの測定
  - [ ] 改善率の確認
- [ ] ドキュメント更新
  - [ ] PHASE2_COMPLETION_REPORT.md作成
  - [ ] パフォーマンス測定結果記録

## 📝 トラブルシューティング

### ビューが作成されない
```sql
-- マテリアライズドビュー確認
SELECT schemaname, matviewname, ispopulated
FROM pg_matviews
WHERE matviewname LIKE 'mv_%';
```

### データが古い
```bash
# 手動でリフレッシュ
curl -X POST \
  "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/refresh-ranking-views" \
  -H "Content-Type: application/json" \
  -H "Content-Length: 0"
```

### パフォーマンスが改善されない
1. マテリアライズドビューにデータが入っているか確認
2. APIエンドポイントが正しくビューを参照しているか確認
3. ビューのインデックスが作成されているか確認

---

**作成日**: 2025年10月13日
**ステータス**: Phase 2実装準備完了
**次のアクション**: 実装開始
