/** @type {import('next').NextConfig} */
import path from 'path';

const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
    styledComponents: true,
  },
  compress: true,
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },
  // Configuration webpack pour CI/CD
  webpack: (config, { isServer }) => {
    // Pour CI/CD, s'assurer que les chemins sont résolus
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      path: false,
    };

    return config;
  },
}

export default nextConfig
