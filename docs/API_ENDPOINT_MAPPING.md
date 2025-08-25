# Miraikakaku API エンドポイント整理・マッピング表

## 概要
フロントエンド（api-client.ts）で使用されるエンドポイントとバックエンド実装状況の完全マッピング

## 1. 実装済みAPI エンドポイント (Backend)

### 基本エンドポイント
| エンドポイント | メソッド | 実装ファイル | 説明 |
|---------------|---------|-------------|------|
| `/` | GET | production_main.py | ルートエンドポイント |
| `/health` | GET | production_main.py | ヘルスチェック |

### 株式・金融データAPI
| エンドポイント | メソッド | 実装ファイル | 説明 |
|---------------|---------|-------------|------|
| `/api/finance/stocks/search` | GET | production_main.py | 株式検索 |
| `/api/finance/stocks/{symbol}/price` | GET | production_main.py | 株価履歴取得 |
| `/api/finance/stocks/{symbol}/predictions` | GET | production_main.py | 株価予測 |
| `/api/finance/stocks/{symbol}/indicators` | GET | production_main.py | テクニカル指標 |
| `/api/finance/rankings/universal` | GET | production_main.py | ユニバーサルランキング |
| `/api/finance/test/indices/{symbol}` | GET | main.py | インデックステストデータ |
| `/api/finance/test/indices/{symbol}/predictions` | GET | main.py | インデックス予測テストデータ |

### WebSocket
| エンドポイント | メソッド | 実装ファイル | 説明 |
|---------------|---------|-------------|------|
| `/ws` | WebSocket | production_main.py | リアルタイム価格配信 |

## 2. フロントエンド使用エンドポイント (Frontend Expected)

### 株式データ関連
| 期待エンドポイント | 使用箇所 | 実装状況 | 差異・備考 |
|------------------|---------|---------|----------|
| `/api/finance/stocks/search` | searchStocks() | ✅ 実装済み | 完全一致 |
| `/api/finance/stocks/{symbol}/price` | getStockPrice() | ✅ 実装済み | パラメータ名: limit → days |
| `/api/finance/stocks/{symbol}/predict` | getStockPredictions() | ❌ 未実装 | `/predictions` は実装済み |
| `/api/finance/stocks/{symbol}/volume` | getStockVolume() | ❌ 未実装 | Volume API未実装 |
| `/api/finance/stocks/{symbol}/volume-predictions` | getVolumePredictions() | ❌ 未実装 | 出来高予測API未実装 |
| `/api/finance/volume-rankings` | getVolumeRankings() | ❌ 未実装 | 出来高ランキング未実装 |
| `/api/finance/sectors` | getSectors() | ❌ 未実装 | セクターAPI未実装 |

### 為替関連
| 期待エンドポイント | 使用箇所 | 実装状況 | 差異・備考 |
|------------------|---------|---------|----------|
| `/api/forex/currency-pairs` | getCurrencyPairs() | ❌ 未実装 | 為替ペア一覧未実装 |
| `/api/forex/currency-rate/{pair}` | getCurrencyRate() | ❌ 未実装 | 為替レート未実装 |
| `/api/forex/currency-history/{pair}` | getCurrencyHistory() | ❌ 未実装 | 為替履歴未実装 |
| `/api/forex/currency-predictions/{pair}` | getCurrencyPredictions() | ❌ 未実装 | 為替予測未実装 |

### AI・予測関連
| 期待エンドポイント | 使用箇所 | 実装状況 | 差異・備考 |
|------------------|---------|---------|----------|
| `/api/predictions/featured` | getFeaturedPredictions() | ❌ 未実装 | 注目予測未実装 |
| `/api/predictions/{prediction_id}/factors` | getPredictionFactors() | ❌ 未実装 | AI判断根拠未実装 |
| `/api/ai-factors/all` | getAllAIFactors() | ❌ 未実装 | AI要因一覧未実装 |

### テーマ・インサイト関連
| 期待エンドポイント | 使用箇所 | 実装状況 | 差異・備考 |
|------------------|---------|---------|----------|
| `/api/insights/themes` | getThemes() | ❌ 未実装 | テーマ一覧未実装 |
| `/api/insights/themes/{theme_name}` | getThemeDetails() | ❌ 未実装 | テーマ詳細未実装 |
| `/api/insights/themes/{theme_id}/follow` | followTheme() | ❌ 未実装 | テーマフォロー未実装 |

### コンテスト関連
| 期待エンドポイント | 使用箇所 | 実装状況 | 差異・備考 |
|------------------|---------|---------|----------|
| `/api/contests/stats` | getContestStats() | ❌ 未実装 | コンテスト統計未実装 |
| `/api/contests/active` | getActiveContests() | ❌ 未実装 | アクティブコンテスト未実装 |
| `/api/contests/leaderboard` | getLeaderboard() | ❌ 未実装 | リーダーボード未実装 |
| `/api/contests/{contest_id}/predict` | submitPrediction() | ❌ 未実装 | 予測投稿未実装 |

