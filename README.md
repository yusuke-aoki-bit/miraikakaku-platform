# 🚀 Miraikakaku - AI株価予測プラットフォーム

**AI駆動の株価予測・投資分析システム** - LSTM・Vertex AIを活用した次世代投資プラットフォーム

[![System Status](https://img.shields.io/badge/System-Fully_Operational-brightgreen.svg)]()
[![API Status](https://img.shields.io/badge/API-v4.0_Integrated-blue.svg)]()
[![Database Status](https://img.shields.io/badge/Database-Connected-green.svg)]()
[![AI System](https://img.shields.io/badge/AI-LSTM%20%2B%20Vertex%20AI-purple.svg)]()
[![Last Updated](https://img.shields.io/badge/Updated-2025--08--27-blue.svg)]()

## 📊 システム概要

Miraikakakuは、**LSTM神経ネットワーク**と**Google Vertex AI**を組み合わせた高度な株価予測プラットフォームです。リアルタイムデータ処理、機械学習予測、包括的な投資分析を統合したシステムです。

## 🎯 核心機能

### 🤖 AI予測システム
- **LSTM予測モデル**: 60日間の履歴データから7日先予測
- **Vertex AI統合**: Google Cloud AutoMLによる高精度予測
- **ハイブリッド予測**: 複数モデル結果の統合
- **信頼度スコア**: 各予測の確実性評価

### 📈 投資分析機能  
- **株価予測**: 個別銘柄の詳細予測とトレンド分析
- **セクター分析**: 業界別パフォーマンス比較
- **テーマ投資**: 投資テーマの発掘と分析
- **ランキング**: 成長ポテンシャル・リスク評価

### 🔧 技術基盤
- **リアルタイムデータ**: Yahoo Finance統合
- **Cloud SQL**: 高可用性データベース
- **フォールバック機能**: 自動エラー回復システム
- **スケーラブル**: Google Cloud Run自動スケーリング

## 🏗️ システム構成

```
Frontend (Next.js) → API (FastAPI) → Cloud SQL
                                   ↓
              Batch System (LSTM + Vertex AI)
```

### コンポーネント
- **Frontend**: https://miraikakaku-front-zbaru5v7za-uc.a.run.app
- **API**: https://miraikakaku-api-465603676610.us-central1.run.app
- **Batch System**: LSTM + Vertex AI予測エンジン
- **Database**: Google Cloud SQL (MySQL 8.4)

## ⚡ 最新アップデート (2025-08-27)

### ✅ 完了済み改善
1. **Cloud SQL接続修復**: データベース完全復旧
2. **統合API**: integrated_main.py による統一システム
3. **LSTM+Vertex AI**: ハイブリッド予測システム稼働
4. **エラーハンドリング**: 自動フォールバック機能
5. **セキュリティ強化**: 機密情報の適切な管理

### 🔧 技術仕様
- **Python**: 3.11
- **TensorFlow**: 2.13+
- **FastAPI**: 0.104+
- **Next.js**: 14 (App Router)
- **MySQL**: 8.4
- **Google Cloud**: Cloud Run, Cloud SQL, Vertex AI

## 📊 現在のステータス (2025-08-27 18:49)

| 項目 | 状態 | 詳細 |
|------|------|------|
| システム | 🟢 完全稼働 | 全機能正常動作 |
| API | 🟢 稼働中 | v4.0統合版 |
| データベース | 🟢 接続済み | Cloud SQL正常 |
| AI予測 | 🟢 稼働中 | LSTM+Vertex AI |
| フロントエンド | 🟢 稼働中 | 全ページアクセス可能 |

## 🚀 クイックスタート

### 開発環境セットアップ

```bash
# Frontend
cd miraikakakufront
npm install
npm run dev

# API
cd miraikakakuapi/functions
pip install -r requirements.txt
python integrated_main.py

# Batch System
cd miraikakakubatch/functions  
pip install -r requirements.txt
python simple_batch_main.py
```

### 環境変数設定

```env
# Cloud SQL
CLOUD_SQL_PASSWORD=[Secret Manager]
CLOUD_SQL_USER=root
CLOUD_SQL_DATABASE=miraikakaku_prod
CLOUD_SQL_INSTANCE=miraikakaku
CLOUD_SQL_REGION=us-central1

# Vertex AI
GOOGLE_CLOUD_PROJECT=pricewise-huqkr
VERTEX_AI_LOCATION=us-central1
```

## 📚 ドキュメント

### 詳細ドキュメント
- [システム構成詳細](/docs/SYSTEM_ARCHITECTURE.md)
- [デプロイメント状況](/docs/DEPLOYMENT_STATUS.md)
- [API実装詳細](/docs/API_IMPLEMENTATION_FINAL_COMPLETE.md)

### 開発・運用
- [開発ガイド](DEVELOPMENT_GUIDE.md)
- [CI/CDセットアップ](CI_CD_SETUP.md)
- [API リファレンス](API_REFERENCE.md)

## 🔍 主要API エンドポイント

```
GET /health                                    # システムヘルスチェック
GET /api/finance/stocks/{symbol}/predictions   # 株価予測
GET /api/finance/stocks/{symbol}/price         # 株価履歴
GET /api/finance/sectors                       # セクター分析
GET /api/finance/rankings/growth-potential     # 成長ランキング
```

## 🏆 システムの特徴

### 💡 技術的優位性
- **AI統合**: LSTM + Vertex AIハイブリッド
- **高可用性**: 99.9%稼働率目標
- **自動回復**: エラー時自動フォールバック
- **スケーラブル**: クラウドネイティブ設計

### 📈 投資家向け機能
- **高精度予測**: 複数AI モデル統合
- **リスク評価**: 信頼度スコア付き予測
- **包括分析**: セクター・テーマ横断分析
- **リアルタイム**: 最新データに基づく判断

## 🤝 貢献・サポート

### 開発チーム
- **アーキテクチャ**: マイクロサービス + クラウドネイティブ
- **AI/ML**: TensorFlow + Google Cloud Vertex AI
- **フロントエンド**: Next.js + TypeScript
- **インフラ**: Google Cloud Platform

### 問題報告
システムに問題が発生した場合:
1. [システムステータス](SYSTEM_STATUS.md) を確認
2. [API ヘルスチェック](https://miraikakaku-api-465603676610.us-central1.run.app/health) を実行
3. 必要に応じて issue を作成

---

**Miraikakaku** - 未来を予測する、今を変える投資プラットフォーム

*Last Updated: 2025-08-27 - System Fully Operational*