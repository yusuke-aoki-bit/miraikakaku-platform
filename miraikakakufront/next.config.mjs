
/** @type {import('next').NextConfig} */
const nextConfig = {
  // API rewrites for proxying to backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL ? 
          `${process.env.NEXT_PUBLIC_API_URL}/api/:path*` : 
          'http://localhost:8080/api/:path*'
      }
    ];
  },
  
  // Image optimization settings
  images: {
    domains: [],
    formats: ['image/webp', 'image/avif'],
  },
  
  // Performance optimizations
  compress: true,
  
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin'
          }
        ]
      }
    ];
  }
};

export default nextConfig;
