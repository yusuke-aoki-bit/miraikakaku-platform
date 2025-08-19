import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import AppContainer from '@/components/layout/AppContainer'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Miraikakaku - AI株価予測プラットフォーム',
  description: '機械学習による株価予測と金融分析プラットフォーム',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body 
        className={`${inter.className} overflow-hidden`}
        suppressHydrationWarning={true}
      >
        <AppContainer>
          {children}
        </AppContainer>
      </body>
    </html>
  )
}
