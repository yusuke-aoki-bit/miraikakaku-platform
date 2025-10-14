#!/bin/bash

# カスタムドメイン設定スクリプト
# Usage: bash setup_custom_domain.sh <your-domain.com>

set -e  # エラーで停止

# 設定
PROJECT_ID="pricewise-huqkr"
REGION="us-central1"
FRONTEND_SERVICE="miraikakaku-frontend"
API_SERVICE="miraikakaku-api"

# カラーコード
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Miraikakaku カスタムドメイン設定    ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ドメイン名の入力
if [ -z "$1" ]; then
    echo -e "${YELLOW}ドメイン名を入力してください（例: miraikakaku.com）:${NC}"
    read DOMAIN
else
    DOMAIN=$1
fi

echo ""
echo -e "${GREEN}✓ ドメイン: ${DOMAIN}${NC}"
echo -e "${GREEN}✓ プロジェクト: ${PROJECT_ID}${NC}"
echo -e "${GREEN}✓ リージョン: ${REGION}${NC}"
echo ""

# 確認
echo -e "${YELLOW}以下のドメインマッピングを作成します:${NC}"
echo "  - www.${DOMAIN} → ${FRONTEND_SERVICE}"
echo "  - ${DOMAIN} → ${FRONTEND_SERVICE}"
echo "  - api.${DOMAIN} → ${API_SERVICE}"
echo ""
echo -e "${YELLOW}続行しますか? (y/n):${NC}"
read CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo -e "${RED}キャンセルしました${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ステップ1: プロジェクト設定        ${NC}"
echo -e "${BLUE}========================================${NC}"

gcloud config set project ${PROJECT_ID}
echo -e "${GREEN}✓ プロジェクト設定完了${NC}"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ステップ2: フロントエンドマッピング ${NC}"
echo -e "${BLUE}========================================${NC}"

# www.domain.com
echo -e "${YELLOW}www.${DOMAIN} をマッピング中...${NC}"
gcloud run domain-mappings create \
  --service=${FRONTEND_SERVICE} \
  --domain=www.${DOMAIN} \
  --region=${REGION} \
  --project=${PROJECT_ID} 2>&1 || echo -e "${YELLOW}既に存在する可能性があります${NC}"

echo -e "${GREEN}✓ www.${DOMAIN} マッピング完了${NC}"
echo ""

# domain.com (ルートドメイン)
echo -e "${YELLOW}${DOMAIN} をマッピング中...${NC}"
gcloud run domain-mappings create \
  --service=${FRONTEND_SERVICE} \
  --domain=${DOMAIN} \
  --region=${REGION} \
  --project=${PROJECT_ID} 2>&1 || echo -e "${YELLOW}既に存在する可能性があります${NC}"

echo -e "${GREEN}✓ ${DOMAIN} マッピング完了${NC}"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ステップ3: APIマッピング            ${NC}"
echo -e "${BLUE}========================================${NC}"

# api.domain.com
echo -e "${YELLOW}api.${DOMAIN} をマッピング中...${NC}"
gcloud run domain-mappings create \
  --service=${API_SERVICE} \
  --domain=api.${DOMAIN} \
  --region=${REGION} \
  --project=${PROJECT_ID} 2>&1 || echo -e "${YELLOW}既に存在する可能性があります${NC}"

echo -e "${GREEN}✓ api.${DOMAIN} マッピング完了${NC}"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ステップ4: DNS設定情報を取得        ${NC}"
echo -e "${BLUE}========================================${NC}"

echo ""
echo -e "${YELLOW}以下のDNSレコードをドメインプロバイダーに設定してください:${NC}"
echo ""

# www.domain.com のDNS設定
echo -e "${BLUE}【 www.${DOMAIN} 用 】${NC}"
gcloud run domain-mappings describe www.${DOMAIN} \
  --region=${REGION} \
  --format="table(status.resourceRecords[].type, status.resourceRecords[].name, status.resourceRecords[].rrdata)" 2>&1 || echo -e "${RED}情報取得失敗${NC}"

echo ""

# domain.com のDNS設定
echo -e "${BLUE}【 ${DOMAIN} 用 】${NC}"
gcloud run domain-mappings describe ${DOMAIN} \
  --region=${REGION} \
  --format="table(status.resourceRecords[].type, status.resourceRecords[].name, status.resourceRecords[].rrdata)" 2>&1 || echo -e "${RED}情報取得失敗${NC}"

echo ""

# api.domain.com のDNS設定
echo -e "${BLUE}【 api.${DOMAIN} 用 】${NC}"
gcloud run domain-mappings describe api.${DOMAIN} \
  --region=${REGION} \
  --format="table(status.resourceRecords[].type, status.resourceRecords[].name, status.resourceRecords[].rrdata)" 2>&1 || echo -e "${RED}情報取得失敗${NC}"

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  DNS設定例（Google Domainsの場合）  ${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "ホスト名 | タイプ | TTL | データ"
echo "---------|-------|-----|-------"
echo "www      | A     | 300 | 216.239.32.21"
echo "www      | A     | 300 | 216.239.34.21"
echo "www      | A     | 300 | 216.239.36.21"
echo "www      | A     | 300 | 216.239.38.21"
echo "@        | A     | 300 | 216.239.32.21"
echo "@        | A     | 300 | 216.239.34.21"
echo "@        | A     | 300 | 216.239.36.21"
echo "@        | A     | 300 | 216.239.38.21"
echo "api      | A     | 300 | 216.239.32.21"
echo "api      | A     | 300 | 216.239.34.21"
echo "api      | A     | 300 | 216.239.36.21"
echo "api      | A     | 300 | 216.239.38.21"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ステップ5: 環境変数の更新           ${NC}"
echo -e "${BLUE}========================================${NC}"

echo ""
echo -e "${YELLOW}フロントエンドの環境変数を更新中...${NC}"
gcloud run services update ${FRONTEND_SERVICE} \
  --set-env-vars="NEXT_PUBLIC_API_URL=https://api.${DOMAIN}" \
  --region=${REGION} \
  --project=${PROJECT_ID}

echo -e "${GREEN}✓ フロントエンド環境変数更新完了${NC}"
echo ""

echo -e "${YELLOW}バックエンドの環境変数を更新中...${NC}"
gcloud run services update ${API_SERVICE} \
  --set-env-vars="ALLOWED_ORIGINS=https://www.${DOMAIN},https://${DOMAIN}" \
  --region=${REGION} \
  --project=${PROJECT_ID}

echo -e "${GREEN}✓ バックエンド環境変数更新完了${NC}"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  完了！                              ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}✓ ドメインマッピングが完了しました！${NC}"
echo ""
echo -e "${YELLOW}次のステップ:${NC}"
echo "1. DNSレコードを設定してください（上記参照）"
echo "2. DNS伝播を待ちます（5-15分、最大48時間）"
echo "3. SSL証明書が自動発行されるまで待ちます（5-15分）"
echo ""
echo -e "${YELLOW}確認コマンド:${NC}"
echo "  nslookup www.${DOMAIN}"
echo "  curl -I https://www.${DOMAIN}"
echo "  curl -I https://api.${DOMAIN}/health"
echo ""
echo -e "${YELLOW}ステータス確認:${NC}"
echo "  gcloud run domain-mappings describe www.${DOMAIN} --region=${REGION}"
echo ""
echo -e "${GREEN}🎉 セットアップ完了！${NC}"
