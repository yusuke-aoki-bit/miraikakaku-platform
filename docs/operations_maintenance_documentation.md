# Miraikakaku AI株式予測プラットフォーム 運用保守ドキュメント

## 概要
本ドキュメントは、Miraikakaku AI株式予測プラットフォームの運用保守に関する包括的なガイドです。システム管理者および運用担当者向けに、日常の監視、メンテナンス、トラブルシューティング手順を提供します。

## システム構成

### 主要コンポーネント
1. **フロントエンド** (Next.js)
   - ポート: 3000
   - インスタンス: 2 (クラスター)
   - 場所: `/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakufront`

2. **API サーバー** (Python/FastAPI)
   - ポート: 8080, 8081, 8082
   - インスタンス: 3 (負荷分散)
   - 場所: `/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakuapi`

3. **バッチ処理システム** (GCP Batch)
   - データ収集・予測生成
   - 場所: `/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch`

4. **データベース** (PostgreSQL on Cloud SQL)
   - ホスト: ${DATABASE_HOST} (設定は環境変数で管理)
   - データベース: miraikakaku

## 自動監視システム

### 継続的監視システム
- **ファイル**: `continuous_monitoring_system.py`
- **機能**: リアルタイム健全性チェック、自動アラート、メンテナンス
- **実行**: 24時間365日稼働

#### 監視項目
- システムリソース（CPU、メモリ、ディスク）
- アプリケーション応答時間
- データベース接続とパフォーマンス
- API エンドポイント可用性
- セキュリティインシデント

### パフォーマンス最適化システム
- **ファイル**: `automated_performance_optimizer.py`
- **機能**: パフォーマンス指標収集、自動最適化
- **実行頻度**: 1時間毎

#### 最適化対象
- データベースクエリ
- メモリ使用量
- ネットワーク遅延
- キャッシュ効率

### セキュリティ更新システム
- **ファイル**: `automated_security_updater.py`
- **機能**: 脆弱性スキャン、自動セキュリティ更新
- **実行頻度**: 日次

#### セキュリティチェック項目
- 依存関係の脆弱性
- ソースコードのセキュリティ問題
- 設定ファイルのセキュリティ
- アクセス制御

## 日常運用手順

### 毎日の監視チェック
1. **システム健全性確認**
   ```bash
   python3 continuous_monitoring_system.py
   ```

2. **パフォーマンス指標確認**
   ```bash
   python3 automated_performance_optimizer.py
   ```

3. **セキュリティスキャン**
   ```bash
   python3 automated_security_updater.py
   ```

### 週次メンテナンス
1. **ログファイル整理**
   ```bash
   # ログローテーション
   find ./logs -name "*.log" -mtime +7 -delete
   ```

2. **データベース統計更新**
   ```bash
   PGPASSWORD="${POSTGRES_PASSWORD}" psql -h ${DATABASE_HOST} -U postgres -d miraikakaku -c "ANALYZE;"
   ```

3. **キャッシュクリア**
   ```bash
   # アプリケーションキャッシュクリア
   pm2 restart all
   ```

### 月次メンテナンス
1. **依存関係更新**
   ```bash
   # Python依存関係
   pip3 install --upgrade -r requirements.txt

   # Node.js依存関係
   npm update
   ```

2. **データベースバックアップ確認**
   ```bash
   gcloud sql backups list --instance=miraikakaku-db
   ```

## トラブルシューティング

### よくある問題と解決方法

#### 1. API応答が遅い
**症状**: API レスポンス時間が5秒以上
**原因**: データベース接続問題またはクエリ最適化不足
**解決方法**:
```bash
# データベース接続確認
PGPASSWORD="${POSTGRES_PASSWORD}" psql -h ${DATABASE_HOST} -U postgres -d miraikakaku -c "SELECT 1;"

# 遅いクエリ確認
PGPASSWORD="${POSTGRES_PASSWORD}" psql -h ${DATABASE_HOST} -U postgres -d miraikakaku -c "
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;"
```

#### 2. メモリ使用量が高い
**症状**: システムメモリ使用率が90%以上
**原因**: メモリリークまたは大量データ処理
**解決方法**:
```bash
# プロセス確認
ps aux --sort=-%mem | head -10

# メモリ最適化
pm2 restart all
```

#### 3. データベース接続エラー
**症状**: Connection refused エラー
**原因**: Cloud SQL インスタンス停止またはネットワーク問題
**解決方法**:
```bash
# Cloud SQL状態確認
gcloud sql instances describe miraikakaku-db

# 接続テスト
nc -zv ${DATABASE_HOST} 5432
```

