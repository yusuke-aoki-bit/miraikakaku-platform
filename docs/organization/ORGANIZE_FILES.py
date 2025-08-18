#!/usr/bin/env python3
"""
Miraikakaku プロジェクトファイル整理スクリプト
重要度に基づいてファイルを分類・整理
"""

import os
import shutil
from datetime import datetime

def organize_files():
    """ファイル整理メイン処理"""
    print("🗂️ Miraikakaku プロジェクトファイル整理開始")
    
    # 現在のファイル一覧取得
    files = []
    for item in os.listdir('.'):
        if os.path.isfile(item) and not item.startswith('.'):
            files.append(item)
    
    # ファイル分類
    file_categories = {
        '🚀 CORE_SYSTEM': [
            'universal_stock_api.py',           # メインAPI
            'comprehensive_japanese_stocks_enhanced.py',  # 日本株DB
            'optimized_etfs_3000.json'          # ETF DB (if exists)
        ],
        
        '🤖 ML_BATCH_SYSTEM': [
            'miraikakakubatch.py',              # メインバッチシステム
            'ml_prediction_system.py',          # ML予測エンジン
            'japanese_stock_updater.py',        # 日本株更新
            'simple_monitor.py',                # 軽量監視
            'test_ml_integration.py'            # MLテスト
        ],
        
        '📊 DOCUMENTATION': [
            'README.md',                        # プロジェクト概要
            'README_BATCH_SYSTEM.md',           # バッチシステム文書
            'README_ML_BATCH_SYSTEM.md'         # ML文書
        ],
        
        '🔧 SETUP_TOOLS': [
            'install_batch_system.py',          # インストーラー
            'setup_monitoring.sh',              # 監視セットアップ
            'miraikakaku-batch.service'         # systemdサービス
        ],
        
        '📈 DATA_BUILDERS': [
            'etf_optimizer.py',                 # ETF最適化
            'global_stock_database.py'          # グローバルDB
        ],
        
        '🗃️ LEGACY_DATA_FILES': [
            'comprehensive_stocks.py',          # 旧556社DB
            'comprehensive_stocks_backup.py',   # バックアップ
            'comprehensive_stocks_expanded.py', # 拡張版
            'comprehensive_stocks_massive.py',  # 大規模版
            'comprehensive_japanese_stocks_complete.py'  # 完全版
        ],
        
        '🔨 DEVELOPMENT_TOOLS': [
            'build_comprehensive_database.py',  # DB構築
            'create_enhanced_japanese_stocks.py', # 強化DB作成
            'create_complete_japanese_stocks.py', # 完全DB作成
            'fetch_comprehensive_stocks.py',    # 包括取得
            'massive_stock_expansion.py'        # 大規模拡張
        ],
        
        '📋 REPORTS': [
            'DATABASE_EXPANSION_REPORT.md',     # DB拡張レポート
            'US_STOCK_DATABASE_ENHANCEMENT_REPORT.md', # 米国株レポート
            'japanese_stock_coverage_report.md' # 日本株レポート
        ],
        
        '🧪 EXPERIMENTAL': [
            'batch_data_populate.py',           # バッチデータ投入
            'ORGANIZE_FILES.py'                 # このファイル
        ]
    }
    
    # ファイル分類結果表示
    print("\n📂 ファイル分類結果:")
    print("=" * 60)
    
    found_files = set()
    
    for category, file_list in file_categories.items():
        print(f"\n{category}:")
        category_files = []
        for file_name in file_list:
            if file_name in files:
                status = "✅ 存在"
                found_files.add(file_name)
                category_files.append(file_name)
            else:
                status = "❌ なし"
            print(f"  {file_name:<40} {status}")
        
        # カテゴリごとの統計
        if category_files:
            total_size = sum(os.path.getsize(f) for f in category_files)
            print(f"    📊 このカテゴリ: {len(category_files)}ファイル ({total_size/1024:.1f}KB)")
    
    # 未分類ファイル
    unclassified = [f for f in files if f not in found_files]
    if unclassified:
        print(f"\n❓ 未分類ファイル:")
        for file_name in unclassified:
            size = os.path.getsize(file_name) / 1024
            print(f"  {file_name:<40} ({size:.1f}KB)")
    
    print("\n" + "=" * 60)
    
    # 整理推奨事項
    print("\n💡 整理推奨事項:")
    
    recommendations = []
    
    # 重要度分析
    core_files = len(file_categories['🚀 CORE_SYSTEM'])
    legacy_files = len([f for f in file_categories['🗃️ LEGACY_DATA_FILES'] if f in files])
    dev_files = len([f for f in file_categories['🔨 DEVELOPMENT_TOOLS'] if f in files])
    
    if legacy_files > 0:
        recommendations.append(f"📦 LEGACY_DATA_FILES ({legacy_files}ファイル) を archives/ に移動")
    
    if dev_files > 3:
        recommendations.append(f"🔨 DEVELOPMENT_TOOLS を tools/ サブディレクトリに整理")
    
    if len(unclassified) > 0:
        recommendations.append(f"❓ 未分類ファイル ({len(unclassified)}ファイル) の用途確認")
    
    # ディレクトリ構造提案
    recommendations.append("📁 推奨ディレクトリ構造:")
    
    directory_structure = """
miraikakaku/
├── 🚀 CORE (実行システム)
│   ├── universal_stock_api.py
│   ├── comprehensive_japanese_stocks_enhanced.py
│   └── optimized_etfs_3000.json
│
├── 🤖 BATCH (自動処理)
│   ├── miraikakakubatch.py
│   ├── ml_prediction_system.py
│   ├── japanese_stock_updater.py
│   └── simple_monitor.py
│
├── 📊 DOCS (文書)
│   ├── README*.md
│   └── reports/
│
├── 🔧 SETUP (セットアップ)
│   ├── install_batch_system.py
│   ├── setup_monitoring.sh
│   └── config/
│
├── 📦 ARCHIVES (アーカイブ)
│   ├── legacy_databases/
│   └── old_versions/
│
└── 🔨 TOOLS (開発ツール)
    ├── builders/
    └── utilities/
"""
    
    for rec in recommendations:
        print(f"  • {rec}")
    
    print(directory_structure)
    
    # 自動整理オプション
    print("\n🤖 自動整理実行しますか？")
    print("1. はい - 推奨構造で整理")
    print("2. いいえ - 現状維持")
    print("3. バックアップ作成のみ")
    
    # choice = input("選択 (1-3): ")
    choice = "3"  # デフォルトで安全な選択
    
    if choice == "1":
        auto_organize_files(file_categories, files)
    elif choice == "3":
        create_backup()
    
    # 統計情報
    print("\n📊 プロジェクト統計:")
    total_files = len(files)
    total_size = sum(os.path.getsize(f) for f in files) / 1024 / 1024
    print(f"  総ファイル数: {total_files}")
    print(f"  総サイズ: {total_size:.2f}MB")
    print(f"  コアシステム: {len([f for f in file_categories['🚀 CORE_SYSTEM'] if f in files])}ファイル")
    print(f"  実行中システム: universal_stock_api.py, miraikakakubatch.py")
    
    print("\n✅ ファイル整理分析完了")

