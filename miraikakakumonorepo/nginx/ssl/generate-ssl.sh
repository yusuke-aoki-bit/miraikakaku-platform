#!/bin/bash

# 開発用SSL証明書生成スクリプト
# 本番環境ではLet's EncryptやCloud Load Balancerを使用

echo "開発用SSL証明書を生成中..."

# 秘密鍵生成
openssl genrsa -out key.pem 2048

# 証明書署名要求 (CSR) 生成
openssl req -new -key key.pem -out cert.csr -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Miraikakaku/OU=Development/CN=localhost"

# 自己署名証明書生成
openssl x509 -req -days 365 -in cert.csr -signkey key.pem -out cert.pem

# CSRファイルを削除
rm cert.csr

echo "SSL証明書生成完了:"
echo "  - 証明書: cert.pem"
echo "  - 秘密鍵: key.pem"
echo ""
echo "⚠️  これは開発用の自己署名証明書です。"
echo "   本番環境では適切なSSL証明書を使用してください。"