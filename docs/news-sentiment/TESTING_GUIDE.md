# ニュースセンチメント分析 - テストガイド

**作成日**: 2025-10-11
**目的**: ニュースセンチメント分析機能の完全なテスト手順

---

## 📋 前提条件

### 必須
- ✅ APIがCloud Runにデプロイ済み
- ✅ データベーススキーマ適用済み
- ✅ `ALPHA_VANTAGE_API_KEY` 環境変数設定済み

### 確認
```bash
# APIが稼働しているか確認
curl https://miraikakaku-api-zbaru5v7za-uc.a.run.app/health

# 期待レスポンス
{"status":"healthy"}
```

---

## 🚀 ステップ1: テスト用銘柄の追加

### 米国株・日本株を追加

```bash
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/add-test-stocks" \
  -H "Content-Type: application/json" \
  -H "Content-Length: 0"
```

**期待レスポンス**:
```json
{
  "status": "success",
  "message": "10 test stocks added/updated",
  "stocks": [
    {"symbol": "AAPL", "company_name": "Apple Inc."},
    {"symbol": "GOOGL", "company_name": "Alphabet Inc."},
    {"symbol": "MSFT", "company_name": "Microsoft Corporation"},
    {"symbol": "AMZN", "company_name": "Amazon.com Inc."},
    {"symbol": "TSLA", "company_name": "Tesla Inc."},
    {"symbol": "9984.T", "company_name": "SoftBank Group Corp."},
    {"symbol": "7203.T", "company_name": "Toyota Motor Corp."},
    {"symbol": "6758.T", "company_name": "Sony Group Corporation"},
    {"symbol": "7974.T", "company_name": "Nintendo Co., Ltd."},
    {"symbol": "8306.T", "company_name": "Mitsubishi UFJ Financial Group"}
  ]
}
```

---

## 🗞️ ステップ2: ニュース収集テスト

### 少数銘柄でテスト (推奨)

```bash
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-news?limit=3" \
  -H "Content-Type: application/json" \
  -H "Content-Length: 0"
```

**所要時間**: 約40秒 (3銘柄 × 12秒間隔)

**期待レスポンス**:
```json
{
  "status": "success",
  "message": "News collection completed for 3 symbols",
  "results": [
    {
      "symbol": "AAPL",
      "company_name": "Apple Inc.",
      "news_collected": 8
    },
    {
      "symbol": "AMZN",
      "company_name": "Amazon.com Inc.",
      "news_collected": 5
    },
    {
      "symbol": "GOOGL",
      "company_name": "Alphabet Inc.",
      "news_collected": 6
    }
  ]
}
```

### より多くの銘柄でテスト

```bash
# 5銘柄でテスト（約60秒）
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-news?limit=5" \
  -H "Content-Type: application/json" \
  -H "Content-Length: 0"

# 全10銘柄でテスト（約120秒）
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-news?limit=10" \
  -H "Content-Type: application/json" \
  -H "Content-Length: 0"
```

---

## 🔍 ステップ3: データベース確認

### ニュースデータ確認

```sql
-- 保存されたニュース件数
SELECT COUNT(*) as total_news FROM stock_news;

-- 銘柄別ニュース数
SELECT
    symbol,
    COUNT(*) as news_count,
    AVG(sentiment_score) as avg_sentiment,
    MIN(published_at) as oldest_news,
    MAX(published_at) as latest_news
FROM stock_news
GROUP BY symbol
ORDER BY news_count DESC;

-- 最新ニュース（上位10件）
SELECT
    symbol,
    title,
    sentiment_score,
    sentiment_label,
    published_at
FROM stock_news
ORDER BY published_at DESC
LIMIT 10;
```

### センチメントサマリー確認

```sql
-- センチメント集計
SELECT
    symbol,
    date,
    news_count,
    avg_sentiment,
    sentiment_trend,
    sentiment_strength,
    positive_count,
    negative_count,
    neutral_count
FROM stock_sentiment_summary
WHERE date = CURRENT_DATE
ORDER BY news_count DESC;

-- センチメント分布
SELECT
    sentiment_trend,
    COUNT(*) as stock_count,
    AVG(avg_sentiment) as average_sentiment,
    SUM(news_count) as total_news
FROM stock_sentiment_summary
WHERE date = CURRENT_DATE
GROUP BY sentiment_trend;
```

