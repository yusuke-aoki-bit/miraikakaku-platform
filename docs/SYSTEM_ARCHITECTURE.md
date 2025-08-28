# Miraikakaku システム構成詳細ドキュメント

## 1. システム概要

Miraikakakuは、AI（LSTM/Vertex AI）を活用した株価予測システムです。リアルタイム株価データ取得、AI予測生成、ユーザーインターフェース提供の3層アーキテクチャで構成されています。

### 主要コンポーネント
- **Frontend**: Next.js + TypeScript製のウェブインターフェース
- **Backend API**: FastAPI + Python製のRESTful API
- **Batch System**: TensorFlow/Keras LSTMモデルを使用した予測バッチ処理
- **Database**: Google Cloud SQL (MySQL)
- **Infrastructure**: Google Cloud Platform (Cloud Run, Cloud Build, Vertex AI)

## 2. アーキテクチャ図

```
┌──────────────────────────────────────────────────────────────┐
│                         User Browser                         │
└──────────────────┬───────────────────────────────────────────┘
                   │ HTTPS
                   ▼
┌──────────────────────────────────────────────────────────────┐
│              Frontend (Next.js + TypeScript)                 │
│         https://miraikakaku-front-zbaru5v7za-uc.a.run.app   │
│                                                              │
│  - Pages: 株価分析、予測、ランキング、セクター分析          │
│  - Components: チャート、テーブル、分析ツール               │
│  - API Client: バックエンドとの通信                         │
└──────────────────┬───────────────────────────────────────────┘
                   │ REST API
                   ▼
┌──────────────────────────────────────────────────────────────┐
│         Backend API (FastAPI + Python)                       │
│      https://miraikakaku-api-465603676610.us-central1.run.app │
│                                                              │
│  実行ファイル: integrated_main.py                           │
│  - /api/finance/stocks/{symbol}/price - 株価取得            │
│  - /api/finance/stocks/{symbol}/predictions - AI予測取得    │
│  - /api/finance/sectors - セクター分析                      │
│  - /api/finance/rankings/* - 各種ランキング                 │
└────────┬─────────────────────────────────┬───────────────────┘
         │                                 │
         ▼                                 ▼
┌──────────────────┐          ┌────────────────────────────────┐
│  Yahoo Finance   │          │      Google Cloud SQL          │
│      API         │          │        (MySQL 8.0)             │
│                  │          │                                │
│  リアルタイム    │          │  Tables:                       │
│  株価データ      │          │  - stock_predictions           │
│                  │          │  - stock_prices                │
└──────────────────┘          │  - stock_master                │
                              └────────────────────────────────┘
                                           ▲
                                           │ データ書き込み
┌──────────────────────────────────────────┴───────────────────┐
│         Batch System (Python + TensorFlow)                   │
│     https://miraikakaku-batch-zbaru5v7za-uc.a.run.app       │
│                                                              │
│  実行ファイル: simple_batch_main.py                         │
│                                                              │
│  Components:                                                 │
│  - models/lstm_predictor.py: LSTM予測モデル                 │
│  - services/vertex_ai_service.py: Vertex AI統合             │
│  - services/report_generator.py: レポート生成               │
│  - database/cloud_sql.py: DB接続管理                        │
│                                                              │
│  Schedule:                                                   │
│  - 09:00 JST: 株価データ更新                                │
│  - 18:00 JST: レポート生成                                  │
│  - 02:00 JST: 古いデータクリーンアップ                      │
└──────────────────────────────────────────────────────────────┘
```

## 3. 各コンポーネント詳細

### 3.1 Frontend (miraikakakufront)

**技術スタック:**
- Next.js 14 (App Router)
- TypeScript 5
- Tailwind CSS
- Chart.js / Recharts
- Material-UI

**主要ファイル:**
```
miraikakakufront/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── page.tsx            # ホームページ
│   │   ├── predictions/        # AI予測ページ
│   │   ├── rankings/           # ランキングページ
│   │   ├── sectors/            # セクター分析
│   │   └── tools/              # 分析ツール
│   ├── components/
│   │   ├── charts/             # チャートコンポーネント
│   │   ├── sectors/            # セクター分析UI
│   │   └── predictions/        # 予測表示UI
│   └── lib/
│       └── api-client.ts       # API通信クライアント
```

