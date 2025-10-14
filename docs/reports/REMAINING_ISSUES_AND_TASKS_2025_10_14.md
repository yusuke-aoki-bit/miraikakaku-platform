# 残課題と問題点 - 2025年10月14日

## 📊 現在のシステム状態

### ✅ 完了済み (Production Ready)

#### バックエンド API
- **Phase 6: 認証システム** - 100% 完了
  - JWT認証 (pbkdf2_sha256)
  - ユーザー登録・ログイン・トークンリフレッシュ
  - 本番環境稼働中

- **Phase 8: ウォッチリスト API** - 100% デプロイ済み
  - 5つのエンドポイント実装
  - CRUD操作完備
  - 本番環境稼働中

- **Phase 9: ポートフォリオ API** - 100% デプロイ済み
  - 6つのエンドポイント実装
  - パフォーマンス追跡機能
  - 本番環境稼働中

- **Phase 10: アラート API** - 100% デプロイ済み
  - 7つのエンドポイント実装
  - 6種類のアラートタイプ
  - 本番環境稼働中

**本番URL:** https://miraikakaku-api-465603676610.us-central1.run.app

---

## ❌ 未完了の課題

### 1. データベーススキーマの適用 🔴 【最優先】

**現状:**
- スキーマファイルは作成済み
- ローカルDBが停止中のため未適用
- 本番環境のCloud SQLに適用が必要

**影響:**
- 新しいAPI（ウォッチリスト、ポートフォリオ、アラート）がテーブル不存在エラーで動作不可
- ユーザーが機能を使用できない

**対応方法:**

#### Option A: ローカルDBを起動して適用
```bash
# PostgreSQLを起動
# (Docker Composeまたはローカルサービス)

# スキーマを適用
cd c:/Users/yuuku/cursor/miraikakaku
bash apply_all_schemas.sh
```

#### Option B: Cloud SQLに直接適用
```bash
# Cloud SQL Proxyを使用
gcloud sql connect miraikakaku-db --user=postgres

# または、Cloud Shellから
psql -h [CLOUD_SQL_IP] -U postgres -d miraikakaku -f create_watchlist_schema.sql
psql -h [CLOUD_SQL_IP] -U postgres -d miraikakaku -f apply_portfolio_schema.sql
psql -h [CLOUD_SQL_IP] -U postgres -d miraikakaku -f create_alerts_schema.sql
```

**必要なテーブル:**
- `user_watchlists` (Phase 8)
- `portfolio_holdings` (Phase 9)
- `portfolio_snapshots` (Phase 9)
- `price_alerts` (Phase 10)

---

### 2. フロントエンドの認証統合 🟡 【高優先度】

**現状:**
- `AuthContext.tsx` は作成済み (`contexts/AuthContext.tsx`)
- 各機能ページは存在 (login, register, watchlist, portfolio)
- `app/layout.tsx` に AuthProvider が統合されていない

**影響:**
- ログイン機能が動作しない
- 認証状態がグローバルで管理されない
- protected routes が機能しない

**対応方法:**

#### Step 1: AuthProviderを layout.tsx に統合
```typescript
// app/layout.tsx に追加
import { AuthProvider } from '@/contexts/AuthContext';

// ProvidersコンポーネントでAuthProviderをラップ
<AuthProvider>
  <Providers>
    {/* 既存のコンテンツ */}
  </Providers>
</AuthProvider>
```

#### Step 2: Headerコンポーネントを更新
```typescript
// components/Header.tsx
import { useAuth } from '@/contexts/AuthContext';

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header>
      {isAuthenticated ? (
        <>
          <span>{user?.username}</span>
          <button onClick={logout}>ログアウト</button>
        </>
      ) : (
        <Link href="/login">ログイン</Link>
      )}
    </header>
  );
}
```

---

### 3. APIクライアントの実装 🟡 【高優先度】

**現状:**
- 各ページでfetchを個別に実装
- 認証ヘッダーの管理が分散
- エラーハンドリングが統一されていない

**対応方法:**

