import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '../styles/globals.css'
import { WebVitals } from '@/components/performance/WebVitals'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap', // Optimisation FOIT/FOUT
  preload: true,
})

export const metadata: Metadata = {
  title: 'Chat Emploi',
  description: 'Votre coach emploi empathique',
  keywords: ['emploi', 'coach', 'IA', 'recherche', 'CV', 'lettre motivation'],
  authors: [{ name: 'Chat Emploi' }],
  creator: 'Chat Emploi',
  publisher: 'Chat Emploi',
  robots: {
    index: false, // Application desktop, pas d'indexation
    follow: false,
  },
  // Optimisation des performances
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="fr" className="scroll-smooth">
      <head>
        {/* Preconnect aux domaines critiques */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />

        {/* Preload des polices */}
        <link
          rel="preload"
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          as="style"
        />

        {/* Favicon optimisé */}
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />

        {/* Manifest pour PWA (future évolution) */}
        <link rel="manifest" href="/manifest.json" />
      </head>
      <body className={`${inter.className} antialiased`}>
        <WebVitals />
        {children}
      </body>
    </html>
  )
}
