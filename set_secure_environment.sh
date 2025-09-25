#!/bin/bash
# セキュアな環境変数設定スクリプト
# 本番環境での実行用

echo "🔐 MiraiKakaku セキュア環境変数設定"
echo "===================================="

# 必要な環境変数をチェック・設定
check_and_set_env() {
    local var_name="$1"
    local description="$2"
    local is_secret="${3:-false}"

    if [ -z "${!var_name}" ]; then
        echo -n "⚠️  $var_name が設定されていません。"
        echo -n "$description: "
        if [ "$is_secret" = "true" ]; then
            read -s value
            echo
        else
            read value
        fi
        export "$var_name"="$value"
        echo "✅ $var_name 設定完了"
    else
        if [ "$is_secret" = "true" ]; then
            echo "✅ $var_name 設定済み (非表示)"
        else
            echo "✅ $var_name = ${!var_name}"
        fi
    fi
}

# データベース設定
echo ""
echo "📊 データベース設定"
check_and_set_env "DB_HOST" "データベースホスト名"
check_and_set_env "DB_PORT" "データベースポート (通常5432)"
check_and_set_env "DB_NAME" "データベース名"
check_and_set_env "DB_USER" "データベースユーザー名"
check_and_set_env "DB_PASSWORD" "データベースパスワード" true

# GCP設定
echo ""
echo "☁️  Google Cloud Platform設定"
check_and_set_env "GCP_PROJECT_ID" "GCPプロジェクトID"
check_and_set_env "USE_SECRET_MANAGER" "Secret Manager使用 (true/false)"

# API設定
echo ""
echo "🌐 API設定"
check_and_set_env "API_URL" "API URL"
check_and_set_env "FRONTEND_URL" "フロントエンドURL"

# セキュリティ設定
echo ""
echo "🔐 セキュリティ設定"
check_and_set_env "JWT_SECRET_KEY" "JWT秘密鍵" true
check_and_set_env "SESSION_SECRET" "セッション秘密鍵" true

# 外部API設定
echo ""
echo "📡 外部API設定"
check_and_set_env "ALPHA_VANTAGE_API_KEY" "Alpha Vantage APIキー" true

echo ""
echo "✅ 環境変数設定完了"
echo ""
echo "💡 推奨事項:"
echo "   1. 本番環境ではGoogle Secret Managerを使用してください"
echo "   2. 環境変数を.envファイルに保存し、.gitignoreに追加してください"
echo "   3. 定期的にパスワードをローテーションしてください"

# .envファイル生成
if [ "$1" = "--save" ]; then
    echo ""
    echo "💾 .envファイルを生成中..."

    cat > .env.production << EOF
# MiraiKakaku Production Environment Variables
# Generated: $(date)

# Database Configuration
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# Google Cloud Platform
GCP_PROJECT_ID=${GCP_PROJECT_ID}
USE_SECRET_MANAGER=${USE_SECRET_MANAGER}

# API Configuration
API_URL=${API_URL}
FRONTEND_URL=${FRONTEND_URL}

# Security
JWT_SECRET_KEY=${JWT_SECRET_KEY}
SESSION_SECRET=${SESSION_SECRET}

# External APIs
ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY}
EOF

    echo "✅ .env.productionファイルを生成しました"
    echo "⚠️  重要: このファイルをGitリポジトリにコミットしないでください"
fi

echo ""
echo "🚀 セットアップ完了！システムの起動が可能です"