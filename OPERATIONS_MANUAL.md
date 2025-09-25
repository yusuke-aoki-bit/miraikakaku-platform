# 未来価格 運用マニュアル
# Miraikakaku Platform Operations Manual

## 🎯 概要

このマニュアルは、未来価格プラットフォームの日常運用、監視、トラブルシューティング、メンテナンスに関する包括的な手順書です。

---

## 📋 日常運用チェックリスト

### 毎日の運用タスク

#### 朝のシステムチェック (9:00 AM)
- [ ] システム全体のヘルスチェック実行
- [ ] 夜間バッチ処理の結果確認
- [ ] アラート・エラーログの確認
- [ ] データ整合性の確認
- [ ] バックアップ状況の確認

#### 日中の監視 (毎2時間)
- [ ] システムパフォーマンス確認
- [ ] ユーザー活動状況の監視
- [ ] API呼び出し状況の確認
- [ ] 予測精度の確認

#### 夕方の総合チェック (6:00 PM)
- [ ] 一日の統計レポート確認
- [ ] システムリソース使用状況
- [ ] 翌日のメンテナンス計画確認

### 週次運用タスク

#### 毎週月曜日
- [ ] 週次パフォーマンス レポート生成
- [ ] セキュリティ スキャン実行
- [ ] 依存関係の脆弱性チェック
- [ ] データベース最適化実行

#### 毎週金曜日
- [ ] 週次バックアップの検証
- [ ] ディスク容量の確認・クリーンアップ
- [ ] ログ ローテーション確認
- [ ] 翌週のデプロイ計画確認

### 月次運用タスク

#### 毎月1日
- [ ] 月次システム レポート作成
- [ ] SLA 達成状況の評価
- [ ] 容量計画の見直し
- [ ] 災害復旧計画の見直し

---

## 🔧 システム起動・停止手順

### 全システム起動手順

#### 1. インフラストラクチャ起動
```bash
# Docker Compose環境の場合
docker-compose up -d postgresql redis

# Kubernetes環境の場合
kubectl apply -f k8s/postgresql.yaml
kubectl apply -f k8s/redis.yaml

# 起動確認 (30秒待機)
sleep 30
```

#### 2. バックエンド サービス起動
```bash
# 統合システム オーケストレーター起動
python3 integrated_system_orchestrator.py &

# または個別起動
cd miraikakakuapi
python3 simple_api_server.py &

# MLシステム起動
python3 advanced_ml_engine.py &
python3 realtime_streaming_engine.py &
```

#### 3. フロントエンド起動
```bash
cd miraikakakufront
npm run build  # プロダクション用
npm start &     # サーバー起動
```

#### 4. 監視システム起動
```bash
python3 monitoring_alert_system.py &
```

#### 5. 起動確認
```bash
# ヘルスチェック実行
curl http://localhost:8080/health
curl http://localhost:3000/api/health

# システム状態確認
python3 -c "
from integrated_system_orchestrator import IntegratedSystemOrchestrator
orchestrator = IntegratedSystemOrchestrator()
status = orchestrator.get_system_dashboard()
print('System Health:', status['overview']['system_health'])
"
```

### 全システム停止手順

#### 1. トラフィック停止
```bash
# ロードバランサーからの除外
# nginx設定変更またはKubernetesサービス停止
kubectl scale deployment miraikakaku-api --replicas=0
kubectl scale deployment miraikakaku-frontend --replicas=0
```

#### 2. アプリケーション停止
```bash
# 統合オーケストレーター経由
python3 -c "
from integrated_system_orchestrator import IntegratedSystemOrchestrator
orchestrator = IntegratedSystemOrchestrator()
orchestrator.stop_system()
"

# または個別停止
pkill -f "simple_api_server.py"
pkill -f "advanced_ml_engine.py"
pkill -f "realtime_streaming_engine.py"
pkill -f "npm start"
```

#### 3. インフラストラクチャ停止
```bash
# Docker Compose
docker-compose down

# Kubernetes
kubectl delete -f k8s/
```

---

## 📊 監視・アラート対応

### アラート レベルと対応

#### 🟢 INFO レベル
**対応**: 情報として記録、即座の対応不要
- システム起動/停止
- 定期メンテナンス開始/完了
- バックアップ完了

#### 🟡 WARNING レベル
**対応**: 30分以内に確認・対応
- CPU使用率 > 80%
- メモリ使用率 > 85%
- レスポンス時間 > 500ms
- 予測精度低下

**対応手順**:
1. アラート詳細確認
2. システムリソース確認: `htop`, `free -h`
3. 負荷分散またはスケールアップ検討
4. 問題解決後、アラート解除

#### 🔴 ERROR レベル
**対応**: 15分以内に確認・対応開始
- サービス停止
- データベース接続エラー
- 高エラー率 (> 5%)
- セキュリティ異常検知

