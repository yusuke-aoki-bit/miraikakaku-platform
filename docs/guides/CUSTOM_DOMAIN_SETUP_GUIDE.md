# カスタムドメイン設定ガイド

## 📅 作成日時
**2025-10-14**

---

## 概要

Cloud Runサービスにカスタムドメインを設定し、プロフェッショナルなURLでサービスを公開します。

**現在のURL**:
- Frontend: https://miraikakaku-frontend-465603676610.us-central1.run.app
- Backend: https://miraikakaku-api-465603676610.us-central1.run.app

**目標URL** (例):
- Frontend: https://www.miraikakaku.com または https://miraikakaku.com
- Backend: https://api.miraikakaku.com

---

## 📋 前提条件

1. **ドメインの所有**
   - ドメインを購入済み（Google Domains、GoDaddy、Namecheapなど）
   - DNSレコードを編集可能

2. **GCPプロジェクト**
   - プロジェクトID: `pricewise-huqkr`
   - Cloud Runサービスがデプロイ済み
   - 必要な権限: Cloud Run管理者、DNS管理者

3. **gcloud CLI**
   - インストール済み
   - 認証済み: `gcloud auth login`
   - プロジェクト設定済み: `gcloud config set project pricewise-huqkr`

---

## 🚀 セットアップ手順

### オプション1: Cloud Run ドメインマッピング（推奨）

#### ステップ1: ドメインの所有権確認

```bash
# ドメインの所有権を確認
gcloud domains verify miraikakaku.com
```

Google Search Consoleでドメインの所有権を確認する必要があります：
1. https://search.google.com/search-console にアクセス
2. 「プロパティを追加」をクリック
3. ドメインを入力
4. TXTレコードをDNSに追加して確認

#### ステップ2: フロントエンドのドメインマッピング

```bash
# www.miraikakaku.com をマッピング
gcloud run domain-mappings create \
  --service=miraikakaku-frontend \
  --domain=www.miraikakaku.com \
  --region=us-central1 \
  --project=pricewise-huqkr

# ルートドメイン miraikakaku.com をマッピング（オプション）
gcloud run domain-mappings create \
  --service=miraikakaku-frontend \
  --domain=miraikakaku.com \
  --region=us-central1 \
  --project=pricewise-huqkr
```

#### ステップ3: バックエンドAPIのドメインマッピング

```bash
# api.miraikakaku.com をマッピング
gcloud run domain-mappings create \
  --service=miraikakaku-api \
  --domain=api.miraikakaku.com \
  --region=us-central1 \
  --project=pricewise-huqkr
```

#### ステップ4: DNSレコードの設定情報を取得

```bash
# フロントエンドのDNS設定を取得
gcloud run domain-mappings describe www.miraikakaku.com \
  --region=us-central1 \
  --format="value(status.resourceRecords)"

# APIのDNS設定を取得
gcloud run domain-mappings describe api.miraikakaku.com \
  --region=us-central1 \
  --format="value(status.resourceRecords)"
```

出力例:
```
TYPE  NAME                        DATA
A     www.miraikakaku.com.       216.239.32.21
A     www.miraikakaku.com.       216.239.34.21
A     www.miraikakaku.com.       216.239.36.21
A     www.miraikakaku.com.       216.239.38.21
AAAA  www.miraikakaku.com.       2001:4860:4802:32::15
AAAA  www.miraikakaku.com.       2001:4860:4802:34::15
AAAA  www.miraikakaku.com.       2001:4860:4802:36::15
AAAA  www.miraikakaku.com.       2001:4860:4802:38::15
```

#### ステップ5: DNSプロバイダーでレコードを設定

**Google Domainsの場合**:
1. https://domains.google.com にログイン
2. miraikakaku.com を選択
3. 「DNS」タブをクリック
4. 「カスタムレコードを管理」を選択
5. 以下のレコードを追加:

| ホスト名 | タイプ | TTL | データ |
|---------|-------|-----|-------|
| www | A | 300 | 216.239.32.21 |
| www | A | 300 | 216.239.34.21 |
| www | A | 300 | 216.239.36.21 |
| www | A | 300 | 216.239.38.21 |
| api | A | 300 | 216.239.32.21 |
| api | A | 300 | 216.239.34.21 |
| api | A | 300 | 216.239.36.21 |
| api | A | 300 | 216.239.38.21 |
| @ | A | 300 | 216.239.32.21 |
| @ | A | 300 | 216.239.34.21 |
| @ | A | 300 | 216.239.36.21 |
| @ | A | 300 | 216.239.38.21 |

**他のDNSプロバイダー（Cloudflare、Route 53など）**:
- 同様のAレコードを追加
- プロキシ設定はOFF（オレンジ雲マークをクリックして灰色に）

#### ステップ6: SSL証明書の自動発行を待つ

```bash
# 証明書の発行状況を確認
gcloud run domain-mappings describe www.miraikakaku.com \
  --region=us-central1 \
  --format="value(status.conditions)"
```

**注意**: SSL証明書の発行には5-15分かかることがあります。

