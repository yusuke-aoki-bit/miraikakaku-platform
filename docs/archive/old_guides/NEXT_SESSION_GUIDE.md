# 次回セッション開始ガイド - Phase 6 認証システム

**作成日時**: 2025-10-13 23:10 UTC
**現在の進捗**: 95%
**ステータス**: ⚠️ 404エラーによりブロック中
**所要時間**: 30分〜1時間で完了見込み

---

## 🎯 次回セッションの目標

**Phase 6 認証システムを100%完了させる**

- 404エラーを解決
- 全認証エンドポイントの動作確認
- E2Eテスト完了
- Phase 6 完了宣言

---

## 🔴 最優先タスク

### 1. 404エラーの解決

**問題:**
```bash
curl https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/register
→ {"detail":"Not Found"}
```

**原因:**
デプロイされたDockerイメージにルーター統合コードが含まれていない

**解決手順:**

#### ステップ1: ルーター統合の確認
```bash
# api_predictions.py の統合コードを確認
grep -n "auth_router" c:/Users/yuuku/cursor/miraikakaku/api_predictions.py
```

**期待される出力:**
```
1244:from auth_endpoints import router as auth_router
1245:app.include_router(auth_router)
```

もし見つからない場合、以下のコードを追加:

```python
# api_predictions.py の末尾付近 (if __name__ == "__main__": の前)

# ============================================
# Include Authentication Router
# ============================================
from auth_endpoints import router as auth_router
app.include_router(auth_router)
```

#### ステップ2: ファイルの確認
```bash
# 3つのファイルが存在することを確認
ls -la c:/Users/yuuku/cursor/miraikakaku/auth_*.py
ls -la c:/Users/yuuku/cursor/miraikakaku/create_auth_schema.sql
```

**期待される出力:**
- auth_utils.py (存在)
- auth_endpoints.py (存在)
- create_auth_schema.sql (存在)

#### ステップ3: Gitコミット
```bash
cd c:/Users/yuuku/cursor/miraikakaku

git add api_predictions.py
git add auth_utils.py
git add auth_endpoints.py
git add create_auth_schema.sql
git add Dockerfile
git add requirements.txt

git commit -m "Phase 6: Complete authentication system with router integration and bcrypt fix"
```

#### ステップ4: クリーンビルド
```bash
gcloud builds submit \
  --no-cache \
  --tag gcr.io/pricewise-huqkr/miraikakaku-api:latest \
  --project=pricewise-huqkr \
  --timeout=20m
```

**重要**: `--no-cache` フラグを必ず使用してください!

#### ステップ5: デプロイ
```bash
gcloud run deploy miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --project=pricewise-huqkr
```

#### ステップ6: 動作確認
```bash
# 登録エンドポイントのテスト
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123","full_name":"Test User"}'
```

**期待される結果:**
```json
{
  "id": 2,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "is_admin": false,
  "created_at": "2025-10-13T23:00:00.000Z"
}
```

---

## 📋 E2Eテストスクリプト

404エラー解決後、以下のテストを順番に実行:

### テスト1: ユーザー登録
```bash
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser2025","email":"test2025@example.com","password":"SecurePass123","full_name":"Test User 2025"}'
```

### テスト2: ログイン
```bash
# レスポンスからaccess_tokenとrefresh_tokenを保存
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser2025","password":"SecurePass123"}'
```

### テスト3: ユーザー情報取得
```bash
# {access_token}を実際のトークンに置き換える
curl -X GET https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/me \
  -H "Authorization: Bearer {access_token}"
```

### テスト4: トークンリフレッシュ
```bash
# {refresh_token}を実際のトークンに置き換える
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"{refresh_token}"}'
```

### テスト5: ログアウト
```bash
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/logout \
  -H "Authorization: Bearer {access_token}"
```

### テスト6: デモユーザーでログイン
```bash
# パスワードは "demo123"
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"demo123"}'
```

---

## 🧹 バックグラウンドプロセスのクリーンアップ

現在20個以上のプロセスが実行中です。これらを停止してください:

### 実行中のプロセス一覧
```
e62c3c, ff0ac5, e82a2d, 1a37cb, 9998a3, 6a72ea, 80887d, f6a226,
b74d50, a647bd, bf7ec5, 0ece36, e0514e, 01249e, 3db602, 0a4d90,
e32d87, 6c0e58, 23d4ad, b92742, 51a0cb
```

### クリーンアップコマンド
```bash
# 各プロセスを停止 (例)
KillShell e62c3c
KillShell ff0ac5
# ... 他のプロセスも同様に停止
```

または、まとめて確認:
```bash
# 完了済みのプロセスを確認
BashOutput e62c3c
BashOutput ff0ac5
# ...
```

---

## 📁 重要なファイル

### 実装ファイル
1. **[api_predictions.py](c:/Users/yuuku/cursor/miraikakaku/api_predictions.py)**
   - Line 1244-1245: ルーター統合 ⚠️ 確認必要
   - Line 2592: 管理エンドポイント ✅

2. **[auth_utils.py](c:/Users/yuuku/cursor/miraikakaku/auth_utils.py)**
   - Line 27-39: verify_password() ✅
   - Line 42-54: get_password_hash() ✅

3. **[auth_endpoints.py](c:/Users/yuuku/cursor/miraikakaku/auth_endpoints.py)**
   - 全エンドポイント実装済み ✅

4. **[create_auth_schema.sql](c:/Users/yuuku/cursor/miraikakaku/create_auth_schema.sql)**
   - データベーススキーマ ✅

