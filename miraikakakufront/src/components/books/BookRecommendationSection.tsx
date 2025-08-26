'use client';

import React from 'react';
import { BookOpen, TrendingUp, Brain } from 'lucide-react';
import { BookRecommendation, BookSection } from '@/types/books';
import BookRecommendationCard from './BookRecommendationCard';

interface BookRecommendationSectionProps {
  section: BookSection;
  contextTitle?: string;
  className?: string;
}

export default function BookRecommendationSection({
  section,
  contextTitle,
  className = ''
}: BookRecommendationSectionProps) {
  if (!section.books || section.books.length === 0) {
    return null;
  }

  const getIcon = () => {
    if (contextTitle?.includes('AI') || contextTitle?.includes('分析')) {
      return <Brain className="w-5 h-5 text-purple-400" />;
    }
    if (contextTitle?.includes('セクター') || contextTitle?.includes('テーマ')) {
      return <TrendingUp className="w-5 h-5 text-blue-400" />;
    }
    return <BookOpen className="w-5 h-5 text-green-400" />;
  };

  const displayBooks = section.maxDisplay 
    ? section.books.slice(0, section.maxDisplay)
    : section.books;

  return (
    <div className={`bg-gray-900/30 border border-gray-800/50 rounded-xl p-6 ${className}`}>
      {/* セクションヘッダー */}
      <div className="flex items-center space-x-3 mb-4">
        {getIcon()}
        <div>
          <h3 className="text-lg font-bold text-white">
            {section.title}
          </h3>
          {section.subtitle && (
            <p className="text-sm text-gray-400 mt-1">
              {section.subtitle}
            </p>
          )}
        </div>
      </div>

      {/* Amazon Associate 免責事項 */}
      <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3 mb-4">
        <p className="text-xs text-orange-200 leading-relaxed">
          📚 <strong>投資知識を深める書籍をご紹介</strong><br />
          こちらの書籍はAmazonアソシエイト・プログラムを利用して紹介しています。
          購入により当サイトが紹介料を得る場合がありますが、購入者に追加料金は発生しません。
        </p>
      </div>

      {/* 書籍表示 */}
      {section.displayType === 'grid' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {displayBooks.map((book) => (
            <BookRecommendationCard
              key={book.asin}
              book={book}
              size="medium"
              showDescription={true}
            />
          ))}
        </div>
      )}

      {section.displayType === 'list' && (
        <div className="space-y-4">
          {displayBooks.map((book) => (
            <BookRecommendationCard
              key={book.asin}
              book={book}
              size="large"
              showDescription={true}
              className="w-full"
            />
          ))}
        </div>
      )}

      {section.displayType === 'carousel' && (
        <div className="flex space-x-4 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-900">
          {displayBooks.map((book) => (
            <div key={book.asin} className="flex-shrink-0">
              <BookRecommendationCard
                book={book}
                size="medium"
                showDescription={false}
                className="w-72"
              />
            </div>
          ))}
        </div>
      )}

      {/* 「もっと見る」リンク（必要に応じて） */}
      {section.books.length > (section.maxDisplay || section.books.length) && (
        <div className="text-center mt-4">
          <button className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors">
            関連書籍をもっと見る →
          </button>
        </div>
      )}

      {/* 学習のヒント */}
      <div className="mt-6 bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
          <div>
            <h4 className="text-sm font-medium text-blue-300 mb-2">
              💡 投資学習のコツ
            </h4>
            <p className="text-xs text-blue-200 leading-relaxed">
              理論と実践のバランスが重要です。書籍で基礎知識を身につけた後は、
              当サイトのAI分析機能で実際の銘柄を分析してみましょう。
              知識が実践的なスキルに変わります。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}