#### ステップ7: 動作確認

```bash
# DNSが伝播したか確認
nslookup www.miraikakaku.com

# HTTPSアクセスをテスト
curl -I https://www.miraikakaku.com
curl -I https://api.miraikakaku.com
```

---

### オプション2: Cloud Load Balancer + Cloud CDN（高度な設定）

より高度な設定が必要な場合（カスタムSSL証明書、複雑なルーティング、Cloud CDN統合）。

#### ステップ1: 静的IPアドレスを予約

```bash
# グローバルIPアドレスを予約
gcloud compute addresses create miraikakaku-ip \
  --ip-version=IPV4 \
  --global

# IPアドレスを確認
gcloud compute addresses describe miraikakaku-ip \
  --global \
  --format="value(address)"
```

#### ステップ2: SSL証明書を作成

**Google管理証明書（推奨）**:
```bash
gcloud compute ssl-certificates create miraikakaku-ssl-cert \
  --domains=miraikakaku.com,www.miraikakaku.com,api.miraikakaku.com \
  --global
```

**自己管理証明書**:
```bash
gcloud compute ssl-certificates create miraikakaku-ssl-cert \
  --certificate=path/to/certificate.crt \
  --private-key=path/to/private.key \
  --global
```

#### ステップ3: バックエンドサービスを作成

```bash
# Serverless NEGを作成（Cloud Run用）
gcloud compute network-endpoint-groups create miraikakaku-frontend-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=miraikakaku-frontend

gcloud compute network-endpoint-groups create miraikakaku-api-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=miraikakaku-api

# バックエンドサービスを作成
gcloud compute backend-services create miraikakaku-frontend-backend \
  --load-balancing-scheme=EXTERNAL \
  --global

gcloud compute backend-services create miraikakaku-api-backend \
  --load-balancing-scheme=EXTERNAL \
  --global

# NEGをバックエンドに追加
gcloud compute backend-services add-backend miraikakaku-frontend-backend \
  --global \
  --network-endpoint-group=miraikakaku-frontend-neg \
  --network-endpoint-group-region=us-central1

gcloud compute backend-services add-backend miraikakaku-api-backend \
  --global \
  --network-endpoint-group=miraikakaku-api-neg \
  --network-endpoint-group-region=us-central1

# Cloud CDNを有効化（オプション）
gcloud compute backend-services update miraikakaku-frontend-backend \
  --enable-cdn \
  --global \
  --cache-mode=CACHE_ALL_STATIC
```

#### ステップ4: URLマップを作成

```bash
# デフォルトバックエンドを設定
gcloud compute url-maps create miraikakaku-lb \
  --default-service=miraikakaku-frontend-backend

# パスルールを追加（API用）
gcloud compute url-maps add-path-matcher miraikakaku-lb \
  --path-matcher-name=api-matcher \
  --default-service=miraikakaku-frontend-backend \
  --backend-service-path-rules="/api/*=miraikakaku-api-backend"
```

#### ステップ5: HTTPSプロキシを作成

```bash
gcloud compute target-https-proxies create miraikakaku-https-proxy \
  --url-map=miraikakaku-lb \
  --ssl-certificates=miraikakaku-ssl-cert
```

#### ステップ6: フォワーディングルールを作成

```bash
gcloud compute forwarding-rules create miraikakaku-https-forwarding \
  --address=miraikakaku-ip \
  --global \
  --target-https-proxy=miraikakaku-https-proxy \
  --ports=443
```

#### ステップ7: DNSレコードを設定

予約したIPアドレスをDNSに設定:

```bash
# IPアドレスを取得
IP=$(gcloud compute addresses describe miraikakaku-ip --global --format="value(address)")
echo "IP Address: $IP"
```

DNSプロバイダーで以下を設定:

| ホスト名 | タイプ | TTL | データ |
|---------|-------|-----|-------|
| @ | A | 300 | [予約したIP] |
| www | A | 300 | [予約したIP] |
| api | A | 300 | [予約したIP] |

---

## 🔐 CORS設定の更新

カスタムドメインを使用する場合、バックエンドのCORS設定を更新する必要があります。

### api_predictions.py の更新

```python
from fastapi.middleware.cors import CORSMiddleware

# 環境変数から許可するオリジンを取得
ALLOWED_ORIGINS = os.getenv(
    'ALLOWED_ORIGINS',
    'https://www.miraikakaku.com,https://miraikakaku.com,https://api.miraikakaku.com'
).split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Cloud Run環境変数の更新

```bash
gcloud run services update miraikakaku-api \
  --set-env-vars="ALLOWED_ORIGINS=https://www.miraikakaku.com,https://miraikakaku.com" \
  --region=us-central1
```

---

## 🔄 フロントエンド環境変数の更新

カスタムドメインを使用する場合、フロントエンドの環境変数を更新します。

### .env.production の作成

```bash
# miraikakakufront/.env.production
NEXT_PUBLIC_API_URL=https://api.miraikakaku.com
NEXTAUTH_URL=https://www.miraikakaku.com
NEXTAUTH_SECRET=your-nextauth-secret-change-in-production
```

### Cloud Run環境変数の更新

```bash
gcloud run services update miraikakaku-frontend \
  --set-env-vars="NEXT_PUBLIC_API_URL=https://api.miraikakaku.com" \
  --region=us-central1
