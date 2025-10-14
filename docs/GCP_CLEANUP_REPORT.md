# GCPリソース整理レポート

## ✅ 現在稼働中の主要リソース

### Cloud Run サービス
- **miraikakaku-frontend** 
  - URL: https://miraikakaku-frontend-zbaru5v7za-uc.a.run.app
  - カスタムドメイン: www.miraikakaku.com
  - リビジョン: miraikakaku-frontend-00012-ndw

- **miraikakaku-api**
  - URL: https://miraikakaku-api-zbaru5v7za-uc.a.run.app  
  - カスタムドメイン: api.miraikakaku.com, api.price-wiser.com
  - リビジョン: miraikakaku-api-00048-g7m

- **lstm-daily-predictions**
  - URL: https://lstm-daily-predictions-465603676610.us-central1.run.app
  - 用途: LSTM予測生成

### カスタムドメイン
✅ 既に設定済み:
- www.miraikakaku.com → miraikakaku-frontend
- api.miraikakaku.com → miraikakaku-api  
- api.price-wiser.com → miraikakaku-api

### Cloud Functions
- **lstm-daily-predictions** (HTTP Trigger)

### Cloud Scheduler Jobs
- (現在0件)

## 🧹 整理完了タスク

1. ✅ バックグラウンドジョブのクリーンアップ
2. ✅ カスタムドメイン設定の確認
3. ✅ 主要リソースの稼働状況確認

## 📝 次のステップ

1. 不要なCloud Runリビジョンの削除
2. 使用されていないCloud Functionsの削除または整理
3. Cloud Schedulerジョブの設定（必要に応じて）
4. 古いコンテナイメージのクリーンアップ

## 🌐 アクセス先

### 本番環境
- **フロントエンド**: https://www.miraikakaku.com
- **API**: https://api.miraikakaku.com
- **予測精度ダッシュボード**: https://www.miraikakaku.com/accuracy

### Cloud Run直接アクセス
- Frontend: https://miraikakaku-frontend-zbaru5v7za-uc.a.run.app
- API: https://miraikakaku-api-zbaru5v7za-uc.a.run.app
