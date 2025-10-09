import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // パフォーマンス最適化
  reactStrictMode: true,

  // Dockerデプロイ用
  output: 'standalone',

  // ESLint設定（ビルド時は警告のみ許容）
  eslint: {
    ignoreDuringBuilds: true,
  },

  // TypeScript設定
  typescript: {
    ignoreBuildErrors: true,
  },

  // 画像最適化
  images: {
    domains: [],
    formats: ['image/avif', 'image/webp'],
  },

  // セキュリティヘッダー
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()'
          }
        ]
      }
    ];
  },

  // コンパイル最適化
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Experimental features
  experimental: {
    optimizePackageImports: ['recharts'],
  },
};

export default nextConfig;
