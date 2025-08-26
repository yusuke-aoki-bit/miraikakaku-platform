'use client';

import React, { useEffect, useRef } from 'react';

interface AdSenseUnitProps {
  /**
   * AdSense広告スロットID
   */
  adSlot: string;
  
  /**
   * 広告の幅
   */
  width?: number;
  
  /**
   * 広告の高さ
   */
  height?: number;
  
  /**
   * レスポンシブ広告かどうか
   */
  responsive?: boolean;
  
  /**
   * 広告のスタイル（レスポンシブ用）
   */
  adStyle?: 'display' | 'in-article' | 'in-feed';
  
  /**
   * 追加のCSSクラス
   */
  className?: string;
  
}

declare global {
  interface Window {
    adsbygoogle?: any[];
  }
}

export default function AdSenseUnit({
  adSlot,
  width = 728,
  height = 90,
  responsive = false,
  adStyle = 'display',
  className = ''
}: AdSenseUnitProps) {
  const adRef = useRef<HTMLModElement>(null);
  const pushedRef = useRef(false);

  useEffect(() => {
    if (typeof window !== 'undefined' && adRef.current && !pushedRef.current) {
      try {
        // AdSenseがまだ読み込まれていない場合は配列を初期化
        if (!window.adsbygoogle) {
          window.adsbygoogle = [];
        }

        // 広告をプッシュ
        window.adsbygoogle.push({});
        pushedRef.current = true;
      } catch (error) {
        console.error('AdSense広告の読み込みに失敗しました:', error);
      }
    }
  }, []);

  const adProps: Record<string, any> = {
    'data-ad-client': 'ca-pub-1941622962098828',
    'data-ad-slot': adSlot,
    'data-ad-format': responsive ? 'auto' : undefined,
    'data-full-width-responsive': responsive ? 'true' : undefined,
  };

  // 固定サイズの場合はスタイルを設定
  if (!responsive) {
    adProps.style = {
      display: 'inline-block',
      width: `${width}px`,
      height: `${height}px`
    };
  }

  return (
    <div className={`flex justify-center items-center my-4 ${className}`}>
      <ins
        ref={adRef}
        className="adsbygoogle"
        {...adProps}
      />
    </div>
  );
}

// よく使われる広告サイズのプリセット
export const AdSensePresets = {
  // バナー広告（横長）
  banner: { width: 728, height: 90, adSlot: '1234567890' },
  mobileBanner: { width: 320, height: 50, adSlot: '1234567891' },
  
  // レクタングル広告
  mediumRectangle: { width: 300, height: 250, adSlot: '1234567892' },
  largeRectangle: { width: 336, height: 280, adSlot: '1234567893' },
  
  // スカイスクレイパー（縦長）
  skyscraper: { width: 120, height: 600, adSlot: '1234567894' },
  wideSkyscraper: { width: 160, height: 600, adSlot: '1234567895' },
  
  // レスポンシブ
  responsive: { responsive: true, adSlot: '1234567896' },
  
  // インフィード広告
  inFeed: { responsive: true, adStyle: 'in-feed' as const, adSlot: '1234567897' },
  
  // 記事内広告
  inArticle: { responsive: true, adStyle: 'in-article' as const, adSlot: '1234567898' }
};