#!/bin/bash

# Miraikakaku Batch Deployment Script
# 3つのバッチジョブをデプロイするスクリプト

set -e

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 設定
PROJECT_ID="pricewise-huqkr"
REGION="us-central1"
IMAGE_NAME="batch"
REPOSITORY="miraikakaku-docker"

echo -e "${GREEN}🚀 Miraikakaku Batch Deployment開始${NC}"

# 1. Docker イメージのビルドとプッシュ
echo -e "${YELLOW}📦 Docker イメージをビルド中...${NC}"
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:latest .

echo -e "${YELLOW}📤 Docker イメージをプッシュ中...${NC}"
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:latest

# 2. バッチジョブのサブミット関数
submit_batch_job() {
    local JOB_TYPE=$1
    local JOB_MODE=$2
    local JOB_NAME="${JOB_TYPE}-${JOB_MODE}-$(date +%Y%m%d-%H%M%S)"

    echo -e "${YELLOW}🔄 ${JOB_TYPE} ${JOB_MODE} ジョブをサブミット中...${NC}"

    gcloud batch jobs submit ${JOB_NAME} \
        --location=${REGION} \
        --config=- <<EOF
{
  "taskGroups": [{
    "taskSpec": {
      "runnables": [{
        "container": {
          "imageUri": "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:latest"
        }
      }],
      "computeResource": {
        "cpuMilli": $([ "$JOB_MODE" = "update" ] && echo "4000" || echo "2000"),
        "memoryMib": $([ "$JOB_MODE" = "update" ] && echo "8192" || echo "4096")
      },
      "maxRunDuration": "$([ "$JOB_MODE" = "update" ] && echo "7200s" || echo "1800s")",
      "maxRetryCount": $([ "$JOB_MODE" = "update" ] && echo "1" || echo "2"),
      "environment": {
        "variables": {
          "BATCH_TYPE": "${JOB_TYPE}",
          "BATCH_MODE": "${JOB_MODE}",
          "DB_HOST": "34.173.9.214",
          "DB_NAME": "miraikakaku",
          "DB_USER": "postgres",
          "DB_PASSWORD": "tu51b!n6vyaO4KMPJ5!!sHkv"
        }
      }
    },
    "taskCount": 1
  }],
  "logsPolicy": {
    "destination": "CLOUD_LOGGING"
  }
}
EOF

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ ${JOB_TYPE} ${JOB_MODE} ジョブ (${JOB_NAME}) をサブミットしました${NC}"
    else
        echo -e "${RED}❌ ${JOB_TYPE} ${JOB_MODE} ジョブのサブミットに失敗しました${NC}"
    fi
}

# 3. メニュー表示
echo -e "${GREEN}実行するジョブを選択してください:${NC}"
echo "1) 銘柄確認 (Symbol Verify)"
echo "2) 銘柄追加 (Symbol Add)"
echo "3) 価格確認 (Price Verify)"
echo "4) 価格更新 (Price Update)"
echo "5) 予測確認 (Prediction Verify)"
echo "6) 予測更新 (Prediction Update)"
echo "7) すべての確認ジョブを実行"
echo "8) すべての更新ジョブを実行"
echo "9) テスト実行（銘柄確認のみ）"
echo "0) 終了"

read -p "選択してください [0-9]: " choice

case $choice in
    1)
        submit_batch_job "symbol" "verify"
        ;;
    2)
        submit_batch_job "symbol" "add"
        ;;
    3)
        submit_batch_job "price" "verify"
        ;;
    4)
        submit_batch_job "price" "update"
        ;;
    5)
        submit_batch_job "prediction" "verify"
        ;;
    6)
        submit_batch_job "prediction" "update"
        ;;
    7)
        echo -e "${YELLOW}すべての確認ジョブを実行します${NC}"
        submit_batch_job "symbol" "verify"
        submit_batch_job "price" "verify"
        submit_batch_job "prediction" "verify"
        ;;
    8)
        echo -e "${YELLOW}すべての更新ジョブを実行します${NC}"
        submit_batch_job "symbol" "add"
        submit_batch_job "price" "update"
        submit_batch_job "prediction" "update"
        ;;
    9)
        echo -e "${YELLOW}テスト実行：銘柄確認のみ${NC}"
        submit_batch_job "symbol" "verify"
        ;;
    0)
        echo -e "${GREEN}終了します${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}無効な選択です${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}✅ デプロイ完了${NC}"
echo -e "${YELLOW}ジョブの状態を確認するには: gcloud batch jobs list --location=${REGION}${NC}"