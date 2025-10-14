# 🚀 Miraikakaku 本番環境デプロイメントガイド

このガイドでは、Miraikakakuフロントエンドアプリケーションを本番環境にデプロイする手順を説明します。

## 📋 目次

1. [前提条件](#前提条件)
2. [環境変数の設定](#環境変数の設定)
3. [ビルドとテスト](#ビルドとテスト)
4. [デプロイメント方法](#デプロイメント方法)
5. [デプロイ後の確認](#デプロイ後の確認)
6. [トラブルシューティング](#トラブルシューティング)

## 前提条件

### 必須要件

- **Node.js**: v18.17.0 以上
- **npm**: v9.0.0 以上
- **Git**: 最新版
- **バックエンドAPI**: 稼働中のMiraikakaku APIサーバー

### 推奨環境

- **OS**: Linux (Ubuntu 20.04+) または Windows 10/11
- **メモリ**: 最低2GB RAM
- **ストレージ**: 最低5GB の空き容量

## 環境変数の設定

### 本番環境用 .env.production ファイルの作成

プロジェクトルートに `.env.production` ファイルを作成します：

```env
# API設定
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# NextAuth設定
NEXTAUTH_SECRET=your-super-secret-key-minimum-32-characters-long
NEXTAUTH_URL=https://yourdomain.com

# セキュリティ設定（オプション）
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn-if-using
```

### 重要な注意事項

⚠️ **NEXTAUTH_SECRET**
- 最低32文字以上のランダムな文字列を使用
- 生成コマンド: `openssl rand -base64 32`
- **絶対にGitにコミットしないこと**

⚠️ **NEXT_PUBLIC_API_URL**
- HTTPSを使用すること（本番環境）
- CORSが適切に設定されていることを確認

## ビルドとテスト

### 1. 依存関係のインストール

```bash
# パッケージのインストール
npm ci

# または、package-lock.jsonがない場合
npm install
```

### 2. 型チェック

```bash
# TypeScriptの型チェック
npx tsc --noEmit
```

### 3. Lintチェック

```bash
# ESLintチェック
npm run lint

# 自動修正
npm run lint -- --fix
```

### 4. 本番ビルドの実行

```bash
# 本番用ビルド
npm run build
```

**ビルド成功の確認:**
- `.next` ディレクトリが生成される
- ビルドエラーがないこと
- ビルド時間: 通常2-5分

### 5. ローカルで本番ビルドをテスト

```bash
# 本番モードでローカル起動
npm run start
```

http://localhost:3000 にアクセスして動作確認

## デプロイメント方法

### オプション 1: Vercel (推奨)

Vercelは、Next.jsアプリケーションに最適化されたホスティングプラットフォームです。

#### Vercel CLIでのデプロイ

```bash
# Vercel CLIのインストール
npm i -g vercel

# ログイン
vercel login

# デプロイ
vercel --prod
```

#### Vercel Dashboardでのデプロイ

1. https://vercel.com にアクセス
2. 「New Project」をクリック
3. GitHubリポジトリを接続
4. `miraikakakufront` ディレクトリを選択
5. 環境変数を設定:
   - `NEXT_PUBLIC_API_URL`
   - `NEXTAUTH_SECRET`
   - `NEXTAUTH_URL`
6. 「Deploy」をクリック

**Vercelの利点:**
- ✅ 自動HTTPS
- ✅ グローバルCDN
- ✅ 自動スケーリング
- ✅ プレビューデプロイメント
- ✅ サーバーレス関数対応

### オプション 2: Docker + Cloud Run (GCP)

Dockerコンテナとして本番環境にデプロイします。

#### Dockerfile の作成

プロジェクトルートに `Dockerfile` を作成:

```dockerfile
# Stage 1: Dependencies
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Builder
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Stage 3: Runner
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

#### next.config.ts の更新

```typescript
const nextConfig: NextConfig = {
  output: 'standalone', // Dockerデプロイ用
  // ... その他の設定
};
```

#### Dockerビルドとデプロイ

```bash
# Dockerイメージのビルド
docker build -t miraikakaku-frontend .

# ローカルテスト
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.yourdomain.com \
  -e NEXTAUTH_SECRET=your-secret \
  -e NEXTAUTH_URL=https://yourdomain.com \
  miraikakaku-frontend

# Google Container Registryにプッシュ
docker tag miraikakaku-frontend gcr.io/your-project-id/miraikakaku-frontend
docker push gcr.io/your-project-id/miraikakaku-frontend

# Cloud Runにデプロイ
gcloud run deploy miraikakaku-frontend \
  --image gcr.io/your-project-id/miraikakaku-frontend \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=https://api.yourdomain.com \
  --set-env-vars NEXTAUTH_URL=https://yourdomain.com \
  --set-secrets NEXTAUTH_SECRET=projects/your-project-id/secrets/nextauth-secret:latest
```

### オプション 3: Traditional Server (VPS/EC2)

#### PM2を使用したデプロイ

```bash
# PM2のインストール
npm install -g pm2

# アプリケーションの起動
pm2 start npm --name "miraikakaku" -- start

# 起動スクリプトの保存
pm2 save

# 自動起動の設定
pm2 startup
```

#### Nginx リバースプロキシ設定

`/etc/nginx/sites-available/miraikakaku`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # HTTPSへリダイレクト
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;

        # セキュリティヘッダー
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 設定を有効化
sudo ln -s /etc/nginx/sites-available/miraikakaku /etc/nginx/sites-enabled/

# Nginx再起動
sudo nginx -t
sudo systemctl restart nginx
```

## デプロイ後の確認

### 1. ヘルスチェック

```bash
# HTTPステータス確認
curl -I https://yourdomain.com

# 期待される応答: HTTP/2 200
```

### 2. 機能テスト

- ✅ ホームページが正常に表示される
- ✅ ダークモード切り替えが機能する
- ✅ API接続が成功する（株価データ表示）
- ✅ 認証機能が動作する
- ✅ ランキングページが読み込まれる
- ✅ 銘柄詳細ページが表示される

### 3. パフォーマンス確認

Google PageSpeed Insightsでスコアを確認:
https://pagespeed.web.dev/

**目標スコア:**
- Performance: 90+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 95+

### 4. エラー監視

ブラウザコンソールでJavaScriptエラーがないことを確認

```javascript
// 開発者ツール > Console
// エラーがないことを確認
```

## トラブルシューティング

### 問題: ビルドが失敗する

**症状:**
```
Error: Failed to compile
```

**解決策:**
1. 依存関係を再インストール
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. TypeScriptエラーを確認
   ```bash
   npx tsc --noEmit
   ```

3. Lintエラーを修正
   ```bash
   npm run lint -- --fix
   ```

### 問題: APIに接続できない

**症状:**
- データが読み込まれない
- "Failed to fetch" エラー

**解決策:**
1. `NEXT_PUBLIC_API_URL` を確認
2. CORSが設定されているか確認
3. APIサーバーが稼働しているか確認
   ```bash
   curl https://api.yourdomain.com/health
   ```

### 問題: 認証が機能しない

**症状:**
- ログインできない
- "Invalid session" エラー

**解決策:**
1. `NEXTAUTH_SECRET` が設定されているか確認
2. `NEXTAUTH_URL` が正しいドメインか確認
3. Cookieが保存されているか確認（ブラウザ設定）

### 問題: ページが404エラー

**症状:**
- 特定のルートで404が表示される

**解決策:**
1. Next.jsのルーティングを確認
2. `.next` ディレクトリを削除して再ビルド
   ```bash
   rm -rf .next
   npm run build
   ```

### 問題: パフォーマンスが遅い

**解決策:**
1. 画像最適化を確認
2. コンポーネントのメモ化を追加
3. CDNを使用
4. キャッシュ戦略を見直す

## セキュリティチェックリスト

デプロイ前に以下を確認してください：

- [ ] `NEXTAUTH_SECRET` が32文字以上のランダム文字列
- [ ] すべての環境変数が `.env.production` に設定されている
- [ ] `.env*` ファイルが `.gitignore` に含まれている
- [ ] HTTPS が有効化されている
- [ ] セキュリティヘッダーが設定されている
- [ ] CORS が適切に設定されている
- [ ] APIキーやシークレットがコードに含まれていない
- [ ] エラーメッセージに機密情報が含まれていない

## 継続的デプロイメント (CI/CD)

### GitHub Actions の設定例

`.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.NEXT_PUBLIC_API_URL }}
          NEXTAUTH_SECRET: ${{ secrets.NEXTAUTH_SECRET }}
          NEXTAUTH_URL: ${{ secrets.NEXTAUTH_URL }}

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

## モニタリングとロギング

### 推奨ツール

1. **Vercel Analytics** (Vercel使用時)
   - リアルタイムアクセス解析
   - Web Vitals計測

2. **Google Analytics**
   ```typescript
   // app/layout.tsx
   import Script from 'next/script';

   <Script
     src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
     strategy="afterInteractive"
   />
   ```

3. **Sentry** (エラー追跡)
   ```bash
   npm install @sentry/nextjs
   ```

## バックアップとロールバック

### Vercel でのロールバック

1. Vercel Dashboardにアクセス
2. Deploymentsタブを開く
3. 前のデプロイメントを選択
4. "Promote to Production" をクリック

### 手動バックアップ

```bash
# ビルド成果物のバックアップ
tar -czf miraikakaku-backup-$(date +%Y%m%d).tar.gz .next

# データベースバックアップ（該当する場合）
# LocalStorageデータは各ユーザーのブラウザに保存
```

## サポートとヘルプ

問題が解決しない場合：

1. GitHubリポジトリのIssuesを確認
2. Next.js公式ドキュメントを参照: https://nextjs.org/docs
3. Vercelサポート: https://vercel.com/support

---

**最終更新**: 2025-10-03
**ドキュメントバージョン**: 2.0.0
