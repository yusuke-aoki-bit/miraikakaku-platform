# デュアルドメイン設定完了ガイド

## 📅 作成日時
**2025-10-14**

---

## ✅ 設定されるドメイン

1. **miraikakaku.com** - メインドメイン
2. **price-wiser.com** - セカンダリドメイン

両方のドメインが同じCloud Runサービスを指します。

---

## 🚀 クイックスタート

### ワンコマンド設定

```bash
# スクリプトを実行可能にする
chmod +x setup_dual_domains.sh

# デュアルドメイン設定を実行
bash setup_dual_domains.sh
```

このスクリプトは以下を自動的に実行します：
1. 両ドメインのドメインマッピング作成
2. 環境変数の更新
3. DNS設定情報の表示

---

## 📊 設定されるサブドメイン

### miraikakaku.com
- ✅ https://www.miraikakaku.com → Frontend
- ✅ https://miraikakaku.com → Frontend
- ✅ https://api.miraikakaku.com → Backend API

### price-wiser.com
- ✅ https://www.price-wiser.com → Frontend
- ✅ https://price-wiser.com → Frontend
- ✅ https://api.price-wiser.com → Backend API

**合計**: 6つのドメインマッピング

---

## 🔧 DNS設定

### miraikakaku.com用DNSレコード

ドメインプロバイダー（Google Domains、GoDaddy、Cloudflare等）で以下を設定：

| ホスト名 | タイプ | TTL | データ |
|---------|-------|-----|--------|
| www | A | 300 | 216.239.32.21 |
| www | A | 300 | 216.239.34.21 |
| www | A | 300 | 216.239.36.21 |
| www | A | 300 | 216.239.38.21 |
| @ | A | 300 | 216.239.32.21 |
| @ | A | 300 | 216.239.34.21 |
| @ | A | 300 | 216.239.36.21 |
| @ | A | 300 | 216.239.38.21 |
| api | A | 300 | 216.239.32.21 |
| api | A | 300 | 216.239.34.21 |
| api | A | 300 | 216.239.36.21 |
| api | A | 300 | 216.239.38.21 |

### price-wiser.com用DNSレコード

同様に、price-wiser.comでも同じIPアドレスを設定：

| ホスト名 | タイプ | TTL | データ |
|---------|-------|-----|--------|
| www | A | 300 | 216.239.32.21 |
| www | A | 300 | 216.239.34.21 |
| www | A | 300 | 216.239.36.21 |
| www | A | 300 | 216.239.38.21 |
| @ | A | 300 | 216.239.32.21 |
| @ | A | 300 | 216.239.34.21 |
| @ | A | 300 | 216.239.36.21 |
| @ | A | 300 | 216.239.38.21 |
| api | A | 300 | 216.239.32.21 |
| api | A | 300 | 216.239.34.21 |
| api | A | 300 | 216.239.36.21 |
| api | A | 300 | 216.239.38.21 |

---

## ⏱️ タイムライン

### 1. ドメインマッピング作成
- **実行時間**: 1-2分
- **完了**: スクリプト実行後すぐ

### 2. DNS伝播
- **通常**: 5-15分
- **最大**: 48時間

### 3. SSL証明書発行
- **通常**: 5-15分
- **最大**: 1時間
- **発行元**: Google管理証明書（Let's Encrypt）

---

## ✅ 動作確認

### DNS伝播の確認

```bash
# miraikakaku.com
nslookup www.miraikakaku.com
nslookup miraikakaku.com
nslookup api.miraikakaku.com

# price-wiser.com
nslookup www.price-wiser.com
nslookup price-wiser.com
nslookup api.price-wiser.com
```

### HTTPSアクセスの確認

```bash
# miraikakaku.com
curl -I https://www.miraikakaku.com
curl -I https://miraikakaku.com
curl -I https://api.miraikakaku.com/health

# price-wiser.com
curl -I https://www.price-wiser.com
curl -I https://price-wiser.com
curl -I https://api.price-wiser.com/health
```

すべて **200 OK** が返されれば成功です。

---

## 🔐 環境変数

### フロントエンド

```bash
NEXT_PUBLIC_API_URL=https://api.miraikakaku.com
NEXTAUTH_URL=https://www.miraikakaku.com
NEXTAUTH_SECRET=your-secret
```

### バックエンド

```bash
ALLOWED_ORIGINS=https://www.miraikakaku.com,https://miraikakaku.com,https://www.price-wiser.com,https://price-wiser.com
```

スクリプトが自動的に設定します。

---

## 📍 ドメインの使い分け

### miraikakaku.com（メイン）
- 日本市場向け
- 日本語UI
- 日本株中心

