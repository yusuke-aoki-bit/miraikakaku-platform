# TOP画面パフォーマンス最適化完了レポート

## 📊 実施日時
2025年10月13日

## 🎯 目的
TOP画面の表示速度改善（ユーザーからの要望: 「TOP画面の表示が遅い」）

## 📈 パフォーマンス改善結果

### Before (最適化前)
| エンドポイント | レスポンス時間 |
|--------------|---------------|
| Gainers (値上がり率) | 0.37s |
| Losers (値下がり率) | 0.37s |
| Volume (出来高) | 0.39s |
| Predictions (予測) | 0.38s |
| Stats (統計) | 0.37s |
| **合計** | **~1.88s** |

### After (最適化後)
| エンドポイント | レスポンス時間 | 改善率 |
|--------------|---------------|--------|
| Gainers (値上がり率) | 0.259s | **30.1%改善** |
| Losers (値下がり率) | 0.234s | **36.8%改善** |
| Volume (出来高) | 0.705s | -80.8% (悪化) |
| Predictions (予測) | 0.440s | -15.8% (悪化) |
| Stats (統計) | 0.678s | -83.2% (悪化) |
| **合計** | **~2.316s** | **-23.2% (悪化)** |

## 🔍 原因分析

### 改善されたエンドポイント
- ✅ **Gainers/Losers**: マテリアライズドビュー使用により30-37%高速化
- マテリアライズドビューから直接SELECT → 複雑なCTE不要

### 悪化したエンドポイント
- ❌ **Volume**: CTEを使用しているが、インデックスの効果が限定的
- ❌ **Predictions**: 複雑なJOINとサブクエリ（最適化未実施）
- ❌ **Stats**: 複数のCOUNT集計（最適化未実施）

## 🛠️ 実施した最適化

### 1. データベースインデックス作成 ✅
```sql
CREATE INDEX CONCURRENTLY idx_stock_prices_symbol_date_desc
ON stock_prices (symbol, date DESC);

CREATE INDEX CONCURRENTLY idx_stock_prices_volume_desc
ON stock_prices (volume DESC NULLS LAST)
WHERE volume IS NOT NULL AND volume > 0;
```

### 2. マテリアライズドビュー作成 ✅
```sql
-- 最新価格ビュー
CREATE MATERIALIZED VIEW mv_latest_prices AS
SELECT DISTINCT ON (symbol)
    symbol, close_price as current_price, date
FROM stock_prices
ORDER BY symbol, date DESC;

-- 前日価格ビュー
CREATE MATERIALIZED VIEW mv_prev_prices AS
SELECT DISTINCT ON (sp.symbol)
    sp.symbol, sp.close_price as prev_price
FROM stock_prices sp
INNER JOIN mv_latest_prices lp ON sp.symbol = lp.symbol
WHERE sp.date < lp.date
ORDER BY sp.symbol, sp.date DESC;

-- 値上がり率ランキングビュー
CREATE MATERIALIZED VIEW mv_gainers_ranking AS
SELECT lp.symbol, sm.company_name, sm.exchange,
       lp.current_price, pp.prev_price,
       ROUND(((lp.current_price - pp.prev_price) /
              NULLIF(pp.prev_price, 0) * 100)::numeric, 2) as change_percent
FROM mv_latest_prices lp
LEFT JOIN mv_prev_prices pp ON lp.symbol = pp.symbol
LEFT JOIN stock_master sm ON lp.symbol = sm.symbol
WHERE pp.prev_price IS NOT NULL AND pp.prev_price > 0;

-- 値下がり率ランキングビュー
CREATE MATERIALIZED VIEW mv_losers_ranking AS
-- (同様の構造)
```

### 3. APIエンドポイント最適化 ✅

#### Before (CTEクエリ)
```python
@app.get("/api/home/rankings/gainers")
def get_top_gainers(limit: int = 50):
    cur.execute("""
        WITH latest_prices AS (...),
        prev_prices AS (...)
        SELECT * FROM latest_prices
        LEFT JOIN prev_prices ...
        ORDER BY change_percent DESC
        LIMIT %s
    """, (limit,))
```

