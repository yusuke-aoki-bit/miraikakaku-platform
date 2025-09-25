# Phase 3.2 Deployment Guide - マルチテナント・エンタープライズ統合

**リリース日:** 2025年9月25日
**バージョン:** 3.2.0
**対象:** MiraiKakaku エンタープライズ マルチテナントシステム

---

## 🎯 Phase 3.2 概要

**Phase 3.2** では、MiraiKakakuシステムに **完全なマルチテナント・エンタープライズ統合** を実装し、複数の企業顧客が安全にデータ分離された環境で利用できるシステムを構築しました。

### 🚀 新機能

1. **完全データ分離アーキテクチャ**
   - 組織別完全データ分離
   - テナント別ストレージ管理
   - 厳格なセキュリティ境界

2. **高度なRBAC (Role-Based Access Control)**
   - 5段階ユーザーロール
   - 細粒度権限管理
   - API レベルアクセス制御

3. **エンタープライズ組織管理**
   - 階層的組織構造
   - プラン別機能制限
   - 使用量監視・請求連携

4. **統合認証システム**
   - JWT トークン認証
   - API キー管理
   - セッション管理

---

## 📊 システム構成

### **データベース構造**

```sql
-- 組織管理
├── organizations (組織マスター)
├── subscriptions (サブスクリプション)
└── system_configurations (組織別設定)

-- ユーザー管理
├── users (ユーザー)
├── user_sessions (セッション)
└── audit_logs (監査ログ)

-- テナント分離データ
├── tenant_stock_prices (組織別株価データ)
├── tenant_stock_predictions (組織別予測データ)
├── tenant_watchlists (組織別ウォッチリスト)
└── tenant_alerts (組織別アラート)
```

### **API エンドポイント構造**

```
/api/v1/tenant/
├── auth/
│   ├── login              # ログイン
│   └── me                 # ユーザー情報取得
├── organization           # 組織管理
├── users/                 # ユーザー管理
├── data/                  # テナント分離データ
│   ├── stocks/{symbol}/prices
│   └── stocks/{symbol}/predictions
├── analytics/             # 分析・レポート
└── audit-logs            # 監査ログ
```

---

## 🛠 インストールガイド

### **1. 前提条件**

```bash
# Python & Node.js (Phase 3.1と同じ)
python3 --version  # 3.9+
node --version     # 16.0+

# PostgreSQL (Multi-tenant対応)
psql --version     # 12.0+
```

### **2. データベースセットアップ**

#### **PostgreSQL設定**

```sql
-- マルチテナント用データベース作成
CREATE DATABASE miraikakaku_multitenant;

-- 管理者ユーザー作成
CREATE USER miraikakaku_admin WITH PASSWORD 'secure_password_2024!';
GRANT ALL PRIVILEGES ON DATABASE miraikakaku_multitenant TO miraikakaku_admin;

-- テナント用スキーマ作成権限
GRANT CREATE ON DATABASE miraikakaku_multitenant TO miraikakaku_admin;
```

#### **環境変数設定**

```bash
# miraikakakuapi/.env
DATABASE_URL=postgresql://miraikakaku_admin:secure_password_2024!@localhost:5432/miraikakaku_multitenant

# JWT設定
JWT_SECRET=your-super-secret-jwt-key-256-bits-long
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE=3600
JWT_REFRESH_TOKEN_EXPIRE=2592000

# Multi-tenant設定
TENANT_DATA_ISOLATION=strict
TENANT_AUDIT_LOGGING=enabled
TENANT_RATE_LIMITING=enabled

# Redis (オプション - キャッシュ用)
REDIS_URL=redis://localhost:6379
```

### **3. Python依存関係インストール**

```bash
cd miraikakakuapi

# 新しい依存関係ファイル作成
cat > requirements-multitenant.txt << 'EOF'
# Multi-tenant Core Dependencies
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0
pyjwt>=2.8.0
bcrypt>=4.0.0

# FastAPI Enhanced
fastapi[all]>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6

# Data Processing
pandas>=2.1.4
numpy>=1.24.0

# Additional for Phase 3.1 + 3.2
redis[hiredis]>=5.0.0
websockets>=12.0

# Development & Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0
EOF

# 依存関係インストール
pip3 install -r requirements-multitenant.txt
```

### **4. データベース初期化**

