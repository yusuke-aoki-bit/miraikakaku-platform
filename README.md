# Miraikakaku - AI株価予測ポートフォリオ管理システム

AIと機械学習を活用した次世代株価予測・ポートフォリオ管理プラットフォーム

## 概要

Miraikakakuは、LSTMニューラルネットワークとEnsemble予測を組み合わせた高精度な株価予測システムと、
リアルタイム通知、ポートフォリオ管理、価格アラートなどの包括的な投資管理機能を提供するWebアプリケーションです。

### 本番環境URL
- **Frontend**: https://miraikakaku-frontend-465603676610.us-central1.run.app
- **Backend API**: https://miraikakaku-api-465603676610.us-central1.run.app
- **API Documentation**: https://miraikakaku-api-465603676610.us-central1.run.app/docs

### カスタムドメイン (準備中)
- miraikakaku.com
- price-wiser.com

---

## 主な機能

### Phase 6-10: 認証とユーザー機能 (100%)
- **JWT認証**: アクセストークン/リフレッシュトークンによる安全な認証
- **ウォッチリスト**: 気になる銘柄の監視・メモ機能
- **ポートフォリオ管理**: 保有銘柄の追加・編集・削除、損益計算
- **価格アラート**: 条件付き価格通知 (閾値/変動率/予測ベース)

### Phase 11: 高度な機能 (100%)
- **リアルタイム通知**: WebSocketによる即時アラート配信
- **プッシュ通知**: Web Push APIによるブラウザ通知
- **ポートフォリオ分析**: VaR、シャープレシオ、ベンチマーク比較
- **バックテスト機能**: 過去データによる戦略シミュレーション

### Phase 12: 機械学習統合 (100%)
- **カスタムLSTM訓練**: 22種類のテクニカル指標による予測精度向上 (27%改善)
- **AutoML統合**: Google Cloud Vertex AI AutoMLサポート
- **アンサンブル予測**: 複数モデルの組み合わせによる高精度予測
- **ファクター分析**: 5ファクターモデル (Value, Momentum, Quality, Size, Volatility)
- **ポートフォリオ最適化**: Markowitzの平均分散最適化

### Phase 13: プロダクション基盤 (100%)
- **Cloud CDN**: グローバル配信とキャッシング
- **Cloud Armor**: DDoS保護とWAF
- **Cloud Monitoring**: アップタイム監視とアラート
- **SEO最適化**: サイトマップ、robots.txt、構造化データ

---

## 技術スタック

### Backend
- **FastAPI** (Python 3.11) - 高速非同期WebAPI
- **PostgreSQL** (Cloud SQL) - リレーショナルデータベース
- **TensorFlow/Keras** - LSTM時系列予測
- **WebSocket** - リアルタイム通信
- **Cloud Run** - サーバーレスコンテナ実行環境

### Frontend
- **Next.js 15** - React SSR/SSGフレームワーク
- **TypeScript** - 型安全な開発
- **TailwindCSS** - ユーティリティファーストCSS
- **PWA** - オフライン対応、ホーム画面追加

### Infrastructure
- **Google Cloud Platform**
  - Cloud Run (Backend/Frontend)
  - Cloud SQL (PostgreSQL)
  - Cloud Storage (静的アセット)
  - Cloud CDN (グローバル配信)
  - Cloud Armor (セキュリティ)
  - Cloud Monitoring (監視)

---

## プロジェクト構造

```
miraikakaku/
├── README.md                        # このファイル
├── requirements.txt                 # Python依存関係
├── Dockerfile                       # Backend コンテナ
├── .env.example                     # 環境変数サンプル
│
├── api_predictions.py               # メインAPIサーバー
├── auth_endpoints.py                # 認証エンドポイント
├── auth_utils.py                    # 認証ユーティリティ
├── watchlist_endpoints.py           # ウォッチリストAPI
├── portfolio_endpoints.py           # ポートフォリオAPI
├── alerts_endpoints.py              # アラートAPI
├── websocket_notifications.py       # WebSocket通知システム
│
├── docs/                            # ドキュメント
│   ├── phases/                      # Phase別実装ドキュメント
│   │   ├── PHASE6_TO_10_COMPLETE.md
│   │   ├── PHASE7_10_DEPLOYMENT_COMPLETE.md
│   │   ├── PHASE11_ADVANCED_FEATURES_IMPLEMENTATION.md
│   │   └── PHASE12_ADVANCED_ML_AND_SOCIAL_FEATURES.md
│   ├── guides/                      # セットアップガイド
│   │   ├── CUSTOM_DOMAIN_SETUP_GUIDE.md
│   │   ├── PRODUCTION_INFRASTRUCTURE_SETUP.md
│   │   └── SYSTEM_DOCUMENTATION.md
│   └── reports/                     # 実装レポート
│       ├── CLEANUP_SUMMARY_2025_10_14.md
│       ├── FINAL_PRODUCTION_SETUP_COMPLETE.md
│       └── ...
│
├── scripts/                         # ユーティリティスクリプト
│   ├── custom_lstm_training.py      # カスタムLSTMトレーニング
│   ├── generate_ensemble_predictions.py
│   ├── database/                    # データベーススクリプト
│   │   ├── apply_all_schemas.sh
│   │   ├── apply_schemas_cloudsql.py
│   │   ├── create_auth_schema.sql
│   │   ├── create_watchlist_schema.sql
│   │   ├── apply_portfolio_schema.sql
│   │   └── create_alerts_schema.sql
│   ├── setup/                       # セットアップスクリプト
│   │   ├── setup_custom_domain.sh
│   │   └── setup_dual_domains.sh
│   └── deployment/                  # デプロイスクリプト
│
├── tests/                           # テストファイル
│   ├── test_phase7_10_api.py
│   └── test_phase7_10_endpoints.sh
│
└── miraikakakufront/                # フロントエンド
    ├── app/                         # Next.jsアプリ
    │   ├── page.tsx                 # ホーム
    │   ├── portfolio/               # ポートフォリオ
    │   ├── watchlist/               # ウォッチリスト
    │   ├── alerts/                  # アラート
    │   ├── accuracy/                # 予測精度
    │   └── monitoring/              # システム監視
    ├── components/                  # Reactコンポーネント
    │   ├── Header.tsx
    │   ├── Footer.tsx
    │   ├── NotificationSystem.tsx
    │   └── ...
    ├── contexts/                    # React Context
    │   └── AuthContext.tsx
    ├── lib/                         # ユーティリティ
    │   ├── api.ts
    │   └── websocket-client.ts
    ├── public/                      # 静的ファイル
    │   ├── manifest.json            # PWA manifest
    │   └── service-worker.js        # Service Worker
    ├── Dockerfile                   # Frontend コンテナ
    └── package.json
```