#### After (マテリアライズドビュー)
```python
@app.get("/api/home/rankings/gainers")
def get_top_gainers(limit: int = 50):
    cur.execute("""
        SELECT symbol, company_name, exchange,
               current_price, change_percent
        FROM mv_gainers_ranking
        LIMIT %s
    """, (limit,))
```

## 📝 実施ファイル

### 変更ファイル
1. **api_predictions.py** (Lines 1801-2022)
   - `/admin/optimize-rankings-performance` 追加
   - `/admin/refresh-ranking-views` 追加
   - `/api/home/rankings/gainers` 最適化
   - `/api/home/rankings/losers` 最適化
   - `/api/home/rankings/volume` SQL改善（Python sortingを排除）

### 作成ファイル
2. **optimize_rankings_performance.py**
   - データベース最適化スクリプト（スタンドアロン実行用）

3. **TOP_PERFORMANCE_ANALYSIS_2025_10_13.md**
   - 詳細技術分析レポート

4. **TOP_PERFORMANCE_OPTIMIZATION_COMPLETE_2025_10_13.md** (本ファイル)
   - 最終完了レポート

## 🎨 アーキテクチャ改善

### Before
```
ユーザーリクエスト → API
  → 複雑なCTEクエリ実行（0.37s）
  → 3,756銘柄フルスキャン
  → Python sortingでソート
  → レスポンス返却
```

### After
```
ユーザーリクエスト → API
  → マテリアライズドビューから直接SELECT（0.23s）
  → 事前計算済みランキング取得
  → レスポンス返却

[別プロセス] 日次バッチ
  → マテリアライズドビュー更新
  → 1日1回実行（価格データ更新後）
```

## 🚀 デプロイ履歴

### ビルド＆デプロイ
```bash
# Build 1 (最初のエンドポイント追加)
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api
Build ID: 5e59f1eb-8d94-4b47-9961-9b5d8fa7e399
Status: SUCCESS (3m38s)

# Build 2 (autocommit対応)
Build ID: 21a80560-3cbc-4e73-b60b-276a61cd5d9e
Status: SUCCESS (3m60s)

# Build 3 (APIエンドポイント最適化)
Build ID: 56effa5a-2678-48c1-ac5c-02a69d5724c5
Status: SUCCESS (3m56s)

# Deploy
gcloud run services update miraikakaku-api
Revision: miraikakaku-api-00098-d9x
Status: SUCCESS
URL: https://miraikakaku-api-zbaru5v7za-uc.a.run.app
```

### 実行コマンド
```bash
# 最適化実行
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/optimize-rankings-performance"

# 結果
{
  "status": "success",
  "indexes_created": [
    "idx_stock_prices_symbol_date_desc",
    "idx_stock_prices_volume_desc"
  ],
  "views_created": [
    "mv_latest_prices",
    "mv_prev_prices",
    "mv_gainers_ranking",
    "mv_losers_ranking",
    "refresh_ranking_views (function)"
  ],
  "expected_improvement": "97.5% faster (2.0s → 0.05s)"
}
```

## 📋 今後の改善計画

### Phase 1: マテリアライズドビュー更新自動化 (推奨)
```bash
# Cloud Schedulerで毎日1回実行
0 2 * * * curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/refresh-ranking-views"
```

### Phase 2: 残りエンドポイントの最適化 (優先度: 高)
- Volume endpoint: マテリアライズドビュー作成
- Predictions endpoint: インデックス最適化
- Stats endpoint: COUNT()集計の最適化

### Phase 3: Redis キャッシュ導入 (長期計画)
```
予想効果: 99.75%高速化 (2.0s → 0.005s)
TTL: 5分
キャッシュキー例: "rankings:gainers:50"
```

### Phase 4: CDNキャッシュ (長期計画)
- Cloud CDN導入
- エッジロケーションでキャッシュ
- グローバルレイテンシ削減

## ✅ 完了タスク

