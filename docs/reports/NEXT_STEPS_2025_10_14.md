# 🚀 次のステップ - Phase 7以降の開発ガイド

**作成日**: 2025-10-14 11:30 JST
**Phase 6ステータス**: ✅ 100% 完了
**次のフェーズ**: Phase 7 - フロントエンド認証統合

---

## 📊 現在の状態

### ✅ 完了したこと（Phase 1-6）

#### Phase 1-3: 基盤構築
- ✅ PostgreSQLデータベース設計
- ✅ FastAPI バックエンド実装
- ✅ LSTM予測モデル実装
- ✅ Ensembleアンサンブル予測システム
- ✅ Cloud Run デプロイ

#### Phase 4-5: API拡張
- ✅ RESTful API エンドポイント
- ✅ ランキングAPI（上昇率、出来高、予測）
- ✅ 銘柄詳細API
- ✅ 統計情報API
- ✅ OpenAPI (Swagger) ドキュメント

#### Phase 6: 認証システム ⭐ **完成！**
- ✅ ユーザー登録・ログイン
- ✅ JWT トークン管理
- ✅ パスワードハッシング（pbkdf2_sha256）
- ✅ データベーススキーマ
- ✅ 本番環境デプロイ
- ✅ E2Eテスト成功

**詳細**: [PHASE6_100_PERCENT_COMPLETE.md](PHASE6_100_PERCENT_COMPLETE.md)

---

## 🎯 Phase 7: フロントエンド認証統合

### 目標

Next.jsフロントエンドに認証機能を統合し、ユーザーがログイン/登録できるようにする。

### 実装タスク

#### 7.1 認証UI実装

**優先度**: 🔴 **高**

##### 7.1.1 ログインページ (`/login`)

**ファイル**: `miraikakakufront/app/login/page.tsx`

**機能**:
- ユーザー名/パスワード入力フォーム
- ログインボタン
- 「登録はこちら」リンク
- エラーメッセージ表示

**API連携**:
```typescript
POST https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/login
Body: {
  "username": string,
  "password": string
}
```

**成功時の処理**:
1. `access_token` と `refresh_token` を受信
2. ローカルストレージまたはCookieに保存
3. ホームページ（`/`）にリダイレクト

##### 7.1.2 登録ページ (`/register`)

**ファイル**: `miraikakakufront/app/register/page.tsx`

**機能**:
- ユーザー名、メール、パスワード、氏名入力フォーム
- パスワード確認フィールド
- 登録ボタン
- 「すでにアカウントをお持ちの方」リンク

**API連携**:
```typescript
POST https://miraikakaku-api-465603676610.us-central1.run.app/api/auth/register
Body: {
  "username": string,
  "email": string,
  "password": string,
  "full_name": string
}
```

**成功時の処理**:
1. 登録完了メッセージ表示
2. 自動的にログイン、またはログインページにリダイレクト

##### 7.1.3 ヘッダーコンポーネント更新

**ファイル**: `miraikakakufront/components/Header.tsx`

**追加機能**:
- ログイン状態の表示（ユーザー名）
- ログアウトボタン
- マイページリンク（将来）
- 未ログイン時は「ログイン」「登録」ボタン

#### 7.2 認証状態管理

**優先度**: 🔴 **高**

##### 7.2.1 AuthContext 作成

**ファイル**: `miraikakakufront/contexts/AuthContext.tsx`

**実装内容**:
```typescript
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_admin: boolean;
}

const AuthContext = createContext<{
  state: AuthState;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
} | undefined>(undefined);
```

**機能**:
- ログイン状態の保持
- トークン管理
- 自動リフレッシュ（30分ごと）
- ローカルストレージとの同期

##### 7.2.2 Protected Route 実装

**ファイル**: `miraikakakufront/components/ProtectedRoute.tsx`

**機能**:
- ログイン必須ページの保護
- 未ログイン時は `/login` にリダイレクト
- ローディング中の表示

