# 🚀 GitHub Actions 自動デプロイ設定手順

## ✅ 作成済みファイル
- `.github/workflows/deploy-frontend.yml` - フロントエンド自動デプロイ
- `.github/workflows/deploy-api.yml` - API自動デプロイ

## 🔧 設定手順

### 1. GitHubリポジトリ作成・プッシュ
```bash
# 新しいリポジトリ作成
git init
git add .
git commit -m "Initial commit with GitHub Actions"
git branch -M main
git remote add origin https://github.com/yourusername/miraikakaku.git
git push -u origin main
```

### 2. Google Cloud Service Account作成
```bash
# サービスアカウント作成
gcloud iam service-accounts create github-actions \
    --description="GitHub Actions deployment" \
    --display-name="GitHub Actions"

# 必要な権限付与
gcloud projects add-iam-policy-binding pricewise-huqkr \
    --member="serviceAccount:github-actions@pricewise-huqkr.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding pricewise-huqkr \
    --member="serviceAccount:github-actions@pricewise-huqkr.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding pricewise-huqkr \
    --member="serviceAccount:github-actions@pricewise-huqkr.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# サービスアカウントキー生成
gcloud iam service-accounts keys create key.json \
    --iam-account=github-actions@pricewise-huqkr.iam.gserviceaccount.com
```

### 3. GitHub Secrets設定
GitHubリポジトリの Settings > Secrets and variables > Actions で以下を設定：

- **Name**: `GCP_SA_KEY`
- **Value**: `key.json`ファイルの内容をコピー&ペースト

### 4. 動作確認
```bash
# mainブランチにプッシュして自動デプロイ開始
git add .
git commit -m "Enable GitHub Actions deployment"
git push origin main
```

## 🎯 期待される結果
- **フロントエンド**: `miraikakakufront/`変更時に自動デプロイ
- **API**: `miraikakakuapi/`変更時に自動デプロイ
- **手動実行**: GitHub Actions タブから手動実行可能
- **通知**: デプロイ成功/失敗をGitHubで確認

## 📊 メリット
- ✅ **完全自動**: プッシュで即座にデプロイ
- ✅ **信頼性**: Ubuntu環境で安定ビルド
- ✅ **履歴管理**: 全デプロイ履歴が記録
- ✅ **ロールバック**: 前バージョンへの復元が容易

## 🚨 重要な注意事項
1. **key.json は絶対にコミットしない**
2. **Secrets は GitHub の暗号化機能で保護**
3. **初回デプロイ後はCI/CDが完全自動化**

この設定により、WSL環境の制約を完全に回避し、最新レイアウトの自動デプロイが実現します。