**対応手順**:
1. 即座にオンコール担当者に通知
2. 影響範囲の特定
3. 緊急対応実施
4. インシデント報告書作成

#### ⚫ CRITICAL レベル
**対応**: 即座に対応開始
- システム全体停止
- データ損失リスク
- セキュリティ侵害
- SLA大幅違反

**対応手順**:
1. 緊急対策本部設置
2. 全チームメンバーに緊急連絡
3. 災害復旧計画実行
4. 経営陣・顧客への報告

### 監視ダッシュボード

#### システム監視項目
```bash
# CPU使用率確認
top -bn1 | grep "Cpu(s)"

# メモリ使用率確認
free -h

# ディスク使用率確認
df -h

# ネットワーク確認
netstat -i
```

#### アプリケーション監視
```bash
# API応答時間確認
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8080/api/health

# データベース接続確認
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://user:pass@localhost/miraikakaku')
    print('Database connection: OK')
except Exception as e:
    print('Database connection: ERROR -', e)
"

# 予測精度確認
python3 -c "
from advanced_analytics_system import AdvancedAnalyticsSystem
analytics = AdvancedAnalyticsSystem()
report = analytics.get_system_dashboard()
print('Prediction Accuracy:', report.get('metrics', {}).get('accuracy', 'N/A'))
"
```

---

## 🔧 トラブルシューティング

### 一般的な問題と解決策

#### 問題: システムが応答しない
**症状**:
- Webサイトにアクセスできない
- APIが応答しない

**診断手順**:
```bash
# 1. プロセス確認
ps aux | grep -E "(simple_api_server|npm)"

# 2. ポート確認
netstat -tlnp | grep -E "(3000|8080)"

# 3. ログ確認
tail -f /var/log/miraikakaku/api.log
tail -f /var/log/miraikakaku/frontend.log

# 4. リソース確認
htop
df -h
```

**解決策**:
```bash
# サービス再起動
systemctl restart miraikakaku-api
systemctl restart miraikakaku-frontend

# Docker環境の場合
docker-compose restart api
docker-compose restart frontend
```

#### 問題: 予測精度が急激に低下
**症状**:
- 予測精度が通常の80%から60%に低下
- 予測結果が明らかに異常

**診断手順**:
```bash
# 1. 学習データ確認
python3 -c "
from advanced_ml_engine import AdvancedMLEngine
engine = AdvancedMLEngine()
health = engine.get_system_health()
print('ML System Status:', health)
"

# 2. データ品質確認
python3 -c "
import pandas as pd
# 最新のデータ品質をチェック
print('Data quality check completed')
"
```

**解決策**:
```bash
# 1. モデル再学習実行
python3 -c "
from advanced_ml_engine import AdvancedMLEngine
engine = AdvancedMLEngine()
engine.retrain_models()
"

# 2. データ品質フィルター強化
# 3. 異常値検出パラメータ調整
```

#### 問題: データベース接続エラー
**症状**:
- "connection refused" エラー
- 遅いクエリ実行

**診断手順**:
```bash
# 1. PostgreSQL状態確認
systemctl status postgresql
pg_isready -h localhost

# 2. 接続数確認
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# 3. スロークエリ確認
sudo -u postgres psql -d miraikakaku -c "
SELECT query, mean_time, calls FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 5;"
```

**解決策**:
```bash
# 1. PostgreSQL再起動
sudo systemctl restart postgresql

# 2. 接続プール設定調整
# config/database.yml でmax_connections調整

# 3. インデックス最適化
sudo -u postgres psql -d miraikakaku -c "REINDEX DATABASE miraikakaku;"
```

### 緊急時対応手順

#### システム全停止時の対応

**段階1: 即座の対応 (0-5分)**
```bash
# 1. 影響範囲確認
curl -I http://miraikakaku.com
curl -I http://api.miraikakaku.com

# 2. 緊急メンテナンスページ表示
# nginx設定でメンテナンスページにリダイレクト

# 3. チーム通知
# Slack緊急チャンネルで状況共有
```

**段階2: 原因調査 (5-15分)**
```bash
# 1. システムログ確認
journalctl -f -u miraikakaku-*

# 2. リソース状況確認
htop
df -h
iostat -x 1

# 3. ネットワーク確認
ping google.com
nslookup miraikakaku.com
```

**段階3: 復旧作業 (15-30分)**
```bash
# 1. バックアップからの復旧
./scripts/restore_from_backup.sh latest

# 2. システム再起動
./scripts/full_system_restart.sh

# 3. 動作確認
./scripts/health_check.sh
```

**段階4: 事後対応 (30分-24時間)**
- インシデント報告書作成
- 根本原因分析
- 再発防止策の策定
- ユーザー向け報告

---

## 🔄 メンテナンス手順

