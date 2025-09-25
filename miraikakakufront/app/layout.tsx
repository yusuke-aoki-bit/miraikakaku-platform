
import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import ClientLayout from "./components/ClientLayout";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: 'swap'
})
export const metadata: Metadata = {
  title: "未来価格 - Miraikakaku 次世代AI株価予測プラットフォーム",
  description: "最先端の機械学習による株価予測と金融分析プラットフォーム",
  metadataBase: new URL('https://www.miraikakaku.com'),
  openGraph: {
    title: 'Miraikakaku - 次世代AI株価予測プラットフォーム'
    description: '最先端の機械学習による株価予測と金融分析'
    url: 'https://www.miraikakaku.com'
    siteName: 'Miraikakaku'
    locale: 'ja_JP'
    type: 'website'
  }
  twitter: {
    card: 'summary_large_image'
    title: 'Miraikakaku - 次世代AI株価予測プラットフォーム'
    description: '最先端の機械学習による株価予測と金融分析'
  }
  robots: {
    index: true
    follow: true
  }
  icons: {
    icon: '/favicon.ico'
  }
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" className={inter.className}>
      <body className="antialiased">
        <ClientLayout>
          {children}
        </ClientLayout>
      </body>
    </html>
}
