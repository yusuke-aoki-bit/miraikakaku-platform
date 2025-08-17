# 🏗️ Miraikakaku プロジェクト群 - 再現可能設計書

## 📋 概要

この文書は、`/mnt/c/Users/yuuku/cursor/` 配下のすべてのMiraikakakuプロジェクトを完全に再現するための包括的な設計書です。

## 🎯 プロジェクト構成

### 1. メインプロジェクト: `miraikakakufront/`
**種類**: Next.js + FastAPI統合プラットフォーム  
**説明**: 金融分析・株価予測のメインプラットフォーム

### 2. APIサーバー: `miraikakakuapi/`
**種類**: FastAPI専用バックエンド  
**説明**: 株価データAPI・機械学習推論サービス

### 3. バッチ処理: `miraikakakubatch/`
**種類**: Python データ処理・ML パイプライン  
**説明**: 定期データ取得・機械学習モデル訓練

### 4. モノレポ統合: `miraikakakumonorepo/`
**種類**: 統合モノレポ構成  
**説明**: 全サービスの統合管理環境

## 🏛️ システムアーキテクチャ

### 技術スタック

#### フロントエンド
- **Framework**: Next.js 15 (App Router)
- **UI**: React 19 + TypeScript
- **Styling**: Tailwind CSS + Framer Motion
- **Charts**: Chart.js, Recharts, Plotly.js
- **State**: Zustand + SWR
- **WebAssembly**: Rust + wasm-pack

#### バックエンド
- **API**: FastAPI + SQLAlchemy
- **Database**: MySQL 8.0 + Cloud SQL
- **Cache**: Redis
- **ML**: TensorFlow, ONNX, Vertex AI
- **Scheduling**: Python Schedule + Kubeflow Pipelines

#### インフラ
- **Container**: Docker + Docker Compose
- **Cloud**: Google Cloud Platform
- **Monitoring**: Prometheus + Grafana + ELK Stack
- **Security**: JWT認証 + RBAC

### データベース設計

#### 主要テーブル
1. **stock_master**: 株式マスターデータ
2. **stock_price_history**: 株価履歴データ
3. **stock_predictions**: AI予測結果
4. **ai_inference_log**: 推論ログ

## 🚀 プロジェクト再現手順

### Phase 1: 基盤インフラ構築

#### 1.1 ディレクトリ構造作成
```bash
mkdir -p /mnt/c/Users/yuuku/cursor/{miraikakakufront,miraikakakuapi,miraikakakubatch,miraikakakumonorepo}
cd /mnt/c/Users/yuuku/cursor
```

#### 1.2 Git リポジトリ初期化
```bash
# 各プロジェクトでGit初期化
cd miraikakakufront && git init
cd ../miraikakakuhost && git init  
cd ../miraikakakubatch && git init
cd ../miraikakakumonorepo && git init
```

### Phase 2: メインプラットフォーム構築 (`miraikakakufront/`)

#### 2.1 Next.js プロジェクト初期化
```bash
cd miraikakakufront
npx create-next-app@latest . --typescript --tailwind --eslint --app --use-npm
```

#### 2.2 パッケージ依存関係
```json
{
  "dependencies": {
    "next": "15.1.0",
    "react": "19.1.0",
    "react-dom": "19.1.0",
    "typescript": "^5.7.2",
    "chart.js": "^4.4.7",
    "chartjs-adapter-date-fns": "^3.0.0",
    "framer-motion": "^11.13.5",
    "swr": "^2.2.5",
    "zustand": "^5.0.2",
    "zod": "^3.24.1",
    "plotly.js": "^2.35.2",
    "react-plotly.js": "^2.6.0",
    "recharts": "^2.13.3",
    "lucide-react": "^0.460.0",
    "bcryptjs": "^2.4.3"
  }
}
```

#### 2.3 ディレクトリ構造
```
src/
├── app/                    # Next.js App Router
│   ├── api/               # API Routes
│   ├── (main)/           # メインページ群
│   ├── auth/             # 認証ページ
│   └── management/       # 管理画面
├── components/           # Reactコンポーネント
│   ├── charts/          # チャート系
│   ├── common/          # 共通コンポーネント
│   ├── features/        # 機能別コンポーネント
│   └── layout/          # レイアウト
├── hooks/               # カスタムフック
├── lib/                 # ユーティリティ・API
├── types/               # TypeScript型定義
└── utils/               # ヘルパー関数
```

### Phase 3: APIサーバー構築 (`miraikakakuhost/`)

#### 3.1 Python環境構築
```bash
cd miraikakakuhost
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

#### 3.2 主要依存関係
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
SQLAlchemy>=2.0.0
pymysql>=1.1.0
cloud-sql-python-connector[pymysql]>=1.2.0
pandas>=2.1.0
numpy>=1.24.0
yfinance>=0.2.0
google-cloud-aiplatform>=1.38.0
scikit-learn>=1.3.0
```

