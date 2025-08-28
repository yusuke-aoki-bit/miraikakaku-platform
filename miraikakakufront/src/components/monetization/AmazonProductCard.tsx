'use client';

import React from 'react';
import { ExternalLink, Star } from 'lucide-react';

interface AmazonProduct {
  id: string;
  title: string;
  price?: string;
  originalPrice?: string;
  rating?: number;
  reviewCount?: number;
  image: string;
  description?: string;
  category?: string;
  amazonUrl: string;
}

interface AmazonProductCardProps {
  product: AmazonProduct;
  showDescription?: boolean;
  compact?: boolean;
  className?: string;
}

export default function AmazonProductCard({
  product,
  showDescription = true,
  compact = false,
  className = ''
}: AmazonProductCardProps) {
  const buildAffiliateUrl = (url: string) => {
    const associateId = 'miraikakaku-22';
    const baseUrl = url.split('?')[0];
    return `${baseUrl}?tag=${associateId}`;
  };

  const handleClick = () => {
    window.open(buildAffiliateUrl(product.amazonUrl), '_blank', 'noopener,noreferrer');
  };

  const renderRating = () => {
    if (!product.rating) return null;
    
    return (
      <div className="flex items-center space-x-1 text-sm">
        <div className="flex">
          {[...Array(5)].map((_, i) => (
            <Star
              key={i}
              className={`w-3 h-3 ${
                i < Math.floor(product.rating!) 
                  ? 'text-yellow-400 fill-current' 
                  : 'text-gray-300'
              }`}
            />
          ))}
        </div>
        <span className="text-gray-600">
          {product.rating.toFixed(1)}
          {product.reviewCount && ` (${product.reviewCount})`}
        </span>
      </div>
    );
  };

  if (compact) {
    return (
      <div 
        className={`bg-white border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow cursor-pointer ${className}`}
        onClick={handleClick}
      >
        <div className="flex space-x-3">
          <img 
            src={product.image} 
            alt={product.title}
            className="w-16 h-16 object-contain rounded"
          />
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-semibold text-gray-800 line-clamp-2 mb-1">
              {product.title}
            </h4>
            {renderRating()}
            <div className="flex items-center justify-between mt-2">
              {product.price && (
                <div className="flex items-center space-x-2">
                  <span className="text-lg font-bold text-red-600">
                    {product.price}
                  </span>
                  {product.originalPrice && (
                    <span className="text-sm text-gray-500 line-through">
                      {product.originalPrice}
                    </span>
                  )}
                </div>
              )}
              <ExternalLink className="w-4 h-4 text-gray-400" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow cursor-pointer ${className}`}
      onClick={handleClick}
    >
      <div className="aspect-w-1 aspect-h-1 bg-gray-100">
        <img 
          src={product.image} 
          alt={product.title}
          className="w-full h-48 object-contain p-4"
        />
      </div>
      
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-800 line-clamp-2 flex-1">
            {product.title}
          </h3>
          <ExternalLink className="w-4 h-4 text-gray-400 ml-2 flex-shrink-0" />
        </div>
        
        {product.category && (
          <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mb-2">
            {product.category}
          </span>
        )}
        
        {renderRating()}
        
        {showDescription && product.description && (
          <p className="text-gray-600 text-sm mt-2 line-clamp-3">
            {product.description}
          </p>
        )}
        
        {product.price && (
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-200">
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold text-red-600">
                {product.price}
              </span>
              {product.originalPrice && (
                <span className="text-sm text-gray-500 line-through">
                  {product.originalPrice}
                </span>
              )}
            </div>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Amazonで見る
            </button>
          </div>
        )}
      </div>
      
      <div className="px-4 pb-3">
        <p className="text-xs text-gray-500 text-center">
          ※ Amazonのアソシエイトとして、当サイトは適格販売により収入を得ています。
        </p>
      </div>
    </div>
  );
}