# 📰 ニュースセンチメント分析統合 - 実装ガイド

**バージョン**: 2.0
**実装日**: 2025-10-11
**ステータス**: 実装完了（テスト準備完了）

---

## 🎯 概要

Miraikakaku株価予測システムに**ニュースセンチメント分析**を統合し、従来のアンサンブル予測（LSTM + ARIMA + MA）にニュース感情を加えた高精度な予測を実現します。

### 新機能

1. **ニュース記事の自動収集** - Alpha Vantage News API使用
2. **センチメント分析** - AIによる感情スコア計算
3. **予測への統合** - センチメントで予測価格を調整
4. **リアルタイムモニタリング** - ニュースの影響を可視化

---

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────────────────────────────┐
│                    ニュースセンチメント統合                        │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                      │
        ▼                     ▼                      ▼
┌──────────────┐   ┌──────────────────┐   ┌─────────────────┐
│ ニュース収集  │   │  センチメント     │   │   予測調整      │
│              │   │   スコア計算      │   │                 │
│ Alpha        │──▶│                  │──▶│ 基本予測 +      │
│ Vantage API  │   │ -1.0 ～ +1.0     │   │ セン

チメント    │
└──────────────┘   └──────────────────┘   └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  データベース     │
                    │  保存            │
                    └──────────────────┘
