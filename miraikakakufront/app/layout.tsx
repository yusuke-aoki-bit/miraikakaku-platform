
'use client';

import type { Metadata } from "next";
import { Inter, Noto_Sans_JP } from "next/font/google";
import { useEffect } from "react";
import { I18nextProvider } from "react-i18next";
import i18n from "./lib/i18n";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });
const notoSansJP = Noto_Sans_JP({ 
  subsets: ["latin"],
  variable: '--font-noto-sans-jp',
  display: 'swap',
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <head>
        <title>未来価格 - AI株価予測プラットフォーム</title>
        <meta name="description" content="高度な機械学習モデルに基づくAI株価予測" />
      </head>
      <body className={`${inter.className} ${notoSansJP.variable}`}>
        <I18nextProvider i18n={i18n}>
          {children}
        </I18nextProvider>
      </body>
    </html>
  );
}
