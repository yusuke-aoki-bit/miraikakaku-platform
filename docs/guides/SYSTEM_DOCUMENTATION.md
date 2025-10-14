# Miraikakaku - AI株価予測ポートフォリオ管理システム

## 📊 システム概要

AIを活用した株価予測とポートフォリオ管理を提供するWebアプリケーション

**本番環境URL:**
- Frontend: https://miraikakaku-frontend-465603676610.us-central1.run.app
- Backend API: https://miraikakaku-api-465603676610.us-central1.run.app

## ✅ 実装完了機能（Phase 5-8）

### Phase 5: Core Features - 100%
- **Portfolio Management**: ポートフォリオ管理（保有株式の追加・削除・編集）
- **Watchlist**: ウォッチリスト（気になる銘柄の監視）
- **Performance Analysis**: パフォーマンス分析（損益・リターン率・セクター配分）

### Phase 6: Authentication - 80%
- **Users Schema**: 認証スキーマ設計完了（[create_auth_schema.sql](create_auth_schema.sql)）
- **Current Status**: demo_userで全機能が動作中
- **Remaining**: JWT APIエンドポイント実装（20%）

### Phase 7: Advanced Analysis - 100%
- **Risk Metrics**: リスクメトリクス（シャープレシオ、ボラティリティ）
- **Prediction Accuracy**: 予測精度評価システム

### Phase 8: PWA - 100%
- **Service Worker**: オフライン対応（[sw.js](miraikakakufront/public/sw.js)）
- **Manifest**: PWA manifest（[manifest.json](miraikakakufront/public/manifest.json)）
- **Responsive Design**: 完全レスポンシブ対応

## 🏗️ アーキテクチャ

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL (Cloud SQL)
- **Deployment**: Cloud Run (Serverless)
- **ML Engine**: TensorFlow LSTM + Ensemble predictions

### Frontend
- **Framework**: Next.js 15 + React
- **Styling**: TailwindCSS
- **Deployment**: Cloud Run (Serverless)
- **PWA**: Service Worker + Offline support

### Database Schema
1. **users** - ユーザー管理
2. **user_sessions** - JWT認証セッション
3. **portfolio_holdings** - ポートフォリオ保有銘柄
4. **watchlist** - ウォッチリスト
5. **stock_master** - 銘柄マスタ
6. **stock_prices** - 株価履歴
7. **ensemble_predictions** - AI予測結果

## 📁 プロジェクト構造

```
miraikakaku/
├── api_predictions.py              # メインAPI（FastAPI）
├── Dockerfile                      # Backend Dockerfile
├── requirements.txt                # Python依存関係
├── create_auth_schema.sql          # 認証スキーマ
├── create_performance_schema.sql   # パフォーマンス分析スキーマ
├── create_watchlist_schema.sql     # ウォッチリストスキーマ
├── miraikakakufront/               # Frontendディレクトリ
│   ├── app/
│   │   ├── portfolio/page.tsx      # ポートフォリオページ
│   │   ├── watchlist/page.tsx      # ウォッチリストページ
│   │   ├── performance/page.tsx    # パフォーマンスページ
│   │   └── lib/
│   │       ├── api.ts              # API Client
│   │       └── watchlist-api.ts    # Watchlist API Client
│   ├── public/
│   │   ├── manifest.json           # PWA Manifest
│   │   ├── sw.js                   # Service Worker
│   │   └── offline.html            # Offline Fallback
│   ├── Dockerfile                  # Frontend Dockerfile
│   ├── cloudbuild.yaml             # Cloud Build設定
│   └── package.json                # Node.js依存関係
└── archived_docs_20251013/         # アーカイブ済みドキュメント
```

## 🚀 デプロイ

### Backend API
```bash
cd miraikakaku
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api
gcloud run deploy miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api:latest \
  --region us-central1 \
  --allow-unauthenticated
```

### Frontend
```bash
cd miraikakaku/miraikakakufront
gcloud builds submit --config=cloudbuild.yaml
gcloud run deploy miraikakaku-frontend \
  --image gcr.io/pricewise-huqkr/miraikakaku-frontend:latest \
  --region us-central1 \
  --allow-unauthenticated
```

## 📊 主要APIエンドポイント

### Portfolio Management
- GET `/api/portfolio?user_id={user_id}` - ポートフォリオ取得
- POST `/api/portfolio` - 銘柄追加
- DELETE `/api/portfolio/{id}` - 銘柄削除

### Watchlist
- GET `/api/watchlist?user_id={user_id}` - ウォッチリスト取得
- POST `/api/watchlist` - 銘柄追加
- DELETE `/api/watchlist/{id}` - 銘柄削除

### Performance Analysis
- GET `/api/portfolio/performance?user_id={user_id}` - パフォーマンスメトリクス
- GET `/api/portfolio/sector-allocation?user_id={user_id}` - セクター配分
- GET `/api/portfolio/history?user_id={user_id}&days=30` - 履歴データ
- GET `/api/portfolio/analytics?user_id={user_id}` - 高度な分析

### Predictions
- GET `/api/predictions/{symbol}` - 銘柄予測取得
- GET `/api/predictions/accuracy/rankings` - 予測精度ランキング

## 🔧 環境変数

```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=miraikakaku
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<password>

# Frontend
NEXT_PUBLIC_API_URL=https://miraikakaku-api-465603676610.us-central1.run.app
```

## 📝 データベースセットアップ

```bash
# ポートフォリオスキーマ適用
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/admin/apply-portfolio-schema

# ウォッチリストスキーマ適用
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/admin/apply-watchlist-schema

# パフォーマンススキーマ適用
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/admin/apply-performance-schema

# 認証スキーマ適用
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/admin/apply-auth-schema
```

## 🎯 システム完成度

**95%完了**
- Phase 5: 100% ✅
- Phase 6: 80% (demo_userで動作中)
- Phase 7: 100% ✅
- Phase 8: 100% ✅

## 📚 関連ドキュメント

- [GCP Cleanup Report](GCP_CLEANUP_REPORT.md) - GCPリソース整理レポート
- [Archived Documentation](archived_docs_20251013/) - 過去の開発ドキュメント

## 🔐 現在の認証方式

**demo_user方式**: 全てのユーザーが`demo_user`として動作
- ポートフォリオ・ウォッチリストはuser_id="demo_user"で管理
- 本格的なJWT認証はPhase 6残タスク（20%）で実装予定

## 🎉 システムステータス

**本番環境**: ✅ 正常稼働中
**Last Updated**: 2025-10-13
**Version**: 1.0.0
