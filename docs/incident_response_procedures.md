# Miraikakaku AI株式予測プラットフォーム インシデント対応手順書

## 概要
本文書は、Miraikakaku AI株式予測プラットフォームにおけるインシデント対応の標準手順を定義します。迅速かつ効果的なインシデント対応により、サービスの継続性とユーザー体験の維持を図ります。

## インシデント分類

### 重要度レベル

#### P0 (最高優先度) - 即座対応
- **システム全体停止**: 5分以内に対応開始
- **データ漏洩の疑い**: 即座に隔離措置
- **セキュリティ侵害**: 緊急セキュリティ対応
- **業務停止**: 完全サービス停止

#### P1 (高優先度) - 1時間以内対応
- **主要機能停止**: 株価予測、データ表示機能停止
- **パフォーマンス大幅劣化**: 応答時間10秒以上
- **データベース接続不能**: 部分的なデータアクセス不能
- **API大量エラー**: エラー率50%以上

#### P2 (中優先度) - 4時間以内対応
- **一部機能障害**: 特定機能の不具合
- **パフォーマンス劣化**: 応答時間5-10秒
- **間欠的エラー**: エラー率10-50%
- **ログエラー増加**: 通常の5倍以上

#### P3 (低優先度) - 24時間以内対応
- **軽微な不具合**: ユーザー体験への軽微な影響
- **ドキュメント不備**: 運用手順書の更新
- **監視アラート調整**: 閾値の最適化

## インシデント対応フロー

### 1. インシデント検知・報告
```
検知 → 初期評価 → 分類 → エスカレーション → 対応開始
```

#### 検知方法
- **自動監視システム**: `continuous_monitoring_system.py`
- **ユーザー報告**: サポート窓口
- **手動発見**: 運用チーム
- **外部監視**: 第三者監視サービス

#### 初期評価チェックリスト
- [ ] 影響範囲の特定
- [ ] 重要度レベルの判定
- [ ] 推定復旧時間の算出
- [ ] 必要なリソースの確認

### 2. 緊急対応手順

#### P0インシデント対応
1. **即座実行（5分以内）**
   ```bash
   # システム状態確認
   python3 continuous_monitoring_system.py

   # 緊急措置（必要に応じて）
   pm2 stop all  # サービス停止
   # または
   pm2 restart all  # サービス再起動
   ```

2. **通知実行**
   ```bash
   # ステークホルダーへの緊急通知
   echo "P0インシデント発生: $(date)" | mail -s "緊急事態" stakeholders@company.com
   ```

3. **ログ収集**
   ```bash
   # システムログ保存
   journalctl --since "1 hour ago" > /tmp/incident_$(date +%Y%m%d_%H%M%S).log

   # アプリケーションログ
   cp miraikakakufront/.next/logs/* /tmp/incident_logs/
   cp miraikakakuapi/logs/* /tmp/incident_logs/
   ```

#### P1インシデント対応
1. **詳細調査（15分以内）**
   ```bash
   # パフォーマンス確認
   python3 automated_performance_optimizer.py

   # データベース状態確認
   PGPASSWORD="${POSTGRES_PASSWORD}" psql -h ${DATABASE_HOST} -U postgres -d miraikakaku -c "
   SELECT
       datname,
       numbackends,
       xact_commit,
       xact_rollback,
       blks_read,
       blks_hit
   FROM pg_stat_database
   WHERE datname = 'miraikakaku';"
   ```

2. **根本原因分析**
   ```bash
   # エラーログ分析
   grep -E "ERROR|FATAL|CRITICAL" /var/log/system.log | tail -100

   # リソース使用状況
   top -b -n 1 | head -20
   df -h
   free -h
   ```

### 3. 復旧手順

#### システム復旧チェックリスト
- [ ] データベース接続復旧
- [ ] API サーバー正常化
- [ ] フロントエンド表示確認
- [ ] データ整合性確認
- [ ] パフォーマンス正常化

#### 段階的復旧手順
1. **データベース復旧**
   ```bash
   # 接続テスト
   PGPASSWORD="${POSTGRES_PASSWORD}" psql -h ${DATABASE_HOST} -U postgres -d miraikakaku -c "SELECT 1;"

   # 必要に応じて再起動
   gcloud sql instances restart miraikakaku-db
   ```

2. **API サーバー復旧**
   ```bash
   # API再起動
   pm2 restart api-1 api-2 api-3

   # ヘルスチェック
   curl -f http://localhost:8080/health || echo "API-1 異常"
   curl -f http://localhost:8081/health || echo "API-2 異常"
   curl -f http://localhost:8082/health || echo "API-3 異常"
   ```

3. **フロントエンド復旧**
   ```bash
   # フロントエンド再起動
   pm2 restart frontend

   # 表示確認
   curl -I http://localhost:3000 | grep "200 OK" || echo "フロントエンド異常"
   ```

### 4. コミュニケーション手順

#### 内部コミュニケーション
- **P0**: 即座に電話 + チャット
- **P1**: 15分以内にチャット通知
- **P2**: 1時間以内にメール
- **P3**: 日次レポートに含める

#### 外部コミュニケーション
- **ユーザー向け**: ステータスページ更新
- **ステークホルダー**: 定期アップデート
- **メディア**: 必要に応じて広報チーム経由

#### コミュニケーションテンプレート

**P0インシデント通知**
```
件名: [P0] Miraikakakuサービス緊急事態
発生時刻: [YYYY-MM-DD HH:MM]
影響範囲: [詳細]
現在の状況: [状況説明]
推定復旧時間: [時間]
対応状況: [対応内容]
次回更新: [時間]
```

