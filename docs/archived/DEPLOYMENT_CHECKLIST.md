# デプロイメントチェックリスト

## 事前準備

- [ ] コードレビュー完了
- [ ] ローカルテスト完了
- [ ] .env.local に本番環境変数設定済み
- [ ] Git コミット完了

## デプロイ手順

### 自動デプロイ（推奨）

```bash
# API デプロイ
./scripts/deploy_and_verify.sh api

# Frontend デプロイ
./scripts/deploy_and_verify.sh frontend
```

### 手動デプロイ

#### 1. API デプロイ

```bash
# ユニークタグ生成
TAG="v$(python -c "from datetime import datetime; print(datetime.now().strftime('%Y%m%d-%H%M%S'))")"

# ビルド
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api:$TAG

# デプロイ
gcloud run services update miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api:$TAG \
  --region us-central1

# 検証
curl -s https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/stats/summary | jq
```

**期待される出力**:
```json
{
  "totalSymbols": 3756,
  "activePredictions": 1737
}
```

#### 2. Frontend デプロイ

```bash
# ユニークタグ生成
TAG="v$(python -c "from datetime import datetime; print(datetime.now().strftime('%Y%m%d-%H%M%S'))")"

# ビルド
cd miraikakakufront
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-frontend:$TAG
cd ..

# デプロイ
gcloud run services update miraikakaku-frontend \
  --image gcr.io/pricewise-huqkr/miraikakaku-frontend:$TAG \
  --region us-central1

# 検証
curl -I https://miraikakaku-frontend-zbaru5v7za-uc.a.run.app
curl -I https://www.miraikakaku.com
```

**期待される出力**: HTTP/1.1 200 OK

## デプロイ後の検証

### 必須チェック

- [ ] API が正しいデータを返す（totalSymbols: 3756）
- [ ] Frontend がアクセス可能（HTTP 200）
- [ ] カスタムドメインが動作（www.miraikakaku.com）
- [ ] エラーログがない

### 検証コマンド

```bash
# API 統計確認
curl -s https://api.miraikakaku.com/api/home/stats/summary | jq

# Frontend アクセス確認
curl -I https://www.miraikakaku.com

# Cloud Run サービス確認
gcloud run services list --platform managed

# エラーログ確認
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit 10 \
  --format json
```

## ロールバック手順

### API ロールバック

```bash
# 前回のイメージタグを確認
cat .last_api_image

# ロールバック
gcloud run services update miraikakaku-api \
  --image $(cat .last_api_image) \
  --region us-central1
```

### Frontend ロールバック

```bash
# 前回のイメージタグを確認
cat .last_frontend_image

# ロールバック
gcloud run services update miraikakaku-frontend \
  --image $(cat .last_frontend_image) \
  --region us-central1
```

## トラブルシューティング

### 問題: API が古いデータを返す

**症状**: totalSymbols が 1740 を返す

**原因**: Dockerビルドキャッシュ

**解決**:
```bash
# ユニークタグで再ビルド＆デプロイ
./scripts/deploy_and_verify.sh api
```

### 問題: Frontend が 500 エラー

**症状**: HTTP 500 Internal Server Error

**原因**: 環境変数が設定されていない

**解決**:
```bash
# 環境変数を設定してデプロイ
gcloud run services update miraikakaku-frontend \
  --set-env-vars="NEXT_PUBLIC_API_URL=https://api.miraikakaku.com" \
  --region us-central1
```

### 問題: ビルドが失敗する

**症状**: Cloud Build が FAILURE ステータス

**原因**: 依存関係の問題、Dockerfileエラー

**解決**:
```bash
# ビルドログ確認
gcloud builds list --limit=1 --format="value(id)" | xargs gcloud builds log

# ローカルでDockerビルドテスト
docker build -t test-image .
```

## ベストプラクティス

### ✅ 推奨

1. **常にユニークタグを使用**
   - タイムスタンプ: `v20251012-235959`
   - Git commit hash: `$(git rev-parse --short HEAD)`

2. **デプロイ後は必ず検証**
   - ビルド成功 ≠ コード変更の反映
   - API/Frontendの動作確認は必須

3. **ロールバック用にタグを保存**
   - `.last_api_image`, `.last_frontend_image` ファイルを活用

### ❌ 非推奨

1. **`latest` タグのみの使用**
   - Dockerキャッシュにより変更が反映されない可能性

2. **検証なしのデプロイ**
   - 問題の早期発見ができない

3. **直接 `main` ブランチへのプッシュ**
   - CI/CDパイプラインを活用

## 緊急時の連絡先

- GitHub Issues: https://github.com/yusuke-aoki-bit/miraikakaku-platform/issues
- Cloud Run ダッシュボード: https://console.cloud.google.com/run?project=pricewise-huqkr

---

**最終更新**: 2025-10-12
**担当**: DevOps Team