#### 4. フロントエンド表示エラー
**症状**: 白画面またはJavaScriptエラー
**原因**: ビルドエラーまたはAPI接続問題
**解決方法**:
```bash
# フロントエンド再ビルド
cd miraikakakufront
npm run build
pm2 restart frontend
```

## アラートレスポンス手順

### 高優先度アラート（即座対応）
- **システムダウン**: 5分以内に調査開始
- **データベース障害**: 10分以内に復旧作業開始
- **セキュリティインシデント**: 即座にアクセス制限実施

### 中優先度アラート（1時間以内対応）
- **パフォーマンス劣化**: 根本原因分析と最適化
- **メモリ不足警告**: リソース調整

### 低優先度アラート（24時間以内対応）
- **ログエラー**: 詳細調査と修正
- **依存関係更新通知**: 計画的更新実施

## パフォーマンス基準値

### 正常範囲
- **CPU使用率**: < 70%
- **メモリ使用率**: < 80%
- **API応答時間**: < 2秒
- **データベース接続時間**: < 500ms
- **ディスク使用率**: < 85%

### 注意範囲
- **CPU使用率**: 70-85%
- **メモリ使用率**: 80-90%
- **API応答時間**: 2-5秒
- **データベース接続時間**: 500ms-1秒
- **ディスク使用率**: 85-95%

### 危険範囲（即座対応必要）
- **CPU使用率**: > 85%
- **メモリ使用率**: > 90%
- **API応答時間**: > 5秒
- **データベース接続時間**: > 1秒
- **ディスク使用率**: > 95%

## セキュリティ監視

### 日次セキュリティチェック
1. **アクセスログ確認**
   ```bash
   grep "401\|403\|404" /var/log/nginx/access.log | tail -100
   ```

2. **異常なトラフィック検出**
   ```bash
   netstat -tuln | grep :80
   ss -tuln | grep :443
   ```

3. **システムファイル整合性確認**
   ```bash
   find /etc -type f -newer /tmp/yesterday -ls
   ```

### セキュリティインシデント対応
1. **疑わしいアクティビティ検出時**
   - 即座にアクセス制限
   - ログ詳細分析
   - 影響範囲調査

2. **データ漏洩疑い時**
   - システム隔離
   - 監査ログ確認
   - 関係者への通知

## バックアップとリカバリ

### 自動バックアップ
- **データベース**: 日次自動バックアップ（GCP Cloud SQL）
- **アプリケーションコード**: Git リポジトリ
- **設定ファイル**: 定期的なスナップショット

### リカバリ手順
1. **データベースリストア**
   ```bash
   gcloud sql backups restore [BACKUP_ID] --restore-instance=miraikakaku-db
   ```

2. **アプリケーションリストア**
   ```bash
   git checkout [COMMIT_HASH]
   pm2 restart all
   ```

## 連絡先とエスカレーション

### 緊急時連絡先
- **システム管理者**: [連絡先情報]
- **開発チーム**: [連絡先情報]
- **インフラチーム**: [連絡先情報]

### エスカレーション基準
- **レベル1**: 30分以内に解決できない場合
- **レベル2**: システム全体に影響する場合
- **レベル3**: データ損失またはセキュリティ侵害の疑い

## 定期レビュー

### 月次レビュー項目
- パフォーマンス傾向分析
- セキュリティインシデントレビュー
- システム容量計画
- 運用プロセス改善

### 四半期レビュー項目
- インフラ最適化
- 災害復旧計画更新
- セキュリティポリシー見直し
- 運用コスト分析

## セキュリティノート

### 環境変数設定

本ドキュメントの例で使用している環境変数は以下のように設定してください：

```bash
# データベース接続情報
export DATABASE_HOST="<実際のデータベースホスト>"
export POSTGRES_PASSWORD="<実際のPostgreSQLパスワード>"
```

**重要**: 実際の認証情報は以下の方法で安全に管理してください：
- Google Secret Manager を使用
- 環境変数ファイル（.env）を使用（GitリポジトリにはCommitしない）
- Kubernetes Secrets を使用（Kubernetes環境の場合）

### Secret Manager を使用した認証情報取得例

```bash
# Secret Manager からパスワードを取得
export POSTGRES_PASSWORD=$(gcloud secrets versions access latest --secret="miraikakaku-db-password")

# Secret Manager からデータベースホストを取得
export DATABASE_HOST=$(gcloud secrets versions access latest --secret="miraikakaku-db-host")
```

---

*最終更新: 2025年9月26日*
*担当者: システム運用チーム*