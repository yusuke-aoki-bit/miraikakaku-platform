'use client';

import Image from 'next/image';
import { useState } from 'react';

interface ArticleBodyProps {
  content: string;
  imageUrl?: string;
}

export default function ArticleBody({ content, imageUrl }: ArticleBodyProps) {
  const [imageError, setImageError] = useState(false);

  // 記事内容を段落に分割し、フォーマットを適用
  const formatContent = (text: string) => {
    // 改行で段落を分割
    const paragraphs = text.split('\n\n').filter(p => p.trim());
    
    return paragraphs.map((paragraph, index) => {
      const trimmed = paragraph.trim();
      
      // 見出しパターンの検出
      if (trimmed.match(/^[●◆■▲★]{1,2}\s*.+/) || trimmed.match(/^【.+】/)) {
        return (
          <h3 key={index} className="text-xl font-semibold text-text-primary mt-8 mb-4 flex items-center">
            <span className="w-1 h-6 bg-accent-primary rounded-full mr-3"></span>
            {trimmed.replace(/^[●◆■▲★]{1,2}\s*/, '').replace(/^【(.+)】/, '$1')}
          </h3>
        );
      }

      // リスト項目の検出
      if (trimmed.match(/^[・•]\s*.+/)) {
        const items = trimmed.split('\n').filter(item => item.trim());
        return (
          <ul key={index} className="list-none space-y-2 my-6">
            {items.map((item, itemIndex) => (
              <li key={itemIndex} className="flex items-start">
                <span className="w-2 h-2 bg-accent-primary rounded-full mt-3 mr-3 flex-shrink-0"></span>
                <span className="text-text-primary leading-relaxed">
                  {item.replace(/^[・•]\s*/, '')}
                </span>
              </li>
            ))}
          </ul>
        );
      }

      // 引用の検出
      if (trimmed.match(/^["「].+["」]$/)) {
        return (
          <blockquote key={index} className="border-l-4 border-accent-primary bg-accent-primary/5 pl-6 pr-4 py-4 my-6 italic">
            <p className="text-text-primary text-lg leading-relaxed">
              {trimmed.replace(/^["「]/, '').replace(/["」]$/, '')}
            </p>
          </blockquote>
        );
      }

      // 数値データや統計の強調
      const highlightedText = trimmed.replace(
        /(\d+(?:\.\d+)?[%％円$¥億兆万千百十])/g,
        '<strong class="text-accent-primary font-semibold">$1</strong>'
      );

      // 企業名や固有名詞の強調
      const finalText = highlightedText.replace(
        /(株式会社|[株式]|Inc\.|Corp\.|Ltd\.|Co\.|Corporation)/g,
        '<span class="font-medium">$1</span>'
      );

      // 通常の段落
      return (
        <p 
          key={index} 
          className="text-text-primary leading-relaxed text-lg mb-6"
          dangerouslySetInnerHTML={{ __html: finalText }}
        />
      );
    });
  };

  return (
    <article className="bg-surface-elevated rounded-lg border border-border-primary overflow-hidden">
      {/* 記事画像 */}
      {imageUrl && !imageError && (
        <div className="relative w-full h-96 mb-8">
          <Image
            src={imageUrl}
            alt="記事画像"
            fill
            className="object-cover"
            onError={() => setImageError(true)}
            priority
          />
        </div>
      )}

      {/* 記事本文 */}
      <div className="p-8">
        <div className="prose prose-lg max-w-none">
          {formatContent(content)}
        </div>

        {/* 記事フッター */}
        <footer className="mt-12 pt-8 border-t border-border-primary">
          <div className="flex items-center justify-between text-sm text-text-secondary">
            <div className="flex items-center space-x-4">
              <span>この記事は信頼できる情報源から収集されています</span>
            </div>
            <div className="flex items-center space-x-2">
              <span>最終更新:</span>
              <time>{new Date().toLocaleDateString('ja-JP')}</time>
            </div>
          </div>

          {/* 免責事項 */}
          <div className="mt-4 p-4 bg-gray-500/5 border border-gray-500/10 rounded-lg">
            <p className="text-xs text-text-secondary">
              <span className="font-medium">免責事項:</span>
              本記事の内容は情報提供を目的としており、投資判断の根拠となることを意図したものではありません。
              投資にはリスクが伴います。投資判断はお客様ご自身の責任においてなさるようお願いいたします。
            </p>
          </div>
        </footer>
      </div>
    </article>
  );
}