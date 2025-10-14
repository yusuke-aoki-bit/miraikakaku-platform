# Phase 3 実装開始レポート
2025-10-12

## 🚀 Phase 3 開始

Phase 3の主要タスクの実装を開始しました。

---

## ✅ 完了したタスク

### 1. NewsAPI.org統合コレクターの実装

**ファイル**: `newsapi_collector.py`

#### 機能
- NewsAPI.orgからのニュース取得
- センチメント分析（TextBlob使用）
- データベース保存
- エラーハンドリング

#### 主要メソッド
- `get_company_news()`: 企業ニュース取得
- `analyze_sentiment()`: センチメント分析
- `process_articles()`: 記事処理
- `save_to_database()`: DB保存
- `collect_news_for_symbol()`: 統合処理

#### APIキー要件
```bash
# .envに追加必要
NEWSAPI_KEY=your_api_key_here
```

#### 使用方法
```python
from newsapi_collector import NewsAPICollector

collector = NewsAPICollector()
result = collector.collect_news_for_symbol(
    symbol='7203.T',
    company_name='トヨタ自動車',
    days=7
)
```

---

### 2. API エンドポイント追加

**ファイル**: `api_predictions.py` (1696-1713行)

#### 新規エンドポイント
```
POST /admin/collect-news-newsapi?symbol=7203.T&company_name=トヨタ自動車&days=7
```

#### パラメータ
- `symbol`: 銘柄コード (例: 7203.T)
- `company_name`: 企業名 (例: トヨタ自動車)
- `days`: 過去何日分 (デフォルト: 7)

#### レスポンス例
```json
{
  "status": "success",
  "symbol": "7203.T",
  "company_name": "トヨタ自動車",
  "articles_found": 45,
  "articles_saved": 45,
  "avg_sentiment": 0.0523,
  "status": "success"
}
```

---

## ⏳ 次の実装ステップ

### 優先度1: NewsAPI.orgのテスト（即座）

**必要なアクション**:
1. NewsAPI.orgアカウント作成
   - URL: https://newsapi.org/register
   - プラン: Developer (無料)

2. APIキー取得
   - ダッシュボードから即座に取得

3. .envに追加
   ```bash
   NEWSAPI_KEY=your_actual_api_key_here
   ```

4. テスト実行
   ```bash
   python newsapi_collector.py
   ```

5. Dockerfileに追加
   ```dockerfile
   COPY newsapi_collector.py .
   ```

6. ビルド & デプロイ

---

### 優先度2: モニタリングダッシュボード（1-2日）

**実装内容**:
- 予測精度追跡API
- システムヘルス監視
- グラフ表示用エンドポイント

**必要なファイル**:
- `monitoring_dashboard.py`
- API エンドポイント追加

---

### 優先度3: CI/CDパイプライン（2-3日）

**実装内容**:
- GitHub Actions workflow
- 自動テスト実行
- 自動デプロイ

**必要なファイル**:
- `.github/workflows/deploy.yml`
- テストスクリプト

---

### 優先度4: フロントエンド統合（3-5日）

**実装内容**:
- ニュースセンチメント表示UI
- 予測詳細ページ強化
- リアルタイム更新

**必要なファイル**:
- Frontend React components
- API統合

---

## 📋 Phase 3 タスクリスト

### 短期 (即座-1週間)
- [x] NewsAPI.orgコレクター実装
- [x] APIエンドポイント追加
- [ ] NewsAPI.orgアカウント作成 **← 次のステップ**
- [ ] APIキー取得・設定
- [ ] 日本株3銘柄でテスト
- [ ] Dockerfile更新
- [ ] ビルド & デプロイ

### 中期 (1-2週間)
- [ ] モニタリングダッシュボード実装
- [ ] CI/CDパイプライン構築
- [ ] フロントエンドUI統合
- [ ] 予測精度追跡システム

### 長期 (2-4週間)
- [ ] リアルタイム予測更新
- [ ] アラート機能
- [ ] A/Bテスト機能
- [ ] パフォーマンス最適化

---