#### Step 1: API Client ライブラリを作成
```typescript
// lib/api-client.ts
import { useAuth } from '@/contexts/AuthContext';

export async function apiClient(
  endpoint: string,
  options: RequestInit = {}
) {
  const token = localStorage.getItem('access_token');

  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
  };

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`,
    config
  );

  if (response.status === 401) {
    // Token expired - redirect to login
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'API request failed');
  }

  return response.json();
}
```

#### Step 2: 環境変数を設定
```bash
# .env.local
NEXT_PUBLIC_API_URL=https://miraikakaku-api-465603676610.us-central1.run.app
```

---

### 4. フロントエンドページの実装状況確認 🟢 【中優先度】

**存在が確認されたページ:**
- ✅ `app/login/page.tsx` - ログインページ
- ✅ `app/register/page.tsx` - 登録ページ
- ✅ `app/watchlist/page.tsx` - ウォッチリスト
- ✅ `app/portfolio/page.tsx` - ポートフォリオ
- ✅ `app/portfolio/add/page.tsx` - ポートフォリオ追加

**確認が必要:**
- [ ] 各ページがAuthContextを使用しているか
- [ ] 認証チェックが実装されているか
- [ ] API統合が完了しているか

**対応方法:**
```bash
# 各ページを確認
- app/watchlist/page.tsx の実装状況
- app/portfolio/page.tsx の実装状況
- app/portfolio/add/page.tsx の実装状況
```

---

### 5. アラートページの不在 🟡 【中優先度】

**現状:**
- アラートAPI (Phase 10) は完成
- フロントエンドページが存在しない

**対応方法:**
- `app/alerts/page.tsx` の作成
- アラート作成フォーム
- アラート一覧表示
- トリガー状態の表示

---

### 6. E2Eテストの実行 🟢 【中優先度】

**現状:**
- テストスクリプトは作成済み (`test_phase7_10_endpoints.sh`)
- 実行されていない
- 本番環境での動作確認が未実施

**対応方法:**
```bash
cd c:/Users/yuuku/cursor/miraikakaku
bash test_phase7_10_endpoints.sh
```

**期待される結果:**
- 24個のテストが実行される
- 認証、ウォッチリスト、ポートフォリオ、アラートの全機能を検証

---

### 7. Cloud Schedulerの設定 🔵 【低優先度】

**現状:**
- アラートの自動チェック機能が未設定
- 手動でアラートチェックAPIを呼び出す必要がある

**対応方法:**
```bash
gcloud scheduler jobs create http alert-checker \
  --schedule="*/15 * * * *" \
  --uri="https://miraikakaku-api-465603676610.us-central1.run.app/api/alerts/check" \
  --http-method=POST \
  --location=us-central1 \
  --project=pricewise-huqkr
```

**スケジュール案:**
- 15分ごとにアラートをチェック
- トリガー条件を満たしたアラートを自動的に無効化

---

### 8. 通知機能の実装 🔵 【低優先度】

**現状:**
- アラートがトリガーされても通知が送信されない
- ユーザーは手動で確認する必要がある

**対応オプション:**

#### Option A: メール通知
- SendGrid または Mailgun を使用
- アラートトリガー時にメール送信
- 推定コスト: 無料枠内（月間数千件まで）

#### Option B: プッシュ通知
- Firebase Cloud Messaging (FCM)
- Web Push API
- ブラウザ通知

#### Option C: アプリ内通知
- 最もシンプル
- ログイン時に未読アラートを表示
- NotificationSystemコンポーネントを活用

---

### 9. Protected Routesの実装 🟡 【高優先度】

**現状:**
- 認証が必要なページに誰でもアクセス可能
- ログインしていなくてもウォッチリストやポートフォリオにアクセスできる

**対応方法:**

#### Step 1: Protected Route コンポーネントを作成
```typescript
// components/ProtectedRoute.tsx
'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function ProtectedRoute({
  children
}: {
  children: React.ReactNode
}) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
```

#### Step 2: 各ページで使用
```typescript
// app/watchlist/page.tsx
import ProtectedRoute from '@/components/ProtectedRoute';

export default function WatchlistPage() {
  return (
    <ProtectedRoute>
      {/* ページコンテンツ */}
    </ProtectedRoute>
  );
}
```

---

### 10. フロントエンドのデプロイ 🟢 【中優先度】

**現状:**
- フロントエンドの最新変更がデプロイされていない可能性
- AuthContext が本番環境に反映されていない

**対応方法:**
```bash
cd c:/Users/yuuku/cursor/miraikakaku/miraikakakufront

# ビルドテスト
npm run build

# デプロイ
gcloud builds submit \
  --tag gcr.io/pricewise-huqkr/miraikakaku-frontend:latest \
  --project=pricewise-huqkr

gcloud run deploy miraikakaku-frontend \
  --image gcr.io/pricewise-huqkr/miraikakaku-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --project pricewise-huqkr
