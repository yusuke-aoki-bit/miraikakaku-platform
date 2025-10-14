# TOP画面パフォーマンス分析レポート - 2025-10-13

## 問題の概要

**症状**: TOP画面の表示が遅い

**測定結果**:
- Frontend初回ロード: 0.39秒
- API個別レスポンス時間: 各0.37-0.39秒
- **合計APIレスポンス時間**: 約2秒（5つのAPIを並列呼び出し）

## 原因分析

### 1. TOP画面のAPI呼び出し

[miraikakakufront/app/page.tsx](miraikakakufront/app/page.tsx:81-87) で5つのAPIを並列呼び出し:

```typescript
const [gainersData, losersData, volumeData, predictionsData, statsData] = await Promise.all([
  apiClient.getTopGainers(50),        // 0.37秒
  apiClient.getTopLosers(50),         // 0.37秒
  apiClient.getTopVolume(50),         // 0.39秒
  apiClient.getTopPredictions(50),    // 0.38秒
  apiClient.getMarketSummaryStats(),  // 0.37秒
]);
```

### 2. APIエンドポイントのボトルネック

各ランキングAPIは**全銘柄をスキャンする複雑なCTEクエリ**を実行:

#### `/api/home/rankings/gainers` ([api_predictions.py:674-705](api_predictions.py:674-705))

```sql
WITH latest_prices AS (
    SELECT DISTINCT ON (symbol)
        symbol, close_price as current_price, date
    FROM stock_prices           -- 全銘柄スキャン (3,756銘柄)
    ORDER BY symbol, date DESC
),
prev_prices AS (
    SELECT DISTINCT ON (sp.symbol)
        sp.symbol, sp.close_price as prev_price
    FROM stock_prices sp
    INNER JOIN latest_prices lp ON sp.symbol = lp.symbol
    WHERE sp.date < lp.date
    ORDER BY sp.symbol, sp.date DESC
)
SELECT ...
FROM latest_prices lp
LEFT JOIN prev_prices pp ON lp.symbol = pp.symbol
LEFT JOIN stock_master sm ON lp.symbol = sm.symbol
ORDER BY change_percent DESC NULLS LAST
LIMIT 50
```

**問題点**:
- `DISTINCT ON (symbol)` で全3,756銘柄をスキャン
- 最新価格と前日価格を毎回計算
- インデックスが効いていない可能性
- 結果は50件のみだが、全銘柄を処理

#### `/api/home/rankings/losers` ([api_predictions.py:730-761](api_predictions.py:730-761))

- `gainers`と同じ構造（ソート順が逆）
- 同様に全銘柄をスキャン

#### `/api/home/rankings/volume` ([api_predictions.py:119-150](api_predictions.py:119-150))

```sql
SELECT DISTINCT ON (sp.symbol)
    sp.symbol, sm.company_name, sm.exchange,
    sp.close_price as price, sp.volume, sp.date
FROM stock_prices sp
LEFT JOIN stock_master sm ON sp.symbol = sm.symbol
WHERE sp.volume IS NOT NULL AND sp.volume > 0
ORDER BY sp.symbol, sp.date DESC, sp.volume DESC
```

その後、**Pythonでソート**:
```python
sorted_results = sorted(all_results, key=lambda x: x['volume'], reverse=True)[:limit]
```

**問題点**:
- 全銘柄をメモリに読み込み
- SQLではなくPythonでソート（非効率）

#### `/api/home/rankings/predictions` ([api_predictions.py:159-178](api_predictions.py:159-178))

```sql
WITH ranked_predictions AS (
    SELECT DISTINCT ON (ep.symbol)
        ep.symbol, ...
    FROM ensemble_predictions ep    -- 全予測レコードをスキャン
    WHERE ep.prediction_date >= CURRENT_DATE
    ORDER BY ep.symbol, ep.prediction_date DESC
)
SELECT * FROM ranked_predictions
ORDER BY predicted_change DESC NULLS LAST
LIMIT 50
```

**問題点**:
- `ensemble_predictions` テーブル全体をスキャン（約254,116レコード）

## 解決策

### 短期的な解決策（即座に実施可能）

#### 1. インデックスの追加

```sql
-- 最新価格取得用の複合インデックス
CREATE INDEX CONCURRENTLY idx_stock_prices_symbol_date_desc
ON stock_prices (symbol, date DESC);

-- 出来高ランキング用
CREATE INDEX CONCURRENTLY idx_stock_prices_volume_desc
ON stock_prices (volume DESC NULLS LAST)
WHERE volume IS NOT NULL AND volume > 0;

-- 予測データ用
CREATE INDEX CONCURRENTLY idx_ensemble_predictions_date_symbol
ON ensemble_predictions (prediction_date DESC, symbol)
WHERE prediction_date >= CURRENT_DATE;
```

**期待効果**: 各API 0.37秒 → **0.1秒** (70%削減)

#### 2. 出来高ランキングのSQL最適化

Pythonソートをやめて、SQLで完結:

