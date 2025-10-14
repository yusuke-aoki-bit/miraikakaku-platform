# 次回セッション開始ガイド - 2025-10-13

## 📌 前回セッション完了内容（2025-10-12）

### ✅ 完了した作業

1. **API Stats エンドポイント修正完了**
   - 問題: 古い値 (1,740銘柄) を返していた
   - 解決: ユニークタグ `v20251012-225834` でビルド＆デプロイ
   - 結果: **3,756銘柄**を正しく表示 ✅

2. **現在のシステム状態**
   - API: リビジョン `00095-t47` で正常稼働中
   - Frontend: デプロイ済み（検証待ち）
   - Database: 3,756銘柄、1,742アクティブ、1,737予測済み
   - Cloud Scheduler: 1個のジョブが有効

3. **NewsAPI.org 統合完了**
   - 630記事収集済み
   - 15社の日本株対応
   - センチメント分析実装済み

## 🎯 次回セッションの優先タスク

### Priority 1: Frontend デプロイ検証 🔴

**目的**: フロントエンドが正しく動作していることを確認

```bash
# 1. フロントエンドアクセス確認
curl -I https://miraikakaku.jp

# 2. API経由で統計データ確認
curl -s https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/stats/summary | jq

# 3. ブラウザで確認すべき項目
# - トップページに「3,756銘柄」が表示されているか
# - キーボードショートカットボタンが削除されているか
# - ランキングデータが正しく表示されているか
```

**期待される結果**:
- [ ] トップページで「3,756銘柄」と表示される
- [ ] キーボードショートカットボタンが表示されない
- [ ] すべてのページが正常にレンダリングされる

### Priority 2: GitHub Actions 修正 🟠

**問題**: すべてのワークフローが失敗している

```bash
# 1. 失敗ログ確認
gh run list --limit 5

# 2. 最新の失敗詳細確認
gh run view --log

# 3. ワークフローファイル確認
cat .github/workflows/ci-cd.yml
cat .github/workflows/deploy-frontend.yml
```

**修正予定**:
- [ ] 失敗原因の特定
- [ ] ワークフロー設定の修正
- [ ] CI/CDパイプラインの復旧

### Priority 3: デプロイプロセス標準化 🟡

**目的**: 再発防止のためのプロセス改善

**実施項目**:
- [ ] タイムスタンプベースのタグ運用を標準化
- [ ] デプロイ後の自動検証スクリプト作成
- [ ] デプロイメントチェックリスト作成

## 🚀 Quick Start コマンド

### システム状態確認

```bash
# 1. Cloud Run サービス確認
gcloud run services list --platform managed \
  --format="table(SERVICE,REGION,URL,LAST_DEPLOYED_AT)"

# 2. API動作確認
curl -s https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/stats/summary | jq

# 3. Database接続確認
PGPASSWORD='Miraikakaku2024!' psql -h localhost -p 5433 -U postgres -d miraikakaku \
  -c "SELECT COUNT(*) as total_symbols FROM stock_master;"

# 4. Cloud Scheduler確認
gcloud scheduler jobs list --location=us-central1

# 5. NewsAPI収集状況確認
PGPASSWORD='Miraikakaku2024!' psql -h localhost -p 5433 -U postgres -d miraikakaku \
  -c "SELECT COUNT(*), MAX(published_at) FROM news_articles;"
```

### Frontend デプロイ（必要な場合）

```bash
# 1. Frontendビルド
cd miraikakakufront
npm run build

# 2. Dockerビルド（ユニークタグ）
BUILD_TAG="v$(python -c "from datetime import datetime; print(datetime.now().strftime('%Y%m%d-%H%M%S'))")"
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-frontend:$BUILD_TAG

# 3. デプロイ
gcloud run deploy miraikakaku-frontend \
  --image gcr.io/pricewise-huqkr/miraikakaku-frontend:$BUILD_TAG \
  --region us-central1 \
  --platform managed

# 4. 検証
curl -I https://miraikakaku.jp
```

### API デプロイ（必要な場合）

```bash
# 1. ユニークタグでビルド
BUILD_TAG="v$(python -c "from datetime import datetime; print(datetime.now().strftime('%Y%m%d-%H%M%S'))")"
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api:$BUILD_TAG

# 2. デプロイ
gcloud run services update miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api:$BUILD_TAG \
  --region us-central1

# 3. 検証
curl -s https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/stats/summary | jq
```

## 📊 現在のシステム構成

### Cloud Run サービス

| サービス | URL | 最新リビジョン | イメージ |
|---------|-----|--------------|---------|
| miraikakaku-api | https://miraikakaku-api-zbaru5v7za-uc.a.run.app | 00095-t47 | gcr.io/.../miraikakaku-api:v20251012-225834 |
| miraikakaku-frontend | https://miraikakaku-frontend-... | TBD | gcr.io/.../miraikakaku-frontend:latest |

