import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  /* config options here */
  output: 'export', // Pour Tauri, on veut une build statique
  images: {
    unoptimized: true, // Nécessaire pour l'export statique
  },
  // eslint: {
  //   ignoreDuringBuilds: true,
  // },
  typescript: {
    ignoreBuildErrors: true,
  },
  // Optimisations de performance
  compiler: {
    // Réduit la taille du bundle en supprimant les console.log en production
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
    // Optimise les styles pour réduire les re-renders
    styledComponents: true,
  },
  // Compression des assets
  compress: true,
  // Optimisation des headers HTTP (désactivé pour export statique)
  // Note: headers ne fonctionne pas avec output: 'export'
  // headers: async () => {
  //   return [
  //     {
  //       source: '/(.*)',
  //       headers: [
  //         {
  //           key: 'X-DNS-Prefetch-Control',
  //           value: 'on'
  //         },
  //         {
  //           key: 'Strict-Transport-Security',
  //           value: 'max-age=63072000; includeSubDomains; preload'
  //         },
  //         {
  //           key: 'X-Content-Type-Options',
  //           value: 'nosniff'
  //         },
  //         {
  //           key: 'X-Frame-Options',
  //           value: 'DENY'
  //         },
  //         {
  //           key: 'X-XSS-Protection',
  //           value: '1; mode=block'
  //         },
  //         {
  //           key: 'Referrer-Policy',
  //           value: 'origin-when-cross-origin'
  //         },
  //         {
  //           key: 'Permissions-Policy',
  //           value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()'
  //         }
  //       ],
  //     },
  //   ]
  // },
  // Optimisation du cache
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },
}

export default nextConfig