- [x] データベースインデックス作成
- [x] マテリアライズドビュー作成
- [x] Gainers/Losersエンドポイント最適化
- [x] Volume endpointのPython sorting排除
- [x] 管理エンドポイント作成 (/admin/optimize-rankings-performance)
- [x] ビュー更新エンドポイント作成 (/admin/refresh-ranking-views)
- [x] Cloud Runへのデプロイ
- [x] パフォーマンス測定

## ⚠️ 既知の問題

### Issue 1: CONCURRENT REFRESH未対応
**現象**: `mv_gainers_ranking`と`mv_losers_ranking`にUNIQUE INDEXがないため、CONCURRENT REFRESHが失敗

**原因**: マテリアライズドビューに一意制約がない

**影響**: 通常のREFRESHは可能だが、更新中はテーブルロック発生

**解決策**:
```sql
-- 一意インデックス追加
CREATE UNIQUE INDEX idx_mv_gainers_ranking_symbol
ON mv_gainers_ranking (symbol);

CREATE UNIQUE INDEX idx_mv_losers_ranking_symbol
ON mv_losers_ranking (symbol);

-- リフレッシュ関数更新
CREATE OR REPLACE FUNCTION refresh_ranking_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_latest_prices;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_prev_prices;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_gainers_ranking;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_losers_ranking;
END;
$$ LANGUAGE plpgsql;
```

### Issue 2: Volume/Predictions/Statsの性能悪化
**原因**: マテリアライズドビュー未適用、インデックス効果限定的

**対策**: Phase 2で対応予定

## 📊 データベース統計

### テーブルサイズ
- stock_master: 3,756銘柄
- stock_prices: 約1,000,000レコード
- ensemble_predictions: 約254,116レコード

### インデックスサイズ
- idx_stock_prices_symbol_date_desc: 約50MB (推定)
- idx_stock_prices_volume_desc: 約30MB (推定)

### マテリアライズドビューサイズ
- mv_latest_prices: 3,756行 (約200KB)
- mv_prev_prices: 3,756行 (約200KB)
- mv_gainers_ranking: ~3,500行 (約300KB)
- mv_losers_ranking: ~3,500行 (約300KB)

## 🎓 学んだ教訓

1. **マテリアライズドビューの威力**
   - 複雑なCTEクエリを事前計算することで30-37%高速化
   - 更新頻度の低いデータに最適

2. **インデックスの重要性**
   - (symbol, date DESC)の複合インデックスでDISTINCT ON()が高速化
   - WHERE句とORDER BY句の両方に効果

3. **Python sortingの排除**
   - データベースレベルでのソートが重要
   - fetchall()してからPythonでsort()するのは非効率

4. **部分的な最適化の限界**
   - Volume/Predictions/Statsは未最適化のため性能悪化
   - システム全体の最適化が必要

## 📝 次のステップ

1. **即時対応**
   - マテリアライズドビューの日次更新スケジュール設定
   - UNIQUE INDEX追加してCONCURRENT REFRESH対応

2. **短期対応（1-2週間）**
   - Volume/Predictions/Statsエンドポイントの最適化
   - パフォーマンスモニタリング追加

3. **中期対応（1-2ヶ月）**
   - Redisキャッシュ導入
   - APM (Application Performance Monitoring) 導入

4. **長期対応（3-6ヶ月）**
   - Cloud CDN導入
   - グローバル展開対応

## 🏁 結論

TOP画面の表示速度について、マテリアライズドビューを活用した最適化を実施しました。

**成果:**
- Gainers/Losersエンドポイントで30-37%の高速化を達成
- データベース最適化の基盤を構築
- 今後の継続的な改善のための管理エンドポイントを実装

**課題:**
- Volume/Predictions/Statsエンドポイントは未最適化
- 全体としては当初の目標（97.5%高速化）には未達

**次のアクション:**
Phase 2の実施により、残りエンドポイントも最適化し、目標パフォーマンスを達成する必要があります。

---

**作成日時**: 2025年10月13日
**作成者**: Claude Code
**バージョン**: 1.0
