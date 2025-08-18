# Miraikakaku プロジェクト ファイル整理サマリー

## 📊 ファイル分析結果

**総ファイル数**: 41ファイル  
**総サイズ**: 2.90MB  
**バックアップ作成済み**: `project_backup_20250818_203459`

## 🚀 重要度別分類

### **TIER 1: 🚀 CORE_SYSTEM (必須・実行中)**
```
✅ universal_stock_api.py                 (68.8KB) - メインAPI (実行中)
✅ comprehensive_japanese_stocks_enhanced.py (1002.4KB) - 日本株4,168社DB
✅ optimized_etfs_3000.json              (2.2KB) - ETF最適化DB
```
**状態**: 🟢 **稼働中・絶対保持**

### **TIER 1: 🤖 ML_BATCH_SYSTEM (重要・自動化)**
```
✅ miraikakakubatch.py                   (25.4KB) - ML統合バッチシステム
✅ ml_prediction_system.py               (23.8KB) - ML予測エンジン
✅ japanese_stock_updater.py             (20.0KB) - 日本株更新システム
✅ simple_monitor.py                     (7.2KB) - 軽量監視スクリプト
✅ test_ml_integration.py                (5.6KB) - MLテスト
```
**状態**: 🟢 **重要システム・保持**

### **TIER 2: 📊 DOCUMENTATION (重要・参照)**
```
✅ README.md                             (4.5KB) - プロジェクト概要
✅ README_BATCH_SYSTEM.md                (6.1KB) - バッチシステム仕様
✅ README_ML_BATCH_SYSTEM.md             (7.6KB) - ML統合システム仕様
```
**状態**: 🟢 **重要ドキュメント・保持**

### **TIER 2: 🔧 SETUP_TOOLS (重要・運用)**
```
✅ install_batch_system.py               (15.9KB) - システムインストーラー
✅ setup_monitoring.sh                   (2.5KB) - 監視自動設定
✅ miraikakaku-batch.service             (0.3KB) - systemdサービス
```
**状態**: 🟢 **運用ツール・保持**

### **TIER 3: 📈 DATA_BUILDERS (有用・保持)**
```
✅ etf_optimizer.py                      (23.0KB) - ETF最適化処理
✅ global_stock_database.py              (5.2KB) - グローバルDB管理
```
**状態**: 🟡 **有用ツール・保持**

### **TIER 4: 🗃️ LEGACY_DATA_FILES (アーカイブ対象)**
```
⚠️ comprehensive_stocks.py               (12.7KB) - 旧556社DB
⚠️ comprehensive_stocks_backup.py        (12.7KB) - 556社バックアップ
⚠️ comprehensive_stocks_expanded.py      (189.8KB) - 拡張版DB
⚠️ comprehensive_stocks_massive.py       (372.1KB) - 大規模版DB
⚠️ comprehensive_japanese_stocks_complete.py (0.5KB) - 完全版(空)
```
**状態**: 🟡 **archives/legacy_databases/ への移動推奨**

### **TIER 4: 🔨 DEVELOPMENT_TOOLS (開発用・整理対象)**
```
⚠️ build_comprehensive_database.py       (4.0KB) - DB構築ツール
⚠️ create_enhanced_japanese_stocks.py    (18.2KB) - 強化DB作成
⚠️ create_complete_japanese_stocks.py    (119.6KB) - 完全DB作成
⚠️ fetch_comprehensive_stocks.py         (3.7KB) - 包括データ取得
⚠️ massive_stock_expansion.py            (6.0KB) - 大規模拡張ツール
```
**状態**: 🟡 **tools/builders/ への移動推奨**

### **TIER 3: 📋 REPORTS (参考資料・保持)**
```
✅ DATABASE_EXPANSION_REPORT.md          (7.1KB) - DB拡張レポート
✅ US_STOCK_DATABASE_ENHANCEMENT_REPORT.md (10.7KB) - 米国株強化レポート
✅ japanese_stock_coverage_report.md     (3.2KB) - 日本株カバレッジレポート
```
**状態**: 🟢 **docs/reports/ への移動推奨**

