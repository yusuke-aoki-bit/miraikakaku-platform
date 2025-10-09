# GCPリソース整理とドメイン修正計画

**作成日時**: 2025-10-09 16:30 JST
**ステータス**: 🔍 分析完了

---

## 🚨 発見された問題

### 1. カスタムドメインエラー
**症状**: `https://www.miraikakaku.com/` が404エラー

**原因**:
```
Domain Mapping: www.miraikakaku.com → miraikakaku-frontend (us-central1)
実際のサービス: miraikakaku-frontend が存在しない ❌
```

**影響**:
- メインドメインがアクセス不可
- ユーザーが404エラーを見る

---

## 📊 現在のGCPリソース状況

### Cloud Run Services (5個)

| サービス名 | URL | リージョン | 用途 | 状態 |
|----------|-----|----------|------|------|
| miraikakaku-api | https://miraikakaku-api-zbaru5v7za-uc.a.run.app | us-central1 | メインAPI | ✅ 稼働中 |
| miraikakaku-api-v3 | https://miraikakaku-api-v3-zbaru5v7za-uc.a.run.app | us-central1 | API V3（テスト） | ⚠️ 重複 |
| parallel-batch-collector | https://parallel-batch-collector-zbaru5v7za-an.a.run.app | asia-northeast1 | データ収集 | ✅ 稼働中 |
| generate-lstm-predictions | https://generate-lstm-predictions-zbaru5v7za-an.a.run.app | asia-northeast1 | LSTM予測 | ✅ 稼働中 |
| daily-predictions-generator | https://daily-predictions-generator-zbaru5v7za-an.a.run.app | asia-northeast1 | 日次予測 | ✅ 稼働中 |

### Cloud Functions (2個)

| 関数名 | ステータス | 用途 | 状態 |
|--------|----------|------|------|
| daily-predictions-generator | 不明 | 日次予測（重複？） | ⚠️ 確認必要 |
| generate-lstm-predictions | 不明 | LSTM予測（重複？） | ⚠️ 確認必要 |

### Cloud Scheduler Jobs

#### asia-northeast1 (11個)
| ジョブ名 | スケジュール | ターゲット | 状態 |
|---------|------------|-----------|------|
| batch-collector-job-1~10 | 0 * * * * | parallel-batch-collector | ✅ 正常（10並列） |
| daily-predictions-job-main | 0 0 * * * | daily-predictions-generator | ✅ 正常 |

#### us-central1 (8個)
| ジョブ名 | スケジュール | ターゲット | 状態 |
|---------|------------|-----------|------|
| parallel-batch-0 | */15 * * * * | parallel-batch-collector | ⚠️ 重複？ |
| lstm-predictions-daily | 0 */6 * * * | vertex-ai-trigger | ⚠️ 存在しないサービス？ |
| vertexai-predictions-daily | 0 */12 * * * | generate-predictions | ⚠️ 存在しないサービス？ |
| symbol-collection-us | 0 4 * * 1 | miraikakaku-scheduler | ⚠️ 存在しないサービス |
| symbol-collection-jp | 0 5 * * 1 | miraikakaku-scheduler | ⚠️ 存在しないサービス |
| symbol-collection-comprehensive | 0 6 1 * * | miraikakaku-scheduler | ⚠️ 存在しないサービス |
| db-optimization | 0 3 1 * * | miraikakaku-scheduler | ⚠️ 存在しないサービス |
| data-quality-check | 0 2 * * 0 | miraikakaku-scheduler | ⚠️ 存在しないサービス |

### Domain Mappings

#### us-central1 (8個)
| ドメイン | サービス | 状態 |
|---------|---------|------|
| api.miraikakaku.com | miraikakaku-api | ✅ 正常 |
| api.price-wiser.com | miraikakaku-api | ✅ 正常 |
| batch.miraikakaku.com | miraikakaku-batch | ❌ サービス不存在 |
| batch.price-wiser.com | miraikakaku-batch | ❌ サービス不存在 |
| miraikakaku.com | miraikakaku-frontend | ❌ サービス不存在 |
| price-wiser.com | miraikakaku-front | ❌ サービス不存在 |
| **www.miraikakaku.com** | **miraikakaku-frontend** | **❌ サービス不存在** |
| www.price-wiser.com | miraikakaku-front | ❌ サービス不存在 |

#### asia-northeast1 (1個)
| ドメイン | サービス | 状態 |
|---------|---------|------|
| api.miraikakaku.com | miraikakaku-api | ❌ サービス不存在（重複） |

---

## 🎯 整理計画

### フェーズ1: 緊急対応（カスタムドメイン修正）

#### 1-1. フロントエンドサービスの確認
```bash
# オプション1: 既存のCloud Runサービスを使用
# 現在フロントエンドに該当するサービスがない可能性

# オプション2: フロントエンドを新規デプロイ
# GitHub Actionsを使用（Cloud Buildは失敗）
```

#### 1-2. ドメインマッピングの修正
```bash
# 不要なマッピングを削除
gcloud beta run domain-mappings delete www.miraikakaku.com --region=us-central1
gcloud beta run domain-mappings delete miraikakaku.com --region=us-central1
gcloud beta run domain-mappings delete batch.miraikakaku.com --region=us-central1
gcloud beta run domain-mappings delete price-wiser.com --region=us-central1
gcloud beta run domain-mappings delete www.price-wiser.com --region=us-central1
gcloud beta run domain-mappings delete batch.price-wiser.com --region=us-central1
gcloud beta run domain-mappings delete api.miraikakaku.com --region=asia-northeast1

# 新しいマッピングを作成（フロントエンドサービス作成後）
# gcloud beta run domain-mappings create --service=[サービス名] --domain=www.miraikakaku.com --region=us-central1
```