```

---

## 📋 優先順位付きアクションプラン

### 🔴 最優先 (今すぐ対応)

1. **データベーススキーマの適用**
   - 所要時間: 10分
   - 影響: 全ユーザー機能が使用不可
   - コマンド: `bash apply_all_schemas.sh`

2. **AuthProviderの統合**
   - 所要時間: 30分
   - 影響: 認証機能が動作しない
   - ファイル: `app/layout.tsx`

3. **Protected Routesの実装**
   - 所要時間: 30分
   - 影響: セキュリティリスク
   - ファイル: `components/ProtectedRoute.tsx`

### 🟡 高優先度 (24時間以内)

4. **APIクライアントの実装**
   - 所要時間: 1時間
   - 影響: コード品質、保守性
   - ファイル: `lib/api-client.ts`

5. **Headerコンポーネントの更新**
   - 所要時間: 30分
   - 影響: ユーザー体験
   - ファイル: `components/Header.tsx`

6. **アラートページの作成**
   - 所要時間: 2時間
   - 影響: Phase 10機能が未完成
   - ファイル: `app/alerts/page.tsx`

### 🟢 中優先度 (1週間以内)

7. **E2Eテストの実行**
   - 所要時間: 30分
   - 影響: 品質保証
   - コマンド: `bash test_phase7_10_endpoints.sh`

8. **フロントエンドページの実装確認**
   - 所要時間: 2時間
   - 影響: 機能完成度

9. **フロントエンドのデプロイ**
   - 所要時間: 30分
   - 影響: ユーザーが最新機能を使用できない

### 🔵 低優先度 (2週間以内)

10. **Cloud Schedulerの設定**
    - 所要時間: 15分
    - 影響: 自動化の欠如

11. **通知機能の実装**
    - 所要時間: 4-8時間
    - 影響: ユーザー体験向上

---

## 🐛 既知の問題

### 問題1: ローカルDBが起動していない
**症状:**
```
psycopg2.OperationalError: connection refused
```

**原因:** PostgreSQL サービスが停止している

**解決策:**
```bash
# Docker Composeの場合
docker-compose up -d postgres

# Windows Serviceの場合
net start postgresql-x64-[version]

# または Cloud SQL Proxy を使用
```

### 問題2: バックグラウンドプロセスが多数実行中
**症状:** 21個のバックグラウンドプロセスが残存

**影響:** システムリソースの無駄遣い

**解決済:** `pkill` コマンドでクリーンアップ完了

### 問題3: フロントエンドのビルドエラーの可能性
**症状:** 未確認だが、新しいcontextsディレクトリが追加されている

**確認方法:**
```bash
cd miraikakakufront
npm run build
```

---

## 📊 進捗サマリー

### バックエンド
| Phase | 機能 | API実装 | デプロイ | DB | 進捗 |
|-------|------|---------|----------|-----|------|
| 6 | 認証 | ✅ | ✅ | ✅ | 100% |
| 8 | ウォッチリスト | ✅ | ✅ | ❌ | 80% |
| 9 | ポートフォリオ | ✅ | ✅ | ❌ | 80% |
| 10 | アラート | ✅ | ✅ | ❌ | 80% |

### フロントエンド
| Phase | 機能 | Context | ページ | 統合 | 進捗 |
|-------|------|---------|--------|------|------|
| 7 | 認証UI | ✅ | ✅ | ❌ | 60% |
| 8 | ウォッチリスト | N/A | ✅ | ❓ | 50% |
| 9 | ポートフォリオ | N/A | ✅ | ❓ | 50% |
| 10 | アラート | N/A | ❌ | ❌ | 20% |

### 全体進捗
- **バックエンド:** 85% 完了
- **フロントエンド:** 45% 完了
- **統合:** 40% 完了
- **テスト:** 0% 完了

---

## 🎯 次のセッションでやるべきこと

### セッション開始時の最初の3ステップ

1. **データベーススキーマを適用する**
   ```bash
   bash apply_all_schemas.sh
   ```

2. **AuthProviderを統合する**
   ```typescript
   // app/layout.tsx を編集
   ```

3. **ローカルでテストする**
   ```bash
   npm run dev
   # ログイン機能をテスト
   ```

### 中期目標（今週中）

- [ ] 全フロントエンドページの実装を完了
- [ ] E2Eテストを実行して全機能を検証
- [ ] フロントエンドを本番環境にデプロイ
- [ ] ユーザーマニュアルの作成

### 長期目標（今月中）

- [ ] 通知機能の実装
- [ ] Cloud Schedulerの設定
- [ ] パフォーマンス最適化
- [ ] セキュリティ監査

---

## 📝 重要なメモ

1. **DBスキーマ適用は最優先**
   - これが完了しないと全ての新機能がエラーになる
   - テストも実行できない

2. **AuthProviderの統合は次に重要**
   - 認証フローの基盤
   - 全てのprotected機能の前提条件

3. **段階的なテストを推奨**
   - スキーマ適用 → DBテスト
   - AuthProvider統合 → ログインテスト
   - 各ページ → 機能テスト
   - E2Eテスト → 全体検証

4. **本番デプロイの前にローカルで完全にテスト**
   - バグを本番で発見すると修正に時間がかかる
   - ローカルでの反復テストが効率的

---

**作成日:** 2025-10-14
**次回更新予定:** スキーマ適用後
**担当:** Claude Code
