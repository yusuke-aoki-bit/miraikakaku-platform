# データ問題診断レポート - 2025年10月14日

## エグゼクティブサマリー

Miraikakakuシステムで2つの重要な問題が発見されました:

1. **株価データが4日古い** - 最新データ: 10/10、現在: 10/14
2. **予測が過去のボラティリティに対して平坦すぎる** - 実際の価格変動を反映していない

## 問題1: データ遅延 (4日)

### 現状
```
最新データ日付: 2025-10-10
現在日付: 2025-10-14
遅延: 4日間

サンプル銘柄:
- AAPL: 2025-10-08
- TSLA: 2025-10-08
- 7203.T (トヨタ): 2025-10-09
- 9984.T (ソフトバンク): 2025-10-09
```

### 影響
- ユーザーが見ている価格が最大4日古い
- 予測の基準となるデータが古いため、予測精度が低下
- リアルタイム性が求められる株価アプリとして致命的

### 解決策

#### 即時対応: 手動データ更新
```bash
# yfinanceを使った最新データ取得
python update_stock_prices_now.py
```

#### 恒久対応: 自動更新の設定
1. **Cloud Scheduler設定** (毎日市場終了後に実行)
2. **GitHub Actions** (バックアップ)
3. **監視アラート** (データが2日以上古くなったら通知)

## 問題2: 予測の平坦化

### 問題の詳細

過去90日間の実績データと予測を比較すると、予測がトレンドラインを追うだけで、
実際の株価が持つ「日々の変動(ボラティリティ)」を反映していない可能性があります。

#### 典型的な症状:
```
実績データ:
AAPL: $150 → $152 → $148 → $153 → $149 → $155  (変動大)

現在の予測:
AAPL: $150 → $150.5 → $151 → $151.5 → $152 → $152.5  (平坦)
```

### 原因

現在の`generate_ensemble_predictions.py`が:
1. **線形トレンドのみを重視**
2. **過去のボラティリティを無視**
3. **ノイズ成分を追加していない**
4. **信頼区間がない**

### 解決策

#### 1. ボラティリティ適応型予測の実装

```python
# 履歴ボラティリティを計算
historical_volatility = calculate_volatility(historical_prices, window=30)

# 予測にボラティリティを反映
for i in range(prediction_days):
    trend_prediction = base_prediction + trend * i

    # ボラティリティに基づくノイズを追加
    noise = np.random.normal(0, historical_volatility * base_prediction)

    final_prediction = trend_prediction + noise
```

#### 2. 信頼区間付き予測

```python
# 上限・下限を含む予測
predictions = {
    'prediction': base_value,
    'upper_bound': base_value * (1 + volatility * 1.96),  # 95%信頼区間
    'lower_bound': base_value * (1 - volatility * 1.96),
    'confidence': calculate_confidence(historical_accuracy)
}
```

#### 3. 複数シナリオ予測

```python
scenarios = {
    'optimistic': trend + (volatility * 1.5),
    'base': trend,
    'pessimistic': trend - (volatility * 1.5)
}
```

## 実装計画

### Phase 1: データ更新 (所要時間: 30分)

1. ✅ 現状診断完了
2. ⏳ 最新データ取得スクリプト実行
3. ⏳ データ更新確認
4. ⏳ 自動更新スケジューラー設定

### Phase 2: 予測改善 (所要時間: 2時間)

1. ⏳ `generate_ensemble_predictions.py`を修正
   - ボラティリティ計算追加
   - ノイズ成分追加
   - 信頼区間計算

2. ⏳ 新しい予測を生成

3. ⏳ A/Bテスト
   - 旧予測 vs 新予測の比較
   - ボラティリティ比率の確認

4. ⏳ デプロイ
   - Backend API更新
   - Frontend表示更新

### Phase 3: 監視強化 (所要時間: 1時間)

1. ⏳ データ新鮮度監視
2. ⏳ 予測品質メトリクス
3. ⏳ アラート設定

## 次のステップ

### 今すぐ実行:
```bash
# 1. 最新データ取得
python update_stock_prices_now.py

# 2. 改善された予測生成
python generate_improved_ensemble_predictions.py

# 3. デプロイ
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api
gcloud run deploy miraikakaku-api --image gcr.io/pricewise-huqkr/miraikakaku-api:latest
```

### 今週中に実装:
- Cloud Schedulerによる自動データ更新
- 予測品質ダッシュボード
- リアルタイム監視システム

## 期待される改善

### データ更新後:
- ✅ 最新の株価情報をユーザーに提供
- ✅ 予測の基準データが最新
- ✅ システムの信頼性向上

### 予測改善後:
- ✅ 実際のボラティリティを反映した予測
- ✅ 信頼区間によるリスク可視化
- ✅ ユーザーの意思決定サポート向上

## 付録: 技術詳細

### 使用するライブラリ
- `yfinance`: 最新データ取得
- `numpy`: ボラティリティ計算
- `pandas`: データ処理

### データベーススキーマ拡張
```sql
ALTER TABLE ensemble_predictions
ADD COLUMN upper_bound DECIMAL(12,2),
ADD COLUMN lower_bound DECIMAL(12,2),
ADD COLUMN volatility_used DECIMAL(8,4),
ADD COLUMN confidence_score DECIMAL(5,4);
```

### APIレスポンス拡張
```json
{
  "symbol": "AAPL",
  "predictions": [
    {
      "date": "2025-10-15",
      "price": 152.50,
      "upper_bound": 155.30,
      "lower_bound": 149.70,
      "confidence": 0.85
    }
  ]
}
```

---

**作成日時**: 2025年10月14日
**作成者**: Claude (診断システム)
**優先度**: 🔴 High
**ステータス**: 対応中