### フェーズ2: 不要なCloud Scheduler削除

#### 2-1. 存在しないサービスへのScheduler削除
```bash
# us-central1の不要なScheduler（8個中5個）
gcloud scheduler jobs delete symbol-collection-us --location=us-central1
gcloud scheduler jobs delete symbol-collection-jp --location=us-central1
gcloud scheduler jobs delete symbol-collection-comprehensive --location=us-central1
gcloud scheduler jobs delete db-optimization --location=us-central1
gcloud scheduler jobs delete data-quality-check --location=us-central1

# 重複または不要なScheduler
gcloud scheduler jobs delete lstm-predictions-daily --location=us-central1
gcloud scheduler jobs delete vertexai-predictions-daily --location=us-central1
gcloud scheduler jobs delete parallel-batch-0 --location=us-central1
```

### フェーズ3: Cloud Functionsの整理

#### 3-1. 重複Functionsの確認と削除
```bash
# Cloud Functionsの詳細を確認
gcloud functions describe daily-predictions-generator --region=asia-northeast1
gcloud functions describe generate-lstm-predictions --region=asia-northeast1

# Cloud Runと重複している場合は削除
# gcloud functions delete daily-predictions-generator --region=asia-northeast1
# gcloud functions delete generate-lstm-predictions --region=asia-northeast1
```

### フェーズ4: API V3サービスの判断

#### 4-1. API V3の確認
```bash
# 現在使用されているか確認
gcloud run services describe miraikakaku-api-v3 --region=us-central1

# テスト用で不要な場合は削除
# gcloud run services delete miraikakaku-api-v3 --region=us-central1
```

---

## 🔧 推奨される最終構成

### Cloud Run Services (4個)
1. **miraikakaku-api** (us-central1) - メインAPI
2. **parallel-batch-collector** (asia-northeast1) - データ収集
3. **generate-lstm-predictions** (asia-northeast1) - LSTM予測
4. **daily-predictions-generator** (asia-northeast1) - 日次予測

### Cloud Scheduler Jobs (11個)
1. **batch-collector-job-1~10** (asia-northeast1) - データ収集（10並列）
2. **daily-predictions-job-main** (asia-northeast1) - 日次予測

### Domain Mappings (2個)
1. **api.miraikakaku.com** → miraikakaku-api (us-central1)
2. **www.miraikakaku.com** → [新しいフロントエンド] (us-central1)

### Cloud Functions (0個)
- 全てCloud Runに移行済み

---

## 📝 実行順序

### ステップ1: バックアップ確認
```bash
# 現在の設定をバックアップ
gcloud run services list > backup_services_$(date +%Y%m%d).txt
gcloud scheduler jobs list --location=us-central1 > backup_scheduler_us_$(date +%Y%m%d).txt
gcloud scheduler jobs list --location=asia-northeast1 > backup_scheduler_an_$(date +%Y%m%d).txt
gcloud beta run domain-mappings list --region=us-central1 > backup_domains_$(date +%Y%m%d).txt
```

### ステップ2: 不要なドメインマッピング削除
- 7個のドメインマッピングを削除

### ステップ3: 不要なScheduler削除
- 8個のSchedulerジョブを削除

### ステップ4: Cloud Functions確認・削除
- 2個のFunctionsを確認して必要に応じて削除

### ステップ5: API V3確認
- 使用状況を確認して削除判断

### ステップ6: フロントエンドデプロイ
- GitHub Actionsでフロントエンドをデプロイ
- ドメインマッピング再設定

---

## 💰 コスト削減見込み

### 現在の無駄なリソース
| リソース | 数量 | 月額コスト（推定） |
|---------|------|------------------|
| 不要なドメインマッピング | 6個 | $0（無料） |
| 不要なScheduler | 8個 | $2.40 |
| 重複Cloud Functions | 2個 | $0-10 |
| API V3（未使用の場合） | 1個 | $0-50 |

**合計削減見込み**: $2.40 - $62.40 / 月

---

## ⚠️ 注意事項

1. **ドメインマッピング削除前の確認**
   - DNSレコードは維持される
   - 削除後も再作成可能

2. **Scheduler削除の影響**
   - 存在しないサービスへのリクエストなので影響なし
   - エラーログが減少

3. **Cloud Functions削除**
   - Cloud Runで同等機能があることを確認してから削除

4. **フロントエンドデプロイ**
   - GitHub Actionsを使用（Cloud Buildは失敗中）
   - デプロイ後にドメインマッピング設定

---

## 🚀 次のアクション

**即座に実施可能**:
1. 不要なドメインマッピング削除（7個）
2. 不要なScheduler削除（8個）

**確認が必要**:
1. Cloud Functionsの詳細確認
2. API V3の使用状況確認
3. フロントエンドデプロイ戦略の決定

**実施すべき順序**:
1. バックアップ作成
2. ドメインマッピング整理
3. Scheduler整理
4. Functions整理
5. フロントエンドデプロイ
6. ドメインマッピング再設定
7. 動作確認

---

**作成者**: Claude Code
**優先度**: 🔴 高（カスタムドメインエラー対応）
**所要時間**: 約30分