**復旧完了通知**
```
件名: [復旧完了] Miraikakakuサービス正常化
復旧時刻: [YYYY-MM-DD HH:MM]
影響時間: [開始時刻-終了時刻]
根本原因: [原因説明]
再発防止策: [対策内容]
```

## 具体的インシデントシナリオ

### シナリオ1: データベース接続エラー
**症状**: APIが"Database connection failed"を返す

**対応手順**:
1. **即座確認**
   ```bash
   # Cloud SQL状態確認
   gcloud sql instances describe miraikakaku-db

   # 接続テスト
   nc -zv ${DATABASE_HOST} 5432
   ```

2. **復旧作業**
   ```bash
   # 接続プール再初期化
   pm2 restart all

   # 必要に応じてSQL再起動
   gcloud sql instances restart miraikakaku-db
   ```

### シナリオ2: メモリ不足
**症状**: システムが応答しない、OOMエラー

**対応手順**:
1. **メモリ状況確認**
   ```bash
   free -h
   ps aux --sort=-%mem | head -10
   ```

2. **緊急対応**
   ```bash
   # メモリを大量消費するプロセス特定・終了
   kill -9 [PID]

   # システム再起動（必要時）
   pm2 restart all
   ```

### シナリオ3: セキュリティインシデント
**症状**: 不審なアクセス、データ改ざんの疑い

**対応手順**:
1. **即座隔離**
   ```bash
   # 疑わしいIPをブロック
   iptables -A INPUT -s [SUSPICIOUS_IP] -j DROP

   # アクセスログ保存
   cp /var/log/nginx/access.log /tmp/security_incident_$(date +%Y%m%d_%H%M%S).log
   ```

2. **詳細調査**
   ```bash
   # セキュリティスキャン実行
   python3 automated_security_updater.py

   # 異常アクセス分析
   grep -E "POST|PUT|DELETE" /var/log/nginx/access.log | grep -v "200\|201\|202"
   ```

## 事後処理

### インシデントレポート作成
1. **タイムライン記録**
   - 発生時刻
   - 検知時刻
   - 対応開始時刻
   - 復旧完了時刻

2. **影響分析**
   - 影響ユーザー数
   - ダウンタイム
   - データ損失有無
   - ビジネス影響

3. **根本原因分析**
   - 技術的原因
   - プロセス的原因
   - 人的原因

### 再発防止策
1. **技術的改善**
   - システム強化
   - 監視改善
   - 自動化拡張

2. **プロセス改善**
   - 手順書更新
   - チェックリスト改訂
   - 訓練計画作成

3. **人的改善**
   - 教育・訓練
   - 責任明確化
   - コミュニケーション改善

## 定期的な準備

### 月次訓練
- **シナリオベース訓練**: 仮想インシデントでの対応訓練
- **ツール習熟度確認**: 復旧ツールの使用方法確認
- **コミュニケーション訓練**: 関係者間の連携確認

### 四半期レビュー
- **手順書更新**: 新たな脅威・技術への対応
- **ツール更新**: 監視・復旧ツールのアップデート
- **体制見直し**: 人員配置・責任分担の最適化

## 連絡先一覧

### 緊急連絡先
- **システム管理者**: [電話番号] / [メール]
- **開発チームリーダー**: [電話番号] / [メール]
- **インフラチーム**: [電話番号] / [メール]
- **経営陣**: [電話番号] / [メール]

### 外部連絡先
- **GCP サポート**: [サポート番号]
- **セキュリティベンダー**: [連絡先]
- **法務部門**: [連絡先]

### エスカレーション基準
- **30分で解決しない**: レベル2エスカレーション
- **1時間で解決しない**: 経営陣報告
- **データ損失疑い**: 即座に法務・経営陣報告

## ツールとリソース

### 主要コマンド集
```bash
# システム監視
python3 continuous_monitoring_system.py

# パフォーマンス確認
python3 automated_performance_optimizer.py

# セキュリティチェック
python3 automated_security_updater.py

# サービス制御
pm2 status
pm2 restart all
pm2 stop all

# データベース確認
PGPASSWORD="${POSTGRES_PASSWORD}" psql -h ${DATABASE_HOST} -U postgres -d miraikakaku

# GCP操作
gcloud sql instances list
gcloud sql instances describe miraikakaku-db
```

### 監視ダッシュボード
- **システムメトリクス**: CPU、メモリ、ディスク使用率
- **アプリケーションメトリクス**: API応答時間、エラー率
- **ビジネスメトリクス**: ユーザー数、予測精度

## セキュリティノート

### 環境変数設定

本ドキュメントの例で使用している環境変数は以下のように設定してください：

```bash
# データベース接続情報
export DATABASE_HOST="<実際のデータベースホスト>"
export POSTGRES_PASSWORD="<実際のPostgreSQLパスワード>"
```

**重要**: 実際の認証情報は以下の方法で安全に管理してください：
- Google Secret Manager を使用（推奨）
- 環境変数ファイル（.env）を使用（GitリポジトリにはCommitしない）
- インシデント対応時は事前に設定された認証情報を使用

### 緊急時の認証情報アクセス

インシデント対応時に認証情報が必要な場合：

```bash
# Secret Manager から認証情報を取得
export POSTGRES_PASSWORD=$(gcloud secrets versions access latest --secret="miraikakaku-db-password")
export DATABASE_HOST=$(gcloud secrets versions access latest --secret="miraikakaku-db-host")
```

---

*最終更新: 2025年9月26日*
*版数: 1.1*
*承認者: システム運用責任者*