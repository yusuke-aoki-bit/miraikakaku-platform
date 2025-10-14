# ニュースセンチメントAI統合完全ガイド

## 📚 目次

1. [概要](#概要)
2. [アーキテクチャ](#アーキテクチャ)
3. [データフロー](#データフロー)
4. [実装詳細](#実装詳細)
5. [使用方法](#使用方法)
6. [APIリファレンス](#apiリファレンス)
7. [学習データ準備](#学習データ準備)
8. [モデル学習](#モデル学習)
9. [予測実行](#予測実行)
10. [パフォーマンス最適化](#パフォーマンス最適化)

---

## 概要

このシステムは、ニュースセンチメントデータを機械学習（LSTM）モデルに統合し、より精度の高い株価予測を実現します。

### 主な機能

1. **ニュース収集**
   - Alpha Vantage（米国株）
   - Finnhub（グローバル）
   - yfinance（日本株）

2. **センチメント分析**
   - TextBlobによる極性分析
   - APIベースのセンチメントスコア
   - ラベル分類（bullish/bearish/neutral）

3. **特徴量抽出**
   - 9次元のニュースセンチメント特徴量
   - 時系列トレンド分析
   - 統計的集約

4. **AI学習統合**
   - LSTM + ニュース特徴のハイブリッドモデル
   - 価格系列とセンチメントの並列処理
   - アンサンブル予測

---

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    ニュース収集層                              │
├─────────────────────────────────────────────────────────────┤
│  Alpha Vantage  │  Finnhub  │  yfinance                      │
│  (米国株)        │ (グローバル)│ (日本株)                       │
└────────┬────────────────┬────────────────┬─────────────────┘
         │                │                │
         └────────────────┴────────────────┘
                         │
         ┌───────────────▼───────────────┐
         │     stock_news テーブル        │
         │  - title, url, source         │
         │  - sentiment_score            │
         │  - sentiment_label            │
         │  - published_at               │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │   特徴量抽出層                  │
         │  NewsFeatureExtractor         │
         │  - 9次元ベクトル生成            │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │      AI予測層                  │
         │  NewsEnhancedLSTM             │
         │  - 価格系列LSTM                │
         │  - ニュース特徴Dense            │
         │  - 統合予測                    │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │  ensemble_predictions         │
         │  - ensemble_prediction        │
         │  - news_sentiment_score       │
         │  - ensemble_confidence        │
         └───────────────────────────────┘
```

---

## データフロー

### 1. ニュース収集フロー

```python
# yfinance例
yfinance API
    ↓
yfinance_jp_news_collector.collect_jp_news_yfinance()
    ↓
stock_news テーブルに保存
    - INSERT ... ON CONFLICT DO NOTHING
    ↓
NewsFeatureExtractor.extract_sentiment_features()
```

### 2. 特徴量抽出フロー

```python
NewsFeatureExtractor
    ↓
過去7日間のニュース取得
    ↓
9次元特徴量計算:
    1. avg_sentiment: 平均センチメントスコア
    2. sentiment_std: 標準偏差
    3. bullish_ratio: 強気ニュース割合
    4. bearish_ratio: 弱気ニュース割合
    5. neutral_ratio: 中立ニュース割合
    6. news_count: ニュース件数
    7. sentiment_trend: トレンド（最近 vs 過去）
    8. max_sentiment: 最大センチメント
    9. min_sentiment: 最小センチメント
```

### 3. AI予測フロー

```python
NewsEnhancedLSTM
    ↓
入力準備:
    - 価格系列: (30日, 1) 正規化済み
    - ニュース特徴: (9,) ベクトル
    ↓
モデル処理:
    - LSTM(64) → LSTM(32) → Dense(16)  # 価格系列
    - Dense(32) → Dense(16)             # ニュース特徴
    - Concatenate → Dense(32) → Dense(1) # 統合
    ↓
予測価格 + 信頼度
```

---

## 実装詳細

### ファイル構成

```
miraikakaku/
├── src/
│   └── ml-models/
│       ├── news_feature_extractor.py      # 特徴量抽出
│       └── news_enhanced_lstm.py          # LSTM モデル
│
├── generate_news_enhanced_predictions.py   # 予測生成スクリプト
│
├── finnhub_news_collector.py              # Finnhubニュース収集
├── yfinance_jp_news_collector.py          # yfinanceニュース収集
│
├── api_predictions.py                     # REST API
│
└── docs/
    └── NEWS_AI_INTEGRATION_COMPLETE_GUIDE.md
```

### コアクラス

#### 1. NewsFeatureExtractor

```python
from news_feature_extractor import NewsFeatureExtractor

extractor = NewsFeatureExtractor(db_config)

# 単一銘柄の特徴量
features = extractor.extract_sentiment_features(
    symbol='AAPL',
    target_date=datetime.now(),
    lookback_days=7
)

# 学習データセット作成
X, y = extractor.create_training_dataset(
    symbols=['AAPL', 'GOOGL', 'MSFT'],
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2025, 10, 1)
)
```

#### 2. NewsEnhancedLSTM

```python
from news_enhanced_lstm import NewsEnhancedLSTM

model = NewsEnhancedLSTM(
    db_config=db_config,
    price_sequence_length=30,
    news_feature_dim=9
)

# モデル構築
model.build_model()

# 学習
history = model.train(
    symbol='AAPL',
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2025, 9, 1),
    epochs=50
)

# 予測
prediction = model.predict(symbol='AAPL')
# {
#     'predicted_price': 185.50,
#     'confidence': 0.85,
#     'news_sentiment': 0.25,
#     'news_count': 15
# }
```

---

## 使用方法

### ステップ1: ニュース収集

```bash
# 日本株ニュース収集（yfinance）
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-jp-news-yfinance?limit=100"

# 米国株ニュース収集（Finnhub）
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-jp-news-finnhub?limit=50"
```

### ステップ2: ニュース統合予測生成

```bash
# バッチ予測
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/generate-news-enhanced-predictions?limit=100"

# 単一銘柄予測
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/generate-news-prediction-for-symbol?symbol=AAPL"
```

### ステップ3: 予測結果確認

```bash
curl "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/stocks/AAPL/predictions"
```

---

## APIリファレンス

### ニュース収集エンドポイント

#### 1. yfinance日本株ニュース収集

```
POST /admin/collect-jp-news-yfinance
```

**パラメータ:**
- `limit` (int, default=20): 収集する銘柄数

**レスポンス:**
```json
{
  "status": "success",
  "successful_count": 20,
  "total_news_collected": 200,
  "results": [...]
}
```

#### 2. Finnhubニュース収集

```
POST /admin/collect-jp-news-finnhub
```

### 予測生成エンドポイント

#### 1. ニュース統合予測（バッチ）

```
POST /admin/generate-news-enhanced-predictions
```

**パラメータ:**
- `limit` (int, default=100): 予測する銘柄数

**レスポンス:**
```json
{
  "status": "success",
  "total_symbols": 100,
  "successful": 95,
  "failed": 5
}
```

#### 2. ニュース統合予測（単一銘柄）

```
POST /admin/generate-news-prediction-for-symbol
```

**パラメータ:**
- `symbol` (string, required): 銘柄コード

**レスポンス:**
```json
{
  "status": "success",
  "symbol": "AAPL",
  "current_price": 180.50,
  "predicted_price": 185.20,
  "confidence": 0.85,
  "news_sentiment": 0.25,
  "news_count": 15,
  "sentiment_trend": 0.10
}
```

---

## 学習データ準備

### Pythonスクリプト例

```python
from news_feature_extractor import NewsFeatureExtractor
from datetime import datetime

db_config = {
    'host': 'localhost',
    'database': 'miraikakaku',
    'user': 'postgres',
    'password': 'your_password'
}

extractor = NewsFeatureExtractor(db_config)

# 学習データ作成
symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']

X, y = extractor.create_training_dataset(
    symbols=symbols,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2025, 9, 1),
    lookback_days=7
)

print(f"Training data shape: X={X.shape}, y={y.shape}")
# Training data shape: X=(1500, 9), y=(1500,)

# NumPyファイルとして保存
import numpy as np
np.save('X_train.npy', X)
np.save('y_train.npy', y)
```

---

## モデル学習

### 学習スクリプト例

```python
from news_enhanced_lstm import NewsEnhancedLSTM
from datetime import datetime

db_config = {
    'host': 'localhost',
    'database': 'miraikakaku',
    'user': 'postgres',
    'password': 'your_password'
}

# モデル初期化
model = NewsEnhancedLSTM(db_config)
model.build_model()

# モデルサマリー表示
model.model.summary()

# 学習実行
history = model.train(
    symbol='AAPL',
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2025, 9, 1),
    epochs=50,
    batch_size=32,
    validation_split=0.2
)

# 学習曲線をプロット
import matplotlib.pyplot as plt

plt.plot(history['loss'], label='Training Loss')
plt.plot(history['val_loss'], label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.savefig('training_history.png')

# モデル保存
model.save_model('models/news_enhanced_lstm_AAPL.h5')
```

---

## 予測実行

### コマンドライン例

```bash
# 単一銘柄予測
python generate_news_enhanced_predictions.py --symbol AAPL

# バッチ予測
python generate_news_enhanced_predictions.py --batch --limit 100
```

### Python例

```python
from generate_news_enhanced_predictions import generate_news_enhanced_prediction

result = generate_news_enhanced_prediction('AAPL')

print(f"""
Symbol: {result['symbol']}
Current Price: ${result['current_price']:.2f}
Predicted Price: ${result['predicted_price']:.2f}
Change: {result['prediction_change_pct']:.2f}%
Confidence: {result['confidence']:.2%}
News Sentiment: {result['news_sentiment']:.3f}
News Count: {result['news_count']}
""")
```

---

## パフォーマンス最適化

### 1. データベースインデックス

```sql
-- ニュースクエリ最適化
CREATE INDEX idx_stock_news_symbol_date
ON stock_news(symbol, published_at DESC);

-- 価格データクエリ最適化
CREATE INDEX idx_stock_prices_symbol_date
ON stock_prices(symbol, date DESC);

-- 予測データクエリ最適化
CREATE INDEX idx_ensemble_predictions_symbol_date
ON ensemble_predictions(symbol, prediction_date DESC);
```

### 2. バッチ処理最適化

```python
# 並列処理でニュース収集
from concurrent.futures import ThreadPoolExecutor

def collect_news_parallel(symbols, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(collect_jp_news_yfinance, conn, symbol)
            for symbol in symbols
        ]
        results = [future.result() for future in futures]
    return results
```

### 3. キャッシング戦略

```python
from functools import lru_cache
from datetime import date

@lru_cache(maxsize=1000)
def get_cached_news_features(symbol: str, target_date: date):
    """キャッシュ付きニュース特徴量取得"""
    extractor = NewsFeatureExtractor(db_config)
    return extractor.extract_sentiment_features(
        symbol,
        datetime.combine(target_date, datetime.min.time())
    )
```

---

## トラブルシューティング

### 問題1: ニュースデータがない

**症状**: `news_count: 0`

**解決策**:
1. ニュース収集を実行
2. 別のニュースソースを試す
3. lookback_days を延長

### 問題2: 予測精度が低い

**症状**: `confidence < 0.6`

**解決策**:
1. より多くの学習データを収集
2. エポック数を増やす
3. ハイパーパラメータ調整

### 問題3: メモリ不足

**症状**: OOM エラー

**解決策**:
1. batch_size を減らす
2. price_sequence_length を短縮
3. 並列処理の max_workers を減らす

---

## ベストプラクティス

### 1. データ品質管理

- 定期的なニュース更新（毎日）
- 古いニュースの削除（90日以上）
- データの整合性チェック

### 2. モデル管理

- 定期的な再学習（月次）
- バージョン管理
- A/Bテスト実施

### 3. 監視とログ

- 予測精度の追跡
- エラーログの監視
- パフォーマンスメトリクスの収集

---

## まとめ

このシステムにより、以下が実現されました：

✅ **ニュースデータのAI学習統合**
✅ **9次元センチメント特徴量**
✅ **ハイブリッドLSTMモデル**
✅ **REST API経由の簡単アクセス**
✅ **包括的なドキュメント**

**次のステップ:**
1. 本番データでの学習実行
2. 予測精度の評価
3. 継続的な改善

---

**作成日**: 2025-10-12
**バージョン**: 1.0.0
**著者**: Claude (AI Assistant)