**API Client設定:**
```typescript
// src/lib/api-client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://miraikakaku-api-zbaru5v7za-uc.a.run.app';

async getSectors(): Promise<APIResponse<any[]>> {
  return this.request('/api/finance/sectors', { method: 'GET' });
}
```

### 3.2 Backend API (miraikakakuapi)

**技術スタック:**
- FastAPI 0.104+
- Python 3.11
- SQLAlchemy 2.0
- PyMySQL
- yfinance
- pandas/numpy

**主要実行ファイル: integrated_main.py**

```python
# integrated_main.py の主要機能

1. データベース接続（フォールバック機能付き）
   - Cloud SQL接続試行
   - 失敗時はYahoo Finance直接取得

2. 予測データ取得フロー:
   def get_predictions_from_db(symbol, days):
       # 1. DBから予測を取得試行
       # 2. なければNone返却
   
   def generate_lstm_predictions(symbol, current_price, days):
       # フォールバック: リアルタイム予測生成
       # LSTMモデル風のアルゴリズムで予測

3. APIエンドポイント:
   - GET /api/finance/stocks/{symbol}/price
   - GET /api/finance/stocks/{symbol}/predictions
   - GET /api/finance/sectors
   - GET /api/finance/rankings/growth-potential
```

**Dockerfile設定:**
```dockerfile
# 統合版を使用
CMD ["uvicorn", "integrated_main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 3.3 Batch System (miraikakakubatch)

**技術スタック:**
- Python 3.11
- TensorFlow 2.13+
- Keras
- scikit-learn
- Google Cloud Vertex AI
- schedule (タスクスケジューラー)

**主要実行ファイル: simple_batch_main.py**

**LSTMモデル構成 (models/lstm_predictor.py):**
```python
class LSTMStockPredictor:
    def __init__(self):
        self.sequence_length = 60  # 60日間のデータを使用
        self.prediction_days = 7   # 7日先まで予測
        
    def build_model(self, input_shape):
        model = Sequential([
            LSTM(100, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(100, return_sequences=True),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(self.prediction_days)
        ])
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
```

**Vertex AI統合 (services/vertex_ai_service.py):**
```python
class VertexAIService:
    - モデルトレーニング
    - モデルデプロイメント
    - 推論エンドポイント管理
    - AutoMLテーブル活用
```

**Dockerfile設定:**
```dockerfile
# LSTMモデル版を使用
CMD ["python", "simple_batch_main.py"]
```

### 3.4 Database Schema (Cloud SQL)

**接続情報:**
- Instance: miraikakaku-db
- Database: stock_analysis
- Engine: MySQL 8.0

**テーブル構造:**

```sql
-- 株価予測テーブル
CREATE TABLE stock_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    prediction_date DATE NOT NULL,
    predicted_price DECIMAL(10, 2),
    confidence_score DECIMAL(5, 2),
    model_type VARCHAR(50) DEFAULT 'LSTM',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_date (symbol, prediction_date)
);

-- 株価履歴テーブル
CREATE TABLE stock_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(10, 2),
    high_price DECIMAL(10, 2),
    low_price DECIMAL(10, 2),
    close_price DECIMAL(10, 2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY idx_symbol_date (symbol, date)
);