---

## 📊 ステップ4: 予測への統合確認

### ensemble_predictions の確認

```sql
-- センチメント統合された予測
SELECT
    symbol,
    prediction_date,
    current_price,
    ensemble_prediction,
    news_sentiment,
    news_impact,
    sentiment_adjusted_prediction,
    (sentiment_adjusted_prediction - ensemble_prediction) / ensemble_prediction * 100 as adjustment_pct
FROM ensemble_predictions
WHERE prediction_date >= CURRENT_DATE
  AND news_sentiment IS NOT NULL
ORDER BY ABS(adjustment_pct) DESC
LIMIT 10;
```

---

## 🧪 テストシナリオ

### シナリオ1: ポジティブニュース多数

**期待される銘柄**: AAPL, MSFT, GOOGL

**確認項目**:
- ✅ `avg_sentiment` > 0.3 (強気)
- ✅ `sentiment_trend` = 'bullish'
- ✅ `sentiment_adjusted_prediction` > `ensemble_prediction`

```sql
SELECT
    symbol,
    avg_sentiment,
    sentiment_trend,
    positive_count,
    negative_count
FROM stock_sentiment_summary
WHERE avg_sentiment > 0.3
ORDER BY avg_sentiment DESC;
```

### シナリオ2: ネガティブニュース多数

**確認項目**:
- ✅ `avg_sentiment` < -0.3 (弱気)
- ✅ `sentiment_trend` = 'bearish'
- ✅ `sentiment_adjusted_prediction` < `ensemble_prediction`

```sql
SELECT
    symbol,
    avg_sentiment,
    sentiment_trend,
    positive_count,
    negative_count
FROM stock_sentiment_summary
WHERE avg_sentiment < -0.3
ORDER BY avg_sentiment ASC;
```

### シナリオ3: センチメント調整の影響度

**目標**: ±2-5%の価格調整

```sql
SELECT
    symbol,
    ensemble_prediction as base,
    sentiment_adjusted_prediction as adjusted,
    (sentiment_adjusted_prediction - ensemble_prediction) / ensemble_prediction * 100 as adjustment_pct,
    news_sentiment,
    news_impact
FROM ensemble_predictions
WHERE prediction_date >= CURRENT_DATE
  AND news_sentiment IS NOT NULL
ORDER BY ABS(adjustment_pct) DESC
LIMIT 20;
```

**期待結果**:
- 最大調整: +3〜5% (強気ニュース多数)
- 最小調整: -3〜5% (弱気ニュース多数)
- 中央値: ±1〜2%

---

## ✅ 成功基準

### 必須項目

| 項目 | 基準 | 確認方法 |
|-----|------|---------|
| ニュース取得 | 最低3銘柄で5件以上 | `SELECT COUNT(*) FROM stock_news` |
| センチメントサマリー | 最低3銘柄 | `SELECT COUNT(*) FROM stock_sentiment_summary` |
| 予測調整 | 最低1銘柄 | `SELECT COUNT(*) FROM ensemble_predictions WHERE news_sentiment IS NOT NULL` |

### 推奨項目

| 項目 | 目標 | 確認方法 |
|-----|------|---------|
| ニュースカバレッジ | 80%以上の銘柄 | 8/10銘柄以上 |
| 平均ニュース数 | 5件以上/銘柄 | `AVG(news_count)` |
| センチメント分布 | バランス良く分散 | bullish/neutral/bearish |

---

## 🐛 トラブルシューティング

### ニュースが取得できない

**症状**: `news_collected: 0`

**原因と対策**:
1. **APIキーが未設定**: 環境変数 `ALPHA_VANTAGE_API_KEY` を確認
   ```bash
   gcloud run services describe miraikakaku-api \
     --region=us-central1 \
     --format="value(spec.template.spec.containers[0].env)"
   ```

