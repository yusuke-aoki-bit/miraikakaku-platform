FROM node:18-alpine

WORKDIR /app

# 依存関係のコピーとインストール
COPY package*.json ./
RUN npm ci --only=production

# アプリケーションファイルのコピー
COPY . .

# ビルド
RUN npm run build

# ポート公開
EXPOSE 3000

# 起動
CMD ["npm", "start"]