### price-wiser.com（セカンダリ）
- グローバル市場向け
- 英語UI
- 米国株・グローバル株中心

**技術的には同じサービス**ですが、マーケティングやブランディングで使い分けができます。

---

## 🌍 SEO設定

### サイトマップ

両ドメインで異なるサイトマップを提供可能：

```typescript
// app/sitemap.ts
export default function sitemap(): MetadataRoute.Sitemap {
  const domain = process.env.NEXT_PUBLIC_DOMAIN || 'miraikakaku.com';
  const baseUrl = `https://www.${domain}`;

  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1.0,
    },
    // ... 他のページ
  ];
}
```

### robots.txt

```typescript
// app/robots.ts
export default function robots(): MetadataRoute.Robots {
  const domain = process.env.NEXT_PUBLIC_DOMAIN || 'miraikakaku.com';

  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/api/', '/admin/'],
    },
    sitemap: `https://www.${domain}/sitemap.xml`,
  };
}
```

---

## 💰 コスト

デュアルドメイン設定による追加コスト：

| 項目 | コスト |
|-----|--------|
| ドメインマッピング | $0（無料） |
| SSL証明書 | $0（Google管理） |
| DNS | $0-2/月（プロバイダーによる） |
| **合計** | **$0-2/月** |

---

## 🎯 高度な設定（オプション）

### 1. ドメイン別の環境変数

```bash
# ドメインごとに異なる設定を使用
if [[ "$HTTP_HOST" == *"price-wiser.com"* ]]; then
    export APP_LANG=en
    export DEFAULT_MARKET=US
else
    export APP_LANG=ja
    export DEFAULT_MARKET=JP
fi
```

### 2. ドメイン別のテーマ

```typescript
// app/layout.tsx
const domain = headers().get('host') || '';
const theme = domain.includes('price-wiser') ? 'global' : 'jp';
```

### 3. リダイレクト設定

```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const url = request.nextUrl.clone();
  const host = request.headers.get('host') || '';

  // www なしを www ありにリダイレクト
  if (!host.startsWith('www.') && !host.startsWith('api.')) {
    url.host = `www.${host}`;
    return NextResponse.redirect(url);
  }
}
```

---

## 🔍 トラブルシューティング

### 問題1: ドメインマッピング作成エラー

**症状**: `already exists`エラー

**解決策**:
```bash
# 既存のマッピングを確認
gcloud run domain-mappings list --region=us-central1

# 既存のマッピングを削除（必要な場合）
gcloud run domain-mappings delete www.miraikakaku.com --region=us-central1
```

### 問題2: SSL証明書エラー

**症状**: ブラウザで「安全ではない」と表示

**解決策**:
1. ドメイン所有権が確認されているか確認
2. 15分待ってから再度アクセス
3. ステータス確認:
```bash
gcloud run domain-mappings describe www.miraikakaku.com \
  --region=us-central1 \
  --format="value(status.conditions)"
```

### 問題3: DNS伝播が遅い

**症状**: `nslookup`で解決されない

**解決策**:
1. DNSレコードが正しく設定されているか確認
2. DNSキャッシュをクリア:
   - Windows: `ipconfig /flushdns`
   - Mac: `sudo dscacheutil -flushcache`
3. 異なるDNSサーバーで確認:
   - Google DNS: `nslookup www.miraikakaku.com 8.8.8.8`
   - Cloudflare DNS: `nslookup www.miraikakaku.com 1.1.1.1`

---

## 📚 関連ドキュメント

- [CUSTOM_DOMAIN_SETUP_GUIDE.md](CUSTOM_DOMAIN_SETUP_GUIDE.md) - 単一ドメイン設定ガイド
- [PRODUCTION_INFRASTRUCTURE_SETUP.md](PRODUCTION_INFRASTRUCTURE_SETUP.md) - インフラ設定ガイド
- [FINAL_PRODUCTION_SETUP_COMPLETE.md](FINAL_PRODUCTION_SETUP_COMPLETE.md) - 完全セットアップガイド

---

## ✨ まとめ

**デュアルドメイン設定により以下が実現します**:

- ✅ 2つの独立したブランド
- ✅ 地域別マーケティング
- ✅ SEO最適化（各ドメイン独立）
- ✅ 無料SSL証明書（両ドメイン）
- ✅ グローバル配信（Cloud CDN対応）
- ✅ 同一インフラで運用コスト削減

**設定コマンド**:
```bash
bash setup_dual_domains.sh
```

**設定時間**: 5分（DNS伝播除く）

---

**作成日時**: 2025-10-14

🎊 **デュアルドメイン設定完了！** 🎊