def auto_organize_files(file_categories, files):
    """自動ファイル整理"""
    print("\n🤖 自動整理実行中...")
    
    # バックアップ作成
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # ディレクトリ作成
    directories = {
        'core': '🚀_CORE_SYSTEM',
        'batch': '🤖_BATCH_SYSTEM', 
        'docs': '📊_DOCUMENTATION',
        'setup': '🔧_SETUP_TOOLS',
        'archives': '📦_ARCHIVES',
        'tools': '🔨_TOOLS'
    }
    
    for dir_name in directories.values():
        os.makedirs(dir_name, exist_ok=True)
    
    # ファイル移動 (実際の移動は危険なのでシミュレーション)
    print("  (シミュレーションモード - 実際の移動は行いません)")
    
    move_plan = {
        '🚀 CORE_SYSTEM': '🚀_CORE_SYSTEM/',
        '🤖 ML_BATCH_SYSTEM': '🤖_BATCH_SYSTEM/',
        '📊 DOCUMENTATION': '📊_DOCUMENTATION/',
        '🔧 SETUP_TOOLS': '🔧_SETUP_TOOLS/',
        '🗃️ LEGACY_DATA_FILES': '📦_ARCHIVES/',
        '🔨 DEVELOPMENT_TOOLS': '🔨_TOOLS/'
    }
    
    for category, target_dir in move_plan.items():
        if category in file_categories:
            for file_name in file_categories[category]:
                if file_name in files:
                    print(f"    {file_name} → {target_dir}")

def create_backup():
    """バックアップ作成"""
    print("\n💾 バックアップ作成中...")
    
    backup_dir = f"project_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # 重要ファイルのみバックアップ
    important_files = [
        'universal_stock_api.py',
        'miraikakakubatch.py',
        'ml_prediction_system.py',
        'comprehensive_japanese_stocks_enhanced.py',
        'README*.md'
    ]
    
    backup_count = 0
    for pattern in important_files:
        if '*' in pattern:
            # ワイルドカード対応
            import glob
            for file_path in glob.glob(pattern):
                if os.path.exists(file_path):
                    shutil.copy2(file_path, backup_dir)
                    backup_count += 1
        else:
            if os.path.exists(pattern):
                shutil.copy2(pattern, backup_dir)
                backup_count += 1
    
    print(f"✅ バックアップ完了: {backup_dir} ({backup_count}ファイル)")

if __name__ == "__main__":
    organize_files()