# API Stats Endpoint Fix Complete - 2025-10-12

## 問題の概要

**症状**: `/api/home/stats/summary` エンドポイントが古い値 (1,740銘柄) を返していた

**原因**: デプロイ済みイメージが古いコード (commit 222dde9以前) を含んでいた

## 根本原因分析

### コード履歴

1. **Commit 222dde9 (古いコード)**:
   ```python
   SELECT COUNT(DISTINCT symbol) as total_symbols
   FROM ensemble_predictions  # ← 予測データのある銘柄のみカウント
   ```
   結果: 1,740銘柄

2. **Commit 51c9330 (修正後)**:
   ```python
   SELECT COUNT(*) as total_symbols
   FROM stock_master  # ← マスターテーブルから総数を取得
   ```
   結果: 3,756銘柄

### デプロイメント問題

- リビジョン `00094-r54` は古いコードを使用していた
- `gcr.io/pricewise-huqkr/miraikakaku-api:latest` タグが更新されていなかった
- Dockerビルドキャッシュにより、コード変更が反映されなかった

## 解決方法

### 実施した対応

1. **ユニークタグでビルド**:
   ```bash
   gcloud builds submit \
     --tag gcr.io/pricewise-huqkr/miraikakaku-api:v20251012-225834 \
     --project=pricewise-huqkr \
     --timeout=20m
   ```
   - ビルドID: `c30a49ff-e499-4c70-8bce-8240bbc4afb2`
   - ステータス: SUCCESS
   - 所要時間: 4分6秒

2. **新しいイメージをデプロイ**:
   ```bash
   gcloud run services update miraikakaku-api \
     --image gcr.io/pricewise-huqkr/miraikakaku-api:v20251012-225834 \
     --region us-central1
   ```
   - 新リビジョン: `miraikakaku-api-00095-t47`
   - トラフィック: 100%
   - デプロイ時刻: 2025-10-12 22:58 JST

## 修正結果

### API レスポンス (修正後)

```json
{
    "totalSymbols": 3756,        ✅ 正しい値 (以前: 1740)
    "activeSymbols": 1742,       ✅ 新規フィールド
    "activePredictions": 1737,   ✅ 正しい値
    "totalPredictions": 1740,    ✅ 新規フィールド
    "avgAccuracy": 85.2,
    "modelsRunning": 3
}
```

### データベース確認

```sql
-- stock_master 総数
SELECT COUNT(*) FROM stock_master;
-- 結果: 3,756

-- アクティブ銘柄数
SELECT COUNT(*) FROM stock_master WHERE is_active = TRUE;
-- 結果: 1,742

-- 予測データあり銘柄数
SELECT COUNT(DISTINCT symbol) FROM ensemble_predictions
WHERE prediction_date >= CURRENT_DATE;
-- 結果: 1,737
```

## システム状態

### Cloud Run サービス

- **サービス名**: miraikakaku-api
- **リージョン**: us-central1
- **現在のリビジョン**: miraikakaku-api-00095-t47
- **デプロイイメージ**: gcr.io/pricewise-huqkr/miraikakaku-api:v20251012-225834
- **URL**: https://miraikakaku-api-zbaru5v7za-uc.a.run.app
- **トラフィック配分**: 100%

### コンテナイメージ

| タグ | Digest | タイムスタンプ | 用途 |
|------|--------|------------|------|
| v20251012-225834 | 097475fd | 2025-10-12 22:58 | 🟢 本番稼働中 |
| latest | dc5e5927 | 2025-10-12 19:31 | 古いバージョン |

## 学んだ教訓

### 問題点

1. **`latest` タグの使用**:
   - Dockerビルドキャッシュにより、同じタグで異なるコンテンツになる可能性
   - デプロイ時に実際のコード変更が反映されない

2. **デプロイ検証不足**:
   - ビルド成功 ≠ コード変更の反映
   - デプロイ後のAPI動作確認が必須

### ベストプラクティス

1. **タグ戦略**:
   ```bash
   # 推奨: タイムスタンプまたはgit commitハッシュ
   --tag gcr.io/.../image:v20251012-225834
   --tag gcr.io/.../image:$(git rev-parse --short HEAD)

   # 非推奨: latest のみ
   --tag gcr.io/.../image:latest
   ```

2. **デプロイ検証**:
   ```bash
   # 1. ビルド
   gcloud builds submit --tag ...

   # 2. デプロイ
   gcloud run services update ...

   # 3. 検証（必須）
   curl https://api-url/endpoint | jq
   ```

## 今後の対応

### 即座に実施

- [x] API stats エンドポイント修正完了
- [x] 正しい値の返却確認
- [x] 本番環境デプロイ完了

### 次回セッション

1. **Frontend デプロイ**:
   - フロントエンドで「3,756銘柄」が表示されることを確認
   - キーボードショートカットボタンが削除されていることを確認

2. **GitHub Actions 修正**:
   - 全ワークフロー失敗の原因調査
   - CI/CDパイプライン復旧

3. **デプロイメントプロセス改善**:
   - タイムスタンプベースのタグ運用を標準化
   - デプロイ後の自動検証スクリプト作成

## 関連ドキュメント

- [NEWSAPI_INTEGRATION_COMPLETE_2025_10_12.md](NEWSAPI_INTEGRATION_COMPLETE_2025_10_12.md)
- [NEXT_SESSION_GUIDE_2025_10_12.md](NEXT_SESSION_GUIDE_2025_10_12.md)
- [SESSION_COMPLETE_2025_10_12.md](SESSION_COMPLETE_2025_10_12.md)

---

**修正完了時刻**: 2025-10-12 23:04 JST
**所要時間**: 約30分
**ステータス**: ✅ 完全解決