-- 銘柄マスターテーブル
CREATE TABLE stock_master (
    symbol VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. デプロイメント構成

### 4.1 Cloud Build設定

**API (miraikakakuapi/cloudbuild.yaml):**
```yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/pricewise-huqkr/miraikakaku-api', '.']
images:
- 'gcr.io/pricewise-huqkr/miraikakaku-api'
```

**Batch (miraikakakubatch/cloudbuild.yaml):**
```yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/pricewise-huqkr/miraikakaku-batch', '.']
images:
- 'gcr.io/pricewise-huqkr/miraikakaku-batch'
```

### 4.2 Cloud Run Services

| サービス | URL | 状態 |
|---------|-----|------|
| miraikakaku-api | https://miraikakaku-api-zbaru5v7za-uc.a.run.app | Active |
| miraikakaku-batch | https://miraikakaku-batch-zbaru5v7za-uc.a.run.app | Active |
| miraikakaku-front | https://miraikakaku-front-zbaru5v7za-uc.a.run.app | Active |

## 5. データフロー

### 5.1 リアルタイム予測取得フロー

```
1. ユーザーがフロントエンドで銘柄を選択
   ↓
2. Frontend が API に予測をリクエスト
   GET /api/finance/stocks/AAPL/predictions?days=7
   ↓
3. API (integrated_main.py) の処理:
   a. Cloud SQLから予測データ取得を試行
   b. データがない場合:
      - Yahoo Financeから現在価格取得
      - generate_lstm_predictions()で予測生成
   ↓
4. JSON形式で予測データ返却
   ↓
5. Frontendでチャート表示
```

### 5.2 バッチ処理フロー

```
1. スケジューラーがタスク起動 (09:00 JST)
   ↓
2. BatchTasks.update_stock_prices() 実行
   ↓
3. Yahoo Finance APIから最新データ取得
   ↓
4. LSTMモデルで予測計算
   - 60日間の履歴データ使用
   - 7日先まで予測
   ↓
5. Cloud SQLに予測結果保存
   ↓
6. レポート生成 (18:00 JST)
```

## 6. エラーハンドリングとフォールバック

### 6.1 データベース接続エラー時

```python
# integrated_main.py
if not DATABASE_AVAILABLE:
    # Yahoo Finance から直接データ取得
    # リアルタイムで予測生成
    predictions = generate_lstm_predictions(symbol, current_price, days)
```

### 6.2 予測モデルエラー時

```python
# フォールバック予測アルゴリズム
def generate_lstm_predictions():
    # ランダムウォーク + トレンドベースの簡易予測
    volatility = 0.02  # 2%の日次ボラティリティ
    trend = np.random.uniform(-0.001, 0.002)
```

## 7. モニタリングとログ

### 7.1 ヘルスチェックエンドポイント

- API: https://miraikakaku-api-zbaru5v7za-uc.a.run.app/health
- Batch: https://miraikakaku-batch-zbaru5v7za-uc.a.run.app/health

### 7.2 ログ確認コマンド

```bash
# APIログ
gcloud run services logs read miraikakaku-api --limit=50

# バッチログ  
gcloud run services logs read miraikakaku-batch --limit=50

# ビルドログ
gcloud builds log [BUILD_ID]
```

## 8. 開発環境セットアップ

### 8.1 必要な環境変数

```env
# .env.production
NEXT_PUBLIC_API_URL=https://miraikakaku-api-zbaru5v7za-uc.a.run.app
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Cloud SQL接続
CLOUD_SQL_PASSWORD=[Set via Google Secret Manager]
CLOUD_SQL_USER=root
CLOUD_SQL_DATABASE=miraikakaku_prod
CLOUD_SQL_INSTANCE=miraikakaku
CLOUD_SQL_REGION=us-central1

# Vertex AI
GCP_PROJECT_ID=pricewise-huqkr
VERTEX_AI_LOCATION=us-central1
```

### 8.2 ローカル開発

```bash
# Frontend
cd miraikakakufront
npm install
npm run dev

# API
cd miraikakakuapi
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python integrated_main.py

# Batch
cd miraikakakubatch
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python simple_batch_main.py
```

## 9. トラブルシューティング

### 問題1: データが参照できない
**原因**: データベース接続失敗
**解決**: integrated_main.py のフォールバック機能が自動的にYahoo Finance を使用

### 問題2: セクター分析エラー
**原因**: APIエンドポイント不一致
**解決**: `/api/sectors` → `/api/finance/sectors` に修正済み

### 問題3: AI予測が表示されない
**原因**: バッチシステムが合成データを生成
**解決**: simple_batch_main.py (LSTMモデル版) に切り替え済み

## 10. 今後の改善点

1. **データベース接続の安定化**
   - Cloud SQL Proxyの導入
   - コネクションプーリングの最適化

2. **LSTMモデルの精度向上**
   - より多くの特徴量追加（テクニカル指標等）
   - ハイパーパラメータチューニング
   - Vertex AI AutoMLの活用

3. **スケーラビリティ**
   - Redis キャッシュ導入
   - 負荷分散の実装
   - CDN活用

4. **監視強化**
   - Cloud Monitoring アラート設定
   - エラー率の閾値設定
   - パフォーマンスメトリクス追跡