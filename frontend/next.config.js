/** @type {import('next').NextConfig} */
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
  // Configuration Turbopack pour éviter les conflits avec webpack
  turbopack: {
    // Configuration minimale pour Turbopack
  },
}

module.exports = nextConfig
