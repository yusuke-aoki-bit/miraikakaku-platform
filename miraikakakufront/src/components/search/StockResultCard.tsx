'use client';

import React, { useState } from 'react';
import { 
  Star, 
  StarOff, 
  ExternalLink, 
  TrendingUp, 
  TrendingDown,
  Zap,
  Building2,
  DollarSign
} from 'lucide-react';
import TripleChart from '@/components/charts/TripleChart';

interface StockResultCardProps {
  stock: {
    symbol: string;
    company_name: string;
    current_price: number;
    change?: number;
    change_percent?: number;
    market: string;
    sector: string;
    market_cap?: number;
    ai_score?: number;
    per?: number;
    pbr?: number;
    dividend_yield?: number;
    chart_data?: {
      historical?: number[];
      past_prediction?: number[];
      future_prediction?: number[];
    };
  };
  onStockClick: (symbol: string) => void;
  onWatchlistToggle: (symbol: string, isWatched: boolean) => void;
  isWatched?: boolean;
  viewMode?: 'card' | 'list';
}

export default function StockResultCard({
  stock,
  onStockClick,
  onWatchlistToggle,
  isWatched = false,
  viewMode = 'card'
}: StockResultCardProps) {
  const [watchlisted, setWatchlisted] = useState(isWatched);

  const handleWatchlistClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    const newStatus = !watchlisted;
    setWatchlisted(newStatus);
    onWatchlistToggle(stock.symbol, newStatus);
  };

  const handleCardClick = () => {
    onStockClick(stock.symbol);
  };

  const formatMarketCap = (marketCap: number): string => {
    if (marketCap >= 1000000000000) {
      return `${(marketCap / 1000000000000).toFixed(1)}兆円`;
    } else if (marketCap >= 100000000) {
      return `${(marketCap / 100000000).toFixed(0)}億円`;
    } else {
      return `${(marketCap / 100000000).toFixed(1)}億円`;
    }
  };

  const isPositiveChange = (stock.change_percent || 0) >= 0;

  if (viewMode === 'list') {
    return (
      <div 
        className="bg-gray-900/30 hover:bg-gray-800/50 border border-gray-800/50 rounded-lg p-4 transition-all cursor-pointer group"
        onClick={handleCardClick}
      >
        <div className="flex items-center justify-between">
          {/* 基本情報 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-3">
              <div>
                <div className="font-semibold text-white group-hover:text-blue-400 transition-colors flex items-center">
                  {stock.symbol}
                  <ExternalLink className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <div className="text-sm text-gray-400 truncate">
                  {stock.company_name}
                </div>
                <div className="text-xs text-gray-500 flex items-center space-x-2 mt-1">
                  <span>{stock.market}</span>
                  <span>•</span>
                  <span>{stock.sector}</span>
                </div>
              </div>
            </div>
          </div>

          {/* 価格情報 */}
          <div className="text-right mr-4">
            <div className="font-semibold text-white">
              {stock.symbol.match(/^[A-Z]+$/) ? '$' : '¥'}
              {stock.current_price.toLocaleString('ja-JP', {
                minimumFractionDigits: stock.symbol.match(/^[A-Z]+$/) ? 2 : 0,
                maximumFractionDigits: stock.symbol.match(/^[A-Z]+$/) ? 2 : 0
              })}
            </div>
            {stock.change_percent !== undefined && (
              <div className={`text-sm flex items-center justify-end ${
                isPositiveChange ? 'text-green-400' : 'text-red-400'
              }`}>
                {isPositiveChange ? (
                  <TrendingUp className="w-3 h-3 mr-1" />
                ) : (
                  <TrendingDown className="w-3 h-3 mr-1" />
                )}
                {isPositiveChange ? '+' : ''}{stock.change_percent.toFixed(2)}%
              </div>
            )}
          </div>

          {/* AIスコア */}
          <div className="text-center mr-4">
            <div className="flex items-center space-x-1">
              <Zap className="w-3 h-3 text-yellow-400" />
              <span className="font-medium text-white">
                {(stock.ai_score || 75).toFixed(0)}
              </span>
            </div>
            <div className="text-xs text-gray-500">AIスコア</div>
          </div>

          {/* TripleChart - 小さめ */}
          <div className="mr-4">
            <TripleChart
              symbol={stock.symbol}
              historicalData={stock.chart_data?.historical}
              pastPredictionData={stock.chart_data?.past_prediction}
              futurePredictionData={stock.chart_data?.future_prediction}
              size="sm"
            />
          </div>

          {/* アクション */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handleWatchlistClick}
              className={`p-2 rounded-lg transition-colors ${
                watchlisted 
                  ? 'text-yellow-400 hover:text-yellow-300' 
                  : 'text-gray-400 hover:text-yellow-400'
              }`}
              title={watchlisted ? 'ウォッチリストから削除' : 'ウォッチリストに追加'}
            >
              {watchlisted ? (
                <Star className="w-4 h-4 fill-current" />
              ) : (
                <StarOff className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // カードモード
  return (
    <div 
      className="bg-gray-900/30 hover:bg-gray-800/50 border border-gray-800/50 rounded-xl p-6 transition-all cursor-pointer group"
      onClick={handleCardClick}
    >
      {/* ヘッダー */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <div className="font-bold text-xl text-white group-hover:text-blue-400 transition-colors flex items-center">
            {stock.symbol}
            <ExternalLink className="w-4 h-4 ml-2 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <div className="text-gray-400 mt-1 line-clamp-2">
            {stock.company_name}
          </div>
          <div className="flex items-center space-x-3 mt-2 text-sm text-gray-500">
            <span className="flex items-center">
              <Building2 className="w-3 h-3 mr-1" />
              {stock.market}
            </span>
            <span>•</span>
            <span>{stock.sector}</span>
          </div>
        </div>
        
        <button
          onClick={handleWatchlistClick}
          className={`p-2 rounded-lg transition-colors ${
            watchlisted 
              ? 'text-yellow-400 hover:text-yellow-300' 
              : 'text-gray-400 hover:text-yellow-400'
          }`}
          title={watchlisted ? 'ウォッチリストから削除' : 'ウォッチリストに追加'}
        >
          {watchlisted ? (
            <Star className="w-5 h-5 fill-current" />
          ) : (
            <StarOff className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* 価格とAIスコア */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="text-2xl font-bold text-white">
            {stock.symbol.match(/^[A-Z]+$/) ? '$' : '¥'}
            {stock.current_price.toLocaleString('ja-JP', {
              minimumFractionDigits: stock.symbol.match(/^[A-Z]+$/) ? 2 : 0,
              maximumFractionDigits: stock.symbol.match(/^[A-Z]+$/) ? 2 : 0
            })}
          </div>
          {stock.change_percent !== undefined && (
            <div className={`flex items-center mt-1 ${
              isPositiveChange ? 'text-green-400' : 'text-red-400'
            }`}>
              {isPositiveChange ? (
                <TrendingUp className="w-4 h-4 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 mr-1" />
              )}
              <span className="font-medium">
                {isPositiveChange ? '+' : ''}{stock.change_percent.toFixed(2)}%
              </span>
              {stock.change && (
                <span className="text-sm ml-2">
                  ({isPositiveChange ? '+' : ''}{stock.change.toFixed(2)})
                </span>
              )}
            </div>
          )}
        </div>

        <div className="text-right">
          <div className="flex items-center space-x-2 mb-1">
            <Zap className="w-4 h-4 text-yellow-400" />
            <span className="text-xl font-bold text-white">
              {(stock.ai_score || 75).toFixed(0)}
            </span>
          </div>
          <div className="text-sm text-gray-400">AIスコア</div>
        </div>
      </div>

      {/* TripleChart */}
      <div className="mb-6">
        <TripleChart
          symbol={stock.symbol}
          historicalData={stock.chart_data?.historical}
          pastPredictionData={stock.chart_data?.past_prediction}
          futurePredictionData={stock.chart_data?.future_prediction}
          size="md"
        />
      </div>

      {/* 財務指標 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-800/50">
        {stock.market_cap && (
          <div className="text-center">
            <div className="text-sm font-medium text-white">
              {formatMarketCap(stock.market_cap)}
            </div>
            <div className="text-xs text-gray-500">時価総額</div>
          </div>
        )}
        
        {stock.per && (
          <div className="text-center">
            <div className="text-sm font-medium text-white">
              {stock.per.toFixed(1)}倍
            </div>
            <div className="text-xs text-gray-500">PER</div>
          </div>
        )}
        
        {stock.pbr && (
          <div className="text-center">
            <div className="text-sm font-medium text-white">
              {stock.pbr.toFixed(2)}倍
            </div>
            <div className="text-xs text-gray-500">PBR</div>
          </div>
        )}
        
        {stock.dividend_yield && (
          <div className="text-center">
            <div className="text-sm font-medium text-white flex items-center justify-center">
              <DollarSign className="w-3 h-3 mr-1" />
              {stock.dividend_yield.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500">配当利回り</div>
          </div>
        )}
      </div>
    </div>
  );
}