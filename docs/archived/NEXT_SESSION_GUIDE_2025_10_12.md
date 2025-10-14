# Next Session Guide - Miraikakaku
**Date**: 2025-10-12
**Session End**: 21:00 JST
**Next Session**: 2025-10-13+

---

## 📋 QUICK START

### このセッションで完了したこと ✅

1. **NewsAPI.org統合完了** - 630記事収集、自動化設定済み
2. **データベースレコード数確認** - 3,756銘柄、254,116予測レコード
3. **キーボードショートカットボタン削除** - UI改善
4. **システムヘルスチェック** - 完全レポート作成
5. **GCP整理実施** - クリーンアップスクリプト作成

### 次回セッションで対応すべきこと ⚠️

1. **🔴 最優先: API統計エンドポイント修正の完全デプロイ**
2. **🟡 重要: GitHub Actions修正**
3. **🟢 通常: フロントエンド動作確認**

---

## 🔴 Priority 1: API統計エンドポイント修正

### 問題

APIエンドポイント `/api/home/stats/summary` が古い値を返し続けています。

**現状**:
```json
GET https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/stats/summary
{
  "totalSymbols": 1740,  // ❌ 間違い - 正しくは 3756
  "activePredictions": 1737
}
```

**期待値**:
```json
{
  "totalSymbols": 3756,  // ✅ stock_master総数
  "activeSymbols": 1742,  // ✅ アクティブ銘柄数
  "activePredictions": 1737,
  "totalPredictions": 1737
}
```

### 原因

- コードは正しく修正済み (コミット: `51c9330`)
- ローカルファイル `api_predictions.py` 行630-666も正しい
- しかし、デプロイされたイメージに反映されていない
- 複数回ビルド・デプロイしたが、古い値のまま

### 対応方法

#### オプション A: Docker Build Cacheクリア (推奨)

```bash
# 1. ビルドキャッシュなしで再ビルド
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api \
  --no-cache \
  --timeout=20m \
  --project=pricewise-huqkr

# 2. 最新イメージでデプロイ
gcloud run deploy miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api:latest \
  --region us-central1 \
  --project=pricewise-huqkr

# 3. 確認
curl -s "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/stats/summary" | python -m json.tool
```

#### オプション B: Dockerfileでキャッシュバスト

```dockerfile
# Dockerfileの先頭に追加
ARG CACHE_BUST=2025-10-13
RUN echo "Cache bust: $CACHE_BUST"
```

```bash
# ビルド
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api \
  --substitutions=_CACHE_BUST=$(date +%s)
```

#### オプション C: 手動で確認

```bash
# 1. ローカルで直接ビルド
docker build -t gcr.io/pricewise-huqkr/miraikakaku-api:test .

# 2. ローカルで実行して確認
docker run -p 8080:8080 -e POSTGRES_HOST=... gcr.io/pricewise-huqkr/miraikakaku-api:test

# 3. テスト
curl localhost:8080/api/home/stats/summary

# 4. 成功したらpush
docker push gcr.io/pricewise-huqkr/miraikakaku-api:test
gcloud run deploy miraikakaku-api --image gcr.io/pricewise-huqkr/miraikakaku-api:test
```

### 確認手順

```bash
# 1. API呼び出し
curl -s "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/stats/summary" | python -m json.tool

# 2. 期待される出力
# {
#   "totalSymbols": 3756,      ← これが表示されるべき
#   "activeSymbols": 1742,
#   "activePredictions": 1737,
#   "totalPredictions": 1737,
#   "avgAccuracy": 85.2,
#   "modelsRunning": 3
# }

# 3. フロントエンドで確認
# https://miraikakaku.jp を開く
# 統計セクションに "3,756銘柄" と表示されるか確認
```

---

## 🟡 Priority 2: GitHub Actions修正

### 問題

すべてのGitHub Actionsワークフローが失敗しています。

**失敗しているワークフロー**:
```
CI/CD Pipeline         : FAILURE
Simple CI/CD Pipeline  : FAILURE
Continuous Integration : FAILURE
```

**最新Run ID**: 18443345114
**URL**: https://github.com/yusuke-aoki-bit/miraikakaku-platform/actions/runs/18443345114

### 対応方法

1. **ログ確認**
```bash
# ブラウザで開く
https://github.com/yusuke-aoki-bit/miraikakaku-platform/actions

# 失敗理由を特定:
# - Docker build error?
# - GCP authentication error?
# - Resource quota exceeded?
# - Workflow syntax error?
```

2. **よくある原因と対策**

**原因A: GCP認証エラー**
```yaml
# .github/workflows/*.yml の確認
- uses: google-github-actions/auth@v1
  with:
    credentials_json: ${{ secrets.GCP_SA_KEY }}
```
→ Secret `GCP_SA_KEY` が正しく設定されているか確認

**原因B: Docker build失敗**
```yaml
# build stepでエラー
- name: Build Docker image
  run: docker build -t gcr.io/... .
```
→ Dockerfileの構文エラー確認

**原因C: Resource quota**
```
ERROR: Quota exceeded for quota metric 'Build time'
```
→ GCPコンソールで quota確認

3. **一時対策: 手動デプロイ**

GitHub Actions修正まで、手動でデプロイを継続:
```bash
# API
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api
gcloud run deploy miraikakaku-api --image gcr.io/pricewise-huqkr/miraikakaku-api:latest

# Frontend
cd miraikakakufront
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-frontend
gcloud run deploy miraikakaku-frontend --image gcr.io/pricewise-huqkr/miraikakaku-frontend:latest
```

