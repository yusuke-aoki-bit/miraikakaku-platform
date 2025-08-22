# 📁 Miraikakaku プロジェクト構成

## 📅 最終整理日: 2025年8月22日

## 🗂️ **ディレクトリ構成**

```
miraikakaku/
├── docs/                           # 📚 すべてのドキュメント
│   ├── migration-reports/          # 🔄 Cloud SQL統合関連レポート
│   ├── sql-scripts/               # 🗃️ データベーススクリプト
│   ├── tools/                     # 🔧 テスト・診断ツール
│   └── PROJECT_ORGANIZATION.md    # 📋 このファイル
├── scripts/                       # 🛠️ 運用スクリプト
│   └── cloud-sql-integration/     # ☁️ Cloud SQL統合ツール
├── shared/                        # 🤝 共通ライブラリ
│   └── config/                    # ⚙️ 共通設定
├── miraikakakuapi/               # 🚀 APIサービス
├── miraikakakubatch/             # ⚡ バッチサービス
├── miraikakakudatafeed/          # 📊 データフィードサービス
├── miraikakakufront/             # 🌐 フロントエンド
└── README.md                      # 📖 プロジェクト概要
```

## 📋 **ファイル分類**

### 🔄 **Migration Reports** (`docs/migration-reports/`)
- `CLOUD_SQL_INTEGRATION_REPORT.md` - Cloud SQL統合調査レポート
- `COMPREHENSIVE_COVERAGE_REPORT.md` - 銘柄カバレッジレポート
- `FINAL_DATABASE_COMPARISON.md` - データベース比較最終レポート
- `FINAL_INTEGRATION_SUCCESS_REPORT.md` - **統合完了成功レポート**
- `PENDING_TASKS_REPORT.md` - 残件管理レポート

### 🗃️ **SQL Scripts** (`docs/sql-scripts/`)
- `cloud_sql_init.sql` - Cloud SQL初期化
- `comprehensive_financial_data.sql` - 包括的データ投入
- `create_schema.sql` - スキーマ作成
- `simple_price_data.sql` - サンプル価格データ
- `verify_*.sql` - データ検証用

### 🔧 **Tools** (`docs/tools/`)
- `test_cloud_sql_connection.py` - **統合接続テストツール**
- `quick_connection_test.py` - 簡易接続診断

### 🛠️ **Integration Scripts** (`scripts/cloud-sql-integration/`)
- `comprehensive_data_loader.py` - 包括的データローダー
- `cloud_sql_data_loader.py` - Cloud SQLデータローダー
- `fix_*.py` - データ修復ツール
- `*_loader.py` - 各種ローダー

## 🎯 **主要サービス**

### 1. **Data Feed Service** (`miraikakakudatafeed/`)
```
ポート: 8000
機能: 統一API Gateway
データソース: Cloud SQL + Yahoo Finance
ファイル: universal_stock_api_v2.py (最新版)
```

### 2. **Frontend** (`miraikakakufront/`)
```
ポート: 3000
接続先: localhost:8000 (統一)
フレームワーク: Next.js
```

### 3. **API Service** (`miraikakakuapi/`)
```
用途: 本番用APIサービス
データベース: Cloud SQL専用
認証: JWT対応
```

### 4. **Batch Service** (`miraikakakubatch/`)
```
用途: データ処理・予測生成
スケジュール: 定期実行
機械学習: LSTM予測モデル
```

## ⚙️ **設定ファイル**

### **共通設定** (`shared/config/`)
- `.env.cloud_sql` - Cloud SQL接続設定
- `database.py` - 共通データベース設定

### **個別サービス設定**
- `miraikakakuapi/functions/database/cloud_sql_only.py` - API用接続
- `miraikakakubatch/functions/database/cloud_sql_only.py` - Batch用接続
- `miraikakakufront/.env.local` - フロントエンド環境変数

## 🗄️ **データベース情報**

### **Cloud SQL** (本番用)
```
ホスト: 34.58.103.36
データベース: miraikakaku_prod
ユーザー: root
銘柄数: 12,107
- 日本株: 4,168社
- 米国株: 7,939銘柄  
- ETF: 2,322ファンド
```

### **テーブル構成**
- `stock_master` - 銘柄マスターデータ
- `stock_prices` - 価格履歴
- `stock_predictions` - AI予測結果
- `batch_logs` - バッチ実行ログ

## 🚀 **起動方法**

### **開発環境**
```bash
# Data Feed Service
cd miraikakakudatafeed
python3 universal_stock_api_v2.py

# Frontend
cd miraikakakufront  
npm run dev
```

### **接続テスト**
```bash
cd docs/tools
python3 test_cloud_sql_connection.py
```

## 📊 **システム状態**

### **✅ 統合完了項目**
- SQLite完全廃止
- Cloud SQL統合完了
- 12,107銘柄データ統合
- Yahoo Finance API統合
- フロントエンド接続統一

### **🎯 アクセスポイント**
- フロントエンド: http://localhost:3000
- API: http://localhost:8000
- ドキュメント: http://localhost:8000/docs

## 📞 **サポート情報**

### **主要コンポーネント**
1. **Data Feed Service v3.0** - 統一APIゲートウェイ
2. **Cloud SQL Database** - 包括的銘柄データ
3. **Yahoo Finance Integration** - リアルタイム価格
4. **Next.js Frontend** - レスポンシブUI

### **トラブルシューティング**
- 接続問題: `docs/tools/test_cloud_sql_connection.py` 実行
- データ確認: `docs/sql-scripts/verify_data.sql` 実行  
- ログ確認: 各サービスのコンソール出力

---

## 📈 **プロジェクト成果**

**✅ 完了済み**: Cloud SQL統合、SQLite廃止、データ統一、API統合  
**🎯 現在状況**: 本格運用可能、12,107銘柄対応  
**🚀 次のステップ**: 機能拡張、パフォーマンス最適化

---

*Project Organization completed on 2025-08-22*  
*Miraikakaku - Comprehensive Financial Platform*