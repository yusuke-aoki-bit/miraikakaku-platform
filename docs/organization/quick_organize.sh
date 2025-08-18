#!/bin/bash
# Miraikakaku プロジェクト クイック整理スクリプト
# 安全な整理（実行中システムには影響なし）

echo "🗂️ Miraikakaku プロジェクト クイック整理開始"
echo "================================================"

# バックアップ確認
if [ -d "project_backup_*" ]; then
    echo "✅ バックアップ確認済み"
else
    echo "⚠️ まずバックアップを作成することを推奨します"
    echo "python3 ORGANIZE_FILES.py を実行してください"
    exit 1
fi

echo ""
echo "📁 ディレクトリ構造作成中..."

# ディレクトリ作成
mkdir -p archives/legacy_databases
mkdir -p archives/old_versions
mkdir -p tools/builders
mkdir -p docs/reports
mkdir -p docker
mkdir -p data

echo "✅ ディレクトリ構造作成完了"

echo ""
echo "📦 ファイル整理実行 (安全モード)..."

# レガシーデータベース移動
echo "  🗃️ レガシーデータベース整理..."
if [ -f "comprehensive_stocks.py" ]; then
    mv comprehensive_stocks*.py archives/legacy_databases/ 2>/dev/null
    echo "    • comprehensive_stocks_*.py → archives/legacy_databases/"
fi

if [ -f "comprehensive_japanese_stocks_complete.py" ]; then
    mv comprehensive_japanese_stocks_complete.py archives/legacy_databases/
    echo "    • comprehensive_japanese_stocks_complete.py → archives/legacy_databases/"
fi

# 開発ツール移動
echo "  🔨 開発ツール整理..."
mv build_comprehensive_database.py tools/builders/ 2>/dev/null
mv create_*_japanese_stocks.py tools/builders/ 2>/dev/null
mv fetch_comprehensive_stocks.py tools/builders/ 2>/dev/null
mv massive_stock_expansion.py tools/builders/ 2>/dev/null
echo "    • DB構築ツール → tools/builders/"

# レポート移動
echo "  📋 レポート整理..."
mv *_REPORT.md docs/reports/ 2>/dev/null
mv japanese_stock_coverage_report.md docs/reports/ 2>/dev/null
echo "    • レポートファイル → docs/reports/"

# Docker関連移動
echo "  🐳 Docker設定整理..."
mv docker-compose*.yml docker/ 2>/dev/null
mv Dockerfile.* docker/ 2>/dev/null
echo "    • Docker設定 → docker/"

# データファイル移動
echo "  📊 データファイル整理..."
mv tse_official_listing.xls data/ 2>/dev/null
mv requirements.txt data/ 2>/dev/null
echo "    • データファイル → data/"

# 旧バージョンAPI（注意深く処理）
echo "  🔄 旧APIファイル確認..."
if [ -f "real_api.py" ] && [ -f "universal_stock_api.py" ]; then
    echo "    ⚠️ real_api.py が存在します"
    echo "    universal_stock_api.py が実行中のため、real_api.py は手動確認してください"
    echo "    不要であれば: mv real_api*.py archives/old_versions/"
fi

if [ -f "production_api.py" ]; then
    echo "    ⚠️ production_api.py が存在します - 手動確認してください"
fi

if [ -f "simple_api.py" ]; then
    mv simple_api.py archives/old_versions/ 2>/dev/null
    echo "    • simple_api.py → archives/old_versions/"
fi

echo ""
echo "📊 整理結果確認..."

# 結果確認
echo "  🚀 CORE_RUNTIME (実行中・保持):"
ls -la universal_stock_api.py comprehensive_japanese_stocks_enhanced.py optimized_etfs_3000.json 2>/dev/null | grep -v "total"

echo ""
echo "  🤖 BATCH_SYSTEM (重要・保持):"
ls -la miraikakakubatch.py ml_prediction_system.py japanese_stock_updater.py simple_monitor.py test_ml_integration.py 2>/dev/null | grep -v "total"

echo ""
echo "  📊 整理されたディレクトリ:"
echo "    archives/legacy_databases: $(ls archives/legacy_databases 2>/dev/null | wc -l) ファイル"
echo "    tools/builders: $(ls tools/builders 2>/dev/null | wc -l) ファイル"
echo "    docs/reports: $(ls docs/reports 2>/dev/null | wc -l) ファイル"
echo "    docker: $(ls docker 2>/dev/null | wc -l) ファイル"
echo "    data: $(ls data 2>/dev/null | wc -l) ファイル"

echo ""
echo "⚠️ 手動確認が必要なファイル:"
remaining_files=$(ls -la *.py *.md 2>/dev/null | grep -v "universal_stock_api.py\|miraikakakubatch.py\|ml_prediction_system.py\|japanese_stock_updater.py\|simple_monitor.py\|test_ml_integration.py\|README.md\|README_BATCH_SYSTEM.md\|README_ML_BATCH_SYSTEM.md\|install_batch_system.py\|ORGANIZE_FILES.py\|FILE_ORGANIZATION_SUMMARY.md" | grep -v "total" || echo "なし")

if [ -n "$remaining_files" ] && [ "$remaining_files" != "なし" ]; then
    echo "$remaining_files"
else
    echo "  🎉 手動確認が必要なファイルはありません"
fi

echo ""
echo "✅ クイック整理完了!"
echo "================================================"
echo ""
echo "🎯 現在のシステム状態:"
echo "  • universal_stock_api.py: 実行中 (port 8000)"
echo "  • miraikakakubatch.py: ML統合バッチシステム"
echo "  • simple_monitor.py: 軽量監視システム"
echo ""
echo "📋 次のステップ:"
echo "  1. 実行中システムの動作確認: curl http://localhost:8000/health"
echo "  2. 整理結果確認: ls -la archives/ tools/ docs/"
echo "  3. 不要ファイルの最終確認・削除"
echo ""
echo "🔒 安全性: 実行中システムファイルは移動していません"