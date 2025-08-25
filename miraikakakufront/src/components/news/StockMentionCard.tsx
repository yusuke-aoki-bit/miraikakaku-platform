'use client';

import Link from 'next/link';
import { useState } from 'react';
import { 
  TrendingUpIcon, 
  TrendingDownIcon,
  EyeIcon,
  PlusIcon,
  CheckIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api-client';

interface StockData {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  context?: string;
}

interface StockMentionCardProps {
  stock: StockData;
  onWatchlistAdd?: (symbol: string) => void;
}

export default function StockMentionCard({ stock, onWatchlistAdd }: StockMentionCardProps) {
  const [isInWatchlist, setIsInWatchlist] = useState(false);
  const [isAdding, setIsAdding] = useState(false);

  const formatCurrency = (amount: number) => {
    if (amount >= 1000000000) {
      return `¥${(amount / 1000000000).toFixed(1)}B`;
    } else if (amount >= 1000000) {
      return `¥${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `¥${(amount / 1000).toFixed(0)}K`;
    }
    return `¥${amount.toLocaleString()}`;
  };

  const formatPrice = (price: number) => {
    return `¥${price.toLocaleString()}`;
  };

  const handleWatchlistAdd = async () => {
    setIsAdding(true);
    try {
      const response = await apiClient.addToWatchlist('default', stock.symbol);
      if (response.status === 'success') {
        setIsInWatchlist(true);
        onWatchlistAdd?.(stock.symbol);
      }
    } catch (error) {
      console.error('Failed to add to watchlist:', error);
    } finally {
      setIsAdding(false);
    }
  };

  const isPositive = stock.change_percent >= 0;

  return (
    <div className="bg-surface-elevated rounded-lg border border-border-primary p-4 hover:shadow-md transition-shadow">
      {/* 銘柄ヘッダー */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <Link
              href={`/stock/${stock.symbol}`}
              className="text-accent-primary hover:text-accent-primary/80 font-medium text-sm transition-colors"
            >
              {stock.symbol}
            </Link>
            <div className={`flex items-center text-xs ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
              {isPositive ? (
                <TrendingUpIcon className="w-3 h-3 mr-1" />
              ) : (
                <TrendingDownIcon className="w-3 h-3 mr-1" />
              )}
              {isPositive ? '+' : ''}{stock.change_percent.toFixed(2)}%
            </div>
          </div>
          <h4 className="font-medium text-text-primary text-sm mt-1 truncate">
            {stock.company_name}
          </h4>
        </div>
      </div>

      {/* 価格情報 */}
      <div className="space-y-2 mb-4">
        <div className="flex justify-between items-center">
          <span className="text-text-secondary text-xs">現在値</span>
          <span className="font-semibold text-text-primary text-sm">
            {formatPrice(stock.current_price)}
          </span>
        </div>
        
        {stock.volume && (
          <div className="flex justify-between items-center">
            <span className="text-text-secondary text-xs">出来高</span>
            <span className="text-text-primary text-xs">
              {stock.volume.toLocaleString()}
            </span>
          </div>
        )}

        {stock.market_cap && (
          <div className="flex justify-between items-center">
            <span className="text-text-secondary text-xs">時価総額</span>
            <span className="text-text-primary text-xs">
              {formatCurrency(stock.market_cap)}
            </span>
          </div>
        )}
      </div>

      {/* 関連コンテキスト */}
      {stock.context && (
        <div className="mb-4 p-3 bg-accent-primary/5 border border-accent-primary/20 rounded-lg">
          <p className="text-xs text-text-secondary italic">
            "{stock.context}..."
          </p>
        </div>
      )}

      {/* アクションボタン */}
      <div className="flex items-center space-x-2">
        <Link
          href={`/stock/${stock.symbol}`}
          className="flex items-center justify-center flex-1 px-3 py-2 bg-accent-primary hover:bg-accent-primary/90 text-white text-xs font-medium rounded-lg transition-colors"
        >
          <EyeIcon className="w-4 h-4 mr-1" />
          詳細を見る
        </Link>

        <button
          onClick={handleWatchlistAdd}
          disabled={isInWatchlist || isAdding}
          className="flex items-center justify-center px-3 py-2 border border-border-primary hover:bg-surface-background text-text-primary text-xs font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAdding ? (
            <div className="w-4 h-4 animate-spin rounded-full border-b-2 border-accent-primary" />
          ) : isInWatchlist ? (
            <CheckIcon className="w-4 h-4 text-green-500" />
          ) : (
            <PlusIcon className="w-4 h-4" />
          )}
        </button>
      </div>
    </div>
  );
}