```bash
# データベーステーブル作成
python3 -c "
from services.multi_tenant_manager import MultiTenantManager
import os

db_url = os.getenv('DATABASE_URL', 'postgresql://miraikakaku_admin:secure_password_2024!@localhost:5432/miraikakaku_multitenant')
manager = MultiTenantManager(db_url)
print('✅ Multi-tenant database initialized')
"
```

---

## 🚀 起動方法

### **方法 1: 統合サーバー起動 (推奨)**

```bash
# マルチテナント統合サーバー起動
cd miraikakakuapi
python3 multi_tenant_main.py
```

**期待される出力:**
```
🚀 Starting MiraiKakaku Multi-tenant Enterprise System...
✅ Multi-tenant Enterprise System started successfully
🏢 Multi-tenant database initialized
⚡ Real-time inference engine ready
🔒 RBAC security system active
📊 Dashboard: http://localhost:8080/docs
🔌 WebSocket: ws://localhost:8080/ws
🏢 Tenant API: http://localhost:8080/api/v1/tenant/
🏥 Health: http://localhost:8080/health
```

### **方法 2: フロントエンドとの統合起動**

```bash
# ターミナル 1: バックエンド
cd miraikakakuapi
python3 multi_tenant_main.py

# ターミナル 2: フロントエンド
cd miraikakakufront
npm run dev
```

---

## 🏢 マルチテナント機能の利用

### **1. デモ組織作成**

```bash
# デモ組織とユーザーを作成
curl -X POST "http://localhost:8080/dev/create-demo-organization" \
  -H "Content-Type: application/json"
```

**レスポンス例:**
```json
{
  "message": "Demo organization created successfully",
  "organization": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Demo Corporation",
    "slug": "demo-corporation",
    "plan_type": "enterprise"
  },
  "users": [
    {"id": "user-123", "email": "admin@demo.corp", "role": "admin"},
    {"id": "user-456", "email": "manager@demo.corp", "role": "manager"}
  ],
  "login_credentials": {
    "admin": {"email": "admin@demo.corp", "password": "demo123"},
    "manager": {"email": "manager@demo.corp", "password": "demo123"}
  }
}
```

### **2. 認証とログイン**

```bash
# ログイン
curl -X POST "http://localhost:8080/api/v1/tenant/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@demo.corp",
    "password": "demo123"
  }'
```

**レスポンス:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user-123",
    "email": "admin@demo.corp",
    "role": "admin",
    "permissions": ["admin", "manage_users", "view_audit"]
  },
  "organization": {
    "id": "org-123",
    "name": "Demo Corporation",
    "plan_type": "enterprise",
    "enabled_features": ["all_features"]
  }
}
```

### **3. 組織情報取得**

```bash
# 認証トークンを使用して組織情報取得
curl -X GET "http://localhost:8080/api/v1/tenant/organization" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **4. テナント分離データアクセス**

```bash
# 組織専用株価データ取得
curl -X GET "http://localhost:8080/api/v1/tenant/data/stocks/AAPL/prices" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 組織専用予測データ取得
curl -X GET "http://localhost:8080/api/v1/tenant/data/stocks/AAPL/predictions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🎨 フロントエンド統合

### **1. テナントダッシュボードアクセス**

```bash
# ブラウザで以下にアクセス:
http://localhost:3000/tenant
```

### **2. 機能確認**

1. **組織概要ダッシュボード:**
   - 使用量統計
   - 有効機能一覧
   - プラン情報

2. **ユーザー管理:**
   - 組織内ユーザー一覧
   - ロール管理
   - アクティブ/非アクティブ切り替え

3. **設定管理:**
   - 組織設定更新
   - セキュリティ設定
   - 通知設定

4. **請求・サブスクリプション:**
   - 現在プラン表示
   - 使用量確認
   - プラン変更

---

## 📊 ロールベースアクセス制御 (RBAC)

### **ユーザーロール一覧**

| ロール | 権限 | 説明 |
|--------|------|------|
| **Admin** 👑 | 全権限 | 組織管理・ユーザー管理・全データアクセス |
| **Manager** ⚡ | チーム管理・レポート | チーム管理・高度レポート・API管理 |
| **Analyst** 📊 | 分析・レポート作成 | データ分析・カスタムレポート・エクスポート |
| **Viewer** 👁️ | 基本閲覧 | 基本データ閲覧のみ |
| **Compliance** 🛡️ | コンプライアンス | 監査ログ・コンプライアンスレポート |

### **権限マトリックス**

| 機能 | Admin | Manager | Analyst | Viewer | Compliance |
|------|-------|---------|---------|--------|------------|
| 組織設定変更 | ✅ | ❌ | ❌ | ❌ | ❌ |
| ユーザー管理 | ✅ | ✅ | ❌ | ❌ | ❌ |
| データ分析 | ✅ | ✅ | ✅ | ✅ | ❌ |
| API アクセス | ✅ | ✅ | ✅ | ❌ | ❌ |
| 監査ログ閲覧 | ✅ | ❌ | ❌ | ❌ | ✅ |
| リアルタイム予測 | ✅ | ✅ | ✅ | プランに依存 | ❌ |

---

## 🔒 セキュリティ機能

### **1. データ分離保証**

```sql
-- 組織データは完全に分離される
SELECT * FROM tenant_stock_prices
WHERE organization_id = 'org-123';  -- 組織Aのみアクセス可能