### 定期メンテナンス

#### 週次メンテナンス (毎週日曜 2:00 AM)

**事前準備**:
```bash
# 1. メンテナンス通知
echo "Maintenance scheduled for $(date)" | \
  curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Weekly maintenance starting"}' \
  $SLACK_WEBHOOK_URL

# 2. 現在の状態バックアップ
./scripts/create_maintenance_backup.sh
```

**メンテナンス実行**:
```bash
# 1. トラフィック停止
./scripts/stop_traffic.sh

# 2. データベース最適化
sudo -u postgres psql -d miraikakaku -c "
VACUUM ANALYZE;
REINDEX DATABASE miraikakaku;
"

# 3. ログローテーション
logrotate /etc/logrotate.d/miraikakaku

# 4. システム更新
./scripts/system_update.sh

# 5. サービス再起動
./scripts/full_system_restart.sh

# 6. 動作確認
./scripts/post_maintenance_check.sh
```

**事後確認**:
```bash
# 1. 全機能テスト実行
python3 load_testing_quality_assurance.py

# 2. パフォーマンス確認
./scripts/performance_check.sh

# 3. メンテナンス完了通知
echo "Maintenance completed successfully" | \
  curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Weekly maintenance completed"}' \
  $SLACK_WEBHOOK_URL
```

#### 月次メンテナンス (第1日曜 2:00 AM)

**追加作業**:
```bash
# 1. セキュリティ更新
./scripts/security_update.sh

# 2. 依存関係更新
pip-review --local --auto
npm audit fix

# 3. SSL証明書確認
certbot certificates

# 4. バックアップ検証
./scripts/verify_all_backups.sh

# 5. 災害復旧テスト
./scripts/dr_test.sh
```

### 緊急メンテナンス

#### セキュリティ緊急パッチ適用
```bash
# 1. 緊急メンテナンス宣言
./scripts/emergency_maintenance_start.sh

# 2. パッチ適用
./scripts/apply_security_patch.sh $PATCH_VERSION

# 3. セキュリティテスト
./scripts/security_test.sh

# 4. 段階的復旧
./scripts/gradual_restore.sh
```

---

## 📊 バックアップ・復旧

### バックアップ戦略

#### 自動バックアップ
```bash
# 毎時バックアップ (cron設定)
0 * * * * /opt/miraikakaku/scripts/hourly_backup.sh

# 日次バックアップ
0 3 * * * /opt/miraikakaku/scripts/daily_backup.sh

# 週次バックアップ
0 4 * * 0 /opt/miraikakaku/scripts/weekly_backup.sh
```

#### バックアップスクリプト例
```bash
#!/bin/bash
# daily_backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/miraikakaku/$DATE"

# データベースバックアップ
pg_dump -h localhost -U postgres miraikakaku > \
  $BACKUP_DIR/database_$DATE.sql

# アプリケーション設定バックアップ
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
  /opt/miraikakaku/config/

# ログバックアップ
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz \
  /var/log/miraikakaku/

# AWS S3にアップロード
aws s3 sync $BACKUP_DIR s3://miraikakaku-backup/$DATE/

echo "Backup completed: $BACKUP_DIR"
```

### 復旧手順

#### データベース復旧
```bash
# 1. 現在のデータベース停止
systemctl stop postgresql

# 2. データディレクトリ退避
mv /var/lib/postgresql/14/main /var/lib/postgresql/14/main.backup

# 3. バックアップから復旧
createdb miraikakaku
psql -d miraikakaku < /backup/database_latest.sql

# 4. PostgreSQL再起動
systemctl start postgresql

# 5. 整合性確認
psql -d miraikakaku -c "SELECT count(*) FROM stock_prices;"
```

#### システム全体復旧
```bash
#!/bin/bash
# full_system_restore.sh

BACKUP_DATE=$1  # 例: 20241201_030000

# 1. サービス停止
./scripts/stop_all_services.sh

# 2. データベース復旧
./scripts/restore_database.sh $BACKUP_DATE

# 3. 設定ファイル復旧
tar -xzf /backup/$BACKUP_DATE/config_$BACKUP_DATE.tar.gz -C /

# 4. アプリケーション復旧
./scripts/deploy_from_backup.sh $BACKUP_DATE

# 5. システム再起動
./scripts/start_all_services.sh

# 6. 動作確認
./scripts/verify_restore.sh
```

---

## 📈 パフォーマンス チューニング

### システム最適化

#### データベース最適化
```sql
-- インデックス作成
CREATE INDEX CONCURRENTLY idx_stock_prices_symbol_date
ON stock_prices (symbol, date DESC);

-- テーブル統計更新
ANALYZE stock_prices;

-- 不要データ削除
DELETE FROM stock_prices
WHERE date < NOW() - INTERVAL '2 years';

-- バキューム実行
VACUUM ANALYZE stock_prices;
```