```

---

## 📊 データベーススキーマ

### 新規テーブル

#### 1. `stock_news` - ニュース記事
```sql
CREATE TABLE stock_news (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    source VARCHAR(100),
    published_at TIMESTAMP NOT NULL,
    summary TEXT,
    sentiment_score NUMERIC(5, 4),      -- -1.0 to 1.0
    sentiment_label VARCHAR(20),        -- positive/negative/neutral
    relevance_score NUMERIC(5, 4),      -- 0.0 to 1.0
    topics TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. `stock_sentiment_summary` - センチメント集計
```sql
CREATE TABLE stock_sentiment_summary (
    symbol VARCHAR(20) PRIMARY KEY,
    date DATE NOT NULL,
    news_count INTEGER DEFAULT 0,
    avg_sentiment NUMERIC(5, 4),
    positive_count INTEGER DEFAULT 0,
    negative_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    sentiment_trend VARCHAR(20),        -- bullish/bearish/neutral
    sentiment_strength NUMERIC(5, 4),   -- 0.0 to 1.0
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 拡張された既存テーブル

#### `ensemble_predictions` に追加された列
```sql
ALTER TABLE ensemble_predictions ADD COLUMN:
- news_sentiment NUMERIC(5, 4)                    -- ニュースセンチメントスコア
- news_impact NUMERIC(5, 4)                       -- ニュースの影響度
- sentiment_adjusted_prediction NUMERIC(12, 2)    -- 調整後予測価格
```

---

## 🔑 Alpha Vantage API

### API選定理由

1. **包括的なカバレッジ** - 日本株（.T）を含む世界中の株式をサポート
2. **AIセンチメント分析** - 記事ごとに感情スコアを提供
3. **無料枠** - 5リクエスト/分（開発・テストに十分）
4. **高品質データ** - 信頼性の高いニュースソース

### 使用例

```python
# Alpha Vantage News & Sentiments API
GET https://www.alphavantage.co/query?
    function=NEWS_SENTIMENT&
    tickers=9984.T&
    time_from=20251004T0000&
    limit=50&
    apikey=YOUR_API_KEY
```

### レスポンス例

```json
{
  "feed": [
    {
      "title": "SoftBank Group Announces New AI Initiative",
      "url": "https://...",
      "time_published": "20251011T093000",
      "source": "Reuters",
      "summary": "...",
      "ticker_sentiment": [
        {
          "ticker": "9984.T",
          "ticker_sentiment_score": "0.752",
          "ticker_sentiment_label": "Bullish",
          "relevance_score": "0.9"
        }
      ]
    }
  ]
}
```

---

## 🧮 センチメント調整アルゴリズム

### 1. センチメントスコアの計算

```python
# 過去7日間のニュースから計算
avg_sentiment = AVG(sentiment_score)  # -1.0 to 1.0
sentiment_strength = ABS(avg_sentiment)  # 0.0 to 1.0
```

### 2. ニュース影響度の計算

```python
# ニュース量に基づく影響度（多いほど影響大）
volume_factor = min(news_count / 20.0, 0.5)

# センチメント強度と量を組み合わせ
news_impact = sentiment_strength * volume_factor
```

### 3. 予測価格の調整

```python
# 最大±10%の調整
max_adjustment = 0.10
price_adjustment_ratio = avg_sentiment * news_impact * max_adjustment

# 調整後の価格
adjusted_prediction = ensemble_prediction * (1 + price_adjustment_ratio)

# 現実的な範囲にクリップ（現在価格から±30%）
min_price = current_price * 0.7
max_price = current_price * 1.3
adjusted_prediction = clip(adjusted_prediction, min_price, max_price)
```

### 調整例

| ケース | センチメント | ニュース数 | 影響度 | 調整 |
|--------|-------------|-----------|--------|------|
| 強気ニュース多数 | +0.6 | 25件 | 0.30 | +1.8% |
| 弱気ニュース中程度 | -0.4 | 15件 | 0.24 | -0.96% |
| 中立ニュース | 0.1 | 10件 | 0.05 | +0.05% |

---

## 📁 実装ファイル

### 1. データベーススキーマ
**ファイル**: `schema_news_sentiment.sql`

**実行方法**:
```bash
psql -h localhost -p 5433 -U postgres -d miraikakaku -f schema_news_sentiment.sql
```

### 2. ニュース分析モジュール
**ファイル**: `news_sentiment_analyzer.py`

**機能**:
- Alpha Vantage APIからニュース取得
- センチメントスコアの解析
- データベースへの保存
- 銘柄別センチメント集計

**実行方法**:
```bash
python news_sentiment_analyzer.py
```

### 3. センチメント統合予測生成
**ファイル**: `generate_sentiment_enhanced_predictions.py`

**機能**:
- 従来のアンサンブル予測生成
- センチメントデータの取得
- センチメント調整の適用
- 拡張予測の保存

**実行方法**:
```bash
python generate_sentiment_enhanced_predictions.py
```

---

## 🚀 セットアップ手順

### 1. 環境変数の設定

`.env`ファイルに以下を追加:
```bash
# News & Sentiment Analysis
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
```

**APIキーの取得**: https://www.alphavantage.co/support/#api-key

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

新規追加パッケージ:
- `statsmodels==0.14.0` - ARIMA予測
- `transformers==4.35.0` - NLP（将来用）
- `torch==2.1.0` - Deep Learning（将来用）

### 3. データベーススキーマの適用

```bash
psql -h localhost -p 5433 -U postgres -d miraikakaku -f schema_news_sentiment.sql
```

**確認**:
```sql
-- テーブルが作成されたか確認
\dt stock_news
\dt stock_sentiment_summary

-- ensemble_predictionsに列が追加されたか確認
\d ensemble_predictions
```

### 4. ニュースデータの初回収集

```bash
# テスト実行（10銘柄）
python news_sentiment_analyzer.py

# 本番実行（全銘柄）
# news_sentiment_analyzer.pyの LIMIT 10 を削除して実行
```

### 5. センチメント統合予測の生成

```bash
python generate_sentiment_enhanced_predictions.py
```

---

## 📊 運用フロー

### 日次バッチ処理

```
1. 午前6:00 - ニュース収集
   python news_sentiment_analyzer.py

2. 午前7:00 - センチメント統合予測生成
   python generate_sentiment_enhanced_predictions.py

3. 午前8:00 - API経由で予測提供
   GET /api/predictions/sentiment-enhanced
```

### Cloud Scheduler設定（推奨）

```yaml
# news-collector-job
schedule: "0 6 * * *"  # 毎日午前6時
url: https://miraikakaku-news-collector-[PROJECT_ID].run.app
timeout: 1800s

# sentiment-predictions-job
schedule: "0 7 * * *"  # 毎日午前7時
url: https://miraikakaku-sentiment-predictions-[PROJECT_ID].run.app
timeout: 1800s
```

---

## 📈 APIエンドポイント（拡張）

### 新規エンドポイント

#### 1. センチメント統合予測取得
```http
GET /api/stocks/{symbol}/sentiment-predictions?days=7
```

**レスポンス**:
```json
{
  "symbol": "9984.T",
  "predictions": [
    {
      "prediction_date": "2025-10-12",
      "ensemble_prediction": 10500,
      "sentiment_adjusted_prediction": 10689,
      "news_sentiment": 0.35,
      "news_impact": 0.18,
      "adjustment_pct": 1.8,
      "confidence": 0.87
    }
  ]
}
```

#### 2. 銘柄ニュース一覧
```http
GET /api/stocks/{symbol}/news?limit=20
```

**レスポンス**:
```json
{
  "symbol": "9984.T",
  "news": [
    {
      "title": "SoftBank Group Announces...",
      "published_at": "2025-10-11T09:30:00Z",
      "sentiment_score": 0.752,
      "sentiment_label": "positive",
      "source": "Reuters",
      "url": "https://..."
    }
  ],
  "sentiment_summary": {
    "avg_sentiment": 0.42,
    "sentiment_trend": "bullish",
    "news_count": 15
  }
}
```

#### 3. センチメントランキング
```http
GET /api/predictions/sentiment-rankings?limit=50
```

**レスポンス**:
```json
{
  "rankings": [
    {
      "symbol": "9984.T",
      "company_name": "SoftBank Group Corp.",
      "sentiment_score": 0.65,
      "sentiment_trend": "bullish",
      "news_count": 25,
      "predicted_change": 3.5
    }
  ]
}
```

---

## 🧪 テストとバリデーション

### 1. データベーステスト

```sql
-- ニュースが保存されているか確認
SELECT COUNT(*), symbol FROM stock_news GROUP BY symbol ORDER BY COUNT DESC LIMIT 10;

-- センチメントサマリーが計算されているか確認
SELECT * FROM stock_sentiment_summary WHERE date = CURRENT_DATE LIMIT 10;

-- 予測データにセンチメントが統合されているか確認
SELECT
    symbol,
    ensemble_prediction,
    sentiment_adjusted_prediction,
    news_sentiment,
    news_impact
FROM ensemble_predictions
WHERE prediction_date >= CURRENT_DATE
  AND news_sentiment IS NOT NULL
LIMIT 10;
```

### 2. センチメント調整の検証

```sql
-- 調整幅の統計
SELECT
    COUNT(*) as total,
    AVG((sentiment_adjusted_prediction - ensemble_prediction) / ensemble_prediction * 100) as avg_adjustment_pct,
    MAX((sentiment_adjusted_prediction - ensemble_prediction) / ensemble_prediction * 100) as max_adjustment_pct,
    MIN((sentiment_adjusted_prediction - ensemble_prediction) / ensemble_prediction * 100) as min_adjustment_pct
FROM ensemble_predictions
WHERE prediction_date >= CURRENT_DATE
  AND news_sentiment IS NOT NULL;
```

### 3. 精度評価（バックテスト）

```python
# バックテスト用スクリプト
# 過去のセンチメントデータと実際の価格変動を比較
python scripts/backtest_sentiment_predictions.py --days=30
```

---

## 📊 モニタリングとアラート

### KPI

1. **ニュース収集率**: 対象銘柄の何%がニュースを持っているか
2. **センチメント分布**: Bullish/Bearish/Neutralの比率
3. **調整幅の分布**: センチメントによる予測調整の平均・最大・最小
4. **精度向上率**: センチメント統合前後の予測精度比較

### ダッシュボードクエリ

```sql
-- 日次サマリー
SELECT
    COUNT(DISTINCT symbol) as symbols_with_news,
    COUNT(*) as total_news,
    AVG(sentiment_score) as avg_sentiment,
    COUNT(*) FILTER (WHERE sentiment_label = 'positive') as positive_news,
    COUNT(*) FILTER (WHERE sentiment_label = 'negative') as negative_news
FROM stock_news
WHERE published_at >= CURRENT_DATE - INTERVAL '1 day';
```

---

## 🔮 今後の拡張

### Phase 2: 高度な機能

1. **LLMによるセンチメント分析**
   - Transformersモデルの活用
   - より詳細な感情分類

2. **イベント検出**
   - 決算発表、M&A、規制変更の自動検出
   - イベントの影響度予測

3. **ソーシャルメディア統合**
   - Twitter/X API
   - Reddit sentiment

4. **リアルタイム更新**
   - WebSocket経由でのニュース配信
   - 即座の予測更新

---

## ⚠️ 注意事項

### API制限

- **Alpha Vantage無料版**: 5リクエスト/分、500リクエスト/日
- **対策**: 銘柄処理の間に12秒の待機時間を設定済み

### データ品質

- 日本株のニュースは英語版が中心
- ニュース量は米国株より少ない傾向
- センチメントスコアの精度は記事の品質に依存

### パフォーマンス

- 全銘柄の処理に約30-60分（2000銘柄想定）
- データベースインデックスの最適化が重要

---

## 📚 参考資料

- [Alpha Vantage Documentation](https://www.alphavantage.co/documentation/)
- [Sentiment Analysis Best Practices](https://polygon.io/blog/sentiment-analysis-with-ticker-news-api-insights)
- [Financial NLP Research](https://pythoninvest.com/long-read/sentiment-analysis-of-financial-news)

---

## 💬 サポート

実装に関する質問や問題がある場合は、以下を確認してください：

1. ログファイル: `news_analysis.log`
2. データベースログ: PostgreSQLログ
3. APIレスポンス: `response.json`（デバッグモード時）

---

**実装完了日**: 2025-10-11
**次のステップ**: 本番環境での初回実行とバックテスト
