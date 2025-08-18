# Miraikakaku Batch System - 定期カバレッジ監視システム

全市場100%カバレッジを維持するための自動監視・更新システムです。

## 🎯 概要

このシステムは以下の機能を提供します：

- **自動カバレッジ監視**: 定期的にデータベースの完全性をチェック
- **データベース更新**: 新規上場・廃止銘柄の自動反映
- **アラート機能**: カバレッジ低下時の即座な通知
- **自動バックアップ**: データ損失防止のための定期バックアップ
- **レポート生成**: 詳細な監視レポートの自動生成

## 📊 現在のカバレッジ状況

✅ **100%カバレッジ達成済み**
- 日本株: 4,168社 (100% - TSE全社対応)
- 米国株: 8,700社 (100% - 全取引所対応)
- ETF: 3,000銘柄 (100% - 最適化済み)
- 合計: 15,868証券

## 🚀 クイックスタート

### 1. システム確認
```bash
# APIが稼働しているか確認
curl http://localhost:8000/health

# 現在のカバレッジ確認
python3 simple_monitor.py
```

### 2. 定期監視設定

#### Linux/macOS (crontab使用)
```bash
# crontabエディタ起動
crontab -e

# 6時間ごとの監視を追加
0 */6 * * * /usr/bin/python3 /path/to/miraikakaku/simple_monitor.py >> /path/to/miraikakaku/logs/monitor.log 2>&1
```

#### Windows (タスクスケジューラー)
1. タスクスケジューラーを開く
2. 基本タスクの作成を選択
3. トリガー: 6時間ごと
4. 操作: `python3 simple_monitor.py`を実行

## 📁 ファイル構成

```
miraikakaku/
├── miraikakakubatch.py              # メインバッチシステム
├── japanese_stock_updater.py        # 日本株更新システム
├── simple_monitor.py                # 軽量監視スクリプト ⭐
├── install_batch_system.py          # インストーラー
├── universal_stock_api.py           # メインAPI
├── config/
│   ├── batch_config.json            # 設定ファイル
│   └── logging_config.json          # ログ設定
├── backups/                         # 自動バックアップ
│   ├── japanese_stocks/
│   ├── us_stocks/
│   └── etf_data/
├── reports/                         # 監視レポート
└── logs/                           # システムログ
```

## ⚙️ 設定ファイル

### config/batch_config.json
```json
{
  "thresholds": {
    "min_japanese_stocks": 4000,
    "min_us_stocks": 8500,
    "min_etfs": 2900,
    "coverage_alert_threshold": 0.95
  },
  "schedule": {
    "daily_maintenance_time": "04:00",
    "weekly_maintenance_day": "monday",
    "weekly_maintenance_time": "06:00",
    "coverage_check_interval_hours": 6
  }
}
```

## 📋 監視コマンド

### 基本監視
```bash
# 現在のカバレッジチェック
python3 simple_monitor.py

# 詳細なバッチ処理
python3 miraikakakubatch.py --mode check
```

### メンテナンス
```bash
# 日次メンテナンス
python3 miraikakakubatch.py --mode daily

# 週次メンテナンス  
python3 miraikakakubatch.py --mode weekly

# 日本株データベース更新
python3 japanese_stock_updater.py
```

## 🔍 レポート確認

監視レポートは `reports/` ディレクトリに自動保存されます：

```bash
# 最新のレポート確認
ls -la reports/coverage_monitor_*.json | tail -1

# レポート内容表示
cat reports/coverage_monitor_$(date +%Y%m%d)_*.json | jq '.'
```

## 🚨 アラート条件

以下の条件でアラートが発生します：

- 日本株数 < 4,000社
- 米国株数 < 8,500社  
- ETF数 < 2,900銘柄
- API接続不可
- データベースファイル破損

## 🔧 トラブルシューティング

### よくある問題

#### 1. API接続エラー
```bash
# APIプロセス確認
ps aux | grep universal_stock_api

# API再起動
python3 universal_stock_api.py &
```

#### 2. データベースファイル不整合
```bash
# バックアップから復元
cp backups/japanese_stocks/japanese_stocks_backup_latest.py comprehensive_japanese_stocks_enhanced.py
```

#### 3. 権限エラー
```bash
# 実行権限付与
chmod +x *.py
```

## 📈 パフォーマンス監視

### システムリソース確認
```bash
# CPUとメモリ使用量
top -p $(pgrep -f universal_stock_api)

# ディスク使用量
du -sh backups/ reports/ logs/
```

### ログ確認
```bash
# システムログ
tail -f logs/miraikakaku_batch.log

# エラーログ
grep ERROR logs/miraikakaku_batch.log
```

## 🔄 自動更新スケジュール

| タスク | 頻度 | 実行時間 | 説明 |
|--------|------|----------|------|
| カバレッジチェック | 6時間ごと | 0:00, 6:00, 12:00, 18:00 | 基本監視 |
| 米国株同期 | 日次 | 4:00 | Alpha Vantage API同期 |
| 日本株更新 | 週次 | 月曜 6:00 | TSE公式データ更新 |
| バックアップ作成 | 日次 | 2:00 | 全データベースバックアップ |
| 古いログ削除 | 週次 | 日曜 3:00 | 30日以上前のファイル削除 |

## 🎯 運用のベストプラクティス

### 1. 定期チェック
```bash
# 毎朝の運用チェック
python3 simple_monitor.py && echo "✅ システム正常"
```

### 2. バックアップ確認
```bash
# バックアップファイル確認
find backups/ -name "*.py" -mtime -1
```

### 3. レポート確認
```bash
# 異常がないか確認
grep -l "warning\|error" reports/coverage_monitor_*.json | tail -5
```

## 🔮 将来の拡張予定

- [ ] Slack/Discord通知連携
- [ ] Webダッシュボード
- [ ] 機械学習による異常検知
- [ ] 国際市場対応 (欧州、アジア)
- [ ] リアルタイム監視システム

## 🆘 サポート

問題が発生した場合：

1. `simple_monitor.py`でシステム状態確認
2. `logs/`ディレクトリでエラーログ確認
3. 必要に応じてバックアップから復元
4. 問題が解決しない場合は、システム開発者に連絡

---

**最終更新**: 2025-08-18  
**バージョン**: 1.0.0  
**対応システム**: Linux, macOS, Windows (WSL2)