# Phase 3 実装計画 - A, B, D, E同時実施

## 📅 実施日時
2025年10月13日

## 🎯 Phase 3の目標
A (フロントエンド最適化)、B (データ収集改善)、D (詳細ページ最適化)、E (データベース最適化) を順次実施し、システム全体のパフォーマンスと品質を向上させる

---

## ✅ Phase 3-A: フロントエンド最適化 (進行中)

### 実装済み
1. **SWRライブラリ導入** ✅
   - `npm install swr` 完了
   - package.json更新済み

2. **カスタムフック作成** ✅
   - `miraikakakufront/app/hooks/useRankings.ts` 作成完了
   - キャッシング戦略実装:
     - refreshInterval: 60秒
     - revalidateOnFocus: false
     - dedupingInterval: 10秒

3. **Skeleton UI** ✅ (既存実装確認)
   - `miraikakakufront/app/page.tsx` にSkeleton UI実装済み
   - SkeletonCard コンポーネント使用

### 次のステップ
1. **page.tsx更新**
   - useRankingsフックを使用するよう変更
   - Progressive Loading実装
   - エラーハンドリング改善

2. **パフォーマンステスト**
   - Lighthouse測定
   - Core Web Vitals確認
   - キャッシュヒット率確認

### 期待効果
- 初回表示速度: 0.26s (API最遅時間)
- 2回目以降: <0.1s (キャッシュヒット時)
- ユーザー体感速度: 大幅改善

---

## 📋 Phase 3-B: データ収集システム改善

### 実装項目

#### 1. 並列バッチコレクターの最適化
**ファイル**: `generate_ensemble_predictions_parallel.py`

**改善内容**:
```python
# エラーハンドリング強化
- リトライロジック追加 (最大3回)
- タイムアウト設定 (30秒/シンボル)
- エラーログ詳細化

# パフォーマンス改善
- バッチサイズ最適化 (500 → 300)
- 並列度調整 (CPU数に応じて動的)
- メモリ使用量モニタリング
```

**実装コード例**:
```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def collect_symbol_data(symbol: str) -> dict:
    """シンボルデータ取得（リトライ付き）"""
    try:
        # データ取得ロジック
        data = fetch_data(symbol)
        return data
    except Exception as e:
        logger.error(f"Symbol {symbol} collection failed: {str(e)}")
        raise
```

#### 2. 予測精度向上
**ファイル**: LSTMモデル関連ファイル

**改善内容**:
- 特徴量エンジニアリング改善
  - 移動平均 (5日、20日、60日)
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - ボリンジャーバンド

- モデルハイパーパラメータチューニング
  - LSTM layers: 2 → 3
  - Units: 50 → 64
  - Dropout: 0.2 → 0.3
  - Epochs: 50 → 100

#### 3. ニュース収集強化
**改善内容**:
- Finnhub API統合強化
- NewsAPI.org レート制限対策
- ニュース品質フィルタリング

---

## 🔍 Phase 3-D: 銘柄詳細ページ最適化

### 実装項目

#### 1. 詳細ページAPI最適化

**新しいマテリアライズドビュー作成**:
```sql
-- 銘柄詳細データビュー
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_stock_details AS
SELECT
    sp.symbol,
    sm.company_name,
    sm.exchange,
    sm.sector,
    sm.industry,
    sp.close_price as current_price,
    sp.volume as current_volume,
    sp.date as last_updated,
    ep.ensemble_prediction,
    ep.ensemble_confidence,
    ROUND(((ep.ensemble_prediction - sp.close_price) /
           NULLIF(sp.close_price, 0) * 100)::numeric, 2) as predicted_change
FROM (
    SELECT DISTINCT ON (symbol)
        symbol, close_price, volume, date
    FROM stock_prices
    ORDER BY symbol, date DESC
) sp
LEFT JOIN stock_master sm ON sp.symbol = sm.symbol
LEFT JOIN (
    SELECT DISTINCT ON (symbol)
        symbol, ensemble_prediction, ensemble_confidence
    FROM ensemble_predictions
    WHERE prediction_date >= CURRENT_DATE - INTERVAL '1 day'
    ORDER BY symbol, prediction_date DESC
) ep ON sp.symbol = ep.symbol;

CREATE UNIQUE INDEX idx_mv_stock_details_symbol ON mv_stock_details (symbol);
```

**api_predictions.pyに追加**:
```python
@app.get("/api/stocks/{symbol}/details")
def get_stock_details(symbol: str):
    """銘柄詳細取得（マテリアライズドビュー使用）"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT * FROM mv_stock_details
            WHERE symbol = %s
        """, (symbol,))

        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Symbol not found")

        return {
            "symbol": result['symbol'],
            "companyName": result['company_name'],
            "exchange": result['exchange'],
            "sector": result['sector'],
            "industry": result['industry'],
            "currentPrice": float(result['current_price']),
            "volume": int(result['current_volume']) if result['current_volume'] else 0,
            "predictedPrice": float(result['ensemble_prediction']) if result['ensemble_prediction'] else None,
            "confidence": float(result['ensemble_confidence']) if result['ensemble_confidence'] else None,
            "predictedChange": float(result['predicted_change']) if result['predicted_change'] else None,
            "lastUpdated": result['last_updated'].isoformat() if result['last_updated'] else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
```

