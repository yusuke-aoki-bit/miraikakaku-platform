# CloudSQL MySQL → AlloyDB 移設計画

## 重要な制約
**AlloyDBはPostgreSQLのみサポート** - MySQLからの直接移行は不可能

## 移設戦略オプション

### オプション1: MySQL → PostgreSQL → AlloyDB (推奨)
1. **フェーズ1**: MySQL → PostgreSQL変換（pgloader使用）
2. **フェーズ2**: PostgreSQL → AlloyDB移行（DMS使用）

### オプション2: CloudSQL MySQL → CloudSQL PostgreSQL → AlloyDB
1. **フェーズ1**: 新CloudSQL PostgreSQLインスタンス作成
2. **フェーズ2**: MySQL→PostgreSQL移行（pgloader）
3. **フェーズ3**: CloudSQL PostgreSQL → AlloyDB（DMS）

### オプション3: AlloyDB移行なし（CloudSQL MySQL継続）
- 現在のMySQLシステムをCloudSQL内で最適化
- HA構成、リードレプリカ追加で性能向上

## 現在の環境
- **インスタンス**: miraikakaku (MYSQL_8_4)
- **リージョン**: us-central1  
- **構成**: db-custom-2-8192 (2vCPU, 8GB RAM)
- **状態**: RUNNABLE

## データ構造分析必要
```sql
-- 主要テーブル
- stock_master (銘柄マスタ)
- stock_price_history (価格履歴) 
- stock_predictions (予測データ)
- stock_aliases (エイリアス)

-- MySQL特有機能使用確認必要
- AUTO_INCREMENT → SERIAL
- DATETIME → TIMESTAMP
- VARCHAR(255) → TEXT制限確認
- Collation: utf8mb4_unicode_ci → UTF8
```

## 移行手順（オプション1）

### ステップ1: PostgreSQL移行準備
```bash
# pgloader インストール
sudo apt install pgloader

# CloudSQL PostgreSQLインスタンス作成
gcloud sql instances create miraikakaku-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-8192 \
  --region=us-central1
```

### ステップ2: スキーマ変換
```bash
# pgloader設定ファイル作成
pgloader mysql://user:pass@host/miraikakaku postgresql://user:pass@host/miraikakaku
```

### ステップ3: AlloyDB移行
```bash
# AlloyDBクラスター作成
gcloud alloydb clusters create miraikakaku-cluster \
  --region=us-central1 \
  --password=STRONG_PASSWORD

# PostgreSQL → AlloyDB移行
gcloud beta alloydb clusters migrate-cloud-sql miraikakaku-cluster \
  --cloud-sql-instance-id=miraikakaku-postgres
```

## リスク評価
- **高**: スキーマ変換の複雑性（MySQL→PostgreSQL）
- **中**: アプリケーション接続文字列変更
- **中**: SQL文法差異対応
- **低**: AlloyDB性能向上効果

## 推奨アプローチ
現在のコレーション問題が解決済みのため、**CloudSQL MySQL継続**を推奨。
AlloyDB移行は複雑で、現時点での性能問題が解決済みであれば不要。