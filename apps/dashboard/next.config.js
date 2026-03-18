/** @type {import('next').NextConfig} */
if (process.env.NODE_ENV === 'development') {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.encypherai.com/api/v1';
  console.info(`[dashboard] NEXT_PUBLIC_API_URL (startup): ${apiBaseUrl}`);
}

const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  webpack(config) {
    config.resolve.alias = {
      ...config.resolve.alias,
      three: require.resolve('three'),
    };
    return config;
  },
  allowedDevOrigins: [
    "s-dashboard.encypherai.com",
    "http://localhost:3001",
    "http://127.0.0.1:3001"
  ],
  transpilePackages: ['@encypher/design-system'],

  // Optimize for production


  // Image optimization
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'dashboard.encypherai.com', pathname: '/**' },
      { protocol: 'https', hostname: 'api.encypherai.com', pathname: '/**' },
      { protocol: 'https', hostname: 'encypherai.com', pathname: '/**' },
      { protocol: 'https', hostname: 'www.encypherai.com', pathname: '/**' },
      { protocol: 'http', hostname: 'localhost', pathname: '/**' },
      { protocol: 'http', hostname: '127.0.0.1', pathname: '/**' },
    ],
    formats: ['image/avif', 'image/webp'],
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://api.encypherai.com/api/v1',
    NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL || 'https://encypherai.com',
  },

  // Headers for security
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