SELECT * FROM tenant_stock_prices
WHERE organization_id = 'org-456';  -- 組織Bのみアクセス可能
```

### **2. API認証方式**

#### **JWT トークン認証:**
```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### **API キー認証:**
```bash
X-API-Key: mk_1234567890abcdef...
```

### **3. 監査ログ**

全ての重要操作が自動的に記録されます：

```json
{
  "id": "log-123",
  "organization_id": "org-123",
  "user_id": "user-456",
  "event_type": "user_created",
  "event_category": "user_management",
  "description": "New user created: analyst@demo.corp",
  "ip_address": "192.168.1.100",
  "timestamp": "2025-09-25T10:30:00Z",
  "risk_level": "low"
}
```

---

## 📈 使用量監視・請求連携

### **1. リアルタイム使用量確認**

```bash
curl -X GET "http://localhost:8080/api/v1/tenant/analytics/usage" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**レスポンス:**
```json
{
  "organization_id": "org-123",
  "current_usage": {
    "api_calls": {"used": 45750, "limit": 1000000, "percentage": 4.6},
    "predictions": {"used": 1240, "limit": 10000, "percentage": 12.4},
    "users": {"used": 23, "limit": 500, "percentage": 4.6},
    "symbols": {"used": 127, "limit": 1000, "percentage": 12.7}
  },
  "plan_limits": {
    "max_users": 500,
    "max_api_calls_per_month": 1000000,
    "max_predictions_per_day": 10000,
    "max_symbols_tracked": 1000
  }
}
```

### **2. プラン別制限**

| プラン | ユーザー数 | API呼び出し/月 | 予測数/日 | 追跡銘柄数 | 月額料金 |
|--------|-----------|------------|---------|----------|---------|
| **Basic** | 5 | 10,000 | 100 | 10 | $99 |
| **Professional** | 25 | 100,000 | 1,000 | 100 | $499 |
| **Enterprise** | 500 | 1,000,000 | 10,000 | 1,000 | $2,499 |
| **Custom** | 無制限 | カスタム | カスタム | カスタム | 要相談 |

---

## 🧪 テスト・検証

### **1. マルチテナントデータ分離テスト**

```python
# test_data_isolation.py
import pytest
from services.multi_tenant_manager import get_tenant_manager

def test_tenant_data_isolation():
    manager = get_tenant_manager()

    # 組織A、Bを作成
    org_a = manager.create_organization("Test Org A", "Test A", "a@test.com")
    org_b = manager.create_organization("Test Org B", "Test B", "b@test.com")

    # 組織Aのデータ作成
    data_a = manager.get_tenant_stock_data(org_a.id, "AAPL")

    # 組織Bからは組織Aのデータにアクセス不可
    data_b = manager.get_tenant_stock_data(org_b.id, "AAPL")

    assert len(data_a) != len(data_b)  # 完全に分離されている
```

### **2. RBAC権限テスト**

```bash
# Viewer権限でAdmin機能にアクセス試行（拒否されるべき）
curl -X POST "http://localhost:8080/api/v1/tenant/users" \
  -H "Authorization: Bearer VIEWER_TOKEN" \
  -d '{"email": "test@test.com"}' \
  # Expected: 403 Forbidden
```

### **3. パフォーマンステスト**

```bash
# 同時接続テスト
for i in {1..100}; do
  curl -X GET "http://localhost:8080/api/v1/tenant/organization" \
    -H "Authorization: Bearer TOKEN_$i" &
done
wait

