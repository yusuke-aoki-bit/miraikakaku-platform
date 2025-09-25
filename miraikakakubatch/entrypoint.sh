#!/bin/bash
set -e

# ログ関数
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# 環境変数確認
log_info "Starting Miraikakaku Batch Job"
log_info "BATCH_TYPE: ${BATCH_TYPE:-default}"
log_info "Python version: $(python --version)"
log_info "Working directory: $(pwd)"

# データベース接続確認
log_info "Checking database connection..."
python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='${DB_HOST:-34.173.9.214}',
        user='${DB_USER:-postgres}',
        password='${DB_PASSWORD:-${DB_PASSWORD}}',
        database='${DB_NAME:-miraikakaku}'
    )
    conn.close()
    print('Database connection: OK')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"

# バッチタイプに応じた実行
case "${BATCH_TYPE}" in
    "symbol")
        log_info "Executing symbol management batch"
        python -m functions.stock_symbol_manager
        ;;
    "enhanced_symbol")
        log_info "Executing enhanced symbol management batch"
        python -m functions.enhanced_symbol_manager
        ;;
    "price")
        log_info "Executing price data collection batch"
        python -m functions.price_data_manager
        ;;
    "multi_source_price")
        log_info "Executing multi-source price data batch"
        python -m functions.multi_source_price_manager
        ;;
    "prediction")
        log_info "Executing prediction data generation batch"
        python -m functions.prediction_data_manager
        ;;
    *)
        log_info "Executing default batch (simple_batch_main)"
        python -m functions.simple_batch_main
        ;;
esac

log_info "Batch job completed successfully"