#!/bin/bash

# デュアルドメイン設定スクリプト
# miraikakaku.com と price-wiser.com の両方を設定

set -e

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
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  デュアルドメイン設定スクリプト      ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ドメイン定義
DOMAIN1="miraikakaku.com"
DOMAIN2="price-wiser.com"

echo -e "${GREEN}設定するドメイン:${NC}"
echo "  1. ${DOMAIN1}"
echo "  2. ${DOMAIN2}"
echo ""
echo -e "${YELLOW}続行しますか? (y/n):${NC}"
read CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo -e "${RED}キャンセルしました${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  プロジェクト設定                    ${NC}"
echo -e "${BLUE}========================================${NC}"

gcloud config set project ${PROJECT_ID}
echo -e "${GREEN}✓ プロジェクト設定完了${NC}"
echo ""

# ドメイン1の設定
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ドメイン1: ${DOMAIN1}              ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}フロントエンドマッピング中...${NC}"

# www.miraikakaku.com
gcloud run domain-mappings create \
  --service=${FRONTEND_SERVICE} \
  --domain=www.${DOMAIN1} \
  --region=${REGION} \
  --project=${PROJECT_ID} 2>&1 || echo -e "${YELLOW}既に存在します${NC}"

echo -e "${GREEN}✓ www.${DOMAIN1}${NC}"

# miraikakaku.com
gcloud run domain-mappings create \
  --service=${FRONTEND_SERVICE} \
  --domain=${DOMAIN1} \
  --region=${REGION} \
  --project=${PROJECT_ID} 2>&1 || echo -e "${YELLOW}既に存在します${NC}"

echo -e "${GREEN}✓ ${DOMAIN1}${NC}"

# api.miraikakaku.com
echo -e "${YELLOW}APIマッピング中...${NC}"
gcloud run domain-mappings create \
  --service=${API_SERVICE} \
  --domain=api.${DOMAIN1} \
  --region=${REGION} \
  --project=${PROJECT_ID} 2>&1 || echo -e "${YELLOW}既に存在します${NC}"

echo -e "${GREEN}✓ api.${DOMAIN1}${NC}"
echo ""

# ドメイン2の設定
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ドメイン2: ${DOMAIN2}              ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}フロントエンドマッピング中...${NC}"

# www.price-wiser.com
gcloud run domain-mappings create \
  --service=${FRONTEND_SERVICE} \
  --domain=www.${DOMAIN2} \
  --region=${REGION} \
  --project=${PROJECT_ID} 2>&1 || echo -e "${YELLOW}既に存在します${NC}"

echo -e "${GREEN}✓ www.${DOMAIN2}${NC}"

# price-wiser.com
gcloud run domain-mappings create \
  --service=${FRONTEND_SERVICE} \
  --domain=${DOMAIN2} \
  --region=${REGION} \
  --project=${PROJECT_ID} 2>&1 || echo -e "${YELLOW}既に存在します${NC}"

echo -e "${GREEN}✓ ${DOMAIN2}${NC}"

# api.price-wiser.com
echo -e "${YELLOW}APIマッピング中...${NC}"
gcloud run domain-mappings create \
  --service=${API_SERVICE} \
  --domain=api.${DOMAIN2} \
  --region=${REGION} \
  --project=${PROJECT_ID} 2>&1 || echo -e "${YELLOW}既に存在します${NC}"

echo -e "${GREEN}✓ api.${DOMAIN2}${NC}"
echo ""

# DNS設定情報を取得
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  DNS設定情報                         ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}【 ${DOMAIN1} 用DNSレコード 】${NC}"
echo ""
echo "以下のAレコードをDNSプロバイダーに設定してください:"
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

echo -e "${YELLOW}【 ${DOMAIN2} 用DNSレコード 】${NC}"
echo ""
echo "以下のAレコードをDNSプロバイダーに設定してください:"
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

# 環境変数の更新
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  環境変数の更新                      ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}フロントエンドの環境変数を更新中...${NC}"
gcloud run services update ${FRONTEND_SERVICE} \
  --set-env-vars="NEXT_PUBLIC_API_URL=https://api.${DOMAIN1}" \
  --region=${REGION} \
  --project=${PROJECT_ID}

echo -e "${GREEN}✓ フロントエンド環境変数更新完了${NC}"
echo ""

echo -e "${YELLOW}バックエンドの環境変数を更新中...${NC}"
gcloud run services update ${API_SERVICE} \
  --set-env-vars="ALLOWED_ORIGINS=https://www.${DOMAIN1},https://${DOMAIN1},https://www.${DOMAIN2},https://${DOMAIN2}" \
  --region=${REGION} \
  --project=${PROJECT_ID}

echo -e "${GREEN}✓ バックエンド環境変数更新完了${NC}"
echo ""

# 完了メッセージ
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  完了！                              ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}✓ デュアルドメイン設定が完了しました！${NC}"
echo ""
echo -e "${YELLOW}設定されたURL:${NC}"
echo "  - https://www.${DOMAIN1}"
echo "  - https://${DOMAIN1}"
echo "  - https://api.${DOMAIN1}"
echo "  - https://www.${DOMAIN2}"
echo "  - https://${DOMAIN2}"
echo "  - https://api.${DOMAIN2}"
echo ""
echo -e "${YELLOW}次のステップ:${NC}"
echo "1. 上記のDNSレコードを両方のドメインプロバイダーに設定"
echo "2. DNS伝播を待つ（5-15分、最大48時間）"
echo "3. SSL証明書の自動発行を待つ（5-15分）"
echo ""
echo -e "${YELLOW}確認コマンド:${NC}"
echo "  nslookup www.${DOMAIN1}"
echo "  nslookup www.${DOMAIN2}"
echo "  curl -I https://www.${DOMAIN1}"
echo "  curl -I https://www.${DOMAIN2}"
echo ""
echo -e "${GREEN}🎉 セットアップ完了！${NC}"
