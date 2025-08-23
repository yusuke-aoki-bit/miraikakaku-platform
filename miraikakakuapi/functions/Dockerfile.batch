FROM python:3.11-slim

WORKDIR /app

# 必要なシステムパッケージをインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 要件をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 追加パッケージ（バッチ処理用）
RUN pip install schedule

# アプリケーションファイルをコピー
COPY . .

# 環境変数
ENV PYTHONPATH=/app
ENV PORT=8080

# ヘルスチェック用のシンプルサーバーを含むエントリーポイント
COPY docker-entrypoint.py .
EXPOSE 8080

CMD ["python", "docker-entrypoint.py"]