'use client';

import React from 'react';
import { ExternalLink, Star, ShoppingCart } from 'lucide-react';
import { motion } from 'framer-motion';

export interface AmazonProduct {
  /**
   * 商品のASIN（Amazon Standard Identification Number）
   */
  asin: string;
  
  /**
   * 商品タイトル
   */
  title: string;
  
  /**
   * 商品の簡単な説明
   */
  description?: string;
  
  /**
   * 商品画像のURL
   */
  imageUrl: string;
  
  /**
   * 価格（文字列形式、例: "¥2,980"）
   */
  price?: string;
  
  /**
   * 評価（1-5）
   */
  rating?: number;
  
  /**
   * レビュー数
   */
  reviewCount?: number;
  
  /**
   * 著者（書籍の場合）
   */
  author?: string;
  
  /**
   * カテゴリ
   */
  category?: string;
  
  /**
   * おすすめ理由
   */
  reason?: string;
}

interface AmazonProductCardProps {
  product: AmazonProduct;
  /**
   * カードのレイアウト
   */
  layout?: 'horizontal' | 'vertical';
  /**
   * カードサイズ
   */
  size?: 'small' | 'medium' | 'large';
  /**
   * 追加のCSSクラス
   */
  className?: string;
  /**
   * アニメーション有効/無効
   */
  animate?: boolean;
}

const ASSOCIATE_ID = 'miraikakaku-22';

export default function AmazonProductCard({
  product,
  layout = 'vertical',
  size = 'medium',
  className = '',
  animate = true
}: AmazonProductCardProps) {
  
  // Amazonアソシエイトリンクを生成
  const generateAmazonUrl = (asin: string) => {
    return `https://www.amazon.co.jp/dp/${asin}/?tag=${ASSOCIATE_ID}`;
  };

  // 星評価を描画
  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating 
                ? 'text-yellow-400 fill-current' 
                : 'text-gray-300'
            }`}
          />
        ))}
        {product.reviewCount && (
          <span className="ml-2 text-sm text-gray-600">
            ({product.reviewCount.toLocaleString()})
          </span>
        )}
      </div>
    );
  };

  const cardContent = (
    <div className={`
      bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200
      ${layout === 'horizontal' ? 'flex' : 'flex flex-col'}
      ${size === 'small' ? 'p-3' : size === 'medium' ? 'p-4' : 'p-6'}
      ${className}
    `}>
      {/* 商品画像 */}
      <div className={`
        ${layout === 'horizontal' 
          ? size === 'small' ? 'w-20 h-20 mr-3' : 'w-32 h-32 mr-4'
          : size === 'small' ? 'w-full h-32' : size === 'medium' ? 'w-full h-40' : 'w-full h-48'
        }
        flex-shrink-0 bg-gray-100 rounded-md overflow-hidden
      `}>
        <img
          src={product.imageUrl}
          alt={product.title}
          className="w-full h-full object-contain"
          loading="lazy"
        />
      </div>

      {/* 商品情報 */}
      <div className={`
        ${layout === 'horizontal' ? 'flex-1' : 'mt-3'}
        flex flex-col
      `}>
        {/* カテゴリ */}
        {product.category && (
          <span className="text-xs text-blue-600 font-medium mb-1">
            {product.category}
          </span>
        )}

        {/* タイトル */}
        <h3 className={`
          font-semibold text-gray-900 line-clamp-2 mb-2
          ${size === 'small' ? 'text-sm' : size === 'medium' ? 'text-base' : 'text-lg'}
        `}>
          {product.title}
        </h3>

        {/* 著者 */}
        {product.author && (
          <p className="text-sm text-gray-600 mb-2">
            著者: {product.author}
          </p>
        )}

        {/* 説明 */}
        {product.description && (
          <p className={`
            text-gray-700 line-clamp-3 mb-3
            ${size === 'small' ? 'text-xs' : 'text-sm'}
          `}>
            {product.description}
          </p>
        )}

        {/* おすすめ理由 */}
        {product.reason && (
          <div className="bg-blue-50 border border-blue-200 rounded-md p-2 mb-3">
            <p className="text-xs text-blue-800">
              <strong>おすすめポイント:</strong> {product.reason}
            </p>
          </div>
        )}

        {/* 評価 */}
        {product.rating && (
          <div className="mb-3">
            {renderStars(product.rating)}
          </div>
        )}

        {/* 価格とボタン */}
        <div className="flex items-center justify-between mt-auto">
          {product.price && (
            <div className="text-lg font-bold text-green-600">
              {product.price}
            </div>
          )}
          
          <a
            href={generateAmazonUrl(product.asin)}
            target="_blank"
            rel="noopener noreferrer"
            className="
              flex items-center px-3 py-2 bg-orange-500 text-white text-sm font-medium 
              rounded-md hover:bg-orange-600 transition-colors duration-200
              focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2
            "
          >
            <ShoppingCart className="w-4 h-4 mr-1" />
            Amazonで見る
            <ExternalLink className="w-3 h-3 ml-1" />
          </a>
        </div>
      </div>
    </div>
  );

  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        whileHover={{ y: -2 }}
      >
        {cardContent}
      </motion.div>
    );
  }

  return cardContent;
}

// 複数商品を表示するグリッドコンポーネント
interface AmazonProductGridProps {
  products: AmazonProduct[];
  title?: string;
  description?: string;
  maxItems?: number;
  gridCols?: 1 | 2 | 3 | 4;
  className?: string;
}

export function AmazonProductGrid({
  products,
  title = "おすすめ商品",
  description,
  maxItems = 4,
  gridCols = 2,
  className = ""
}: AmazonProductGridProps) {
  const displayProducts = products.slice(0, maxItems);
  
  const gridClass = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
  };

  return (
    <div className={`bg-gray-50 border border-gray-200 rounded-lg p-6 ${className}`}>
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
        {description && (
          <p className="text-sm text-gray-600">{description}</p>
        )}
      </div>
      
      <div className={`grid ${gridClass[gridCols]} gap-4`}>
        {displayProducts.map((product, index) => (
          <AmazonProductCard
            key={product.asin}
            product={product}
            size="small"
            animate={true}
          />
        ))}
      </div>

      {/* Amazon アソシエイト表記 */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          ※ 当サイトはAmazon.co.jpアソシエイトプログラムに参加しています
        </p>
      </div>
    </div>
  );
}