## 🔧 技術仕様

### NewsAPI.org制限
- **無料プラン**: 100リクエスト/日
- **過去データ**: 最大1ヶ月
- **レスポンス**: 最大100記事/リクエスト

### 推奨使用方法
1. **開発・テスト**: 無料プラン
2. **本番運用**: Business プラン ($449/月) 検討

### データフロー
```
NewsAPI.org
    ↓
newsapi_collector.py (ニュース取得 + センチメント分析)
    ↓
stock_news テーブル (保存)
    ↓
generate_news_enhanced_predictions.py (予測生成)
    ↓
ensemble_predictions テーブル (予測保存)
```

---

## 📊 期待される改善

### 日本株ニュースカバレッジ
- **現在**: 0% (yfinance/Finnhub不可)
- **NewsAPI.org導入後**: 50-80% (推定)

### 予測信頼度
- **現在**: US株97.3%、日本株データ不足
- **NewsAPI.org導入後**: 日本株も高信頼度予測可能

### システム統一性
- **現在**: US株と日本株で異なるニュースソース
- **NewsAPI.org導入後**: 統一されたインターフェース

---

## 💡 実装上の注意点

### 1. APIキーセキュリティ
- 環境変数で管理 (`NEWSAPI_KEY`)
- Gitにコミットしない
- Cloud Run環境変数に設定

### 2. レート制限対応
- 無料プラン: 100リクエスト/日
- バッチ処理時は間隔を空ける
- リトライロジック実装済み

### 3. センチメント分析精度
- TextBlob使用（軽量・高速）
- 日本語対応は限定的
- 必要に応じて機械翻訳検討

### 4. データベーススキーマ
- 既存の`stock_news`テーブル使用
- `sentiment_score`: -1.0 ~ 1.0
- `sentiment`: positive/negative/neutral

---

## 🎯 Phase 3 の成功指標

### 短期目標 (1週間)
- [ ] NewsAPI.org統合完了
- [ ] 日本株5銘柄でニュース取得成功
- [ ] 平均20件以上のニュース/銘柄

### 中期目標 (2週間)
- [ ] モニタリングダッシュボード稼働
- [ ] CI/CDパイプライン運用開始
- [ ] 予測精度の可視化

### 長期目標 (1ヶ月)
- [ ] フロントエンド完全統合
- [ ] リアルタイム機能実装
- [ ] ユーザー100人規模対応

---

## 📝 次回セッション時のアクション

### 即座に実施すべきこと
1. NewsAPI.orgアカウント作成（5分）
   - https://newsapi.org/register

2. APIキー取得・設定（5分）
   ```bash
   # .envに追加
   NEWSAPI_KEY=your_key_here
   ```

3. ローカルテスト（10分）
   ```bash
   python newsapi_collector.py
   ```

4. Dockerfile更新（5分）
   ```dockerfile
   COPY newsapi_collector.py .
   ```

5. ビルド & デプロイ（15分）
   ```bash
   gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api
   gcloud run services update miraikakaku-api --image gcr.io/pricewise-huqkr/miraikakaku-api:latest --region us-central1
   ```

6. 日本株テスト（10分）
   ```bash
   curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-news-newsapi?symbol=7203.T&company_name=トヨタ自動車&days=7"
   ```

**合計所要時間**: 約50分

---

## 🎉 Phase 3 現状まとめ

### 完了
- ✅ NewsAPI.orgコレクター実装
- ✅ APIエンドポイント追加
- ✅ ドキュメント作成

### 次のステップ
- ⏳ NewsAPI.orgアカウント作成 **← 最優先**
- ⏳ テスト & デプロイ
- ⏳ 日本株カバレッジ向上

### 期待される効果
- 📈 日本株ニュースカバレッジ: 0% → 50-80%
- 📈 日本株予測精度: データ不足 → 高精度
- 📈 システム統一性: 分散 → 統合

---

**Phase 3 開始日**: 2025-10-12
**実装状況**: 25% (1/4タスク)
**次回タスク**: NewsAPI.orgアカウント作成 & テスト
