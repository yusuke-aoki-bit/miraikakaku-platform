# 🚀 次回セッション クイックスタートガイド

**所要時間**: 30分
**目標**: Phase 6 を 95% → 100% に完了させる

---

## ⚡ 3ステップで完了

### ステップ1: ルーター統合を確認 (5分)

```bash
# 1. 統合コードの有無を確認
grep -n "auth_router" c:/Users/yuuku/cursor/miraikakaku/api_predictions.py
```

**期待される出力:**
```
1244:from auth_endpoints import router as auth_router
1245:app.include_router(auth_router)
```

**もし見つからない場合、以下を実行:**

```bash
# api_predictions.py を確認
cd c:/Users/yuuku/cursor/miraikakaku
grep -n "if __name__" api_predictions.py
```

`if __name__ == "__main__":` の行番号を確認し、その前に以下のコードを追加:

```python
# ============================================
# Include Authentication Router
# ============================================
from auth_endpoints import router as auth_router
app.include_router(auth_router)
```

### ステップ2: クリーンビルド & デプロイ (7分)

```bash
# 1. Gitコミット
cd c:/Users/yuuku/cursor/miraikakaku
git add api_predictions.py auth_utils.py auth_endpoints.py create_auth_schema.sql
git commit -m "Phase 6: Complete authentication with router integration"

# 2. クリーンビルド (--no-cache が重要!)
gcloud builds submit \
  --no-cache \
  --tag gcr.io/pricewise-huqkr/miraikakaku-api:latest \
  --project=pricewise-huqkr \
  --timeout=20m

# 3. デプロイ
gcloud run deploy miraikakaku-api \
  --image gcr.io/pricewise-huqkr/miraikakaku-api:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --project=pricewise-huqkr
```

### ステップ3: E2Eテスト (10分)

```bash
# テスト1: ユーザー登録
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser2025","email":"test2025@example.com","password":"SecurePass123","full_name":"Test User"}'

# 期待: 201 Created + ユーザー情報

# テスト2: ログイン
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser2025","password":"SecurePass123"}'

# 期待: 200 OK + access_token + refresh_token
# ✅ トークンをコピーして次のテストで使用

# テスト3: ユーザー情報取得 (トークンを置き換える)
curl -X GET https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/me \
  -H "Authorization: Bearer {ここにaccess_tokenを貼り付け}"

# 期待: 200 OK + ユーザー情報

# テスト4: デモユーザーでログイン
curl -X POST https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"demo123"}'

# 期待: 200 OK + トークン
```

---

## ✅ 完了チェックリスト

- [ ] ルーター統合コード確認
- [ ] Gitコミット実行
- [ ] `--no-cache` でビルド
- [ ] Cloud Run デプロイ
- [ ] ユーザー登録テスト成功
- [ ] ログインテスト成功
- [ ] ユーザー情報取得テスト成功
- [ ] デモユーザーログイン成功
- [ ] **Phase 6 完了宣言!** 🎉

---

## 🔧 トラブルシューティング

### 問題: まだ404エラー

**確認:**
```bash
# 1. ルーター統合があるか再確認
cat c:/Users/yuuku/cursor/miraikakaku/api_predictions.py | grep -A 2 "auth_router"

# 2. auth_endpoints.py が存在するか
ls -la c:/Users/yuuku/cursor/miraikakaku/auth_endpoints.py

# 3. Dockerfileに含まれているか
grep "auth_endpoints" c:/Users/yuuku/cursor/miraikakaku/Dockerfile
```

### 問題: bcryptエラー

**確認:**
```bash
# verify_password と get_password_hash に修正があるか確認
grep -A 8 "def verify_password" c:/Users/yuuku/cursor/miraikakaku/auth_utils.py
grep -A 12 "def get_password_hash" c:/Users/yuuku/cursor/miraikakaku/auth_utils.py
```

期待: 両方の関数に72バイトトランケーション処理がある

---

## 📁 重要ファイル

| ファイル | 確認ポイント |
|---------|-------------|
| api_predictions.py | Line 1244-1245: ルーター統合 |
| auth_utils.py | Line 27-39, 42-54: bcrypt修正 |
| auth_endpoints.py | 全350行 |
| create_auth_schema.sql | 全185行 |
| Dockerfile | Line 9-10, 21: 認証ファイル |

---

## 🎯 成功の目安

全テストが以下のステータスコードを返せば成功:

- ユーザー登録: **201 Created**
- ログイン: **200 OK**
- ユーザー情報取得: **200 OK**
- トークンリフレッシュ: **200 OK**
- ログアウト: **200 OK**

---

**次回セッション開始時にこのファイルを開いて、3ステップを順番に実行してください!**

**所要時間**: 30分で完了
**Phase 6 完了まであと一歩!** 🚀
