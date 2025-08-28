# Miraikakaku デプロイメントガイド

## 🏗️ アーキテクチャ概要

### システム構成
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Frontend (Next)   │    │   API (FastAPI)     │    │   Batch Processor   │
│                     │    │                     │    │                     │
│ Cloud Run (3000)    │────│ Cloud Run (8000)    │────│ Cloud Run (8001)    │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                      │                            │
                                      │                            │
                           ┌─────────────────────┐                 │
                           │   Cloud SQL MySQL   │─────────────────┘
                           │   (34.58.103.36)    │
                           └─────────────────────┘
```

### 技術スタック
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **API**: Python FastAPI, SQLAlchemy, Pydantic
- **Batch**: Python, pandas, numpy, yfinance
- **Database**: Cloud SQL MySQL 8.0
- **Infrastructure**: Google Cloud Run, Cloud Build, Artifact Registry

## 🚀 デプロイ手順

### 前提条件
1. Google Cloud CLI (`gcloud`) がインストール済み
2. プロジェクト認証済み: `gcloud auth login`
3. プロジェクト設定: `gcloud config set project pricewise-huqkr`

### API デプロイ

#### 方法1: ソースコードから直接デプロイ（推奨）
```bash
cd /path/to/miraikakakuapi
gcloud run deploy miraikakaku-api-fastapi \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars="LOG_LEVEL=INFO,NODE_ENV=production"
```

#### 方法2: Cloud Buildを使用
```bash
cd /path/to/miraikakakuapi
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api-fastapi --timeout=1200s
gcloud run deploy miraikakaku-api-fastapi \
  --image gcr.io/pricewise-huqkr/miraikakaku-api-fastapi \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10
```

### Batch デプロイ
```bash
cd /path/to/miraikakakubatch
gcloud run deploy miraikakaku-batch-final \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8001 \
  --memory 4Gi \
  --cpu 2 \
  --max-instances 1 \
  --timeout 3600 \
  --set-env-vars="LOG_LEVEL=INFO"
```

### Frontend デプロイ
```bash
cd /path/to/miraikakakufront
gcloud run deploy miraikakaku-front \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 3000 \
  --memory 2Gi \
  --cpu 1 \
  --max-instances 10
```

## 🗄️ データベース設定

### Cloud SQL 接続情報
```yaml
Host: 34.58.103.36
Port: 3306
Database: miraikakaku_prod
User: root
Password: [環境変数 CLOUD_SQL_PASSWORD]
```

### 接続文字列形式
```python
# ローカル開発・Cloud Run環境
mysql+pymysql://root:{password}@{host}:3306/miraikakaku_prod

# App Engine環境
mysql+pymysql://root:{password}@/miraikakaku_prod?unix_socket=/cloudsql/{connection_name}
```

### 必要なテーブル
```sql
-- 実装済み
CREATE TABLE stock_master (...);
CREATE TABLE stock_prices (...);  
CREATE TABLE stock_predictions (...);
CREATE TABLE ai_decision_factors (...);
CREATE TABLE theme_insights (...);
CREATE TABLE analysis_reports (...);
CREATE TABLE batch_logs (...);

-- 未実装（将来の機能）
CREATE TABLE user_profiles (...);
CREATE TABLE user_watchlists (...);
CREATE TABLE user_portfolios (...);
CREATE TABLE prediction_contests (...);
CREATE TABLE user_contest_predictions (...);
```

## 🔧 環境変数設定

### API (.env)
```bash
# Database
CLOUD_SQL_HOST=34.58.103.36
CLOUD_SQL_PASSWORD=Yuuku717
CLOUD_SQL_CONNECTION_NAME=pricewise-huqkr:asia-northeast1:miraikakaku-db

# Application
LOG_LEVEL=INFO
NODE_ENV=production
FRONTEND_URL=https://miraikakaku-front-465603676610.us-central1.run.app

# Optional
GAE_ENV=standard  # App Engine環境の場合
```

### Batch (.env)
```bash
# Database (APIと共通)
CLOUD_SQL_HOST=34.58.103.36
CLOUD_SQL_PASSWORD=Yuuku717

# Batch specific
BATCH_SIZE=1000
MAX_WORKERS=4
LOG_LEVEL=INFO
```

## 📦 Docker設定

### API Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ libffi-dev libssl-dev curl pkg-config \
    default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "main.py"]
```