### Database (Cloud SQL)

| テーブル | レコード数 | 備考 |
|---------|----------|------|
| stock_master | 3,756 | 総銘柄数 |
| stock_master (active) | 1,742 | アクティブ銘柄 |
| ensemble_predictions | ~254,116 | 総予測レコード |
| ensemble_predictions (future) | 1,737 | 将来予測あり銘柄 |
| news_articles | 630+ | NewsAPI収集記事 |

### Cloud Scheduler

| ジョブ名 | スケジュール | 状態 | 説明 |
|---------|------------|------|------|
| newsapi-daily-collection | 30 5 * * * | ENABLED | 毎日5:30にニュース収集 |

## 🔧 トラブルシューティング

### Issue 1: API が古い値を返す

**症状**: `/api/home/stats/summary` が 1,740 を返す

**解決方法**:
```bash
# ユニークタグでビルド＆デプロイ（latest タグを使わない）
BUILD_TAG="v$(python -c "from datetime import datetime; print(datetime.now().strftime('%Y%m%d-%H%M%S'))")"
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api:$BUILD_TAG
gcloud run services update miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api:$BUILD_TAG \
  --region us-central1
```

### Issue 2: Frontend が古いデータを表示

**症状**: トップページに「1,740銘柄」と表示される

**解決方法**:
1. APIが正しい値を返すか確認
2. Frontendのキャッシュをクリア
3. 必要に応じてFrontendを再デプロイ

### Issue 3: GitHub Actions が失敗

**症状**: すべてのワークフローが失敗

**確認手順**:
```bash
# 1. 失敗ログ確認
gh run list --limit 5
gh run view <run-id> --log

# 2. シークレット確認
gh secret list

# 3. ワークフローファイル確認
cat .github/workflows/ci-cd.yml
```

## 📚 関連ドキュメント

### 前回セッションドキュメント
- [SESSION_FINAL_COMPLETE_2025_10_12.md](SESSION_FINAL_COMPLETE_2025_10_12.md) - セッション完了報告
- [API_STATS_FIX_COMPLETE_2025_10_12.md](API_STATS_FIX_COMPLETE_2025_10_12.md) - API修正完了レポート
- [NEWSAPI_INTEGRATION_COMPLETE_2025_10_12.md](NEWSAPI_INTEGRATION_COMPLETE_2025_10_12.md) - NewsAPI統合レポート

### 技術ドキュメント
- [newsapi_collector.py](newsapi_collector.py) - NewsAPI収集モジュール
- [api_predictions.py](api_predictions.py) - メインAPIアプリケーション
- [miraikakakufront/app/layout.tsx](miraikakakufront/app/layout.tsx) - フロントエンドレイアウト

### Git コミット履歴
```
51c9330  Fix home stats API to show actual database record counts  ← 本日の修正
91a0541  Remove keyboard shortcuts button from layout
222dde9  Add missing prediction ranking and accuracy endpoints
```

## 🎯 セッション目標（次回）

### 必達目標
1. ✅ Frontend動作確認完了
2. ✅ GitHub Actions修正完了
3. ✅ 全システムの正常稼働確認

### 追加目標
1. デプロイプロセス標準化
2. 自動検証スクリプト作成
3. ドキュメント更新

## ⚠️ 重要な注意事項

### Dockerビルドのベストプラクティス

**❌ 非推奨**: `latest` タグのみの使用
```bash
gcloud builds submit --tag gcr.io/.../image:latest  # キャッシュ問題が発生
```

**✅ 推奨**: ユニークタグの使用
```bash
# タイムスタンプ
gcloud builds submit --tag gcr.io/.../image:v$(date +%Y%m%d-%H%M%S)

# Git commit hash
gcloud builds submit --tag gcr.io/.../image:$(git rev-parse --short HEAD)
```

### デプロイ検証の必須ステップ

1. ビルド実行
2. デプロイ実行
3. **動作確認（必須！）**
   ```bash
   curl <endpoint> | jq
   ```

ビルド成功 ≠ コード変更の反映

---

## 📞 サポート情報

**問題が発生した場合**:
1. 前回セッションドキュメントを確認
2. トラブルシューティングセクションを参照
3. システム状態確認コマンドを実行

**緊急時の連絡先**:
- GitHub Issues: https://github.com/yusuke-aoki-bit/miraikakaku-platform/issues
- ドキュメント: このディレクトリ内の各種MDファイル

---

**作成日時**: 2025-10-12 23:10 JST
**前回セッション**: 2025-10-12 22:30-23:06 JST（達成率: 100%）
**次回セッション予定**: Priority 1から開始
