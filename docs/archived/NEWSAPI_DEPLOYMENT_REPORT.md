# NewsAPI.org デプロイ & テストレポート
2025-10-12

## 📊 実行サマリー

### デプロイ状況
- **ステータス**: ✅ **SUCCESS**
- **リビジョン**: miraikakaku-api-00083-6kl
- **デプロイ時刻**: 2025-10-12
- **環境変数**: NEWSAPI_KEY設定済み

### テスト状況
- **ステータス**: ⚠️ **ISSUE FOUND**
- **問題**: APIからニュース0件返却
- **根本原因**: コード内のロジック問題（APIキー自体は正常動作）

---

## ✅ 成功した項目

### 1. ビルド
- **ビルドID**: 3956287e-36bf-43a8-beaf-705b2a0e227c
- **ステータス**: SUCCESS
- **所要時間**: 3分38秒
- **イメージ**: gcr.io/pricewise-huqkr/miraikakaku-api:latest

### 2. デプロイ
- **リビジョン**: 00083-6kl
- **トラフィック**: 100%
- **URL**: https://miraikakaku-api-465603676610.us-central1.run.app
- **環境変数**: NEWSAPI_KEY=9223124674e248adaa667c76606cd12a

### 3. NewsAPI.org動作確認
- **直接API**: ✅ 正常動作
- **トヨタ記事**: 395件取得成功
- **レスポンス**: 正常

---

## ⚠️ 発見された問題

### 問題: ニュース0件返却

#### テスト結果
```bash
# トヨタ自動車
curl -X POST ".../admin/collect-news-newsapi?symbol=7203.T&company_name=Toyota&days=7"
→ "articles_found":0

# ソニー
curl -X POST ".../admin/collect-news-newsapi?symbol=6758.T&company_name=Sony&days=7"
→ "articles_found":0

# ソフトバンク
curl -X POST ".../admin/collect-news-newsapi?symbol=9984.T&company_name=SoftBank&days=7"
→ "articles_found":0
```

#### 検証: NewsAPI.org直接テスト
```bash
curl "https://newsapi.org/v2/everything?q=Toyota&language=en&pageSize=5&from=2025-10-05&apiKey=***"
→ "totalResults":395 ✅ 成功
```

#### 結論
- **APIキー**: ✅ 正常
- **NewsAPI.org**: ✅ 正常動作（395件取得可能）
- **問題箇所**: ❌ `newsapi_collector.py`内のロジック

---

## 🔍 原因分析

### 推定原因

#### 1. from/to日付範囲の問題
```python
# newsapi_collector.py内
from_date = to_date - timedelta(days=days)
params = {
    'from': from_date.strftime('%Y-%m-%d'),
    'to': to_date.strftime('%Y-%m-%d'),
}
```

**問題点**: 無料プランは過去1ヶ月のみアクセス可能

#### 2. クエリパラメータの問題
```python
params = {
    'q': f'{company_name} OR {symbol}',  # 例: "Toyota OR 7203.T"
    'language': language,
}
```

**問題点**: 銘柄コード（7203.T）が記事に含まれることは稀

#### 3. APIレスポンス処理の問題
```python
if response.status_code == 200:
    data = response.json()
    articles = data.get('articles', [])
    return articles
```

**問題点**: エラーハンドリングが不十分

---

## 🛠️ 修正提案

### 修正1: クエリを企業名のみに変更
```python
# Before
params = {'q': f'{company_name} OR {symbol}'}

# After
params = {'q': company_name}  # シンプルに企業名のみ
```

### 修正2: 日付範囲を最近1週間に限定
```python
# Before
from_date = to_date - timedelta(days=days)

# After
from_date = max(to_date - timedelta(days=days), to_date - timedelta(days=30))
# 無料プランの1ヶ月制限を考慮
```

### 修正3: デバッグログ追加
```python
logger.info(f"Query params: {params}")
logger.info(f"API Response status: {response.status_code}")
logger.info(f"API Response: {response.text[:200]}")
```

---

## 📈 次のアクション

### 即座に実施（30分）

#### ステップ1: コード修正（10分）
```python
# newsapi_collector.pyの修正
def get_company_news(self, company_name: str, symbol: str, days: int = 7):
    # 日付範囲（無料プランは30日まで）
    to_date = datetime.now()
    from_date = max(
        to_date - timedelta(days=days),
        to_date - timedelta(days=30)
    )

    # クエリをシンプルに
    params = {
        'q': company_name,  # 企業名のみ
        'language': 'en',    # 英語記事
        'sortBy': 'publishedAt',
        'from': from_date.strftime('%Y-%m-%d'),
        'to': to_date.strftime('%Y-%m-%d'),
        'pageSize': 100
    }

    # デバッグログ
    logger.info(f"Fetching news for {company_name} with params: {params}")

    response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)

    logger.info(f"Response status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        logger.info(f"Total results: {data.get('totalResults', 0)}")
        return data.get('articles', [])
```

#### ステップ2: テスト（5分）
```bash
# ローカルでテスト
python newsapi_collector.py
```

#### ステップ3: ビルド & デプロイ（15分）
```bash
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api
gcloud run services update miraikakaku-api --image gcr.io/pricewise-huqkr/miraikakaku-api:latest --region us-central1
```

---

## 📊 現在の状況

### Phase 3 進捗
- ✅ NewsAPI.org統合実装
- ✅ ビルド成功
- ✅ デプロイ成功
- ⚠️ **コードバグ発見**（修正必要）
- ⏳ 再テスト
- ⏳ 日本株ニュース収集実現

### システム状態
- **Cloud Run**: リビジョン00083-6kl稼働中
- **APIキー**: 正常動作確認済み
- **NewsAPI.org**: 395件記事取得可能
- **課題**: コード内ロジック修正必要

---

## 🎯 期待される修正後の効果

### Before（現状）
- API呼び出し: ✅ 成功
- 記事取得: ❌ 0件

### After（修正後）
- API呼び出し: ✅ 成功
- 記事取得: ✅ 30-50件/銘柄

### 予測への影響
- 修正後、日本株ニュース統合予測が可能に
- 予測信頼度: 60-70% → 90%+（推定）

---

## 📝 学んだ教訓

### 1. テスト駆動開発の重要性
- コード実装前に直接APIテストを実施すべきだった
- ローカルでの単体テスト実施が重要

### 2. デバッグログの重要性
- 本番環境でのデバッグが困難
- 詳細なロギングを最初から実装すべき

### 3. APIドキュメント熟読
- NewsAPI.org無料プランの制限（30日）を見落とし
- クエリパラメータの最適化が必要

---

## 🏆 今日の成果

### Phase 1-3 総合
| Phase | 達成率 | 主要成果 |
|---|---|---|
| Phase 1 | 83% | ニュース強化予測システム稼働 |
| Phase 2 | 100% | 自動化・最適化完了 |
| Phase 3 | 40% | NewsAPI統合・デプロイ完了、バグ発見 |

### 全体達成度: 74%

---

## 🔄 次のセッション

### 優先タスク（30分）
1. newsapi_collector.py修正（10分）
2. ローカルテスト（5分）
3. ビルド & デプロイ（15分）
4. 日本株3銘柄でテスト（5分）

### 成功の定義
- トヨタ: 30+件
- ソニー: 20+件
- ソフトバンク: 25+件

---

**レポート作成日**: 2025-10-12
**デプロイリビジョン**: 00083-6kl
**問題**: コード内ロジック
**次のステップ**: newsapi_collector.py修正 & 再デプロイ
