# CI/CD セットアップガイド

## 🚀 GitHub Actions CI/CD パイプライン

このプロジェクトには2つのCI/CDワークフローが用意されています：

1. **ci-cd.yml** - フル機能版（Docker Build + Push + Deploy）
2. **ci-cd-simple.yml** - 簡易版（Source-based Deploy）

## 🔑 必要なGitHub Secrets

GitHubリポジトリの Settings > Secrets and variables > Actions で以下のSecretsを設定してください：

### 必須Secrets
```bash
GCP_SA_KEY                  # Google Cloud サービスアカウントキー（JSON形式）
GCP_PROJECT_ID             # Google Cloud プロジェクID（例: pricewise-huqkr）
CLOUD_SQL_HOST             # Cloud SQL IPアドレス（例: 34.58.103.36）
CLOUD_SQL_PASSWORD         # Cloud SQL rootパスワード（例: Yuuku717）
```

### オプションSecrets（フル版CI/CDで使用）
```bash
DATABASE_URL               # 完全なデータベース接続URL
JWT_SECRET_KEY            # JWT署名用シークレットキー
VERTEX_AI_PROJECT_ID      # Vertex AI プロジェクト ID
```

## 🛠️ サービスアカウント設定

### 1. Google Cloud サービスアカウント作成
```bash
# サービスアカウント作成
gcloud iam service-accounts create github-actions \
  --description="GitHub Actions CI/CD" \
  --display-name="GitHub Actions"

# 必要な権限を付与
gcloud projects add-iam-policy-binding pricewise-huqkr \
  --member="serviceAccount:github-actions@pricewise-huqkr.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding pricewise-huqkr \
  --member="serviceAccount:github-actions@pricewise-huqkr.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding pricewise-huqkr \
  --member="serviceAccount:github-actions@pricewise-huqkr.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# キーファイル生成
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@pricewise-huqkr.iam.gserviceaccount.com
```

### 2. GitHubにキー登録
```bash
# キーファイルの内容をコピー
cat github-actions-key.json

# GitHub > Settings > Secrets > GCP_SA_KEY にペースト
```

## 🔄 ワークフロー構成

### 簡易版ワークフロー（推奨）
**ファイル**: `.github/workflows/ci-cd-simple.yml`

**特徴**:
- ✅ 迅速なデプロイ（5-10分）
- ✅ Source-basedデプロイ（Dockerビルド不要）
- ✅ 基本的なバリデーション
- ✅ エラー耐性が高い

**実行タイミング**:
- `main`ブランチへのpush時にデプロイ
- PR作成時に検証のみ実行

### フル機能版ワークフロー
**ファイル**: `.github/workflows/ci-cd.yml`

**特徴**:
- 🔍 詳細なテストとセキュリティスキャン
- 🐳 Dockerイメージビルド・プッシュ
- 📊 コードカバレッジレポート
- 🔐 セキュリティ脆弱性チェック

**実行タイミング**:
- `main`, `develop`ブランチへのpush/PR時

## 📋 デプロイ対象サービス

### 3つのCloud Runサービス
1. **miraikakaku-api-fastapi** (Port 8000)
   - FastAPI バックエンド
   - Memory: 2Gi, CPU: 2

2. **miraikakaku-front** (Port 3000)
   - Next.js フロントエンド
   - Memory: 2Gi, CPU: 1

3. **miraikakaku-batch-final** (Port 8001)
   - Python バッチプロセッサ
   - Memory: 4Gi, CPU: 2

## 🔧 トラブルシューティング

### よくある問題と解決策

#### 1. 権限エラー
```bash
Error: (gcloud.run.deploy) PERMISSION_DENIED
```
**解決策**: サービスアカウントの権限を確認
```bash
gcloud projects get-iam-policy pricewise-huqkr \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:github-actions@pricewise-huqkr.iam.gserviceaccount.com"
```

#### 2. ビルドエラー
```bash
Error: npm ci failed
```
**解決策**: package-lock.jsonの整合性確認
```bash
cd miraikakakufront
npm cache clean --force
npm ci
```

#### 3. Cloud SQL接続エラー
```bash
Error: can't connect to database
```
**解決策**: 
- CLOUD_SQL_HOSTが正しいIPアドレスか確認
- CLOUD_SQL_PASSWORDが正しいか確認
- Cloud SQLインスタンスが稼働中か確認

#### 4. メモリ不足エラー
```bash
Error: Container failed to allocate memory
```
**解決策**: メモリ制限を増加
```bash
# CI/CDファイルで --memory を調整
--memory 4Gi  # 2Gi から 4Gi に変更
```

## ⚡ パフォーマンス最適化

### ビルド時間短縮
1. **キャッシュ活用**
   - npm依存関係のキャッシュ
   - pip依存関係のキャッシュ
   - Dockerレイヤーキャッシュ

2. **並列実行**
   - テストジョブの並列化
   - ビルドジョブの並列化

3. **条件付き実行**
   - mainブランチでのみデプロイ実行
   - 変更ファイルに基づく条件分岐

### リソース最適化
```yaml
# 推奨設定
resources:
  frontend: memory=2Gi, cpu=1
  api: memory=2Gi, cpu=2  
  batch: memory=4Gi, cpu=2
```

## 📊 監視・ログ

### GitHub Actions ログ
- **Actions タブ**でワークフロー実行状況確認
- **失敗時の詳細ログ**を確認
- **再実行機能**でトラブルシューティング

### Cloud Run ログ
```bash
# デプロイ後のログ確認
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=miraikakaku-api-fastapi" --limit=50

# エラーログのみ確認
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit=20
```

## ✅ デプロイ成功確認

### 自動ヘルスチェック
CI/CDパイプラインに組み込まれたヘルスチェック：
```bash
curl -f "https://miraikakaku-api-fastapi-465603676610.us-central1.run.app/health"
```

### 手動確認
```bash
# 各サービスの動作確認
curl "https://miraikakaku-api-fastapi-465603676610.us-central1.run.app/health"
curl "https://miraikakaku-front-465603676610.us-central1.run.app"
curl "https://miraikakaku-batch-final-465603676610.us-central1.run.app/health"
```

---

## 🔄 CI/CD ワークフロー状況

### 現在の修正状況
- ✅ **実際のサービス名に対応**
- ✅ **不要な依存関係を削除**
- ✅ **エラー耐性を向上**
- ✅ **実際のプロジェクト構造に適合**
- ✅ **環境変数を適切に設定**

### 推奨デプロイ方法
1. **初回**: 簡易版ワークフロー（ci-cd-simple.yml）を使用
2. **安定化後**: フル機能版ワークフロー（ci-cd.yml）に移行
3. **問題発生時**: 手動デプロイにフォールバック

---

*最終更新: 2025-08-23 21:30 JST*
*CI/CD Status: ✅ Ready for Production*