**使用例**:
```typescript
// /watchlist ページはログイン必須
export default function WatchlistPage() {
  return (
    <ProtectedRoute>
      <WatchlistContent />
    </ProtectedRoute>
  );
}
```

#### 7.3 API クライアント更新

**優先度**: 🔴 **高**

##### 7.3.1 認証付きAPIクライアント

**ファイル**: `miraikakakufront/lib/api.ts`

**更新内容**:
```typescript
// トークンを自動的に付与
async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const token = getAccessToken();

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
  });

  // 401エラー時は自動リフレッシュ
  if (response.status === 401) {
    await refreshAccessToken();
    return apiRequest(endpoint, options); // リトライ
  }

  return response;
}
```

**機能**:
- 自動的にBearerトークンを付与
- 401エラー時の自動リフレッシュ
- トークン期限切れの処理

#### 7.4 トークンストレージ

**優先度**: 🟡 **中**

##### 選択肢1: LocalStorage（推奨）

**メリット**:
- 実装が簡単
- サーバーサイドレンダリング不要

**デメリット**:
- XSS攻撃に脆弱

**実装**:
```typescript
localStorage.setItem('access_token', token);
localStorage.setItem('refresh_token', refreshToken);
```

##### 選択肢2: HTTP-Only Cookie

**メリット**:
- XSS攻撃に強い
- より安全

**デメリット**:
- 実装が複雑
- サーバーサイド処理が必要

**実装**:
```typescript
// バックエンド側でSet-Cookieヘッダーを返す
// フロントエンドは自動的にCookieを送信
```

**推奨**: Phase 7ではLocalStorageを使用し、Phase 8以降でCookieに移行

---

## 🎯 Phase 8: ウォッチリスト機能

### 目標

ユーザーがお気に入りの銘柄を保存・管理できる機能を実装する。

### 実装タスク

#### 8.1 データベーススキーマ

**テーブル**: `user_watchlists`

```sql
CREATE TABLE user_watchlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE(user_id, symbol)
);

CREATE INDEX idx_user_watchlists_user_id ON user_watchlists(user_id);
CREATE INDEX idx_user_watchlists_symbol ON user_watchlists(symbol);
```

#### 8.2 バックエンドAPI

**エンドポイント**:

1. **ウォッチリスト取得**
   - `GET /api/watchlist`
   - 認証必須
   - 現在のユーザーのウォッチリストを返す

2. **銘柄追加**
   - `POST /api/watchlist`
   - Body: `{"symbol": "7203.T"}`
   - 認証必須

3. **銘柄削除**
   - `DELETE /api/watchlist/{symbol}`
   - 認証必須

4. **ウォッチリスト詳細**
   - `GET /api/watchlist/details`
   - 各銘柄の現在価格・予測を含む

#### 8.3 フロントエンドUI

**ページ**: `/watchlist`

**機能**:
- ウォッチリストの一覧表示
- 各銘柄の現在価格・変動率・予測
- 銘柄の追加・削除
- メモ機能
- ソート機能（名前、変動率、予測）

**コンポーネント**:
- `WatchlistTable.tsx`
- `AddToWatchlistButton.tsx`
- `RemoveFromWatchlistButton.tsx`

---

## 🎯 Phase 9: ポートフォリオ管理

### 目標

ユーザーが保有銘柄と数量を記録し、ポートフォリオのパフォーマンスを追跡できるようにする。

### 実装タスク

#### 9.1 データベーススキーマ

**テーブル**: `user_portfolios`

```sql
CREATE TABLE user_portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(15, 4) NOT NULL,
    average_buy_price DECIMAL(15, 2) NOT NULL,
    buy_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_portfolios_user_id ON user_portfolios(user_id);
```

#### 9.2 バックエンドAPI

**エンドポイント**:

1. **ポートフォリオ取得**
   - `GET /api/portfolio`
   - 現在のポートフォリオ一覧

