FROM python:3.12-slim

WORKDIR /app

# システム依存関係をインストール（最小限）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    pkg-config \
    libpq-dev \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Python依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY functions/ ./functions/

# 環境変数
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# エントリーポイントスクリプトを作成
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# 非rootユーザーを作成
RUN groupadd -r batchuser && useradd -r -g batchuser batchuser

# ログディレクトリ作成
RUN mkdir -p /app/logs

# 権限設定
RUN chown -R batchuser:batchuser /app
USER batchuser

# バッチタイプに応じた実行
ENTRYPOINT ["/app/entrypoint.sh"]