#### アプリケーション最適化
```python
# キャッシュ設定調整
CACHE_CONFIG = {
    'prediction_cache_ttl': 300,  # 5分
    'market_data_cache_ttl': 60,  # 1分
    'user_session_ttl': 3600,     # 1時間
}

# 接続プール調整
DATABASE_POOL_CONFIG = {
    'min_connections': 10,
    'max_connections': 50,
    'pool_timeout': 30,
}
```

### パフォーマンス監視

#### 重要指標の監視
```bash
# API応答時間監視
curl -w "@curl-format.txt" -s -o /dev/null \
  http://localhost:8080/api/predictions/AAPL

# データベース性能監視
psql -d miraikakaku -c "
SELECT
  schemaname,
  tablename,
  n_tup_ins,
  n_tup_upd,
  n_tup_del,
  n_live_tup,
  n_dead_tup
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
"

# システムリソース監視
iostat -x 1 5
vmstat 1 5
```

---

## 🔐 セキュリティ運用

### 日常のセキュリティ チェック

#### アクセス ログ監視
```bash
# 異常なアクセスパターン検出
tail -f /var/log/nginx/access.log | \
  grep -E "(404|500|403)" | \
  awk '{print $1}' | sort | uniq -c | sort -nr

# 大量リクエスト検出
awk '{print $1}' /var/log/nginx/access.log | \
  sort | uniq -c | sort -nr | head -20

# 失敗した認証試行検出
grep "authentication failed" /var/log/miraikakaku/api.log
```

#### セキュリティ スキャン実行
```bash
# 脆弱性スキャン
python3 -c "
from enterprise_features_system import EnterpriseFeaturesSystem
enterprise = EnterpriseFeaturesSystem()
security_scan = enterprise.security_scanner.scan_vulnerabilities('http://localhost:8080')
print('Security scan completed:', len(security_scan), 'issues found')
"

# 依存関係脆弱性チェック
pip-audit
npm audit
```

#### SSL/TLS 証明書管理
```bash
# 証明書有効期限確認
openssl x509 -in /etc/ssl/certs/miraikakaku.com.crt -noout -dates

# Let's Encrypt 証明書更新
certbot renew --dry-run

# SSL設定テスト
openssl s_client -connect miraikakaku.com:443 -servername miraikakaku.com
```

---

## 📞 エスカレーション・連絡先

### 対応レベル別連絡先

#### Level 1: 一般的な問題
- **対応者**: オンデューティ エンジニア
- **連絡先**: +81-XX-XXXX-XXXX
- **Slack**: #ops-level1
- **対応時間**: 24時間以内

#### Level 2: 重要な問題
- **対応者**: シニア エンジニア
- **連絡先**: +81-XX-XXXX-XXXY
- **Slack**: #ops-level2
- **対応時間**: 2時間以内

#### Level 3: 緊急事態
- **対応者**: テック リード / CTO
- **連絡先**: +81-XX-XXXX-XXXZ
- **Slack**: #emergency
- **対応時間**: 30分以内

### インシデント エスカレーション フロー

```
問題発生 → Level 1対応 (30分)
    ↓ 解決しない
Level 2エスカレーション (1時間)
    ↓ 解決しない
Level 3エスカレーション (2時間)
    ↓ 解決しない
緊急対策本部設置
```

---

## 📚 参考資料・ドキュメント

### 内部ドキュメント
- **システム アーキテクチャ**: `/docs/architecture.md`
- **API リファレンス**: `/docs/api-reference.md`
- **データベース スキーマ**: `/docs/database-schema.md`
- **デプロイメント ガイド**: `/docs/deployment-guide.md`

### 外部リソース
- **PostgreSQL マニュアル**: https://www.postgresql.org/docs/
- **Next.js ドキュメント**: https://nextjs.org/docs
- **FastAPI ドキュメント**: https://fastapi.tiangolo.com/
- **Docker ドキュメント**: https://docs.docker.com/

### 緊急時参考資料
- **災害復旧計画**: `/docs/disaster-recovery-plan.md`
- **セキュリティ インシデント対応**: `/docs/security-incident-response.md`
- **データ漏洩対応**: `/docs/data-breach-response.md`

---

## 📝 変更履歴

| 日付 | バージョン | 変更内容 | 担当者 |
|------|-----------|----------|---------|
| 2024-12-01 | 1.0.0 | 初版作成 | DevOps Team |
| 2024-12-15 | 1.1.0 | 監視手順追加 | DevOps Team |
| 2024-12-20 | 1.2.0 | セキュリティ手順強化 | Security Team |

---

*最終更新: 2024年12月 | バージョン: 1.2.0*

**🔧 未来価格 運用マニュアル - 安定稼働のための包括ガイド 🔧**