```sql
SELECT DISTINCT ON (sp.symbol)
    sp.symbol, sm.company_name, sm.exchange,
    sp.close_price as price, sp.volume
FROM stock_prices sp
LEFT JOIN stock_master sm ON sp.symbol = sm.symbol
WHERE sp.volume IS NOT NULL AND sp.volume > 0
ORDER BY sp.symbol, sp.date DESC
ORDER BY volume DESC NULLS LAST
LIMIT 50;
```

### 中期的な解決策（推奨）

#### 3. マテリアライズドビューの作成

事前計算された結果を保持:

```sql
-- 最新価格ビュー
CREATE MATERIALIZED VIEW mv_latest_prices AS
SELECT DISTINCT ON (symbol)
    symbol, close_price as current_price, date
FROM stock_prices
ORDER BY symbol, date DESC;

CREATE UNIQUE INDEX ON mv_latest_prices (symbol);

-- 前日価格ビュー
CREATE MATERIALIZED VIEW mv_prev_prices AS
SELECT DISTINCT ON (sp.symbol)
    sp.symbol, sp.close_price as prev_price
FROM stock_prices sp
INNER JOIN mv_latest_prices lp ON sp.symbol = lp.symbol
WHERE sp.date < lp.date
ORDER BY sp.symbol, sp.date DESC;

CREATE UNIQUE INDEX ON mv_prev_prices (symbol);

-- 値上がり率ランキングビュー
CREATE MATERIALIZED VIEW mv_gainers_ranking AS
SELECT
    lp.symbol, sm.company_name, sm.exchange,
    lp.current_price, pp.prev_price,
    ROUND(((lp.current_price - pp.prev_price) / NULLIF(pp.prev_price, 0) * 100)::numeric, 2) as change_percent
FROM mv_latest_prices lp
LEFT JOIN mv_prev_prices pp ON lp.symbol = pp.symbol
LEFT JOIN stock_master sm ON lp.symbol = sm.symbol
WHERE pp.prev_price IS NOT NULL AND pp.prev_price > 0
ORDER BY change_percent DESC NULLS LAST;

CREATE INDEX ON mv_gainers_ranking (change_percent DESC NULLS LAST);
```

**修正後のAPIエンドポイント**:

```python
@app.get("/api/home/rankings/gainers")
def get_top_gainers(limit: int = 50):
    """値上がり率ランキング（マテリアライズドビュー使用）"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT symbol, company_name, exchange, current_price, change_percent
            FROM mv_gainers_ranking
            LIMIT %s
        """, (limit,))

        results = cur.fetchall()
        return [
            {
                "symbol": row['symbol'],
                "name": row['company_name'] or row['symbol'],
                "exchange": row['exchange'] or '',
                "price": float(row['current_price']),
                "change": float(row['change_percent'])
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
```

**期待効果**: 各API 0.37秒 → **0.01秒** (97%削減)

#### 4. ビューの更新スケジュール

```sql
-- 更新関数
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

Cloud Schedulerで毎日更新:
- 日本市場終了後: 16:00 JST
- 米国市場終了後: 06:00 JST

### 長期的な解決策

#### 5. Redisキャッシュの導入

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.get("/api/home/rankings/gainers")
def get_top_gainers(limit: int = 50):
    # キャッシュチェック
    cache_key = f"rankings:gainers:{limit}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # データベースクエリ
    results = ... # クエリ実行

    # キャッシュ保存（5分間）
    redis_client.setex(cache_key, 300, json.dumps(results))

    return results
```

**期待効果**: キャッシュヒット時 0.37秒 → **0.001秒** (99.7%削減)

## 実装手順

### フェーズ1: インデックス追加（即座）

1. `optimize_rankings_performance.py` を実行
   ```bash
   python optimize_rankings_performance.py
   ```

2. インデックス作成を確認

### フェーズ2: マテリアライズドビュー（推奨）

1. ビュー作成
   ```bash
   python optimize_rankings_performance.py
   ```

2. [api_predictions.py](api_predictions.py) のランキングエンドポイントを修正

3. Cloud Schedulerでビュー更新ジョブを設定

4. デプロイ＆検証

### フェーズ3: Redisキャッシュ（長期）

1. Redis インスタンス作成（Cloud Memorystore）
2. Pythonアプリにredis連携コード追加
3. デプロイ＆検証

## パフォーマンス改善予測

| 施策 | 現在 | 改善後 | 削減率 |
|------|------|--------|--------|
| インデックス追加 | 2.0秒 | 0.5秒 | 75% |
| マテリアライズドビュー | 2.0秒 | 0.05秒 | 97.5% |
| Redisキャッシュ | 2.0秒 | 0.005秒 | 99.75% |

## 作成ファイル

1. [optimize_rankings_performance.py](optimize_rankings_performance.py) - 最適化スクリプト
2. このレポート

## 次のステップ

1. **即座に実施**: インデックス追加
   - Cloud SQLに直接接続してスクリプト実行
   - または、管理者APIエンドポイントを追加

2. **今週中に実施**: マテリアライズドビュー
   - ビュー作成
   - APIエンドポイント修正
   - デプロイ

3. **来月実施**: Redisキャッシュ
   - Cloud Memorystore セットアップ
   - コード統合

---

**作成日**: 2025-10-13
**分析者**: AI Assistant
**ステータス**: 分析完了、実装待ち