2. **銘柄追加**
   - `POST /api/portfolio`
   - Body: `{"symbol": "7203.T", "quantity": 100, "buy_price": 2500}`

3. **銘柄更新**
   - `PUT /api/portfolio/{id}`
   - 数量・購入価格の更新

4. **銘柄削除**
   - `DELETE /api/portfolio/{id}`

5. **パフォーマンス分析**
   - `GET /api/portfolio/performance`
   - 総資産、損益、ポートフォリオ構成比

#### 9.3 フロントエンドUI

**ページ**: `/portfolio`

**機能**:
- 保有銘柄一覧
- 現在価格と購入価格の比較
- 損益計算（絶対値・パーセンテージ）
- ポートフォリオ構成円グラフ
- パフォーマンスチャート

---

## 🎯 Phase 10: アラート機能

### 目標

価格や予測が特定の条件を満たした時にユーザーに通知する。

### 実装タスク

#### 10.1 データベーススキーマ

**テーブル**: `price_alerts`

```sql
CREATE TABLE price_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    alert_type VARCHAR(20) NOT NULL, -- 'price_above', 'price_below', 'prediction_up', etc.
    threshold DECIMAL(15, 2) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 10.2 アラートエンジン

**バックグラウンドジョブ**:
- Cloud Schedulerで5分ごとに実行
- すべてのアクティブなアラートをチェック
- 条件を満たしたらユーザーに通知

**通知方法**:
- メール（Phase 10）
- Webプッシュ通知（Phase 11）
- アプリ内通知（Phase 11）

---

## 📅 開発スケジュール（推奨）

| フェーズ | タスク | 推定工数 | 優先度 |
|---------|-------|---------|--------|
| **Phase 7** | フロントエンド認証統合 | 2-3日 | 🔴 高 |
| **Phase 8** | ウォッチリスト機能 | 2-3日 | 🔴 高 |
| **Phase 9** | ポートフォリオ管理 | 3-4日 | 🟡 中 |
| **Phase 10** | アラート機能 | 2-3日 | 🟡 中 |
| **Phase 11** | プッシュ通知 | 2日 | 🟢 低 |
| **Phase 12** | ダッシュボード強化 | 3日 | 🟢 低 |

**総計**: 約2-3週間

---

## 🛠️ Phase 7 の詳細実装手順

### Step 1: 認証コンテキストの作成（1時間）

```bash
cd miraikakakufront
mkdir -p contexts
touch contexts/AuthContext.tsx
```

**実装内容**: [上記の AuthContext セクション参照](#721-authcontext-作成)

### Step 2: APIクライアントの更新（30分）

**ファイル**: `miraikakakufront/lib/api.ts`

```typescript
// 既存のapi.tsに以下を追加

export async function login(username: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error('Login failed');
  }

  return await response.json();
}

export async function register(userData: RegisterData) {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    throw new Error('Registration failed');
  }

  return await response.json();
}

export async function getCurrentUser(token: string) {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error('Failed to get user info');
  }

  return await response.json();
}
```

### Step 3: ログインページの作成（2時間）

```bash
mkdir -p app/login
touch app/login/page.tsx
```

**実装例**:

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      router.push('/'); // ホームページにリダイレクト
    } catch (err) {
      setError('ログインに失敗しました。ユーザー名とパスワードを確認してください。');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <h1 className="text-2xl font-bold text-center mb-6">ログイン</h1>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              ユーザー名
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              required
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">
              パスワード
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              required
            />
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'ログイン中...' : 'ログイン'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm">
          アカウントをお持ちでない方は
          <a href="/register" className="text-blue-600 hover:underline ml-1">
            こちら
          </a>
        </p>
      </div>
    </div>
  );
}
```

### Step 4: 登録ページの作成（2時間）

```bash
mkdir -p app/register
touch app/register/page.tsx
```

**実装**: ログインページと同様の構造で、追加フィールド（email, full_name）を含める

### Step 5: ヘッダーコンポーネントの更新（1時間）

