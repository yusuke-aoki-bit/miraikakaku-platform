'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { TradingTool } from '@/data/tradingTools';
import { 
  ExternalLink, 
  Star, 
  Users, 
  Monitor, 
  Cpu, 
  Armchair, 
  Calculator,
  Wifi,
  HardDrive,
  Camera,
  Package
} from 'lucide-react';

interface TradingToolCardProps {
  tool: TradingTool;
  size?: 'small' | 'medium' | 'large';
  showSpecs?: boolean;
  className?: string;
}

export default function TradingToolCard({
  tool,
  size = 'medium',
  showSpecs = true,
  className = ''
}: TradingToolCardProps) {
  const [imageError, setImageError] = useState(false);
  
  const sizeClasses = {
    small: 'p-4 max-w-xs',
    medium: 'p-6 max-w-md',
    large: 'p-6 max-w-lg'
  };

  const imageClasses = {
    small: 'w-24 h-24',
    medium: 'w-32 h-32',
    large: 'w-40 h-40'
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'monitor': return <Monitor className="w-4 h-4" />;
      case 'pc-hardware': return <Cpu className="w-4 h-4" />;
      case 'ergonomics': return <Armchair className="w-4 h-4" />;
      case 'calculator': return <Calculator className="w-4 h-4" />;
      case 'networking': return <Wifi className="w-4 h-4" />;
      case 'backup': return <HardDrive className="w-4 h-4" />;
      case 'accessories': return <Camera className="w-4 h-4" />;
      default: return <Package className="w-4 h-4" />;
    }
  };

  const getCategoryLabel = (category: string) => {
    const labels: { [key: string]: string } = {
      'monitor': 'モニター',
      'pc-hardware': 'PCハードウェア',
      'ergonomics': '人間工学',
      'calculator': '金融電卓',
      'networking': 'ネットワーク',
      'backup': 'ストレージ',
      'accessories': 'アクセサリー'
    };
    return labels[category] || 'その他';
  };

  const handlePurchaseClick = () => {
    window.open(tool.amazonUrl, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className={`
      bg-gray-900/50 border border-gray-800/50 rounded-xl hover:border-gray-700/50 
      transition-all duration-300 hover:shadow-xl group ${sizeClasses[size]} ${className}
    `}>
      {/* カテゴリーバッジ */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2 text-xs">
          <div className="flex items-center space-x-1 bg-blue-500/20 text-blue-400 px-2 py-1 rounded-full border border-blue-500/30">
            {getCategoryIcon(tool.category)}
            <span>{getCategoryLabel(tool.category)}</span>
          </div>
        </div>
        
        <div className="bg-orange-500 text-white text-xs px-2 py-1 rounded-full font-medium">
          Amazon
        </div>
      </div>

      {/* 商品画像 */}
      <div className={`relative ${imageClasses[size]} mx-auto mb-4 bg-gray-800 rounded-lg overflow-hidden`}>
        {!imageError ? (
          <Image
            src={tool.imageUrl}
            alt={tool.name}
            fill
            className="object-contain p-2 group-hover:scale-105 transition-transform duration-300"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-500">
            <Package className="w-8 h-8" />
          </div>
        )}
      </div>

      {/* 商品名 */}
      <h3 className="font-bold text-white text-lg mb-2 line-clamp-2 group-hover:text-blue-400 transition-colors">
        {tool.name}
      </h3>

      {/* 評価と価格 */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3 text-sm">
          {tool.rating && (
            <div className="flex items-center space-x-1">
              <Star className="w-4 h-4 text-yellow-400 fill-current" />
              <span className="text-gray-300">{tool.rating}</span>
            </div>
          )}
          
          {tool.reviewCount && (
            <div className="flex items-center space-x-1">
              <Users className="w-4 h-4 text-gray-500" />
              <span className="text-gray-400">{tool.reviewCount}</span>
            </div>
          )}
        </div>
        
        <span className="text-orange-400 font-bold text-lg">
          {tool.price}
        </span>
      </div>

      {/* 説明 */}
      <p className="text-gray-400 text-sm mb-4 line-clamp-3">
        {tool.description}
      </p>

      {/* 特徴 */}
      <div className="mb-4">
        <h4 className="text-white font-medium text-sm mb-2">主な特徴</h4>
        <ul className="space-y-1">
          {tool.features.slice(0, size === 'small' ? 3 : 4).map((feature, index) => (
            <li key={index} className="text-xs text-gray-400 flex items-center">
              <div className="w-1 h-1 bg-blue-400 rounded-full mr-2 flex-shrink-0"></div>
              {feature}
            </li>
          ))}
        </ul>
      </div>

      {/* なぜおすすめか */}
      <div className="mb-4 bg-green-900/20 border border-green-500/30 rounded-lg p-3">
        <h4 className="text-green-400 font-medium text-sm mb-1 flex items-center">
          💡 おすすめポイント
        </h4>
        <p className="text-green-200 text-xs">
          {tool.whyRecommended}
        </p>
      </div>

      {/* 用途 */}
      <div className="mb-4">
        <h4 className="text-white font-medium text-sm mb-2">主な用途</h4>
        <div className="flex flex-wrap gap-1">
          {tool.useCase.slice(0, size === 'small' ? 2 : 4).map((useCase, index) => (
            <span
              key={index}
              className="bg-purple-500/10 text-purple-400 text-xs px-2 py-1 rounded border border-purple-500/20"
            >
              {useCase}
            </span>
          ))}
        </div>
      </div>

      {/* スペック（largeサイズのみ） */}
      {showSpecs && size === 'large' && tool.specs && (
        <div className="mb-4">
          <h4 className="text-white font-medium text-sm mb-2">主なスペック</h4>
          <div className="bg-gray-800/50 rounded-lg p-3">
            {Object.entries(tool.specs).map(([key, value]) => (
              <div key={key} className="flex justify-between items-center py-1 text-xs">
                <span className="text-gray-400">{key}:</span>
                <span className="text-gray-300">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 購入ボタン */}
      <button
        onClick={handlePurchaseClick}
        className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 
                   text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 
                   flex items-center justify-center space-x-2 group-hover:shadow-lg"
      >
        <span>Amazonで詳細を見る</span>
        <ExternalLink className="w-4 h-4" />
      </button>

      {/* 投資効果ヒント */}
      <div className="mt-3 text-center">
        <p className="text-xs text-blue-300">
          💰 <strong>投資効果:</strong> 作業効率向上により年間収益アップが期待できます
        </p>
      </div>
    </div>
  );
}