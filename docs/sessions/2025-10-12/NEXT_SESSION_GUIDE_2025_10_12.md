# 次セッション実行ガイド
**作成日**: 2025-10-12
**前回の成果**: NewsAPI.org統合100%完了

---

## 📋 現在の状態

### ✅ 完了事項
1. **NewsAPI.org統合** - 100%完了
   - Toyota: 98記事収集・保存成功
   - シンボルベースマッピング実装(15社対応)
   - Cloud SQL接続設定完了
   - データベーススキーマ対応完了

2. **バッチエンドポイント作成**
   - `/admin/collect-news-newsapi-batch` 追加
   - 15社の日本株を一括処理
   - レート制限対応(300ms間隔)

3. **Cloud Scheduler設定済み**
   - daily-news-collection (06:00 JST)
   - daily-sentiment-predictions (07:00 JST)
   - daily-news-enhanced-predictions (08:00 JST)

---

## 🚀 次セッションの優先タスク

### Phase 1: デプロイとテスト (30分)

#### 1. 最新コードをデプロイ
\`\`\`bash
# Docker imageビルド
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api --project=pricewise-huqkr

# Cloud Runデプロイ
gcloud run services update miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api:latest \
  --region us-central1
\`\`\`

#### 2. バッチエンドポイントテスト
\`\`\`bash
# 15社一括ニュース収集
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-news-newsapi-batch?limit=15"
\`\`\`

**期待結果**:
- 15社のニュース収集成功
- 合計500-1000記事保存
- 成功率: 90%以上

---

**次セッション開始時のコマンド**:
\`\`\`bash
# 1. 最新状態確認
gcloud builds list --limit=3
gcloud run services describe miraikakaku-api --region=us-central1 --format="value(status.url)"

# 2. バッチテスト実行
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-news-newsapi-batch?limit=3"

# 3. 結果確認
curl "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/check-news-data?symbol=7203.T&limit=5"
\`\`\`

---

**作成者**: Claude  
**最終更新**: 2025-10-12 10:30 UTC
