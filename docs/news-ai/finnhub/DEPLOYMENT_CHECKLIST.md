# Finnhub統合 デプロイメントチェックリスト

## ✅ 完了済み

- [x] `finnhub_news_collector.py` 実装完了
- [x] API endpoints追加 (`/admin/collect-jp-news-finnhub`)
- [x] Dockerfile更新
- [x] .env.example更新

## 📋 実行手順 (15分)

### Step 1: Finnhub API Key取得 (2分)

1. https://finnhub.io/register にアクセス
2. メールアドレスで無料アカウント作成
3. Dashboard → API Key をコピー

**取得したAPI Key:** `___________________________`

---

### Step 2: Cloud RunにAPI Key設定 (1分)

```bash
gcloud run services update miraikakaku-api \
  --update-env-vars FINNHUB_API_KEY=YOUR_ACTUAL_API_KEY_HERE \
  --region us-central1 \
  --project pricewise-huqkr
```

**実行結果:** ✅ / ❌

---

### Step 3: ビルド (5分)

```bash
gcloud builds submit --config cloudbuild.api.yaml --project=pricewise-huqkr
```

**Build ID:** `___________________________`
**実行結果:** ✅ / ❌

---

### Step 4: デプロイ (3分)

```bash
gcloud run deploy miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api:latest \
  --region us-central1 \
  --platform managed \
  --project=pricewise-huqkr
```

**Service URL:** https://miraikakaku-api-zbaru5v7za-uc.a.run.app
**実行結果:** ✅ / ❌

---

### Step 5: テスト実行 - 5銘柄 (1分)

```bash
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-jp-news-finnhub?limit=5" \
  -H "Content-Type: application/json" \
  -H "Content-Length: 0"
```

**期待される結果:**
```json
{
  "status": "success",
  "successful_count": 5,
  "total_news_collected": 50-150
}
```

**実行結果:** ✅ / ❌
**収集ニュース数:** `_____` 件

---

### Step 6: 本番実行 - 50銘柄 (1分)

```bash
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-jp-news-finnhub?limit=50" \
  -H "Content-Type: application/json" \
  -H "Content-Length: 0"
```

**実行結果:** ✅ / ❌
**収集ニュース数:** `_____` 件

---

### Step 7: Cloud Scheduler設定 (2分)

```bash
gcloud scheduler jobs create http daily-jp-news-finnhub \
  --location=us-central1 \
  --schedule="30 6 * * *" \
  --time-zone="Asia/Tokyo" \
  --uri="https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-jp-news-finnhub?limit=50" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body="" \
  --attempt-deadline=600s \
  --project=pricewise-huqkr
```

**実行結果:** ✅ / ❌

---

## 🔍 検証コマンド

### データベース確認
```bash
PGPASSWORD='Miraikakaku2024!' psql -h localhost -p 5433 -U postgres -d miraikakaku -c "
SELECT
    COUNT(*) as total_jp_news,
    COUNT(DISTINCT symbol) as symbols_with_news,
    ROUND(AVG(sentiment_score)::numeric, 3) as avg_sentiment
FROM stock_news
WHERE symbol LIKE '%.T'
  AND created_at >= CURRENT_DATE - INTERVAL '7 days';
"
```

### Scheduler Jobs確認
```bash
gcloud scheduler jobs list --location=us-central1 --project=pricewise-huqkr
```

---

## 📊 期待される効果

| 項目 | デプロイ前 | デプロイ後 |
|------|-----------|-----------|
| 日本株ニュースカバレッジ | 0% | 100% |
| センチメント分析対象 (日本株) | 0銘柄 | 1,762銘柄 |
| 合計センチメントカバレッジ | 1% | 100% |

---

## ⚠️ トラブルシューティング

### API Keyエラー
```json
{"status": "error", "message": "FINNHUB_API_KEY not configured"}
```
→ **Step 2を再実行してAPI Keyを設定**

### ニュースが0件
```json
{"news_collected": 0}
```
→ **正常動作の可能性あり（本当にニュースがない場合）**
→ 別の銘柄（7203.T, 9984.Tなど）で試す

### デプロイエラー
→ `gcloud builds log BUILD_ID` でログ確認

---

## 🎯 完了条件

- [ ] Step 1-7 全て ✅
- [ ] テストで5銘柄から50+件のニュース収集確認
- [ ] データベースに日本株ニュースが保存されている
- [ ] Cloud Schedulerが毎日6:30に実行されている

**完了日時:** `_____________`