### 主要依存関係 (requirements.txt)
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
SQLAlchemy>=2.0.0
pymysql>=1.1.0
cloud-sql-python-connector[pymysql]>=1.2.0
pandas>=2.1.0
numpy>=1.24.0
pydantic[email]>=2.5.0
python-dotenv>=1.0.0
requests>=2.31.0
```

## 🔍 デプロイ後確認手順

### 1. ヘルスチェック
```bash
curl https://miraikakaku-api-fastapi-465603676610.us-central1.run.app/health
```

### 2. API動作確認
```bash
# 銘柄検索
curl "https://miraikakaku-api-fastapi-465603676610.us-central1.run.app/api/finance/stocks/search?query=AAPL&limit=1"

# 価格データ
curl "https://miraikakaku-api-fastapi-465603676610.us-central1.run.app/api/finance/stocks/1401/price?limit=3"

# 予測データ
curl "https://miraikakaku-api-fastapi-465603676610.us-central1.run.app/api/finance/stocks/1401/predictions?limit=3"

# AI決定要因
curl "https://miraikakaku-api-fastapi-465603676610.us-central1.run.app/api/ai-factors/all?limit=3"

# テーマ洞察
curl "https://miraikakaku-api-fastapi-465603676610.us-central1.run.app/api/insights/themes" | head -10
```

### 3. バッチ処理確認
```bash
# データベース統計確認
curl https://miraikakaku-batch-final-465603676610.us-central1.run.app/health

# または直接バッチを実行
curl -X POST https://miraikakaku-batch-final-465603676610.us-central1.run.app/run-batch
```

## 🛠️ トラブルシューティング

### よくある問題と解決策

#### 1. Build Timeout
```bash
# タイムアウト設定を延長
gcloud builds submit --timeout=1200s
```

#### 2. Memory Error
```bash
# メモリを増加
gcloud run deploy {service} --memory 4Gi
```

#### 3. Database Connection Error
- Cloud SQL IPアドレスが正しいか確認
- パスワードが正しく設定されているか確認
- Cloud SQL AuthN/AuthZ設定を確認

#### 4. Import Error
```bash
# 依存関係を確認
pip install -r requirements.txt

# Python pathを確認
export PYTHONPATH="${PYTHONPATH}:/path/to/functions"
```

### ログ確認
```bash
# Cloud Run ログ
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=miraikakaku-api-fastapi" --limit=50

# Cloud Build ログ
gcloud logging read "resource.type=build" --limit=20
```

## 📊 モニタリング設定

### Cloud Run メトリクス
- Request count/latency
- Instance count
- Memory/CPU utilization
- Error rate

### データベースメトリクス
- Connection count
- Query performance
- Storage usage
- Backup status

### アラート設定例
```yaml
# CPU利用率が80%を超えた場合
cpu_utilization > 0.8 for 5 minutes

# エラー率が5%を超えた場合  
error_rate > 0.05 for 2 minutes

# レスポンス時間が2秒を超えた場合
response_time > 2000ms for 1 minute
```

## 🔒 セキュリティ考慮事項

### 1. IAM設定
- Cloud Run Invoker権限の適切な設定
- Cloud SQL Client権限の最小化
- サービスアカウントの適切な設定

### 2. ネットワークセキュリティ
- VPC Connectorの使用検討
- Private IP設定
- Firewall ルール設定

### 3. シークレット管理
- 環境変数でのパスワード管理
- Secret Managerの活用検討
- API キーの適切な管理

## 📋 デプロイメントチェックリスト

### デプロイ前
- [ ] 環境変数の設定確認
- [ ] requirements.txt の更新
- [ ] Dockerfile の検証
- [ ] ローカルテストの実行
- [ ] データベース接続確認

### デプロイ実行
- [ ] API デプロイ実行
- [ ] Batch デプロイ実行
- [ ] Frontend デプロイ実行（必要に応じて）
- [ ] ヘルスチェック確認
- [ ] エンドポイント動作確認

### デプロイ後
- [ ] ログ監視
- [ ] パフォーマンス確認
- [ ] エラー率監視
- [ ] バッチ処理動作確認
- [ ] データ増加状況確認

---

*最終更新: 2025-08-23 21:00 JST*
*Deployment Version: Production v1.0*