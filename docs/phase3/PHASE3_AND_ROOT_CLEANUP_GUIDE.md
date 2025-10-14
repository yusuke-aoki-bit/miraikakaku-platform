# Phase 3 実装 & ルートディレクトリ整理ガイド

## 📋 Phase 3 実装状況

### ✅ 完了済み
- **Phase 3-A: フロントエンド最適化**
  - SWRライブラリ導入 ✅
  - カスタムフック作成 (`useRankings.ts`) ✅
  - キャッシング戦略実装 (60秒自動更新) ✅

- **Phase 2完了** (前回セッション)
  - 全7個のマテリアライズドビュー稼働中
  - TOP画面51.9%高速化達成

### 📝 次回実装推奨

#### Phase 3-D: 銘柄詳細ページ最適化
**api_predictions.pyに以下を追加**:

```python
# optimize-rankings-performance エンドポイント内に追加

# Step 2-8: 銘柄詳細ビュー (Phase 3-D)
try:
    cur.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_stock_details AS
        SELECT
            sp.symbol,
            sm.company_name,
            sm.exchange,
            sm.sector,
            sm.industry,
            sp.close_price as current_price,
            sp.open_price,
            sp.high_price,
            sp.low_price,
            sp.volume as current_volume,
            sp.date as last_updated,
            ep.ensemble_prediction,
            ep.ensemble_confidence,
            ROUND(((ep.ensemble_prediction - sp.close_price) /
                   NULLIF(sp.close_price, 0) * 100)::numeric, 2) as predicted_change
        FROM (
            SELECT DISTINCT ON (symbol)
                symbol, close_price, open_price, high_price, low_price, volume, date
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
        ) ep ON sp.symbol = ep.symbol
    """)
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_stock_details_symbol ON mv_stock_details (symbol)")
    conn.commit()
    results["views_created"].append("mv_stock_details")
except Exception as e:
    results["errors"].append(f"mv_stock_details: {str(e)}")

# リフレッシュ関数更新
# refresh_ranking_views() 関数内に以下を追加:
# REFRESH MATERIALIZED VIEW CONCURRENTLY mv_stock_details;
```

**新しいAPIエンドポイント追加**:

```python
@app.get("/api/stocks/{symbol}/details")
def get_stock_details(symbol: str):
    """銘柄詳細取得（Phase 3-D最適化版）"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT * FROM mv_stock_details
            WHERE UPPER(symbol) = UPPER(%s)
        """, (symbol,))

        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Symbol not found")

        return {
            "symbol": result['symbol'],
            "companyName": result['company_name'] or result['symbol'],
            "exchange": result['exchange'] or '',
            "sector": result['sector'] or 'N/A',
            "industry": result['industry'] or 'N/A',
            "currentPrice": float(result['current_price']),
            "openPrice": float(result['open_price']) if result['open_price'] else None,
            "highPrice": float(result['high_price']) if result['high_price'] else None,
            "lowPrice": float(result['low_price']) if result['low_price'] else None,
            "volume": int(result['current_volume']) if result['current_volume'] else 0,
            "predictedPrice": float(result['ensemble_prediction']) if result['ensemble_prediction'] else None,
            "confidence": float(result['ensemble_confidence']) if result['ensemble_confidence'] else None,
            "predictedChange": float(result['predicted_change']) if result['predicted_change'] else None,
            "lastUpdated": result['last_updated'].isoformat() if result['last_updated'] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
```

#### Phase 3-E: データベース追加インデックス
**Pythonスクリプトで実行**:

```python
import psycopg2
import os

def create_phase3_indexes():
    """Phase 3-E: 追加インデックス作成"""
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5433)),
        database=os.getenv('POSTGRES_DB', 'miraikakaku'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    indexes = [
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ensemble_predictions_symbol_date_desc ON ensemble_predictions (symbol, prediction_date DESC)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_news_symbol_date_desc ON stock_news (symbol, published_at DESC) WHERE published_at IS NOT NULL",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_master_exchange_active ON stock_master (exchange, is_active) WHERE is_active = TRUE",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_master_sector_industry ON stock_master (sector, industry) WHERE is_active = TRUE AND sector IS NOT NULL",
    ]

    for idx_sql in indexes:
        try:
            cur.execute(idx_sql)
            print(f"✅ Created: {idx_sql[:80]}...")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    create_phase3_indexes()
```

#### Phase 3-B: バッチコレクター改善
**generate_ensemble_predictions_parallel.py に追加**:

```python
# tenacityライブラリでリトライ実装
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def safe_predict_symbol(symbol: str) -> dict:
    """リトライ付き予測実行"""
    try:
        result = predict_symbol(symbol)
        return result
    except Exception as e:
        logger.error(f"Prediction failed for {symbol}: {str(e)}")
        raise

# バッチサイズ最適化
BATCH_SIZE = 300  # 500 → 300に削減
MAX_WORKERS = min(os.cpu_count() * 2, 16)  # CPU数の2倍、最大16
```

---

## 🗂️ ルートディレクトリ整理ガイド

### 📁 現在のルート構成の問題点
- 300個以上のMarkdownドキュメントが散乱
- 不要な一時ファイル、バックアップファイルが混在
- ドキュメントの整理が必要

### 🎯 整理方針

#### 1. ドキュメント整理
**作成するディレクトリ構造**:
```
docs/
├── phase1/          # Phase 1関連ドキュメント
├── phase2/          # Phase 2関連ドキュメント
├── phase3/          # Phase 3関連ドキュメント
├── archived/        # 古いドキュメント (2025年10月5日以前)
└── current/         # 最新の重要ドキュメント
```

