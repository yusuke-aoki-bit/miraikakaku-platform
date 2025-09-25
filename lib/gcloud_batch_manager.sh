#!/bin/bash
#
# Google Cloud Batch Job Manager for Miraikakaku
# 様々なバッチタイプを管理・実行するスクリプト
#

set -e

# 設定変数
PROJECT_ID="pricewise-huqkr"
REGION="us-central1"
IMAGE_URI="us-central1-docker.pkg.dev/${PROJECT_ID}/miraikakaku/miraikakaku-batch-production:latest"

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 使用方法表示
show_usage() {
    echo "使用方法: $0 [COMMAND] [BATCH_TYPE] [OPTIONS]"
    echo ""
    echo "COMMANDS:"
    echo "  submit        バッチジョブを送信"
    echo "  list          実行中のジョブ一覧"
    echo "  status        特定ジョブのステータス確認"
    echo "  logs          ジョブのログ表示"
    echo "  delete        ジョブ削除"
    echo "  build         Dockerイメージビルド"
    echo ""
    echo "BATCH_TYPES:"
    echo "  symbol            - シンボル管理"
    echo "  enhanced_symbol   - 拡張シンボル管理"
    echo "  price            - 価格データ収集"
    echo "  multi_source_price - 複数ソース価格データ"
    echo "  prediction       - 予測データ生成"
    echo ""
    echo "例:"
    echo "  $0 submit symbol"
    echo "  $0 list"
    echo "  $0 status symbol-job-20231122-001"
    echo "  $0 logs symbol-job-20231122-001"
}

# Dockerイメージビルド
build_image() {
    log_info "Dockerイメージをビルド中..."

    cd miraikakakubatch

    # Cloud Buildでビルド
    gcloud builds submit \
        --config cloudbuild.batch.yaml \
        --region=${REGION} \
        --project=${PROJECT_ID} .

    log_success "Dockerイメージビルド完了"
}

# バッチジョブ送信
submit_job() {
    local batch_type=$1
    local job_name="${batch_type}-job-$(date +%Y%m%d-%H%M%S)"

    log_info "バッチジョブ送信中: ${job_name} (タイプ: ${batch_type})"

    # 一時的なジョブ設定ファイル作成
    local temp_job_file="/tmp/${job_name}.yaml"

    cat > "${temp_job_file}" <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: ${job_name}
spec:
  taskGroups:
  - taskSpec:
      runnables:
      - container:
          imageUri: ${IMAGE_URI}
          env:
            - name: BATCH_TYPE
              value: "${batch_type}"
            - name: DB_HOST
              value: "34.173.9.214"
            - name: DB_USER
              value: "postgres"
            - name: DB_PASSWORD
              value: "${DB_PASSWORD}"
            - name: DB_NAME
              value: "miraikakaku"
            - name: PYTHONUNBUFFERED
              value: "1"
            - name: PYTHONPATH
              value: "/app"
          resources:
            cpuMilli: 2000
            memoryMib: 4096
      computeResource:
        cpuMilli: 2000
        memoryMib: 4096
      maxRetryCount: 3
      maxRunDuration: "3600s"
    taskCount: 1
    parallelism: 1
  allocationPolicy:
    instances:
    - policy:
        machineType: e2-standard-2
        provisioningModel: STANDARD
    location:
      allowedLocations:
      - "regions/${REGION}"
  logsPolicy:
    destination: CLOUD_LOGGING
EOF

    # ジョブ送信
    gcloud batch jobs submit ${job_name} \
        --location=${REGION} \
        --config="${temp_job_file}" \
        --project=${PROJECT_ID}

    # 一時ファイル削除
    rm -f "${temp_job_file}"

    log_success "ジョブ送信完了: ${job_name}"
    echo "ステータス確認: $0 status ${job_name}"
    echo "ログ確認: $0 logs ${job_name}"
}

# ジョブ一覧表示
list_jobs() {
    log_info "実行中のバッチジョブ一覧:"
    gcloud batch jobs list \
        --location=${REGION} \
        --project=${PROJECT_ID} \
        --format="table(name,createTime,state)"
}

# ジョブステータス確認
check_status() {
    local job_name=$1

    if [ -z "$job_name" ]; then
        log_error "ジョブ名を指定してください"
        show_usage
        exit 1
    fi

    log_info "ジョブステータス確認: ${job_name}"
    gcloud batch jobs describe ${job_name} \
        --location=${REGION} \
        --project=${PROJECT_ID}
}

# ジョブログ表示
show_logs() {
    local job_name=$1

    if [ -z "$job_name" ]; then
        log_error "ジョブ名を指定してください"
        show_usage
        exit 1
    fi

    log_info "ジョブログ表示: ${job_name}"
    gcloud logging read "resource.type=\"gce_instance\" AND labels.job_name=\"${job_name}\"" \
        --limit=50 \
        --format="table(timestamp,severity,textPayload)" \
        --project=${PROJECT_ID}
}

# ジョブ削除
delete_job() {
    local job_name=$1

    if [ -z "$job_name" ]; then
        log_error "ジョブ名を指定してください"
        show_usage
        exit 1
    fi

    log_warning "ジョブ削除: ${job_name}"
    read -p "本当に削除しますか? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud batch jobs delete ${job_name} \
            --location=${REGION} \
            --project=${PROJECT_ID} \
            --quiet
        log_success "ジョブ削除完了: ${job_name}"
    else
        log_info "削除をキャンセルしました"
    fi
}

# メイン処理
main() {
    case $1 in
        submit)
            if [ -z "$2" ]; then
                log_error "バッチタイプを指定してください"
                show_usage
                exit 1
            fi
            submit_job $2
            ;;
        list)
            list_jobs
            ;;
        status)
            check_status $2
            ;;
        logs)
            show_logs $2
            ;;
        delete)
            delete_job $2
            ;;
        build)
            build_image
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "無効なコマンド: $1"
            show_usage
            exit 1
            ;;
    esac
}

# 引数チェック
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# メイン処理実行
main "$@"