**ファイル**: `miraikakakufront/components/Header.tsx`

```typescript
'use client';

import { useAuth } from '@/contexts/AuthContext';

export default function Header() {
  const { state, logout } = useAuth();

  return (
    <header className="bg-white shadow">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">Miraikakaku</h1>

        <nav>
          {state.isAuthenticated ? (
            <div className="flex items-center gap-4">
              <span>こんにちは、{state.user?.username}さん</span>
              <button
                onClick={logout}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                ログアウト
              </button>
            </div>
          ) : (
            <div className="flex gap-4">
              <a href="/login" className="px-4 py-2 text-blue-600 hover:underline">
                ログイン
              </a>
              <a href="/register" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                新規登録
              </a>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
```

### Step 6: テストとデバッグ（2時間）

**テスト項目**:
- [ ] ログイン成功時の挙動
- [ ] ログイン失敗時のエラー表示
- [ ] 登録成功時の挙動
- [ ] 登録失敗時のエラー表示（重複ユーザー名など）
- [ ] トークンの保存と読み込み
- [ ] ページリロード後の認証状態の保持
- [ ] ログアウト機能

---

## 🔧 開発環境セットアップ

### Phase 7開発前の準備

```bash
# フロントエンドディレクトリに移動
cd miraikakakufront

# 最新の依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev

# 別ターミナルでバックエンドをローカルで起動（任意）
cd ..
python -m uvicorn api_predictions:app --host 0.0.0.0 --port 8080 --reload
```

### 環境変数の設定

**ファイル**: `miraikakakufront/.env.local`

```bash
NEXT_PUBLIC_API_URL=https://miraikakaku-api-465603676610.us-central1.run.app
```

---

## 📚 参考リソース

### 認証関連

- **Next.js Authentication**: https://nextjs.org/docs/authentication
- **JWT Best Practices**: https://tools.ietf.org/html/rfc8725
- **React Context API**: https://react.dev/reference/react/useContext

### UI/UX

- **Tailwind CSS**: https://tailwindcss.com/docs
- **Shadcn UI Components**: https://ui.shadcn.com/
- **React Hook Form**: https://react-hook-form.com/

### テスト

- **Playwright E2E Testing**: https://playwright.dev/
- **Jest Unit Testing**: https://jestjs.io/

---

## ⚠️ 注意事項

### セキュリティ

1. **トークンの取り扱い**
   - LocalStorageに保存する場合、XSS攻撃に注意
   - HTTPS必須
   - トークンをURLパラメータに含めない

2. **パスワード**
   - フロント側でもバリデーション実施
   - 最小8文字推奨
   - 強度チェッカーの実装を推奨

3. **CORS設定**
   - バックエンドで適切なCORS設定を確認
   - 本番環境では特定のオリジンのみ許可

### パフォーマンス

1. **トークンリフレッシュ**
   - アクセストークン有効期限（30分）に注意
   - 自動リフレッシュの実装
   - リフレッシュ失敗時のログアウト処理

2. **API呼び出し最適化**
   - 不要なAPI呼び出しを避ける
   - キャッシュ戦略の検討
   - React QueryまたはSWRの使用を推奨

---

## 🎉 まとめ

**Phase 6の完成、おめでとうございます！**

認証システムが完全に動作しており、次のステップに進む準備が整いました。

### 推奨される進め方

1. **Phase 7**: フロントエンド認証統合（2-3日）
   - ユーザー体験の向上
   - パーソナライゼーションの基盤

2. **Phase 8**: ウォッチリスト機能（2-3日）
   - ユーザーエンゲージメントの向上
   - リピート率の改善

3. **Phase 9**: ポートフォリオ管理（3-4日）
   - 差別化機能
   - ユーザー価値の向上

**次回のセッションで Phase 7 を開始する準備ができています！**

---

**プロジェクト**: Miraikakaku Stock Prediction Platform
**作成者**: Claude (AI Assistant)
**最終更新**: 2025-10-14 11:30 JST