#### 3.3 ディレクトリ構造
```
functions/
├── api/                 # API エンドポイント
│   ├── finance/        # 金融データAPI
│   └── models/         # データモデル
├── database/           # データベース設定
│   └── models/         # SQLAlchemyモデル
├── repositories/       # データアクセス層
├── services/           # ビジネスロジック
│   ├── finance/        # 金融サービス
│   └── external/       # 外部API連携
└── utils/              # ユーティリティ
```

### Phase 4: バッチ処理システム (`miraikakakubatch/`)

#### 4.1 構造
```
functions/
├── main.py             # エントリーポイント
├── database/           # データベース接続
├── services/           # バッチサービス
│   ├── data_pipeline_robust.py
│   ├── ml_pipeline.py
│   └── vertex_ai_service.py
└── utils/              # バッチユーティリティ
```

#### 4.2 機能
- 定期的な株価データ取得
- 機械学習モデル訓練
- Vertex AI での推論
- データ品質監視

### Phase 5: モノレポ統合 (`miraikakakumonorepo/`)

#### 5.1 パッケージ構成
```
packages/
├── frontend/           # Next.js フロントエンド
├── api/               # FastAPI バックエンド  
├── batch/             # バッチ処理
└── shared/            # 共通型定義・ユーティリティ
```

#### 5.2 共通設定
- Workspaces設定
- 統一開発スクリプト
- 型共有システム
- Docker Compose統合

## 🔧 設定ファイル

### 環境変数設定

#### メインプロジェクト (`.env`)
```env
NODE_ENV=development
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_FINANCE_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
API_BASE_URL=http://localhost:8000
```

#### APIサーバー (`.env`)
```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/miraikakakufront
CLOUD_SQL_CONNECTION_NAME=project:region:instance
GOOGLE_APPLICATION_CREDENTIALS=gcp-service-account.json
VERTEX_AI_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1
LOG_LEVEL=INFO
```

### Docker設定

#### docker-compose.yml
- MySQL 8.0 (ポート3306)
- Redis (ポート6379)
- FastAPI (ポート8000)
- Next.js (ポート3000)
- Prometheus (ポート9090)
- Grafana (ポート3001)
- Elasticsearch + Kibana

## 🧪 テスト環境

### フロントエンド
- **Unit**: Jest + React Testing Library
- **E2E**: Playwright
- **Component**: Storybook (削除済み)

### バックエンド
- **Unit**: pytest
- **Integration**: pytest + SQLAlchemy
- **Load**: Locust (推奨)

## 🚀 デプロイメント

### Google Cloud Platform
- **Frontend**: Cloud Run
- **API**: Cloud Run + Cloud SQL
- **Batch**: Cloud Functions + Vertex AI
- **Monitoring**: Cloud Monitoring + Cloud Logging

### 本番環境設定
- Cloud SQL (MySQL)
- Cloud Storage (静的ファイル)
- Cloud CDN
- Cloud Load Balancing

## 📊 監視・運用

### メトリクス
- アプリケーション: Prometheus + Grafana
- インフラ: Google Cloud Monitoring
- ログ: ELK Stack
- セキュリティ: Cloud Security Command Center

### アラート
- API レスポンス時間
- データベース接続
- ML モデル精度
- システムリソース使用率

## 🔐 セキュリティ

### 認証・認可
- JWT ベース認証
- RBAC (Role-Based Access Control)
- API レート制限
- CORS設定

### データ保護
- 機密データ暗号化
- API キー管理 (Secret Manager)
- SQL インジェクション対策
- XSS 対策

## 📈 機械学習パイプライン

### モデル種類
- **時系列予測**: LSTM, Prophet
- **分類**: Random Forest, XGBoost  
- **回帰**: Linear Regression, SVR

### MLOps
- Vertex AI Pipelines
- モデルバージョニング
- A/B テスト
- ドリフト検出

## 🔄 開発ワークフロー

### 1. ローカル開発
```bash
# 統一開発環境起動
npm run dev:unified

# 個別サービス起動
npm run dev:frontend  # フロントエンド
npm run dev:api       # API
npm run dev:batch     # バッチ
```

### 2. Docker開発
```bash
npm run docker:dev    # 開発環境
npm run docker:logs   # ログ確認
npm run docker:down   # 停止
```

### 3. 本番デプロイ
```bash
npm run build:all     # 全体ビルド
npm run deploy:prod   # 本番デプロイ
```

## 📁 重要ファイル

### 設定ファイル
- `package.json`: Node.js依存関係
- `requirements.txt`: Python依存関係
- `docker-compose.yml`: Docker設定
- `tsconfig.json`: TypeScript設定
- `next.config.js`: Next.js設定