### **TIER 5: ❓ 未分類ファイル (確認・整理必要)**
```
❓ real_api.py                           (68.8KB) - 旧メインAPI
❓ real_api_backup.py                    (45.6KB) - 旧APIバックアップ
❓ production_api.py                     (20.2KB) - 本番API候補
❓ simple_api.py                         (9.5KB) - シンプルAPI
❓ tse_official_listing.xls              (822.5KB) - TSE公式データ
❓ docker-compose.yml                    (4.6KB) - Docker構成
❓ docker-compose.prod.yml               (1.0KB) - 本番Docker構成
❓ Dockerfile.api                        (0.8KB) - APIコンテナ
❓ requirements.txt                      (0.2KB) - Python依存関係
❓ validate_japanese_stocks.py           (2.8KB) - データ検証ツール
```
**状態**: 🟡 **用途確認・適切なディレクトリへ移動**

## 🎯 整理アクションプラン

### **即座に実行推奨**

1. **🗂️ ディレクトリ構造作成**
```bash
mkdir -p archives/legacy_databases
mkdir -p archives/old_versions  
mkdir -p tools/builders
mkdir -p docs/reports
mkdir -p docker
```

2. **📦 レガシーファイル移動**
```bash
mv comprehensive_stocks*.py archives/legacy_databases/
mv comprehensive_japanese_stocks_complete.py archives/legacy_databases/
```

3. **🔨 開発ツール整理**
```bash
mv build_comprehensive_database.py tools/builders/
mv create_*_japanese_stocks.py tools/builders/
mv fetch_comprehensive_stocks.py tools/builders/
mv massive_stock_expansion.py tools/builders/
```

4. **📋 レポート整理**
```bash
mv *_REPORT.md docs/reports/
mv japanese_stock_coverage_report.md docs/reports/
```

5. **🐳 Docker関連整理**
```bash
mv docker-compose*.yml docker/
mv Dockerfile.* docker/
```

### **要検討事項**

1. **旧APIファイルの扱い**
   - `real_api.py` vs `universal_stock_api.py` の関係確認
   - `production_api.py` の本番環境での使用有無
   - 不要であれば archives/old_versions/ へ

2. **TSE公式データファイル**
   - `tse_official_listing.xls` (822.5KB) の継続使用有無
   - 使用中なら data/ ディレクトリへ移動

3. **requirements.txt の更新**
   - 現在のシステム依存関係に合わせて更新

## 🎯 最終推奨ディレクトリ構造

```
miraikakaku/
├── 🚀 CORE_RUNTIME/
│   ├── universal_stock_api.py           # メインAPI (実行中)
│   ├── comprehensive_japanese_stocks_enhanced.py # 日本株DB
│   └── optimized_etfs_3000.json        # ETF DB
│
├── 🤖 BATCH_SYSTEM/
│   ├── miraikakakubatch.py             # ML統合バッチ
│   ├── ml_prediction_system.py         # ML予測エンジン
│   ├── japanese_stock_updater.py       # 株式更新
│   ├── simple_monitor.py               # 監視スクリプト
│   └── test_ml_integration.py          # MLテスト
│
├── 🔧 SETUP/
│   ├── install_batch_system.py         # インストーラー
│   ├── setup_monitoring.sh             # 監視設定
│   ├── miraikakaku-batch.service       # systemd
│   └── config/                         # 設定ファイル群
│
├── 📊 DOCS/
│   ├── README.md                       # メイン説明
│   ├── README_BATCH_SYSTEM.md          # バッチ仕様
│   ├── README_ML_BATCH_SYSTEM.md       # ML仕様
│   └── reports/                        # レポート群
│
├── 📈 UTILITIES/
│   ├── etf_optimizer.py                # ETF最適化
│   ├── global_stock_database.py        # グローバルDB
│   └── validate_japanese_stocks.py     # 検証ツール
│
├── 🔨 TOOLS/
│   └── builders/                       # DB構築ツール群
│
├── 📦 ARCHIVES/
│   ├── legacy_databases/               # 旧DBファイル群
│   └── old_versions/                   # 旧バージョン群
│
├── 🐳 DOCKER/
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── Dockerfile.api
│
└── 📋 DATA/
    ├── tse_official_listing.xls        # TSE公式データ
    └── requirements.txt                # Python依存関係
```

## ✅ 現在の推奨アクション

1. **🟢 即座継続**: CORE_RUNTIME, BATCH_SYSTEM, DOCS - そのまま使用
2. **🟡 整理推奨**: LEGACY_FILES, DEVELOPMENT_TOOLS - 移動・整理
3. **🟠 要確認**: 未分類ファイル - 用途確認後に適切な場所へ
4. **🔒 バックアップ済み**: 重要ファイルは安全にバックアップ完了

**整理実行時の注意**: 実行中のシステム (`universal_stock_api.py`, `miraikakakubatch.py`) は移動しないこと！