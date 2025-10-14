# ニュースセンチメント分析 - クイックスタートガイド

**所要時間**: 15分
**前提条件**: Cloud Runデプロイ完了、Alpha Vantage APIキー取得済み

---

## 📌 3ステップで開始

### ステップ1: データベーススキーマ適用 (1分)

APIエンドポイントを使用してスキーマを適用:

```bash
curl -X POST https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/apply-news-schema
```

**成功レスポンス例**:
```json
{
  "status": "success",
  "message": "News sentiment schema applied successfully",
  "tables_created": [
    "news_analysis_log",
    "stock_news",
    "stock_sentiment_summary"
  ],
  "columns_added": [
    "news_impact",
    "news_sentiment",
    "sentiment_adjusted_prediction"
  ]
}
```

---

### ステップ2: ニュースデータ収集 (5-10分)

Alpha Vantage APIキーを設定して実行:

```bash
# .envファイルにAPIキーを追加
echo "ALPHA_VANTAGE_API_KEY=your_api_key_here" >> .env

# ニュース収集実行（テスト: 10銘柄）
python news_sentiment_analyzer.py
```

**期待される出力**:
```
================================================================================
ニュースセンチメント分析システム
================================================================================

対象銘柄数: 10

[1/10] 9984.T - SoftBank Group Corp.
  ニュース: 8件保存
  センチメント: bullish (スコア: 0.452, 強度: 0.452)
  内訳: Pos:5 Neg:2 Neu:1

[2/10] 7203.T - Toyota Motor Corp.
  ニュース: 6件保存
  センチメント: neutral (スコア: 0.089, 強度: 0.089)
  内訳: Pos:3 Neg:2 Neu:1

...

処理完了
対象銘柄: 10
ニュース取得: 56件
ニュース保存: 48件
センチメント計算: 8銘柄
```

---

### ステップ3: センチメント統合予測生成 (3-5分)

ニュースセンチメントを統合した予測を生成:

```bash
python generate_sentiment_enhanced_predictions.py
```

**期待される出力**:
```
================================================================================
センチメント強化アンサンブル予測生成
================================================================================

1. アクティブ銘柄とセンチメント取得
対象銘柄数: 250
センチメントデータあり: 8銘柄

2. 予測生成（センチメント統合）
処理中: 10/250 (9984.T)
処理中: 20/250 (7203.T)
...

3. 処理結果
予測生成: 1000件
センチメント調整あり: 32件
平均調整: +1.25%
最大調整: +3.45%
最小調整: -2.10%

4. センチメント調整例

9984.T - SoftBank Group Corp.
  センチメント: +0.452 (bullish, 8件)
  基本予測: 10,500円
  調整後: 10,689円 (+1.80%)

7203.T - Toyota Motor Corp.
  センチメント: +0.089 (neutral, 6件)
  基本予測: 2,450円
  調整後: 2,459円 (+0.37%)
```

---

## ✅ 動作確認

### 1. データベース確認

```sql
-- ニュースが保存されているか
SELECT COUNT(*), symbol
FROM stock_news
GROUP BY symbol
ORDER BY COUNT DESC
LIMIT 10;

-- センチメントサマリー確認
SELECT *
FROM stock_sentiment_summary
WHERE date = CURRENT_DATE
LIMIT 10;

-- 予測にセンチメントが統合されているか
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

### 2. ビューの確認

```sql
-- 最新ニュースセンチメント
SELECT * FROM latest_news_sentiment LIMIT 10;

-- センチメント強化予測
SELECT * FROM sentiment_enhanced_predictions LIMIT 10;
```

---

## 🎯 実用例

### 例1: 強気ニュース多数の場合

**銘柄**: 9984.T (SoftBank Group)
**ニュース**: 15件
**センチメント**: +0.65 (強気)

**計算**:
```
volume_factor = min(15 / 20.0, 0.5) = 0.50
news_impact = 0.65 * 0.50 = 0.325
adjustment = 0.65 * 0.325 * 0.10 = 0.021125 (2.11%)

