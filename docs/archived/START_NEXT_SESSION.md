# 次セッション クイックスタート

## 📍 前回の成果
✅ NewsAPI.org統合 100%完了  
✅ Toyota: 98記事収集・保存成功  
✅ バッチエンドポイント実装完了

---

## 🚀 今すぐ実行

### Step 1: バッチエンドポイントをデプロイ (5分)
```bash
cd ~/cursor/miraikakaku
gcloud builds submit --tag gcr.io/pricewise-huqkr/miraikakaku-api --project=pricewise-huqkr
gcloud run services update miraikakaku-api --image gcr.io/pricewise-huqkr/miraikakaku-api:latest --region us-central1
```

### Step 2: 15社バッチテスト (3分)
```bash
curl -X POST "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/collect-news-newsapi-batch?limit=15" | python -m json.tool
```

### Step 3: 結果確認 (2分)
```bash
# Toyota確認
curl "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/check-news-data?symbol=7203.T&limit=5" | python -m json.tool

# Sony確認  
curl "https://miraikakaku-api-zbaru5v7za-uc.a.run.app/admin/check-news-data?symbol=6758.T&limit=5" | python -m json.tool
```

---

## 📚 詳細ドキュメント

完全なガイドは以下を参照:
- [NEXT_SESSION_GUIDE_2025_10_12.md](docs/sessions/2025-10-12/NEXT_SESSION_GUIDE_2025_10_12.md)
- [SESSION_SUMMARY_2025_10_12.md](docs/sessions/2025-10-12/SESSION_SUMMARY_2025_10_12.md)

---

**最終更新**: 2025-10-12 10:40 UTC
