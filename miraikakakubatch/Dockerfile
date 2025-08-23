FROM python:3.11-slim

WORKDIR /app

# Cloud SQL用システム依存関係をインストール（SQLite削除）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    cron \
    curl \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY functions/ ./

# 非rootユーザーを作成
RUN groupadd -r batchuser && useradd -r -g batchuser batchuser
RUN chown -R batchuser:batchuser /app
USER batchuser

# ログディレクトリ作成
RUN mkdir -p /app/logs

# HTTPサーバー用のポートを公開
EXPOSE 8080

# ヘルスチェック
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# バッチ処理メイン実行 (Enhanced版を使用)
CMD ["python", "enhanced_batch_main.py"]