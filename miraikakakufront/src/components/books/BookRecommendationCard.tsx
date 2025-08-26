'use client';

import React from 'react';
import Image from 'next/image';
import { BookRecommendation } from '@/types/books';
import { ExternalLink, Star, Users } from 'lucide-react';

interface BookRecommendationCardProps {
  book: BookRecommendation;
  size?: 'small' | 'medium' | 'large';
  showDescription?: boolean;
  className?: string;
}

export default function BookRecommendationCard({
  book,
  size = 'medium',
  showDescription = true,
  className = ''
}: BookRecommendationCardProps) {
  const sizeClasses = {
    small: 'p-3 max-w-xs',
    medium: 'p-4 max-w-sm',
    large: 'p-6 max-w-md'
  };

  const imageClasses = {
    small: 'w-16 h-20',
    medium: 'w-20 h-28',
    large: 'w-24 h-32'
  };

  const handleClick = () => {
    // Amazon Associate リンクをクリック
    window.open(book.amazonUrl, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className={`
      bg-gray-900/50 border border-gray-800/50 rounded-xl hover:border-gray-700/50 
      transition-all duration-200 hover:shadow-lg cursor-pointer group
      ${sizeClasses[size]} ${className}
    `}>
      <div className="flex space-x-4">
        {/* 書籍画像 */}
        <div className={`relative ${imageClasses[size]} flex-shrink-0`}>
          <Image
            src={book.imageUrl}
            alt={book.title}
            fill
            className="object-cover rounded-md shadow-md group-hover:shadow-lg transition-shadow duration-200"
            onError={(e) => {
              // 画像読み込みエラーの場合はプレースホルダーを表示
              const target = e.target as HTMLImageElement;
              target.src = '/images/book-placeholder.png';
            }}
          />
          
          {/* Amazon Associate バッジ */}
          <div className="absolute -top-1 -right-1 bg-orange-500 text-white text-xs px-1.5 py-0.5 rounded-full font-medium">
            Amazon
          </div>
        </div>

        {/* 書籍情報 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-2">
            <h3 className="font-semibold text-white text-sm leading-tight line-clamp-2 group-hover:text-blue-400 transition-colors">
              {book.title}
            </h3>
            <ExternalLink className="w-4 h-4 text-gray-500 group-hover:text-blue-400 transition-colors flex-shrink-0 ml-2" />
          </div>

          <p className="text-gray-400 text-xs mb-2">
            著者: {book.author}
          </p>

          {/* 評価と価格 */}
          <div className="flex items-center space-x-3 mb-2 text-xs">
            {book.rating && (
              <div className="flex items-center space-x-1">
                <Star className="w-3 h-3 text-yellow-400 fill-current" />
                <span className="text-gray-300">{book.rating}</span>
              </div>
            )}
            
            {book.reviewCount && (
              <div className="flex items-center space-x-1">
                <Users className="w-3 h-3 text-gray-500" />
                <span className="text-gray-400">{book.reviewCount}</span>
              </div>
            )}
            
            {book.price && (
              <span className="text-orange-400 font-medium">
                {book.price}
              </span>
            )}
          </div>

          {/* タグ */}
          <div className="flex flex-wrap gap-1 mb-2">
            {book.tags.slice(0, size === 'small' ? 2 : 3).map((tag, index) => (
              <span
                key={index}
                className="bg-blue-500/10 text-blue-400 text-xs px-1.5 py-0.5 rounded border border-blue-500/20"
              >
                {tag}
              </span>
            ))}
          </div>

          {/* 説明文 */}
          {showDescription && size !== 'small' && (
            <p className="text-gray-400 text-xs line-clamp-2 mb-3">
              {book.description}
            </p>
          )}

          {/* アクションボタン */}
          <button
            onClick={handleClick}
            className="w-full bg-orange-500 hover:bg-orange-600 text-white text-xs py-2 px-3 rounded-md transition-colors duration-200 font-medium"
          >
            Amazonで詳細を見る
          </button>
        </div>
      </div>
    </div>
  );
}