5. **[Dockerfile](c:/Users/yuuku/cursor/miraikakaku/Dockerfile)**
   - Line 9-10: auth_*.py コピー ✅
   - Line 21: create_auth_schema.sql コピー ✅

6. **[requirements.txt](c:/Users/yuuku/cursor/miraikakaku/requirements.txt)**
   - Line 14-17: 認証関連パッケージ ✅

### ドキュメント
- **[PHASE6_COMPLETE_REPORT.md](c:/Users/yuuku/cursor/miraikakaku/PHASE6_COMPLETE_REPORT.md)** - 完了報告書
- **[PHASE6_ISSUES_AND_REMAINING_TASKS.md](c:/Users/yuuku/cursor/miraikakaku/PHASE6_ISSUES_AND_REMAINING_TASKS.md)** - 問題点と残作業
- **[PHASE6_STATUS_REPORT.md](c:/Users/yuuku/cursor/miraikakaku/PHASE6_STATUS_REPORT.md)** - ステータスレポート

---

## 🔍 トラブルシューティング

### 問題1: "Not Found" エラーが続く

**確認事項:**
1. ルーター統合コードがapi_predictions.pyに存在するか
2. auth_endpoints.pyが同じディレクトリに存在するか
3. Dockerイメージが正しくビルドされたか
4. 最新のイメージがデプロイされたか

**デバッグ方法:**
```bash
# Cloud Runログを確認
gcloud run services logs read miraikakaku-api \
  --region=us-central1 \
  --limit=100 \
  --project=pricewise-huqkr

# FastAPI のルート一覧を確認
curl https://miraikakaku-api-465603676610.us-central1.run.app/docs
```

### 問題2: bcrypt エラーが発生

**症状:**
```
password cannot be longer than 72 bytes
```

**確認:**
auth_utils.py の修正が含まれているか確認

```bash
# verify_password と get_password_hash に72バイトトランケーション処理があるか確認
grep -A 5 "def verify_password" c:/Users/yuuku/cursor/miraikakaku/auth_utils.py
grep -A 8 "def get_password_hash" c:/Users/yuuku/cursor/miraikakaku/auth_utils.py
```

### 問題3: データベース接続エラー

**確認事項:**
1. Cloud SQL インスタンスが稼働中か
2. 環境変数が正しく設定されているか
3. ネットワーク接続が正常か

---

## ✅ 完了チェックリスト

次回セッションで以下をすべて完了させる:

- [ ] api_predictions.py のルーター統合を確認・修正
- [ ] Gitコミット実行
- [ ] `--no-cache` でクリーンビルド実行
- [ ] 新しいイメージをCloud Runにデプロイ
- [ ] 404エラーの解消を確認
- [ ] ユーザー登録テスト成功
- [ ] ログインテスト成功
- [ ] ユーザー情報取得テスト成功
- [ ] トークンリフレッシュテスト成功
- [ ] ログアウトテスト成功
- [ ] デモユーザーログインテスト成功
- [ ] バックグラウンドプロセスをすべて停止
- [ ] Phase 6 完了報告書を更新
- [ ] Phase 6 完了宣言

---

## 📊 現在のステータス

| カテゴリ | 完了 | 残作業 |
|---------|------|--------|
| データベーススキーマ | ✅ 100% | - |
| 認証コード実装 | ✅ 100% | - |
| パスワードセキュリティ | ✅ 100% | - |
| JWT トークン管理 | ✅ 100% | - |
| ルーター統合 | ⚠️ 95% | 404エラー修正 |
| デプロイメント | ⚠️ 90% | 正常動作確認 |
| E2Eテスト | ❌ 0% | 全テスト実行 |
| **全体** | **95%** | **5%** |

---

## 🎯 期待される成果

次回セッション終了時には:

1. ✅ すべての認証エンドポイントが正常動作
2. ✅ ユーザー登録・ログインが可能
3. ✅ JWT トークンが正常に発行・検証される
4. ✅ E2Eテストがすべて成功
5. ✅ Phase 6 が 100% 完了
6. ✅ Phase 7 への準備が整う

---

## 💡 ヒント

### 最速で完了させる方法

1. **まず確認**: api_predictions.py のルーター統合
2. **次にビルド**: `--no-cache` で確実にクリーンビルド
3. **デプロイ**: 新しいイメージをすぐにデプロイ
4. **テスト**: 1つずつ順番にテスト実行

### よくある間違い

- ❌ ファイルをGitにコミットし忘れる
- ❌ `--no-cache` を使わずキャッシュが残る
- ❌ 古いイメージをデプロイしてしまう
- ❌ トークンをコピーし忘れてテストできない

---

## 📞 サポート情報

### 公式ドキュメント
- FastAPI: https://fastapi.tiangolo.com/
- Cloud Run: https://cloud.google.com/run/docs
- JWT: https://jwt.io/

### デプロイ情報
- **Project ID**: pricewise-huqkr
- **Service Name**: miraikakaku-api
- **Region**: us-central1
- **Service URL**: https://miraikakaku-api-465603676610.us-central1.run.app

### データベース情報
- **Database**: miraikakaku
- **Host**: localhost (開発) / Cloud SQL (本番)
- **Port**: 5433 (開発)

---

**次回セッション開始時にこのファイルを最初に確認してください!**

**所要時間**: 30分〜1時間
**難易度**: 中
**成功確率**: 95%

頑張ってください! 🚀