### スクリプト
- `scripts/dev-unified.sh`: 統一開発サーバー
- `scripts/env-manager.sh`: 環境変数管理
- `scripts/start_all_services.sh`: 全サービス起動

### API仕様
- `openapi.json`: OpenAPI仕様書
- `lib/generated-api-stub/`: 自動生成APIクライアント

## 🔄 データフロー

```
External APIs (yfinance, Alpha Vantage)
    ↓
Batch Processing (miraikakakubatch)
    ↓
Database (MySQL)
    ↓
API Server (miraikakakuhost)
    ↓
Frontend (miraikakakufront)
    ↓
Users
```

## 🛠️ 開発環境セットアップ

### 必要なソフトウェア
- Node.js 18+ & npm 8+
- Python 3.9+
- Docker & Docker Compose
- MySQL 8.0
- Redis 7.0

### インストール手順
```bash
# 1. リポジトリクローン
git clone <repository-url>
cd miraikakakufront

# 2. 依存関係インストール
npm install
npm run build:shared

# 3. 環境変数設定
npm run env:init
npm run env:validate

# 4. データベース初期化
docker-compose up mysql redis -d
npm run db:migrate

# 5. 開発サーバー起動
npm run dev:unified
```

## 📦 パッケージ管理

### NPM Workspaces
```json
{
  "workspaces": ["apps/shared"],
  "scripts": {
    "build:shared": "npm run build -w @miraikakakufront/shared"
  }
}
```

### Python仮想環境
```bash
# APIサーバー
cd miraikakakuhost
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# バッチ処理
cd miraikakakubatch  
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🔧 カスタマイズ可能要素

### 環境変数
- データベース接続情報
- 外部APIキー
- Google Cloud設定
- セキュリティ設定

### 設定ファイル
- `next.config.js`: フロントエンド設定
- `config.py`: バックエンド設定  
- `docker-compose.yml`: インフラ設定

## 📚 ドキュメント参照

### 既存ドキュメント
- `docs/miraikakaku_system_design.md`: システム設計詳細
- `docs/ENV_USAGE_GUIDE.md`: 環境変数ガイド
- `MONOREPO_MIGRATION_GUIDE.md`: モノレポ移行手順
- `deploy/gcp/README.md`: GCPデプロイガイド

### API仕様
- OpenAPI 3.1.0準拠
- 自動生成クライアントコード
- TypeScript型定義連携

## 🔄 継続的インテグレーション

### GitHub Actions
- `.github/workflows/ci-cd.yml`: メインCI/CD
- `.github/workflows/e2e-tests.yml`: E2Eテスト
- `.github/workflows/security-scan.yml`: セキュリティスキャン

### テスト戦略
- **Unit**: 各パッケージでのユニットテスト
- **Integration**: サービス間連携テスト
- **E2E**: ユーザーシナリオテスト

## 🎯 再現時の注意点

### 1. 環境依存設定
- Google Cloud プロジェクト設定
- サービスアカウントキー配置
- データベース認証情報

### 2. 外部サービス連携
- Alpha Vantage API キー
- yfinance 設定
- Vertex AI モデル配置

### 3. セキュリティ設定
- JWT シークレット生成
- CORS オリジン設定
- API レート制限調整

## 🔍 トラブルシューティング

### よくある問題
1. **データベース接続エラー**: 認証情報・ネットワーク確認
2. **API キー不正**: 外部サービス設定確認
3. **Docker 起動失敗**: ポート競合・リソース不足確認
4. **TypeScript エラー**: 型定義更新・ビルド実行

### デバッグコマンド
```bash
npm run health           # システム状態確認
npm run logs            # ログ確認
npm run env:validate    # 環境変数検証
docker-compose logs -f  # Docker ログ
```

## 📋 チェックリスト

### 基盤構築
- [ ] Node.js/Python 環境構築
- [ ] Docker 環境構築
- [ ] Git リポジトリ初期化
- [ ] 依存関係インストール

### サービス設定  
- [ ] データベース設定・マイグレーション
- [ ] 環境変数設定・検証
- [ ] 外部API キー設定
- [ ] Docker Compose 起動確認

### 動作確認
- [ ] フロントエンド (http://localhost:3000)
- [ ] API サーバー (http://localhost:8000)
- [ ] データベース接続確認
- [ ] バッチ処理動作確認

### 本番対応
- [ ] Google Cloud 設定
- [ ] CI/CD パイプライン設定
- [ ] 監視・アラート設定
- [ ] セキュリティ設定

---

この設計書に従うことで、Miraikakaku プロジェクト群を完全に再現できます。各フェーズを順次実行し、チェックリストで進捗を確認してください。