2. **API制限に達した**: 5リクエスト/分、500リクエスト/日
   - 待機してから再試行
   - 有料プランへのアップグレード検討

3. **銘柄がカバーされていない**: Alpha Vantageは主に米国株と日本株
   - 米国株（AAPL, MSFT等）を優先してテスト
   - 韓国株（.KS）、香港株（.HK）はカバレッジが低い

### センチメントサマリーが生成されない

**症状**: `stock_sentiment_summary` が空

**原因と対策**:
1. **トリガーが動作していない**: 手動でトリガー実行
   ```sql
   -- 手動でセンチメント集計
   INSERT INTO stock_sentiment_summary (
       symbol, date, news_count, avg_sentiment,
       positive_count, negative_count, neutral_count,
       sentiment_trend, sentiment_strength
   )
   SELECT
       symbol,
       CURRENT_DATE,
       COUNT(*),
       AVG(sentiment_score),
       COUNT(*) FILTER (WHERE sentiment_label = 'positive'),
       COUNT(*) FILTER (WHERE sentiment_label = 'negative'),
       COUNT(*) FILTER (WHERE sentiment_label = 'neutral'),
       CASE
           WHEN AVG(sentiment_score) > 0.3 THEN 'bullish'
           WHEN AVG(sentiment_score) < -0.3 THEN 'bearish'
           ELSE 'neutral'
       END,
       ABS(AVG(sentiment_score))
   FROM stock_news
   WHERE published_at >= CURRENT_DATE - INTERVAL '7 days'
   GROUP BY symbol
   ON CONFLICT (symbol) DO UPDATE SET
       date = EXCLUDED.date,
       news_count = EXCLUDED.news_count,
       avg_sentiment = EXCLUDED.avg_sentiment,
       positive_count = EXCLUDED.positive_count,
       negative_count = EXCLUDED.negative_count,
       neutral_count = EXCLUDED.neutral_count,
       sentiment_trend = EXCLUDED.sentiment_trend,
       sentiment_strength = EXCLUDED.sentiment_strength,
       updated_at = NOW();
   ```

### 予測に反映されない

**症状**: `news_sentiment` カラムが NULL

**原因**: センチメント統合予測スクリプトが未実行

**対策**:
```bash
# センチメント統合予測を生成
cd scripts/news-sentiment
python generate_sentiment_enhanced_predictions.py
```

---

## 📈 KPI・モニタリング

### 日次チェック

```sql
-- 本日のニュース収集状況
SELECT
    DATE(created_at) as date,
    COUNT(DISTINCT symbol) as symbols_covered,
    COUNT(*) as total_news,
    AVG(sentiment_score) as avg_sentiment
FROM stock_news
WHERE created_at >= CURRENT_DATE
GROUP BY DATE(created_at);

-- 本日のセンチメント分布
SELECT
    sentiment_trend,
    COUNT(*) as count,
    AVG(news_count) as avg_news_per_symbol
FROM stock_sentiment_summary
WHERE date = CURRENT_DATE
GROUP BY sentiment_trend;
```

### 週次レビュー

```sql
-- 過去7日のトレンド
SELECT
    DATE(published_at) as date,
    COUNT(*) as news_count,
    AVG(sentiment_score) as avg_sentiment,
    COUNT(DISTINCT symbol) as symbols
FROM stock_news
WHERE published_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(published_at)
ORDER BY date DESC;
```

---

## 🎉 テスト完了チェックリスト

- [ ] テスト用銘柄10個を追加
- [ ] 3銘柄以上でニュース収集成功
- [ ] 合計15件以上のニュースを取得
- [ ] センチメントサマリーが生成される
- [ ] 少なくとも1銘柄でbullish/bearishが判定される
- [ ] ensemble_predictions にセンチメントが統合される
- [ ] 価格調整が±1-5%の範囲内
- [ ] データベースクエリが正常動作
- [ ] APIレスポンスが正常

---

**作成**: Claude AI
**バージョン**: 1.0
**最終更新**: 2025-10-11
