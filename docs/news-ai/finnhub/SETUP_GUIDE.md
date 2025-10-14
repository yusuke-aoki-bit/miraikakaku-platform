# Finnhub統合セットアップガイド

## ✅ 完了済み実装

1. ✅ `finnhub_news_collector.py` - Finnhubニュース収集モジュール
2. ✅ `/admin/collect-jp-news-finnhub` - 日本株ニュース一括収集エンドポイント
3. ✅ `/admin/collect-jp-news-for-symbol-finnhub` - 個別銘柄収集エンドポイント
4. ✅ `Dockerfile` - Finnhubモジュール追加
5. ✅ `.env.example` - FINNHUB_API_KEY追加

## 🚀 次のステップ

### Step 1: Finnhub API Key取得

1. **登録**: https://finnhub.io/register
2. **無料アカウント作成** (メールアドレスのみ)
3. **Dashboard → API Key**をコピー

### Step 2: Cloud RunにAPI Key設定

```bash
# Finnhub API Keyを環境変数に設定
gcloud run services update miraikakaku-api \
  --update-env-vars FINNHUB_API_KEY=your_actual_finnhub_api_key_here \
  --region us-central1 \
  --project pricewise-huqkr
```

### Step 3: ビルドとデプロイ

```bash
# ビルド
gcloud builds submit --config cloudbuild.api.yaml --project=pricewise-huqkr

# デプロイ (ビルド完了後)
gcloud run deploy miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api:latest \
  --region us-central1 \
  --platform managed \
  --project=pricewise-huqkr
```

### Step 4: テスト実行 (5銘柄)

```bash
# 日本株5銘柄でテスト
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-jp-news-finnhub?limit=5" \
  -H "Content-Type: application/json" \
  -H "Content-Length: 0"
```

**期待される結果:**
```json
{
  "status": "success",
  "message": "Finnhubから5銘柄のニュース収集完了",
  "successful_count": 5,
  "failed_count": 0,
  "total_news_collected": 150,
  "results": [
    {
      "status": "success",
      "symbol": "1430.T",
      "company_name": "First-corporation Inc.",
      "news_collected": 30,
      "sentiment_score": 0.15,
      "bullish_percent": 65.0,
      "bearish_percent": 20.0
    }
  ]
}
```

### Step 5: 日本株50銘柄で本番実行

```bash
# 日本株50銘柄のニュース収集 (約1分)
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-jp-news-finnhub?limit=50" \
  -H "Content-Type: application/json" \
  -H "Content-Length: 0"
```

### Step 6: センチメント統合予測生成

```bash
# 日本株を含む50銘柄の予測生成
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/generate-sentiment-predictions?limit=50" \
  -d ""
```

### Step 7: Cloud Scheduler設定

```bash
# 毎日6:30 JSTに日本株ニュース収集
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

## 📊 Finnhub API仕様

### Company News API
```
GET https://finnhub.io/api/v1/company-news?symbol=7203.T&from=2025-10-05&to=2025-10-12&token=YOUR_KEY
```

**レスポンス:**
```json
[
  {
    "category": "company news",
    "datetime": 1728691200,
    "headline": "トヨタ自動車、新型EVを発表",
    "id": 123456,
    "source": "Reuters",
    "summary": "トヨタ自動車は...",
    "url": "https://..."
  }
]
```

### News Sentiment API
```
GET https://finnhub.io/api/v1/news-sentiment?symbol=7203.T&token=YOUR_KEY
```

**レスポンス:**
```json
{
  "sentiment": {
    "bearishPercent": 0.15,
    "bullishPercent": 0.70,
    "neutralPercent": 0.15
  },
  "buzz": {
    "articlesInLastWeek": 50
  }
}
```

## 🎯 期待される効果

| 項目 | 現在 | Finnhub統合後 |
|------|------|--------------|
| 日本株ニュースカバレッジ | 0% | 100% |
| センチメント統合予測 (米国株) | 17銘柄 | 17銘柄 |
| センチメント統合予測 (日本株) | 0銘柄 | 1,762銘柄 |
| **合計センチメントカバレッジ** | **1%** | **100%** |

## ⚠️ 注意事項

1. **APIレート制限**: 無料プラン = 60 calls/分
   - 50銘柄収集 = 約50秒 (1.2秒間隔)
   - 1,762銘柄全て = 約35分

2. **センチメントスコア計算**:
   ```python
   sentiment_score = (bullish_percent - bearish_percent)
   # 範囲: -1.0 (超弱気) ～ +1.0 (超強気)
   ```

3. **コスト**:
   - 無料プラン: $0/月
   - Starter: $59.99/月 (必要に応じて)

## 🔍 トラブルシューティング

### API Keyが設定されていない
```json
{"status": "error", "message": "FINNHUB_API_KEY not configured"}
```
**解決策**: Step 2を実行してAPI Keyを設定

### ニュースが0件
```json
{"news_collected": 0, "feed_count": 0}
```
**原因**:
- その銘柄のニュースが本当にない
- Finnhubが対応していない銘柄
- APIレート制限超過

**解決策**: 別の銘柄で試す、時間を空けて再試行

## ✨ 次のアクション

**即座に実行:**
1. Finnhub API Key取得 (2分)
2. Cloud Runに設定 (1分)
3. ビルド&デプロイ (10分)
4. テスト実行 (5銘柄, 1分)
5. 本番実行 (50銘柄, 1分)

**合計所要時間: 約15分**

これで日本株1,762銘柄全てにセンチメント分析が適用されます！