---

## 🟢 Priority 3: フロントエンド動作確認

### 確認項目

1. **サイトアクセス**
```
https://miraikakaku.jp
→ 正常に表示されるか？
```

2. **統計表示** (API修正デプロイ後)
```
TOP画面の統計セクション:
- 銘柄数: 3,756 (現在: 1,740)
- カバレッジ: 46.2%
- 予測データ: 1,737
```

3. **キーボードショートカットボタン**
```
画面右下に青い設定ボタンが表示されていないか確認
→ 削除されているべき (コミット: 91a0541)
```

4. **ブラウザコンソール**
```
F12 → Console
→ JavaScriptエラーがないか確認
```

---

## 📊 Current System Status

### Services ✅
```
Backend API:
- URL: https://miraikakaku-api-zbaru5v7za-uc.a.run.app
- Revision: 00094-r54
- Status: HEALTHY

Frontend:
- URL: https://miraikakaku.jp
- Revision: 00013-892
- Status: HEALTHY (要確認)

Parallel Batch:
- URL: https://parallel-batch-collector-zbaru5v7za-an.a.run.app
- Revision: 00005-wbt
- Status: HEALTHY
```

### Database ✅
```
Cloud SQL: miraikakaku-postgres
- Region: us-central1
- Tier: db-f1-micro
- Status: RUNNING

Record Counts:
- stock_master: 3,756 symbols
- stock_prices: ~500,000+ records
- ensemble_predictions: 254,116 records
- stock_news: 1,386 articles (27 symbols)
```

### Scheduler ✅
```
4 jobs ENABLED:
- newsapi-daily-collection     : 05:30 JST
- daily-news-collection         : 06:00 JST
- daily-sentiment-predictions   : 07:00 JST
- daily-news-enhanced-predictions: 08:00 JST
```

### CI/CD ❌
```
GitHub Actions: ALL FAILING
- Last success: Unknown
- Last failure: 2025-10-12T11:30:49Z
- Action required: Fix workflows
```

---

## 📁 Important Files

### Documentation Created This Session
```
NEWSAPI_INTEGRATION_COMPLETE_2025_10_12.md
DATABASE_COMPLETE_STATS_2025_10_12.md
SYSTEM_HEALTH_REPORT_2025_10_12.md
NEXT_SESSION_GUIDE_2025_10_12.md (this file)
gcp_cleanup_script.sh
```

### Modified Files
```
api_predictions.py (lines 630-666) - API stats endpoint
miraikakakufront/app/layout.tsx - Removed keyboard shortcuts
newsapi_collector.py - NewsAPI integration
```

### Scripts
```
check_db_counts.py - Database count verification
get_db_complete_stats.py - Complete statistics
gcp_cleanup_script.sh - GCP resource cleanup
```

---

## 🔧 Quick Commands

### Check API Stats
```bash
curl -s "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/api/home/stats/summary" | python -m json.tool
```

### Check Database Counts
```bash
curl -s "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/stock-statistics" | python -m json.tool | grep -E "(total_stocks|us_stocks|jp_stocks)"
```

### Check Service Health
```bash
gcloud run services describe miraikakaku-api --region us-central1 --format="value(status.conditions[0].status,status.latestReadyRevisionName)"
```

### Check Latest Logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=miraikakaku-api" --limit 20 --format "table(timestamp,textPayload)" --project=pricewise-huqkr
```

### Manual Deploy
```bash
# API
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api --no-cache
gcloud run deploy miraikakaku-api --image gcr.io/pricewise-huqkr/miraikakaku-api:latest --region us-central1

# Frontend
cd miraikakakufront
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-frontend --no-cache
gcloud run deploy miraikakaku-frontend --image gcr.io/pricewise-huqkr/miraikakaku-frontend:latest --region us-central1
```

---

## 📝 Session Summary

### What We Accomplished
- ✅ NewsAPI.org integration (630 articles collected)
- ✅ Database record verification (3,756 symbols confirmed)
- ✅ UI improvement (removed keyboard shortcut button)
- ✅ System health check (comprehensive report)
- ✅ GCP cleanup (script created)
- ✅ API stats endpoint fix (coded but not deployed correctly)

### What's Pending
- ⏳ API stats endpoint deployment (priority 1)
- ⏳ GitHub Actions fix (priority 2)
- ⏳ Frontend verification (priority 3)

### Estimated Time for Next Session
- API stats fix: 30-60 minutes
- GitHub Actions fix: 30-90 minutes
- Frontend verification: 15 minutes

**Total**: 1.5-3 hours

---

## 🎯 Success Criteria for Next Session

1. **API Stats Endpoint** ✅
   - `/api/home/stats/summary` returns `totalSymbols: 3756`
   - Frontend displays "3,756銘柄"

2. **GitHub Actions** ✅
   - At least one workflow passes
   - Automatic deployment working

3. **System Verification** ✅
   - https://miraikakaku.jp loads correctly
   - No console errors
   - Statistics display correctly
   - Keyboard shortcut button removed

---

**Guide Created**: 2025-10-12 21:00 JST
**For Session**: 2025-10-13+
**Priority**: 🔴 API Stats Fix → 🟡 GitHub Actions → 🟢 Frontend Check
