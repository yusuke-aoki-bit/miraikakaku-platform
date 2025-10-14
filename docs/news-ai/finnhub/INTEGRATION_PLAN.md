# Finnhub 日本株ニュース統合プラン

## 概要
Alpha Vantageでカバーできていない日本株1,762銘柄のニュースセンチメント分析を、Finnhubを使用して実装します。

## Finnhub APIの特徴

### 料金プラン
- **Free Tier:** 無料、60 API calls/分 (十分)
- **Starter:** $59.99/月
- API Key取得: https://finnhub.io/register

### 対応市場
- ✅ 東京証券取引所 (TSE)
- ✅ JPX
- ✅ シンボル形式: `7203.T` (トヨタ)、`9984.T` (ソフトバンク)

### APIエンドポイント

#### 1. Company News
```bash
GET https://finnhub.io/api/v1/company-news
Parameters:
  - symbol: 7203.T
  - from: 2025-10-05
  - to: 2025-10-12
  - token: YOUR_API_KEY

Response:
[
  {
    "category": "company news",
    "datetime": 1728691200,
    "headline": "トヨタ自動車、新型EVを発表",
    "id": 123456,
    "image": "https://...",
    "related": "7203.T",
    "source": "Reuters",
    "summary": "トヨタ自動車は...",
    "url": "https://..."
  }
]
```

#### 2. News Sentiment
```bash
GET https://finnhub.io/api/v1/news-sentiment
Parameters:
  - symbol: 7203.T
  - token: YOUR_API_KEY

Response:
{
  "buzz": {
    "articlesInLastWeek": 50,
    "buzz": 0.8,
    "weeklyAverage": 40
  },
  "companyNewsScore": 0.75,
  "sectorAverageBullishPercent": 0.65,
  "sectorAverageNewsScore": 0.70,
  "sentiment": {
    "bearishPercent": 0.15,
    "bullishPercent": 0.70,
    "neutralPercent": 0.15
  },
  "symbol": "7203.T"
}
```

## 実装ステップ

### Step 1: Finnhub API Key取得
1. https://finnhub.io/register でアカウント作成
2. Dashboard → API Keyを取得
3. `.env`に追加: `FINNHUB_API_KEY=your_key_here`

### Step 2: APIエンドポイント追加

#### `api_predictions.py`に追加:

```python
@app.post("/admin/collect-jp-news-finnhub")
def collect_jp_news_finnhub(limit: int = 20):
    """日本株ニュースをFinnhubから収集（管理者用）"""
    import requests
    from datetime import datetime, timedelta

    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')

    if not FINNHUB_API_KEY:
        return {"status": "error", "message": "FINNHUB_API_KEY not configured"}

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 日本株銘柄を取得
        cur.execute("""
            SELECT symbol, company_name
            FROM stock_master
            WHERE symbol LIKE '%.T'
              AND is_active = TRUE
            ORDER BY symbol
            LIMIT %s
        """, (limit,))
        symbols = cur.fetchall()

        results = []
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        to_date = datetime.now().strftime("%Y-%m-%d")

        for symbol_info in symbols:
            symbol = symbol_info['symbol']

            # Finnhub Company News API
            params = {
                'symbol': symbol,
                'from': from_date,
                'to': to_date,
                'token': FINNHUB_API_KEY
            }

            try:
                response = requests.get(
                    'https://finnhub.io/api/v1/company-news',
                    params=params,
                    timeout=30
                )
                news_data = response.json()

                # Finnhub News Sentiment API
                sentiment_response = requests.get(
                    'https://finnhub.io/api/v1/news-sentiment',
                    params={'symbol': symbol, 'token': FINNHUB_API_KEY},
                    timeout=30
                )
                sentiment_data = sentiment_response.json()

                news_saved = 0

                # ニュース記事を保存
                for article in news_data:
                    # センチメントスコアを計算
                    # Finnhubのsentiment dataから取得
                    sentiment_score = 0.0
                    if 'sentiment' in sentiment_data:
                        bullish = float(sentiment_data['sentiment'].get('bullishPercent', 0))
                        bearish = float(sentiment_data['sentiment'].get('bearishPercent', 0))
                        sentiment_score = (bullish - bearish) * 2 - 1  # -1 to +1に正規化

                    try:
                        cur.execute("""
                            INSERT INTO stock_news (
                                symbol, title, url, source, published_at,
                                summary, sentiment_score, sentiment_label, relevance_score
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (symbol, url) DO NOTHING
                        """, (
                            symbol,
                            article.get('headline', ''),
                            article.get('url', ''),
                            article.get('source', 'Unknown'),
                            datetime.fromtimestamp(article.get('datetime', 0)),
                            article.get('summary', ''),
                            sentiment_score,
                            'bullish' if sentiment_score > 0.1 else ('bearish' if sentiment_score < -0.1 else 'neutral'),
                            0.8  # Finnhubは関連性スコアがないのでデフォルト値
                        ))
                        news_saved += 1
                    except Exception as e:
                        continue

                conn.commit()

                results.append({
                    "symbol": symbol,
                    "company_name": symbol_info['company_name'],
                    "news_collected": news_saved,
                    "sentiment_score": sentiment_score if 'sentiment' in sentiment_data else None,
                    "articles_in_week": sentiment_data.get('buzz', {}).get('articlesInLastWeek', 0) if isinstance(sentiment_data, dict) else 0
                })

                # APIレート制限対策: 1秒待機
                import time
                time.sleep(1)

            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "error": str(e)
                })

        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": f"Finnhubから{len(results)}銘柄のニュース収集完了",
            "results": results
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
```

### Step 3: Cloud Scheduler追加

```bash
gcloud scheduler jobs create http daily-jp-news-finnhub \
  --location=us-central1 \
  --schedule="0 6 * * *" \
  --time-zone="Asia/Tokyo" \
  --uri="https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-jp-news-finnhub?limit=50" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body="" \
  --attempt-deadline=600s \
  --project=pricewise-huqkr
```

## 実装優先度

### 即座に実装可能:
1. ✅ Finnhub API Key取得 (無料)
2. ✅ エンドポイント実装 (30分)
3. ✅ テスト実行 (10分)
4. ✅ Cloud Scheduler設定 (5分)

### メリット:
- ✅ 日本株1,762銘柄全てカバー可能
- ✅ センチメントスコア付き
- ✅ 無料プランで十分 (60 calls/分 = 3,600 calls/時)
- ✅ Alpha Vantageと統合可能

### 期待される結果:
- 日本株ニュースカバレッジ: 0% → 100%
- センチメント統合予測: 米国株17 + 日本株1,762 = 1,779銘柄
- システム完成度: 95% → 100%

## 代替案: NewsAPI.org + Google NLP

もしFinnhubのセンチメントスコアが不十分な場合:

1. **NewsAPI.org**で日本語ニュース取得
2. **Google Cloud Natural Language API**で日本語センチメント分析
3. より高精度な日本語センチメント分析が可能

コスト比較:
- NewsAPI: $449/月
- Google NLP: 最初5,000ドキュメント無料
- **合計**: 月$449 + $50 = $499/月

Finnhub Starter ($59.99/月) の方がコスト効率が良い。

## 次のアクション

実装を希望される場合:
1. Finnhub API Key取得を指示
2. コード実装とデプロイ
3. テスト実行
4. Cloud Scheduler設定

これにより、日本株1,762銘柄全てにセンチメント統合予測が適用されます！