**移動対象**:
```bash
# Phase 1ドキュメント
mv TOP_PERFORMANCE_*.md docs/phase1/
mv PHASE1_*.md docs/phase1/

# Phase 2ドキュメント
mv PHASE2_*.md docs/phase2/
mv TOP_PERFORMANCE_OPTIMIZATION_COMPLETE*.md docs/phase2/

# Phase 3ドキュメント
mv PHASE3_*.md docs/phase3/
mv NEXT_PHASE_*.md docs/phase3/

# アーカイブ対象 (2025年10月5日以前のドキュメント)
mv LAYER*.md docs/archived/
mv ROUND_*.md docs/archived/
mv FINAL_*.md docs/archived/
mv COMPLETE_*.md docs/archived/
mv COMPREHENSIVE_*.md docs/archived/
mv *_2025_10_0[1-5]*.md docs/archived/

# 最新の重要ドキュメント
cp README.md docs/current/
cp CURRENT_STATUS*.md docs/current/
cp NEXT_SESSION*.md docs/current/
```

#### 2. 不要ファイル削除
**削除対象**:
```bash
# バックアップファイル
rm -f *.backup
rm -f *_backup_*.md

# 一時ファイル
rm -f .*~
rm -f *~

# 重複ドキュメント
# (内容を確認してから削除)
```

#### 3. 残すべきファイル (ルート直下)
```
miraikakaku/
├── README.md                                    # プロジェクト説明
├── PHASE3_AND_ROOT_CLEANUP_GUIDE.md            # 本ファイル
├── PHASE3_ABDE_QUICK_IMPLEMENTATION_SUMMARY.md # Phase 3実装サマリー
├── GCP_CLEANUP_REPORT.md                       # インフラ状況
├── requirements.txt                            # Python依存関係
├── api_predictions.py                          # メインAPI
├── generate_ensemble_predictions_parallel.py   # バッチ処理
├── .env.example                                # 環境変数テンプレート
├── .gitignore                                  # Git除外設定
├── Dockerfile                                  # Dockerビルド
├── miraikakakufront/                           # フロントエンド
├── cloud_functions/                            # Cloud Functions
└── docs/                                       # 整理済みドキュメント
```

### 🚀 実行コマンド

**Step 1: ディレクトリ作成**
```bash
mkdir -p docs/{phase1,phase2,phase3,archived,current}
```

**Step 2: Phase別ドキュメント移動**
```bash
# Phase 1
find . -maxdepth 1 -name "TOP_PERFORMANCE_*.md" -o -name "PHASE1_*.md" | xargs -I {} mv {} docs/phase1/

# Phase 2
find . -maxdepth 1 -name "PHASE2_*.md" -o -name "*OPTIMIZATION_COMPLETE*.md" | xargs -I {} mv {} docs/phase2/

# Phase 3
find . -maxdepth 1 -name "PHASE3_*.md" -o -name "NEXT_PHASE_*.md" | xargs -I {} mv {} docs/phase3/
```

**Step 3: アーカイブ対象移動**
```bash
# LAYER, ROUND, FINAL系
find . -maxdepth 1 \( -name "LAYER*.md" -o -name "ROUND_*.md" -o -name "FINAL_*.md" \) | xargs -I {} mv {} docs/archived/

# 10月5日以前のドキュメント
find . -maxdepth 1 -name "*_2025_10_0[1-5]*.md" | xargs -I {} mv {} docs/archived/
```

**Step 4: 最新ドキュメントコピー**
```bash
cp README.md docs/current/ 2>/dev/null || true
cp CURRENT_STATUS*.md docs/current/ 2>/dev/null || true
cp NEXT_SESSION*.md docs/current/ 2>/dev/null || true
```

**Step 5: 不要ファイル削除**
```bash
# バックアップファイル削除
find . -maxdepth 1 -name "*.backup" -delete
find . -maxdepth 1 -name "*_backup_*.md" -delete

# 一時ファイル削除
find . -maxdepth 1 -name ".*~" -delete
find . -maxdepth 1 -name "*~" -delete
```

**Step 6: 整理完了確認**
```bash
# ルート直下のMDファイル数確認
ls -1 *.md | wc -l
# 目標: 10個以下

# docsディレクトリ内確認
ls -lR docs/
```

---

## 📊 期待される成果

### Phase 3完了後
- **Phase 3-A**: キャッシュヒット時<0.1秒
- **Phase 3-D**: 銘柄詳細ページ75%高速化
- **Phase 3-E**: 全体的なクエリ50%高速化
- **Phase 3-B**: エラー率50%削減

### ルート整理完了後
- ルート直下のMDファイル: 300個 → 10個以下
- 体系的なドキュメント構造
- メンテナンス性向上

---

## 🔧 次のセッションでの実装手順

1. **Phase 3-Eから開始** (15分)
   - `create_phase3_indexes.py` 作成・実行
   - 追加インデックス作成

2. **Phase 3-D実装** (30分)
   - `api_predictions.py` 更新
   - Build & Deploy
   - `/admin/optimize-rankings-performance` 実行

3. **ルート整理** (15分)
   - 上記コマンド順次実行
   - 整理完了確認

4. **Phase 3-B改善** (1時間、時間があれば)
   - バッチコレクターエラーハンドリング強化
   - テスト実行

---

**作成日**: 2025年10月13日
**次のアクション**: Phase 3-E → Phase 3-D → ルート整理 → Phase 3-B
