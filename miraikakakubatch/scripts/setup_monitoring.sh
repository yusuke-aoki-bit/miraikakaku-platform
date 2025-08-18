#!/bin/bash
# Miraikakaku 監視システム自動セットアップスクリプト
# Usage: bash setup_monitoring.sh

echo "🎯 Miraikakaku 監視システム自動セットアップ"
echo "=============================================="

# 現在のディレクトリ取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/simple_monitor.py"

echo "📍 作業ディレクトリ: $SCRIPT_DIR"

# Pythonとファイル存在チェック
if ! command -v python3 &> /dev/null; then
    echo "❌ python3が見つかりません"
    exit 1
fi

if [ ! -f "$MONITOR_SCRIPT" ]; then
    echo "❌ $MONITOR_SCRIPT が見つかりません"
    exit 1
fi

# 実行権限付与
chmod +x "$MONITOR_SCRIPT"
echo "✅ 実行権限設定完了"

# テスト実行
echo "🧪 監視システムテスト実行中..."
if python3 "$MONITOR_SCRIPT"; then
    echo "✅ テスト実行成功"
else
    echo "❌ テスト実行失敗"
    exit 1
fi

# crontab設定
echo ""
echo "⏰ crontab定期実行設定"
echo "現在のcrontab設定:"
crontab -l 2>/dev/null || echo "(crontabが設定されていません)"

echo ""
echo "以下の設定をcrontabに追加しますか? (y/N)"
echo "# Miraikakaku カバレッジ監視 (6時間ごと)"
echo "0 */6 * * * cd $SCRIPT_DIR && python3 simple_monitor.py >> logs/monitor.log 2>&1"

read -p "追加する場合は 'y' を入力: " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # ログディレクトリ作成
    mkdir -p "$SCRIPT_DIR/logs"
    
    # crontab設定追加
    (crontab -l 2>/dev/null; echo "# Miraikakaku カバレッジ監視 (6時間ごと)"; echo "0 */6 * * * cd $SCRIPT_DIR && python3 simple_monitor.py >> logs/monitor.log 2>&1") | crontab -
    
    echo "✅ crontab設定完了"
    echo ""
    echo "設定された監視スケジュール:"
    echo "  実行時間: 0:00, 6:00, 12:00, 18:00 (毎日)"
    echo "  ログファイル: $SCRIPT_DIR/logs/monitor.log"
else
    echo "crontab設定をスキップしました"
fi

echo ""
echo "🔍 手動でのcrontab確認・編集方法:"
echo "  crontab -l     # 現在の設定確認"
echo "  crontab -e     # 設定編集"

echo ""
echo "📋 システムコマンド:"
echo "  監視実行:       python3 $MONITOR_SCRIPT"
echo "  ログ確認:       tail -f $SCRIPT_DIR/logs/monitor.log"
echo "  レポート確認:   ls -la $SCRIPT_DIR/reports/"

echo ""
echo "✅ セットアップ完了!"
echo "監視システムが6時間ごとに自動実行されます。"