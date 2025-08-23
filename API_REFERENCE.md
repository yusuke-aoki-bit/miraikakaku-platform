# Miraikakaku API リファレンス

## 🌐 Base URL
```
https://miraikakaku-api-fastapi-465603676610.us-central1.run.app
```

## 📋 エンドポイント一覧

### ヘルスチェック
- `GET /health` - システム稼働状況確認

### ドキュメント
- `GET /docs` - Swagger UI (インタラクティブAPIドキュメント)
- `GET /redoc` - ReDoc形式APIドキュメント

## 📈 株式データAPI

### 価格データ
```http
GET /api/finance/stocks/{symbol}/price?limit={limit}
```
**Parameters:**
- `symbol`: 銘柄コード (例: "1401", "AAPL")
- `limit`: 取得件数 (オプション, デフォルト: 20)

**Response:**
```json
[
  {
    "symbol": "1401",
    "date": "2025-08-22T00:00:00",
    "open_price": 1410.0,
    "high_price": 1423.0,
    "low_price": 1388.0,
    "close_price": 1405.0,
    "volume": 24100,
    "data_source": "database"
  }
]
```

### 予測データ
```http
GET /api/finance/stocks/{symbol}/predictions?limit={limit}&model_type={model}
```
**Parameters:**
- `symbol`: 銘柄コード
- `limit`: 取得件数 (オプション, デフォルト: 30) 
- `model_type`: モデル種別 (オプション)

**Response:**
```json
[
  {
    "symbol": "1401",
    "prediction_date": "2025-09-23T00:00:00",
    "predicted_price": 1410.0072,
    "confidence_score": 0.3,
    "model_type": "CONTINUOUS_247_V1",
    "prediction_horizon": 30,
    "is_active": true
  }
]
```

### 銘柄検索
```http
GET /api/finance/stocks/search?query={query}&limit={limit}
```
**Parameters:**
- `query`: 検索キーワード (銘柄コードまたは企業名)
- `limit`: 取得件数 (オプション, デフォルト: 10)

**Response:**
```json
[
  {
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "exchange": "NASDAQ",
    "sector": "Technology",
    "industry": null
  }
]
```

### 利用可能銘柄一覧
```http
GET /api/finance/v2/available-stocks?limit={limit}&offset={offset}
```
**Parameters:**
- `limit`: 取得件数 (オプション, デフォルト: 100)
- `offset`: オフセット (オプション, デフォルト: 0)

**Response:**
```json
{
  "count": 5,
  "stocks": [
    {
      "symbol": "1401",
      "name": "mbs,inc.",
      "market": "グロース",
      "country": "Japan"
    }
  ]
}
```

## 🤖 AI機能API

### AI決定要因
```http
GET /api/ai-factors/all?limit={limit}&offset={offset}
```
**Parameters:**
- `limit`: 取得件数 (オプション, デフォルト: 100)
- `offset`: オフセット (オプション, デフォルト: 0)

**Response:**
```json
[
  {
    "id": 31647,
    "factor_type": "pattern",
    "factor_name": "Chart",
    "influence_score": 85.56,
    "description": "IBHHのチャートパターン",
    "confidence": 76.05,
    "created_at": "2025-08-23T20:40:51"
  }
]
```

### 銘柄別AI決定要因
```http
GET /api/ai-factors/symbol/{symbol}?limit={limit}
```

### 強化予測（AI決定要因付き）
```http
GET /api/stocks/{symbol}/predictions/enhanced?limit={limit}
```

## 💡 テーマ洞察API

### テーマ一覧
```http
GET /api/insights/themes
```
**Response:**
```json
[
  "AI革命加速 #1",
  "5G普及加速 #1",
  "EV革命本格化 #1",
  ...
]
```

### テーマ詳細
```http
GET /api/insights/themes/{theme_name}?limit={limit}
```
**Response:**
```json
[
  {
    "id": 6,
    "theme_name": "AI革命加速 #1",
    "theme_category": "technology",
    "insight_date": "2025-07-31",
    "title": "AIの商業化が急速に進展 - Week 1",
    "summary": "人工知能技術の実用化が様々な産業で加速している...",
    "key_metrics": {
      "growth_rate": 57.4,
      "adoption_rate": 46.6,
      "investment_increase": 38.8,
      "market_size_billion": 70.9
    },
    "related_symbols": {
      "primary": ["ORCL", "AAPL", "MSFT"],
      "secondary": ["AAPL", "ORCL"],
      "weight": [0.51, 0.41, 0.45]
    },
    "trend_direction": "bullish",
    "impact_score": 89.9,
    "created_at": "2025-08-23T16:01:43"
  }
]
```

## 👤 ユーザーAPI

### ユーザープロファイル
```http
GET /api/users/{user_id}/profile
```
**Note**: 現在はモック実装

**Response:**
```json
{
  "id": 1,
  "user_id": "test123",
  "username": "user_test123",
  "email": "test123@example.com",
  "investment_style": "moderate",
  "risk_tolerance": "medium",
  "investment_experience": "beginner",
  "preferred_sectors": ["Technology", "Healthcare"],
  "investment_goals": "Long-term growth",
  "total_portfolio_value": 100000.0,
  "created_at": "2025-08-23T21:04:37.967420",
  "updated_at": "2025-08-23T21:04:37.967425"
}
```

## 📊 テスト用エンドポイント

### 主要指数データ
```http
GET /api/finance/test/indices/{symbol}?days={days}
```
**Symbols**: nikkei, topix, dow, sp500

### 主要指数予測
```http
GET /api/finance/test/indices/{symbol}/predictions?days={days}
```

## 🔧 エラーレスポンス

### 標準エラー形式
```json
{
  "detail": "エラーメッセージ"
}
```

### 一般的なHTTPステータスコード
- `200` - 成功
- `404` - リソースが見つからない
- `422` - バリデーションエラー
- `500` - サーバー内部エラー

## 📋 データ型定義

### Investment Style
- `conservative` - 保守的
- `moderate` - 中庸
- `aggressive` - 積極的
- `growth` - 成長重視
- `value` - バリュー重視

### Risk Tolerance
- `low` - 低リスク
- `medium` - 中リスク
- `high` - 高リスク

### Factor Type
- `technical` - テクニカル分析
- `fundamental` - ファンダメンタル分析
- `sentiment` - センチメント分析
- `news` - ニュース分析
- `pattern` - パターン分析

### Theme Category
- `technology` - テクノロジー
- `energy` - エネルギー
- `finance` - 金融
- `healthcare` - ヘルスケア
- `consumer` - 消費者
- `industrial` - 産業
- `materials` - 素材

### Trend Direction
- `bullish` - 強気
- `bearish` - 弱気
- `neutral` - 中立

## 🚀 レスポンス最適化のヒント

1. **ページネーション**: `limit`と`offset`パラメータを活用
2. **フィルタリング**: 必要なデータのみを指定して取得
3. **キャッシュ**: 静的データは適切にキャッシュ
4. **並列リクエスト**: 関連性の低いデータは並列取得

---

*最終更新: 2025-08-23 21:00 JST*
*API Version: v1.0*