### ユーザー管理関連
| 期待エンドポイント | 使用箇所 | 実装状況 | 差異・備考 |
|------------------|---------|---------|----------|
| `/api/user/profile` | getUserProfile() | ❌ 未実装 | ユーザープロフィール未実装 |
| `/api/user/watchlist` | getWatchlist() | ❌ 未実装 | ウォッチリスト未実装 |
| `/api/user/2fa/enable` | enable2FA() | ❌ 未実装 | 2FA未実装 |
| `/api/user/notifications` | getNotificationSettings() | ❌ 未実装 | 通知設定未実装 |

### ポートフォリオ関連
| 期待エンドポイント | 使用箇所 | 実装状況 | 差異・備考 |
|------------------|---------|---------|----------|
| `/api/portfolios` | getPortfolios() | ❌ 未実装 | ポートフォリオ一覧未実装 |
| `/api/portfolios/{portfolio_id}` | getPortfolioDetails() | ❌ 未実装 | ポートフォリオ詳細未実装 |
| `/api/portfolios/{portfolio_id}/transactions` | addTransaction() | ❌ 未実装 | 取引記録未実装 |

### ニュース関連 (新規追加)
| 期待エンドポイント | 使用箇所 | 実装状況 | 差異・備考 |
|------------------|---------|---------|----------|
| `/api/news` | getNews() | ❌ 未実装 | ニュース一覧未実装 |
| `/api/news/{news_id}` | getNewsDetails() | ❌ 未実装 | ニュース詳細未実装 |
| `/api/news/{news_id}/bookmark` | toggleNewsBookmark() | ❌ 未実装 | ニュースブックマーク未実装 |

### ユーザーランキング関連 (新規追加)
| 期待エンドポイント | 使用箇所 | 実装状況 | 差異・備考 |
|------------------|---------|---------|----------|
| `/api/user-rankings` | getUserRankings() | ❌ 未実装 | ユーザーランキング未実装 |
| `/api/user-rankings/stats` | getUserRankingStats() | ❌ 未実装 | ランキング統計未実装 |

## 3. 実装優先度分析

### 🔴 高優先度 (コア機能)
1. **株式予測API** - `/api/finance/stocks/{symbol}/predict`
2. **出来高関連API** - Volume系エンドポイント
3. **セクターAPI** - `/api/finance/sectors`
4. **テーマ・インサイトAPI** - `/api/insights/themes` 系

### 🟡 中優先度 (機能拡張)
1. **為替API** - Forex系全エンドポイント
2. **AI判断根拠API** - `/api/predictions/*/factors`
3. **コンテストAPI** - Contest系全エンドポイント
4. **ニュースAPI** - News系全エンドポイント

### 🟢 低優先度 (付加機能)
1. **ユーザー管理API** - User系エンドポイント
2. **ポートフォリオAPI** - Portfolio系エンドポイント
3. **通知・設定API** - Settings系エンドポイント

## 4. パラメータ差異

### 既存API差異
| フロントエンド | バックエンド | 対応方法 |
|---------------|-------------|---------|
| `limit` | `days` | `/api/finance/stocks/{symbol}/price` |
| `/predict` | `/predictions` | URL命名統一が必要 |

## 5. 推奨実装アクション

### Phase 1: コア機能実装
- [ ] Volume関連API実装 (出来高データ・予測・ランキング)
- [ ] Sector API実装 (セクター分析機能)
- [ ] Theme/Insights API実装 (テーマ分析機能)

### Phase 2: 機能拡張
- [ ] Forex API実装 (為替機能)
- [ ] Contest API実装 (予測コロシアム)
- [ ] AI Factors API実装 (判断根拠表示)

### Phase 3: ユーザー機能
- [ ] User Management API実装
- [ ] Portfolio API実装
- [ ] News API実装

## 6. 技術的推奨事項

### エンドポイント統一化
```
推奨: /api/finance/stocks/{symbol}/predictions
現在: /api/finance/stocks/{symbol}/predictions ✅

推奨: /api/finance/stocks/{symbol}/predict (POST)
現在: 未実装 ❌
```

### レスポンス形式統一
すべてのAPIが以下の形式を返却することを推奨:
```json
{
  "status": "success" | "error",
  "data": <actual_data>,
  "message"?: "optional_message",
  "error"?: "error_details"
}
```

## 7. まとめ

- **実装済み**: 7エンドポイント (基本・検索・株価・予測・指標・ランキング)
- **未実装**: 50+エンドポイント (出来高・為替・AI・テーマ・コンテスト・ユーザー管理等)
- **実装率**: 約12% (7/60)

フロントエンドは完全実装されているが、バックエンドAPIが大幅に不足している状況。Core機能から段階的な実装が必要。

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Analyze API endpoints used in frontend", "status": "completed", "activeForm": "Analyzing API endpoints used in frontend"}, {"content": "Review actual API backend endpoints", "status": "completed", "activeForm": "Reviewing actual API backend endpoints"}, {"content": "Compare and organize endpoint mappings", "status": "completed", "activeForm": "Comparing and organizing endpoint mappings"}, {"content": "Create comprehensive endpoint documentation", "status": "completed", "activeForm": "Creating comprehensive endpoint documentation"}]