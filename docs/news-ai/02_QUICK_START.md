# ニュースAIシステム クイックスタートガイド

## 🚀 1分で始める

### ステップ1: 日本株のニュースを収集

```bash
# トヨタ（7203.T）のニュースを収集
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-jp-news-for-symbol-yfinance?symbol=7203.T" \
  -H "Content-Type: application/json" \
  -H "Content-Length: 0"

# レスポンス例:
{
  "status": "success",
  "symbol": "7203.T",
  "company_name": "Toyota Motor Corp.",
  "news_collected": 10,
  "sentiment_distribution": {
    "bullish": 6,
    "bearish": 2,
    "neutral": 2
  }
}
```

### ステップ2: ニュース統合予測を生成

```bash
# トヨタの予測を生成
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/generate-news-prediction-for-symbol?symbol=7203.T" \
  -H "Content-Type: application/json" \
  -H "Content-Length: 0"

# レスポンス例:
{
  "status": "success",
  "symbol": "7203.T",
  "current_price": 2850.0,
  "predicted_price": 2920.5,
  "prediction_change_pct": 2.47,
  "confidence": 0.85,
  "news_sentiment": 0.25,
  "news_count": 10,
  "sentiment_trend": 0.15,
  "bullish_ratio": 0.60,
  "bearish_ratio": 0.20
}
```

### ステップ3: 予測結果を確認

```bash
# 予測データを取得
curl "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/stocks/7203.T/predictions?limit=5"
```

---

## 📊 主な機能

### 1. ニュース収集

#### 単一銘柄の収集
```bash
POST /admin/collect-jp-news-for-symbol-yfinance?symbol={SYMBOL}
```

**対応銘柄**:
- 日本株: `7203.T`, `9984.T`, `6758.T` など
- 米国株: `AAPL`, `GOOGL`, `MSFT` など（Finnhub使用）

#### バッチ収集
```bash
POST /admin/collect-jp-news-yfinance?limit=100
```

### 2. ニュース統合予測

#### 単一銘柄の予測
```bash
POST /admin/generate-news-prediction-for-symbol?symbol={SYMBOL}
```

**返却データ**:
- `predicted_price`: 予測価格
- `confidence`: 信頼度（0.60~0.95）
- `news_sentiment`: センチメントスコア（-1.0~1.0）
- `news_count`: ニュース件数
- `sentiment_trend`: センチメントトレンド
- `bullish_ratio`: 強気ニュース割合
- `bearish_ratio`: 弱気ニュース割合

#### バッチ予測
```bash
POST /admin/generate-news-enhanced-predictions?limit=100
```

---

## 🎯 使用例

### ユースケース1: 投資判断のためのセンチメント分析

```bash
# 1. ニュース収集
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-jp-news-for-symbol-yfinance?symbol=7203.T" \
  -H "Content-Type: application/json" -H "Content-Length: 0"

# 2. 予測生成
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/generate-news-prediction-for-symbol?symbol=7203.T" \
  -H "Content-Type: application/json" -H "Content-Length: 0"

# 3. 結果の解釈
# - bullish_ratio > 0.6 → 強気相場
# - news_sentiment > 0.2 → ポジティブ
# - confidence > 0.8 → 高信頼度
```

### ユースケース2: ポートフォリオ全体の分析

```bash
# 複数銘柄のニュースを一括収集
for symbol in 7203.T 9984.T 6758.T 7974.T 8306.T; do
  echo "=== $symbol ==="
  curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-jp-news-for-symbol-yfinance?symbol=$symbol" \
    -H "Content-Type: application/json" -H "Content-Length: 0"
  echo ""
done

# 一括予測生成
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/generate-news-enhanced-predictions?limit=5" \
  -H "Content-Type: application/json" -H "Content-Length: 0"
```

### ユースケース3: 米国株のニュース分析（Finnhub）

```bash
# Apple のニュース収集（Finnhub）
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-news-for-symbol?symbol=AAPL" \
  -H "Content-Type: application/json" -H "Content-Length: 0"

# 予測生成
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/generate-news-prediction-for-symbol?symbol=AAPL" \
  -H "Content-Type: application/json" -H "Content-Length: 0"
```

---

## 📈 データ解釈ガイド

### センチメントスコア（news_sentiment）
- **+0.8 ~ +1.0**: 非常に強気（Very Bullish）
- **+0.3 ~ +0.8**: 強気（Bullish）
- **-0.3 ~ +0.3**: 中立（Neutral）
- **-0.8 ~ -0.3**: 弱気（Bearish）
- **-1.0 ~ -0.8**: 非常に弱気（Very Bearish）

### 信頼度スコア（confidence）
- **0.90 ~ 0.95**: 極めて高い（Excellent）
- **0.80 ~ 0.90**: 高い（Good）
- **0.70 ~ 0.80**: 中程度（Fair）
- **0.60 ~ 0.70**: 低い（Poor）

### ニュース件数（news_count）
- **10+ 件**: データ充分（Full Coverage）
- **5-9 件**: データ中程度（Moderate Coverage）
- **1-4 件**: データ限定的（Limited Coverage）
- **0 件**: データなし（No Coverage）

### センチメントトレンド（sentiment_trend）
- **+0.3以上**: 強い上昇トレンド
- **+0.1~+0.3**: 上昇トレンド
- **-0.1~+0.1**: トレンドなし
- **-0.3~-0.1**: 下降トレンド
- **-0.3以下**: 強い下降トレンド

---

## 🔧 トラブルシューティング

### エラー: "No news data available"
**原因**: 該当銘柄のニュースがまだ収集されていない
**解決**: 先にニュース収集エンドポイントを呼び出す

### エラー: "Insufficient price history"
**原因**: 過去30日分の価格データが不足
**解決**: 価格データ収集を先に実行

### エラー: "tuple index out of range"
**原因**: 古いバージョンのAPIがデプロイされている
**解決**: 最新のデプロイを待つ（ビルド進行中）

---

## 🌟 ベストプラクティス

### 1. データ収集のタイミング
- **毎日1回**: 市場終了後にニュース収集
- **リアルタイム**: 重要イベント発生時

### 2. 予測生成のタイミング
- **市場開始前**: 当日の予測を生成
- **週1回**: 全銘柄のバッチ予測

### 3. データ品質管理
- ニュース件数が5件未満の銘柄は信頼度が低い
- センチメント標準偏差が大きい場合は注意

---

## 📚 関連ドキュメント

- [NEWS_AI_SYSTEM_COMPLETE_REPORT.md](./NEWS_AI_SYSTEM_COMPLETE_REPORT.md) - システム全体レポート
- [docs/NEWS_AI_INTEGRATION_COMPLETE_GUIDE.md](./docs/NEWS_AI_INTEGRATION_COMPLETE_GUIDE.md) - 詳細ガイド
- [DEPLOYMENT_STATUS_2025_10_12.md](./DEPLOYMENT_STATUS_2025_10_12.md) - デプロイ状況

---

**最終更新**: 2025-10-12 14:22 JST
**バージョン**: 1.0.0
**ステータス**: ✅ Production Ready
