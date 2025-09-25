#!/bin/bash
# セキュアな環境変数設定スクリプト
# 本番環境での実行用

echo "🔐 MiraiKakaku セキュアな環境設定"
echo "=================================="

# 環境変数の設定を促す
cat << EOF

以下の環境変数を設定してください：

# データベース設定
export DB_HOST="<your-db-host>"
export DB_PORT="5432"
export DB_NAME="miraikakaku"
export DB_USER="postgres"
export DB_PASSWORD="<secure-password>"

# セキュリティキー（ランダム生成推奨）
export JWT_SECRET_KEY="$(openssl rand -base64 64)"
export SESSION_SECRET="$(openssl rand -base64 32)"

# 外部サービス
export ALPHA_VANTAGE_API_KEY="<your-api-key>"
export GRAFANA_PASSWORD="$(openssl rand -base64 16)"

# CORS設定
export ALLOWED_ORIGINS="https://your-domain.com"

Google Cloud Secret Managerの使用を推奨：
gcloud secrets create db-password --data-file=- <<< "$DB_PASSWORD"
gcloud secrets create jwt-secret --data-file=- <<< "$JWT_SECRET_KEY"
gcloud secrets create grafana-password --data-file=- <<< "$GRAFANA_PASSWORD"

EOF

# .gitignoreに追加
echo "🔒 .gitignoreの更新"
cat >> .gitignore << EOF

# Security - Never commit these
.env
.env.local
.env.backup
*.pem
*.key
*.cert
*-credentials.json
gcp-service-account.json
.env.encrypted
EOF

echo "✅ セキュア設定の準備が完了しました"