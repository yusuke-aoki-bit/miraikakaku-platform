# 本番環境インフラストラクチャセットアップガイド

## 📅 作成日時
**2025-10-14**

---

## 概要

本番環境の完全なインフラストラクチャ設定ガイドです。Cloud CDN、Cloud Armor、Cloud Monitoring、SEO最適化などを実装します。

---

## 📋 目次

1. [Cloud CDN有効化](#1-cloud-cdn有効化)
2. [Cloud Armor設定](#2-cloud-armor設定)
3. [Cloud Monitoring設定](#3-cloud-monitoring設定)
4. [カスタム404ページ](#4-カスタム404ページ)
5. [SEO最適化](#5-seo最適化)
6. [パフォーマンス最適化](#6-パフォーマンス最適化)

---

## 1. Cloud CDN有効化

### 1.1 前提条件

Cloud CDNを使用するには、Cloud Load Balancerが必要です。

### 1.2 Serverless NEGの作成

```bash
# プロジェクト設定
PROJECT_ID="pricewise-huqkr"
REGION="us-central1"

# Serverless NEG（Network Endpoint Group）を作成
gcloud compute network-endpoint-groups create miraikakaku-frontend-neg \
  --region=${REGION} \
  --network-endpoint-type=serverless \
  --cloud-run-service=miraikakaku-frontend \
  --project=${PROJECT_ID}

gcloud compute network-endpoint-groups create miraikakaku-api-neg \
  --region=${REGION} \
  --network-endpoint-type=serverless \
  --cloud-run-service=miraikakaku-api \
  --project=${PROJECT_ID}
```

### 1.3 バックエンドサービスの作成

```bash
# フロントエンド用バックエンドサービス
gcloud compute backend-services create miraikakaku-frontend-backend \
  --load-balancing-scheme=EXTERNAL_MANAGED \
  --global \
  --project=${PROJECT_ID}

# API用バックエンドサービス
gcloud compute backend-services create miraikakaku-api-backend \
  --load-balancing-scheme=EXTERNAL_MANAGED \
  --global \
  --project=${PROJECT_ID}

# NEGをバックエンドに追加
gcloud compute backend-services add-backend miraikakaku-frontend-backend \
  --global \
  --network-endpoint-group=miraikakaku-frontend-neg \
  --network-endpoint-group-region=${REGION} \
  --project=${PROJECT_ID}

gcloud compute backend-services add-backend miraikakaku-api-backend \
  --global \
  --network-endpoint-group=miraikakaku-api-neg \
  --network-endpoint-group-region=${REGION} \
  --project=${PROJECT_ID}
```

### 1.4 Cloud CDNの有効化

```bash
# フロントエンドでCDNを有効化
gcloud compute backend-services update miraikakaku-frontend-backend \
  --enable-cdn \
  --global \
  --cache-mode=CACHE_ALL_STATIC \
  --default-ttl=3600 \
  --max-ttl=86400 \
  --client-ttl=3600 \
  --project=${PROJECT_ID}

# APIでは選択的キャッシング
gcloud compute backend-services update miraikakaku-api-backend \
  --enable-cdn \
  --global \
  --cache-mode=USE_ORIGIN_HEADERS \
  --project=${PROJECT_ID}
```

### 1.5 キャッシュポリシーの設定

Next.jsの`next.config.js`で適切なCache-Controlヘッダーを設定:

```javascript
// miraikakakufront/next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=60, s-maxage=300, stale-while-revalidate=86400',
          },
        ],
      },
    ];
  },
};
```

### 1.6 CDNキャッシュのクリア

```bash
# 全てのキャッシュをクリア
gcloud compute url-maps invalidate-cdn-cache miraikakaku-lb \
  --path="/*" \
  --async \
  --project=${PROJECT_ID}

# 特定のパスのみクリア
gcloud compute url-maps invalidate-cdn-cache miraikakaku-lb \
  --path="/api/*" \
  --async \
  --project=${PROJECT_ID}
```

---

## 2. Cloud Armor設定

### 2.1 セキュリティポリシーの作成

```bash
# セキュリティポリシーを作成
gcloud compute security-policies create miraikakaku-security-policy \
  --description="Security policy for Miraikakaku" \
  --project=${PROJECT_ID}
```

### 2.2 DDoS保護ルールの追加

```bash
# レート制限ルール（1分間に100リクエスト）
gcloud compute security-policies rules create 1000 \
  --security-policy=miraikakaku-security-policy \
  --expression="true" \
  --action=rate-based-ban \
  --rate-limit-threshold-count=100 \
  --rate-limit-threshold-interval-sec=60 \
  --ban-duration-sec=600 \
  --conform-action=allow \
  --exceed-action=deny-429 \
  --enforce-on-key=IP \
  --project=${PROJECT_ID}
```

### 2.3 地域制限ルール

```bash
# 特定の国からのアクセスを許可（日本、米国、EU）
gcloud compute security-policies rules create 2000 \
  --security-policy=miraikakaku-security-policy \
  --expression="origin.region_code in ['JP', 'US'] || origin.region_code.startsWith('EU')" \
  --action=allow \
  --description="Allow JP, US, EU traffic" \
  --project=${PROJECT_ID}

# その他の国はブロック（オプション）
gcloud compute security-policies rules create 3000 \
  --security-policy=miraikakaku-security-policy \
  --expression="true" \
  --action=deny-403 \
  --description="Block all other traffic" \
  --project=${PROJECT_ID}
```

### 2.4 SQLインジェクション対策

```bash
# SQLインジェクション検出
gcloud compute security-policies rules create 4000 \
  --security-policy=miraikakaku-security-policy \
  --expression="evaluatePreconfiguredExpr('sqli-stable')" \
  --action=deny-403 \
  --description="Block SQL injection attempts" \
  --project=${PROJECT_ID}

# XSS攻撃検出
gcloud compute security-policies rules create 4001 \
  --security-policy=miraikakaku-security-policy \
  --expression="evaluatePreconfiguredExpr('xss-stable')" \
  --action=deny-403 \
  --description="Block XSS attempts" \
  --project=${PROJECT_ID}

# LFI（Local File Inclusion）攻撃検出
gcloud compute security-policies rules create 4002 \
  --security-policy=miraikakaku-security-policy \
  --expression="evaluatePreconfiguredExpr('lfi-stable')" \
  --action=deny-403 \
  --description="Block LFI attempts" \
  --project=${PROJECT_ID}
```

### 2.5 ポリシーをバックエンドに適用

```bash
# フロントエンドに適用
gcloud compute backend-services update miraikakaku-frontend-backend \
  --security-policy=miraikakaku-security-policy \
  --global \
  --project=${PROJECT_ID}

# APIに適用
gcloud compute backend-services update miraikakaku-api-backend \
  --security-policy=miraikakaku-security-policy \
  --global \
  --project=${PROJECT_ID}
```

---

## 3. Cloud Monitoring設定

### 3.1 アップタイムチェックの作成

```bash
# フロントエンドのアップタイムチェック
gcloud monitoring uptime create frontend-uptime \
  --resource-type=uptime-url \
  --display-name="Miraikakaku Frontend Uptime" \
  --host="miraikakaku-frontend-465603676610.us-central1.run.app" \
  --path="/" \
  --check-interval=60s \
  --timeout=10s \
  --project=${PROJECT_ID}

# APIのアップタイムチェック
gcloud monitoring uptime create api-uptime \
  --resource-type=uptime-url \
  --display-name="Miraikakaku API Uptime" \
  --host="miraikakaku-api-465603676610.us-central1.run.app" \
  --path="/health" \
  --check-interval=60s \
  --timeout=10s \
  --project=${PROJECT_ID}
```

### 3.2 アラートポリシーの作成

```yaml
# alert-policies.yaml
displayName: "High Error Rate Alert"
conditions:
  - displayName: "Error rate > 5%"
    conditionThreshold:
      filter: |
        resource.type="cloud_run_revision"
        AND metric.type="run.googleapis.com/request_count"
        AND metric.labels.response_code_class="5xx"
      comparison: COMPARISON_GT
      thresholdValue: 0.05
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_RATE
notificationChannels:
  - projects/pricewise-huqkr/notificationChannels/[CHANNEL_ID]
alertStrategy:
  autoClose: 604800s  # 7 days
```

```bash
# アラートポリシーを作成
gcloud alpha monitoring policies create \
  --policy-from-file=alert-policies.yaml \
  --project=${PROJECT_ID}
```

### 3.3 通知チャネルの設定

```bash
# メール通知チャネル
gcloud alpha monitoring channels create \
  --display-name="Admin Email" \
  --type=email \
  --channel-labels=email_address=admin@miraikakaku.com \
  --project=${PROJECT_ID}

# Slack通知チャネル（Slackアプリ設定が必要）
gcloud alpha monitoring channels create \
  --display-name="Slack Alerts" \
  --type=slack \
  --channel-labels=url=https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  --project=${PROJECT_ID}
```

### 3.4 ダッシュボードの作成

```bash
# ダッシュボード定義をエクスポート
gcloud monitoring dashboards create --config-from-file=dashboard.json \
  --project=${PROJECT_ID}
```

`dashboard.json` の内容:
```json
{
  "displayName": "Miraikakaku Production Dashboard",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Request Count",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
                }
              }
            }]
          }
        }
      },
      {
        "xPos": 6,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Request Latency",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\""
                }
              }
            }]
          }
        }
      }
    ]
  }
}
```

---

## 4. カスタム404ページ

### 4.1 404ページの作成

```typescript
// miraikakakufront/app/not-found.tsx
import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center px-4">
        <h1 className="text-9xl font-bold text-indigo-600">404</h1>
        <h2 className="text-3xl font-semibold text-gray-800 mt-4">
          ページが見つかりません
        </h2>
        <p className="text-gray-600 mt-4 max-w-md mx-auto">
          お探しのページは存在しないか、移動された可能性があります。
        </p>

        <div className="mt-8 space-x-4">
          <Link
            href="/"
            className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            ホームへ戻る
          </Link>
          <Link
            href="/search"
            className="inline-block bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300 transition-colors"
          >
            銘柄を検索
          </Link>
        </div>

        <div className="mt-12">
          <p className="text-sm text-gray-500">
            問題が続く場合は、
            <a href="mailto:support@miraikakaku.com" className="text-indigo-600 hover:underline">
              サポート
            </a>
            までお問い合わせください。
          </p>
        </div>
      </div>
    </div>
  );
}
```

### 4.2 エラーページの作成

```typescript
// miraikakakufront/app/error.tsx
'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-orange-100">
      <div className="text-center px-4">
        <h1 className="text-6xl font-bold text-red-600">エラーが発生しました</h1>
        <p className="text-gray-600 mt-4 max-w-md mx-auto">
          申し訳ございません。予期しないエラーが発生しました。
        </p>

        <button
          onClick={() => reset()}
          className="mt-8 inline-block bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
        >
          再試行
        </button>
      </div>
    </div>
  );
}
```

---

## 5. SEO最適化

### 5.1 サイトマップの生成

```typescript
// miraikakakufront/app/sitemap.ts
import { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://www.miraikakaku.com';

  // 静的ページ
  const staticPages = [
    '',
    '/about',
    '/pricing',
    '/terms',
    '/privacy',
    '/contact',
  ].map(route => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: 'monthly' as const,
    priority: route === '' ? 1.0 : 0.8,
  }));

  // 動的ページ（銘柄ページ）
  // 実際にはAPIから取得
  const symbols = ['AAPL', 'MSFT', 'GOOGL', '7203.T', '9984.T'];
  const stockPages = symbols.map(symbol => ({
    url: `${baseUrl}/stocks/${symbol}`,
    lastModified: new Date(),
    changeFrequency: 'daily' as const,
    priority: 0.7,
  }));

  return [...staticPages, ...stockPages];
}
```

### 5.2 robots.txtの作成

```typescript
// miraikakakufront/app/robots.ts
import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/admin/', '/_next/'],
      },
      {
        userAgent: 'Googlebot',
        allow: '/',
        disallow: ['/api/', '/admin/'],
      },
    ],
    sitemap: 'https://www.miraikakaku.com/sitemap.xml',
  };
}
```

### 5.3 メタデータの最適化

```typescript
// miraikakakufront/app/layout.tsx
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: {
    default: 'Miraikakaku - AI株価予測プラットフォーム',
    template: '%s | Miraikakaku',
  },
  description: 'LSTMとAIを活用した次世代株価予測プラットフォーム。日本株・米国株の価格予測、ポートフォリオ管理、リアルタイム通知機能を提供。',
  keywords: ['株価予測', 'AI', 'LSTM', '投資', 'ポートフォリオ管理', '日本株', '米国株'],
  authors: [{ name: 'Miraikakaku Team' }],
  creator: 'Miraikakaku',
  publisher: 'Miraikakaku',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://www.miraikakaku.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'Miraikakaku - AI株価予測プラットフォーム',
    description: 'LSTMとAIを活用した次世代株価予測プラットフォーム',
    url: 'https://www.miraikakaku.com',
    siteName: 'Miraikakaku',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Miraikakaku OG Image',
      },
    ],
    locale: 'ja_JP',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Miraikakaku - AI株価予測プラットフォーム',
    description: 'LSTMとAIを活用した次世代株価予測プラットフォーム',
    images: ['/twitter-image.png'],
    creator: '@miraikakaku',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'google-site-verification-code',
    yandex: 'yandex-verification-code',
  },
};
```

### 5.4 構造化データ（JSON-LD）

```typescript
// miraikakakufront/app/components/StructuredData.tsx
export function StructuredData() {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'Miraikakaku',
    url: 'https://www.miraikakaku.com',
    description: 'AI株価予測プラットフォーム',
    potentialAction: {
      '@type': 'SearchAction',
      target: 'https://www.miraikakaku.com/search?q={search_term_string}',
      'query-input': 'required name=search_term_string',
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
    />
  );
}
```

---

## 6. パフォーマンス最適化

### 6.1 画像最適化

```typescript
// next.config.js
module.exports = {
  images: {
    domains: ['storage.googleapis.com'],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
  },
};
```

### 6.2 コード分割

```typescript
// 動的インポートの使用
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <p>Loading...</p>,
  ssr: false,
});
```

### 6.3 フォント最適化

```typescript
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export default function RootLayout({ children }: { children: React.Node }) {
  return (
    <html lang="ja" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
```

---

## 💰 コスト見積もり

| サービス | 用途 | コスト/月 |
|---------|------|----------|
| Cloud CDN | グローバル配信 | $5-20 |
| Cloud Armor | DDoS保護・WAF | $25-50 |
| Cloud Monitoring | アラート・ダッシュボード | $5-15 |
| **合計** | | **$35-85/月** |

---

## ✅ チェックリスト

- [ ] Cloud CDN有効化
- [ ] キャッシュポリシー設定
- [ ] Cloud Armor設定
- [ ] DDoS保護ルール追加
- [ ] SQLインジェクション対策
- [ ] アップタイムチェック作成
- [ ] アラートポリシー設定
- [ ] 通知チャネル設定
- [ ] カスタム404ページ作成
- [ ] サイトマップ生成
- [ ] robots.txt作成
- [ ] メタデータ最適化
- [ ] 構造化データ追加
- [ ] 画像最適化設定
- [ ] フォント最適化

---

## 📚 参考リンク

- [Cloud CDN Documentation](https://cloud.google.com/cdn/docs)
- [Cloud Armor Documentation](https://cloud.google.com/armor/docs)
- [Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs)
- [Next.js SEO](https://nextjs.org/learn/seo/introduction-to-seo)

---

**作成日時**: 2025-10-14

🎊 **本番環境インフラストラクチャセットアップガイド完成！** 🎊