```

### 再デプロイ

```bash
# 環境変数を含めて再ビルド・デプロイ
cd miraikakakufront
npm run build
gcloud builds submit --config=cloudbuild.yaml
```

---

## ✅ 動作確認

### 1. DNS伝播の確認

```bash
# www.miraikakaku.com
nslookup www.miraikakaku.com

# api.miraikakaku.com
nslookup api.miraikakaku.com

# オンラインツールで確認
# https://dnschecker.org/
```

### 2. SSL証明書の確認

```bash
# SSL証明書の有効性をチェック
curl -vI https://www.miraikakaku.com 2>&1 | grep "SSL certificate"

# ブラウザで確認
# アドレスバーの鍵マークをクリック
```

### 3. APIアクセスの確認

```bash
# ヘルスチェック
curl https://api.miraikakaku.com/health

# 株価データ取得
curl https://api.miraikakaku.com/api/stocks/AAPL

# 認証エンドポイント
curl -X POST https://api.miraikakaku.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

### 4. フロントエンドアクセスの確認

```bash
# HTTPSアクセス
curl -I https://www.miraikakaku.com

# HTTPからHTTPSへのリダイレクト確認
curl -I http://www.miraikakaku.com
```

---

## 🔍 トラブルシューティング

### 問題1: DNSが伝播しない

**症状**: `nslookup`でドメインが解決されない

**解決策**:
1. DNSレコードが正しく設定されているか確認
2. TTLが低い値（300秒）に設定されているか確認
3. 最大48時間待つ（通常は5-15分）
4. DNSキャッシュをクリア: `ipconfig /flushdns` (Windows) / `sudo dscacheutil -flushcache` (Mac)

### 問題2: SSL証明書エラー

**症状**: ブラウザで「接続が安全ではありません」と表示

**解決策**:
1. ドメインマッピングのステータスを確認:
   ```bash
   gcloud run domain-mappings describe www.miraikakaku.com \
     --region=us-central1
   ```
2. 証明書発行に15分程度かかることがある
3. ドメインの所有権が確認されているか確認

### 問題3: CORSエラー

**症状**: ブラウザコンソールで「CORS policy」エラー

**解決策**:
1. バックエンドのALLOWED_ORIGINS環境変数を確認
2. フロントエンドのNEXT_PUBLIC_API_URLが正しいか確認
3. プリフライトリクエスト（OPTIONS）が許可されているか確認

### 問題4: 404 Not Found

**症状**: カスタムドメインにアクセスすると404エラー

**解決策**:
1. ドメインマッピングが正しいサービスを指しているか確認
2. Cloud Runサービスが実行中か確認:
   ```bash
   gcloud run services list --region=us-central1
   ```
3. ドメインマッピングを再作成

---

## 💰 コスト見積もり

### Cloud Run ドメインマッピング
- **無料** - 追加コストなし
- SSL証明書: 無料（Google管理証明書）

### Cloud Load Balancer（オプション）
- **フォワーディングルール**: $0.025/時間 = 約$18/月
- **データ処理**: $0.008-0.012/GB
- **SSL証明書**: 無料（Google管理）/ $10/月（カスタム証明書）
- **合計**: 約$20-50/月

---

## 📋 チェックリスト

- [ ] ドメインを購入済み
- [ ] Google Search Consoleでドメイン所有権を確認
- [ ] Cloud Runドメインマッピングを作成（www、api）
- [ ] DNSレコードを設定（Aレコード）
- [ ] DNS伝播を確認（nslookup）
- [ ] SSL証明書が発行されたか確認
- [ ] CORS設定を更新
- [ ] フロントエンド環境変数を更新
- [ ] 再デプロイ
- [ ] HTTPSアクセスを確認
- [ ] APIエンドポイントをテスト
- [ ] ブラウザで動作確認

---

## 📚 参考リンク

- [Cloud Run Custom Domains](https://cloud.google.com/run/docs/mapping-custom-domains)
- [Cloud Load Balancing](https://cloud.google.com/load-balancing/docs)
- [Google Domains](https://domains.google.com)
- [DNS Checker](https://dnschecker.org/)
- [SSL Test](https://www.ssllabs.com/ssltest/)

---

## 🎯 推奨設定

本番環境では以下の設定を推奨します：

1. **Cloud Run ドメインマッピング** - シンプルで無料
2. **Cloud CDN** - グローバル配信とキャッシング
3. **Cloud Armor** - DDoS保護とWAF
4. **Cloud Monitoring** - アラート設定
5. **カスタムドメイン** - プロフェッショナルなブランディング

---

**作成日時**: 2025-10-14
**更新日時**: 2025-10-14

🎊 **カスタムドメイン設定ガイド完成！** 🎊