---

## クイックスタート

### 前提条件
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Google Cloud SDK (本番デプロイ用)

### ローカル開発

#### 1. Backendセットアップ

```bash
# リポジトリクローン
git clone <repository-url>
cd miraikakaku

# Python仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .envを編集してデータベース接続情報を設定

# データベーススキーマ適用
bash scripts/database/apply_all_schemas.sh

# サーバー起動
python api_predictions.py
# または: uvicorn api_predictions:app --reload --host 0.0.0.0 --port 8080
```

APIドキュメント: http://localhost:8080/docs

#### 2. Frontendセットアップ

```bash
cd miraikakakufront

# 依存関係インストール
npm install

# 環境変数設定
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8080 に設定

# 開発サーバー起動
npm run dev
```

アプリケーション: http://localhost:3000

---

## 本番デプロイ

### Backend (Cloud Run)

```bash
# Docker イメージビルド & プッシュ
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api --project=pricewise-huqkr

# Cloud Run デプロイ
gcloud run deploy miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars POSTGRES_HOST=<cloud-sql-ip>,POSTGRES_DB=miraikakaku
```

### Frontend (Cloud Run)

```bash
cd miraikakakufront

# Docker イメージビルド & プッシュ
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-frontend --project=pricewise-huqkr

# Cloud Run デプロイ
gcloud run deploy miraikakaku-frontend \
  --image gcr.io/pricewise-huqkr/miraikakaku-frontend:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=https://miraikakaku-api-465603676610.us-central1.run.app
```

---

## API エンドポイント

### 認証
- `POST /api/auth/register` - ユーザー登録
- `POST /api/auth/login` - ログイン (JWT発行)
- `GET /api/auth/me` - ユーザー情報取得
- `POST /api/auth/refresh` - トークン更新

### ウォッチリスト
- `GET /api/watchlist` - ウォッチリスト取得
- `POST /api/watchlist` - 銘柄追加
- `PUT /api/watchlist/{symbol}` - メモ更新
- `DELETE /api/watchlist/{symbol}` - 銘柄削除

### ポートフォリオ
- `GET /api/portfolio` - 保有銘柄取得
- `GET /api/portfolio/performance` - パフォーマンス分析
- `GET /api/portfolio/summary` - サマリー統計
- `POST /api/portfolio` - 銘柄追加
- `PUT /api/portfolio/{id}` - 保有情報更新
- `DELETE /api/portfolio/{id}` - 銘柄削除

### アラート
- `GET /api/alerts` - アラート一覧
- `POST /api/alerts` - アラート作成
- `POST /api/alerts/check` - 手動トリガーチェック
- `PUT /api/alerts/{id}` - アラート更新
- `DELETE /api/alerts/{id}` - アラート削除

### 予測
- `GET /api/predictions/{symbol}` - 銘柄予測取得
- `GET /api/predictions/accuracy` - 予測精度評価

---

## テスト

### API テスト
```bash
# 全APIエンドポイントテスト
python tests/test_phase7_10_api.py

# E2Eテスト
bash tests/test_phase7_10_endpoints.sh
```

### Frontend テスト
```bash
cd miraikakakufront
npm test
```

---

## ドキュメント

詳細なドキュメントは [docs/](docs/) フォルダを参照してください:

- **実装フェーズ**: [docs/phases/](docs/phases/)
- **セットアップガイド**: [docs/guides/](docs/guides/)
- **実装レポート**: [docs/reports/](docs/reports/)

---

## システムステータス

| Phase | 機能 | 完成度 |
|-------|------|--------|
| Phase 1-5 | 基本機能・予測システム | 100% |
| Phase 6 | 認証システム | 100% |
| Phase 7 | フロントエンド認証統合 | 100% |
| Phase 8 | ウォッチリストAPI | 100% |
| Phase 9 | ポートフォリオAPI | 100% |
| Phase 10 | アラートAPI | 100% |
| Phase 11 | WebSocket/Push通知/分析 | 100% |
| Phase 12 | ML統合/ソーシャル機能 | 100% |
| Phase 13 | プロダクション基盤 | 100% |

**本番環境**: 正常稼働中
**Last Updated**: 2025-10-14
**Version**: 2.0.0

---

## ライセンス

Copyright (c) 2025 Miraikakaku Project

---

## サポート

問題が発生した場合は、[Issues](https://github.com/your-repo/miraikakaku/issues) を作成してください。
