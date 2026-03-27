// eslint-disable-next-line
const path = require('path');
// eslint-disable-next-line
const dotenv = require('dotenv');
const fs = require('fs');

// Try to load environment variables from multiple possible files
// Order of precedence: process.env > .env.production > .env.local > .env
const envFiles = ['.env.production', '.env.local', '.env'];

for (const file of envFiles) {
  const envPath = path.resolve(process.cwd(), file);
  try {
    if (fs.existsSync(envPath)) {
      console.log(`[Next Config] Loading environment variables from ${file}`);
      dotenv.config({ path: envPath });
    }
  } catch (error) {
    console.warn(`[Next Config] Error loading ${file}: ${error.message}`);
  }
}

/** @type {import('next').NextConfig} */
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://backend.encypher.com';
console.log(`[Next Config] Using API base URL: ${apiBaseUrl}`);

// No longer throwing an error if the variable isn't set - using default value instead
// if (!apiBaseUrl) {
//   throw new Error("NEXT_PUBLIC_API_BASE_URL is not set. Please define it in your environment or .env.production.");
// }

const nextConfig = {
  // Enable compression
  compress: true,
  webpack(config) {
    config.resolve.alias = {
      ...config.resolve.alias,
      three: require.resolve('three'),
    };
    return config;
  },
  // Optimize production builds
  productionBrowserSourceMaps: false,
  // Optimize React
  reactStrictMode: true,
  poweredByHeader: false,
  // Transpile the design system package
  transpilePackages: ['@encypher/design-system'],
  allowedDevOrigins: [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:52924",
    "http://127.0.0.1:52924",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "s-www.encypher.com"
  ],
  async headers() {
    // Security headers applied to all routes
    const securityHeaders = [
      {
        key: 'X-DNS-Prefetch-Control',
        value: 'on',
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
        value: 'strict-origin-when-cross-origin',
      },
      {
        key: 'Permissions-Policy',
        value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()',
      },
    ];

    return [
      {
        // Apply security headers to all routes
        source: '/:path*',
        headers: securityHeaders,
      },
      {
        source: '/:all*(svg|jpg|jpeg|png|webp|avif|gif|ico)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
          ...securityHeaders,
        ],
      },
      {
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
  async redirects() {
    return [
      { source: '/features', destination: '/platform', permanent: true },

      { source: '/about', destination: '/company', permanent: true },

      { source: '/tools/encode-decode', destination: '/tools/sign-verify', permanent: true },
      { source: '/tools/encode', destination: '/tools/sign', permanent: true },
      { source: '/tools/decode', destination: '/tools/verify', permanent: true },
    ];
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/tools/:path*',
        destination: apiBaseUrl + '/api/v1/tools/:path*',
      },
    ];
  },
  // Disable ESLint during production builds
  eslint: {
    // Warning rather than error
    ignoreDuringBuilds: true,
  },
  // Disable TypeScript type checking during builds
  typescript: {
    // Handled by IDE/local development
    ignoreBuildErrors: true,
  },
  // Enable standalone output mode for Docker deployment
  output: 'standalone',
  // Disable static optimization for pages that use client-side features
  experimental: {
    // This prevents Next.js from attempting to statically optimize pages that use client features
    optimizeCss: false,
    // Increase the timeout for static generation
    // staticPageGenerationTimeout: 180, // Commented out due to deprecation and warnings
  },
  // Optimize JavaScript output for modern browsers
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production' ? { exclude: ['error', 'warn'] } : false,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'i.ytimg.com',
      },
    ],
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 60,
  },
  // Optimize bundle size
  // Note: lucide-react modularization removed due to icon naming conflicts
  // The package already tree-shakes well with modern bundlers
};

module.exports = nextConfig;
