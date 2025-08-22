import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import AppContainer from '@/components/layout/AppContainer'
import { AccessibilityProvider } from '@/components/accessibility/AccessibilityProvider'
import KeyboardShortcuts from '@/components/accessibility/KeyboardShortcuts'
import { PerformanceIndicator } from '@/components/performance/PerformanceMonitor'
import ServiceWorkerRegistrar from '@/components/pwa/ServiceWorkerRegistrar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Miraikakaku - AI株価予測プラットフォーム',
  description: '機械学習による株価予測と金融分析プラットフォーム',
  manifest: '/manifest.json',
}

export const viewport: Viewport = {
  themeColor: '#2196f3',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#2196f3" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
      </head>
      <body 
        className={`${inter.className} overflow-hidden`}
        suppressHydrationWarning={true}
      >
        <AccessibilityProvider>
          <AppContainer>
            <main id="main-content" role="main">
              {children}
            </main>
          </AppContainer>
          <KeyboardShortcuts />
          <PerformanceIndicator />
          <ServiceWorkerRegistrar />
        </AccessibilityProvider>
      </body>
    </html>
  )
}