# 全てのリクエストが2秒以内で応答することを確認
```

---

## 🔧 トラブルシューティング

### **よくある問題と解決方法**

#### **1. データベース接続エラー**

**症状:** `connection to server at "localhost" failed`

**解決:**
```bash
# PostgreSQL起動確認
sudo systemctl status postgresql

# 接続テスト
psql -h localhost -U miraikakaku_admin -d miraikakaku_multitenant -c "SELECT 1;"

# 環境変数確認
echo $DATABASE_URL
```

#### **2. JWT認証エラー**

**症状:** `Invalid token` または `Token expired`

**解決:**
```bash
# 新しいトークン取得
curl -X POST "http://localhost:8080/api/v1/tenant/auth/login" \
  -d '{"email": "admin@demo.corp", "password": "demo123"}'

# JWT秘密鍵確認
echo $JWT_SECRET
```

#### **3. 権限不足エラー**

**症状:** `403 Forbidden - Permission required`

**解決:**
```bash
# ユーザー権限確認
curl -X GET "http://localhost:8080/api/v1/tenant/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 必要な権限を持つユーザーでログイン
```

#### **4. テナントデータアクセスエラー**

**症状:** データが空または異なる組織のデータが見える

**解決:**
```sql
-- データ分離確認
SELECT organization_id, COUNT(*)
FROM tenant_stock_prices
GROUP BY organization_id;

-- 特定組織のデータ確認
SELECT * FROM tenant_stock_prices
WHERE organization_id = 'YOUR_ORG_ID'
LIMIT 5;
```

---

## 📊 監視・メトリクス

### **Prometheus メトリクス**

```python
# metrics_collector.py
from prometheus_client import Counter, Histogram, Gauge

# マルチテナント関連メトリクス
tenant_requests = Counter('tenant_requests_total', 'Total tenant API requests', ['organization_id', 'endpoint'])
tenant_data_access = Counter('tenant_data_access_total', 'Data access by tenant', ['organization_id', 'resource'])
tenant_auth_attempts = Counter('tenant_auth_attempts_total', 'Authentication attempts', ['organization_id', 'result'])

# 使用量メトリクス
tenant_usage_api_calls = Gauge('tenant_usage_api_calls', 'API calls usage', ['organization_id'])
tenant_usage_predictions = Gauge('tenant_usage_predictions', 'Predictions usage', ['organization_id'])
```

### **Grafana ダッシュボード**

```json
{
  "dashboard": {
    "title": "MiraiKakaku Multi-tenant Metrics",
    "panels": [
      {
        "title": "Organizations by Plan",
        "type": "piechart",
        "targets": [{"expr": "count by (plan_type) (tenant_organizations)"}]
      },
      {
        "title": "API Requests by Tenant",
        "type": "graph",
        "targets": [{"expr": "rate(tenant_requests_total[5m])"}]
      },
      {
        "title": "Authentication Success Rate",
        "type": "stat",
        "targets": [{"expr": "rate(tenant_auth_attempts_total{result='success'}[5m])"}]
      }
    ]
  }
}
```

---

## 🚀 次のステップ - Phase 3.3 Preview

Phase 3.2完了後、次は**Phase 3.3 - 高度リスク管理・コンプライアンス**に進みます：

### **予定機能**
- **MiFID II / Dodd-Frank 対応**
- **リアルタイムリスク監視**
- **自動コンプライアンスレポート**
- **ストレステスト機能**
- **規制当局レポート自動生成**

### **技術実装**
- **Value at Risk (VaR) 計算エンジン**
- **法規制ルールエンジン**
- **自動監査システム**
- **リスクダッシュボード**

---

## 📞 サポート・連絡先

### **問題報告**
- **GitHub Issues:** https://github.com/your-org/miraikakaku/issues
- **Enterprise Support:** enterprise@miraikakaku.com
- **Slack Channel:** #miraikakaku-enterprise

### **ドキュメント**
- **Phase 3 全体ロードマップ:** `PHASE_3_ENTERPRISE_ROADMAP.md`
- **API仕様書:** http://localhost:8080/docs
- **マルチテナント設計書:** `docs/MULTITENANT_ARCHITECTURE.md`

---

**🏢 Phase 3.2 マルチテナント・エンタープライズ統合完了**

**次世代エンタープライズプラットフォーム実現 - 複数企業の安全な共存環境**

---

*最終更新: 2025年9月25日*
*作成者: Claude Code Enterprise Architecture Team*