基本予測: 10,500円
調整後: 10,500 * (1 + 0.021125) = 10,722円 (+2.11%)
```

### 例2: 弱気ニュース中程度の場合

**銘柄**: 8306.T (三菱UFJ)
**ニュース**: 8件
**センチメント**: -0.35 (弱気)

**計算**:
```
volume_factor = min(8 / 20.0, 0.5) = 0.40
news_impact = 0.35 * 0.40 = 0.14
adjustment = -0.35 * 0.14 * 0.10 = -0.0049 (-0.49%)

基本予測: 1,200円
調整後: 1,200 * (1 - 0.0049) = 1,194円 (-0.49%)
```

### 例3: 中立・ニュース少数の場合

**銘柄**: 6758.T (Sony)
**ニュース**: 3件
**センチメント**: +0.12 (中立)

**計算**:
```
volume_factor = min(3 / 20.0, 0.5) = 0.15
news_impact = 0.12 * 0.15 = 0.018
adjustment = 0.12 * 0.018 * 0.10 = 0.000216 (0.02%)

基本予測: 12,500円
調整後: 12,500 * (1 + 0.000216) = 12,503円 (+0.02%)
```

---

## 🔄 日次運用

### 推奨スケジュール

```yaml
# Cloud Scheduler設定

# 1. ニュース収集ジョブ
- name: news-collector-daily
  schedule: "0 6 * * *"  # 毎日午前6時
  timezone: Asia/Tokyo
  command: python news_sentiment_analyzer.py
  timeout: 30m

# 2. センチメント統合予測ジョブ
- name: sentiment-predictions-daily
  schedule: "0 7 * * *"  # 毎日午前7時
  timezone: Asia/Tokyo
  command: python generate_sentiment_enhanced_predictions.py
  timeout: 30m
```

### 手動実行

```bash
# 全銘柄のニュース収集（60分）
python news_sentiment_analyzer.py

# センチメント統合予測生成（30分）
python generate_sentiment_enhanced_predictions.py
```

---

## 📊 パフォーマンスモニタリング

### KPI

```sql
-- 1. ニュース収集率
SELECT
    COUNT(DISTINCT sn.symbol) * 100.0 / COUNT(DISTINCT sm.symbol) as coverage_percent
FROM stock_master sm
LEFT JOIN stock_news sn ON sm.symbol = sn.symbol
WHERE sm.is_active = TRUE
  AND sn.published_at >= CURRENT_DATE - INTERVAL '7 days';

-- 2. センチメント分布
SELECT
    sentiment_trend,
    COUNT(*) as count,
    AVG(avg_sentiment) as avg_score
FROM stock_sentiment_summary
WHERE date = CURRENT_DATE
GROUP BY sentiment_trend;

-- 3. 調整幅の統計
SELECT
    COUNT(*) as total,
    AVG((sentiment_adjusted_prediction - ensemble_prediction) / ensemble_prediction * 100) as avg_adj,
    MAX((sentiment_adjusted_prediction - ensemble_prediction) / ensemble_prediction * 100) as max_adj,
    MIN((sentiment_adjusted_prediction - ensemble_prediction) / ensemble_prediction * 100) as min_adj
FROM ensemble_predictions
WHERE prediction_date >= CURRENT_DATE
  AND news_sentiment IS NOT NULL;
```

---

## ❓ FAQ

### Q1: APIキーはどこで取得？
**A**: https://www.alphavantage.co/support/#api-key
無料版は5リクエスト/分、500リクエスト/日。

### Q2: 全銘柄処理にどれくらいかかる？
**A**: 約30-60分 (2000銘柄、API制限考慮済み)。

### Q3: 日本株のニュースは取得できる？
**A**: はい。Alpha VantageはTokyoを含む主要取引所をカバー。ただし英語ニュース中心。

### Q4: センチメント調整の上限は？
**A**: ±10% (現在価格から±30%内に制限)。

### Q5: リアルタイム更新は可能？
**A**: 現在は日次バッチ。Phase 2でWebSocket対応予定。

---

## 🚀 次のステップ (Phase 2)

1. **LLMセンチメント分析**: Transformersモデル活用
2. **イベント検出**: 決算、M&A、規制変更の自動検出
3. **ソーシャルメディア統合**: Twitter/X, Reddit
4. **リアルタイム更新**: WebSocket経由
5. **多言語対応**: 日本語ニュース対応

---

**作成日**: 2025-10-11
**バージョン**: 1.0
**ステータス**: 本番環境対応可能