#### 2. チャート表示最適化
- データポイント削減 (1日足 → 週足オプション)
- レンダリング最適化
- Progressive Loading実装

---

## 🗄️ Phase 3-E: データベース全体最適化

### 実装項目

#### 1. 追加インデックス作成

**よく使われるクエリのインデックス**:
```sql
-- 1. 銘柄詳細ページ用
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date
ON stock_prices (symbol, date DESC);

-- 2. 予測履歴取得用
CREATE INDEX IF NOT EXISTS idx_ensemble_predictions_symbol_date
ON ensemble_predictions (symbol, prediction_date DESC);

-- 3. ニュース検索用
CREATE INDEX IF NOT EXISTS idx_stock_news_symbol_date
ON stock_news (symbol, published_at DESC);

-- 4. 複合インデックス（銘柄 + 取引所）
CREATE INDEX IF NOT EXISTS idx_stock_master_symbol_exchange
ON stock_master (symbol, exchange) WHERE is_active = TRUE;

-- 5. セクター・業種別検索用
CREATE INDEX IF NOT EXISTS idx_stock_master_sector_industry
ON stock_master (sector, industry) WHERE is_active = TRUE;
```

#### 2. PostgreSQL設定最適化

**Cloud SQL設定変更**:
```sql
-- 1. 共有バッファサイズ増加
-- shared_buffers = 25% of RAM (推奨)
ALTER SYSTEM SET shared_buffers = '2GB';

-- 2. ワークメモリ増加
ALTER SYSTEM SET work_mem = '64MB';

-- 3. メンテナンスワークメモリ
ALTER SYSTEM SET maintenance_work_mem = '512MB';

-- 4. 有効なキャッシュサイズ
ALTER SYSTEM SET effective_cache_size = '6GB';

-- 5. ランダムページコスト
ALTER SYSTEM SET random_page_cost = 1.1;  -- SSD環境用
```

#### 3. EXPLAIN ANALYZE実行

**主要クエリの分析**:
```bash
# Gainers ranking分析
EXPLAIN ANALYZE SELECT * FROM mv_gainers_ranking LIMIT 50;

# Losers ranking分析
EXPLAIN ANALYZE SELECT * FROM mv_losers_ranking LIMIT 50;

# Volume ranking分析
EXPLAIN ANALYZE SELECT * FROM mv_volume_ranking LIMIT 50;

# Predictions ranking分析
EXPLAIN ANALYZE SELECT * FROM mv_predictions_ranking LIMIT 50;

# Stats summary分析
EXPLAIN ANALYZE SELECT * FROM mv_stats_summary;
```

---

## 📊 実装スケジュール

### Phase 3-A: フロントエンド最適化 (優先度: 最高)
- [x] SWRライブラリ導入
- [x] カスタムフック作成
- [ ] page.tsx更新
- [ ] パフォーマンステスト
- **推定時間**: 残り2-3時間

### Phase 3-B: データ収集改善 (優先度: 高)
- [ ] バッチコレクター最適化
- [ ] 予測精度向上
- [ ] ニュース収集強化
- **推定時間**: 6-8時間

### Phase 3-D: 詳細ページ最適化 (優先度: 中)
- [ ] 詳細ページAPI作成
- [ ] マテリアライズドビュー追加
- [ ] フロントエンド更新
- **推定時間**: 4-5時間

### Phase 3-E: データベース最適化 (優先度: 高)
- [ ] 追加インデックス作成
- [ ] PostgreSQL設定チューニング
- [ ] EXPLAIN ANALYZE分析
- **推定時間**: 3-4時間

---

## 🎯 次のアクション

### 即座に実施 (Phase 3-A完了)
1. page.txを更新してuseRankingsフック使用
2. パフォーマンステスト実施
3. 結果をドキュメント化

### 続けて実施 (Phase 3-E)
1. データベース追加インデックス作成
2. EXPLAIN ANALYZE分析
3. PostgreSQL設定最適化

### その後実施 (Phase 3-D → Phase 3-B)
1. 詳細ページAPI実装
2. データ収集システム改善

---

## 📝 関連ドキュメント

1. NEXT_PHASE_RECOMMENDATIONS_2025_10_13.md - Phase 3提案
2. PHASE2_COMPLETION_REPORT_2025_10_13.md - Phase 2完了レポート
3. PHASE3_IMPLEMENTATION_PLAN_2025_10_13.md - Phase 3実装計画 (本ファイル)

---

**作成日**: 2025年10月13日
**ステータス**: Phase 3-A 進行中
**次のアクション**: page.tsx更新 & パフォーマンステスト
