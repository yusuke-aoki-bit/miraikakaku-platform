FROM python:3.11-slim

WORKDIR /app

# システム依存関係をインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    cron \
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

# バッチ処理用のポートを公開（メトリクス用）
EXPOSE 8001

# ヘルスチェック（軽量チェック）
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# バッチ処理メイン実行
CMD ["python", "main.py"]