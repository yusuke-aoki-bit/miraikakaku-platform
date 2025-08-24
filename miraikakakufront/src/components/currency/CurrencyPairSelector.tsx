'use client';

import React from 'react';
import { Globe } from 'lucide-react';

interface CurrencyPair {
  pair: string;
  base: string;
  quote: string;
  flag1: string;
  flag2: string;
  current?: number;
  change?: number;
  changePercent?: number;
}

interface CurrencyPairSelectorProps {
  pairs: CurrencyPair[];
  selectedPair: string;
  onPairChange: (pair: string) => void;
  loading?: boolean;
}

const POPULAR_PAIRS = [
  { pair: 'USD/JPY', base: 'USD', quote: 'JPY', flag1: '🇺🇸', flag2: '🇯🇵' },
  { pair: 'EUR/USD', base: 'EUR', quote: 'USD', flag1: '🇪🇺', flag2: '🇺🇸' },
  { pair: 'GBP/JPY', base: 'GBP', quote: 'JPY', flag1: '🇬🇧', flag2: '🇯🇵' },
  { pair: 'EUR/JPY', base: 'EUR', quote: 'JPY', flag1: '🇪🇺', flag2: '🇯🇵' },
  { pair: 'AUD/USD', base: 'AUD', quote: 'USD', flag1: '🇦🇺', flag2: '🇺🇸' },
  { pair: 'USD/CHF', base: 'USD', quote: 'CHF', flag1: '🇺🇸', flag2: '🇨🇭' },
  { pair: 'GBP/USD', base: 'GBP', quote: 'USD', flag1: '🇬🇧', flag2: '🇺🇸' },
  { pair: 'USD/CAD', base: 'USD', quote: 'CAD', flag1: '🇺🇸', flag2: '🇨🇦' },
];

export default function CurrencyPairSelector({ 
  pairs, 
  selectedPair, 
  onPairChange, 
  loading = false 
}: CurrencyPairSelectorProps) {
  const displayPairs = pairs.length > 0 ? pairs : POPULAR_PAIRS;

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <Globe className="w-5 h-5 text-blue-400" />
        <h3 className="text-lg font-semibold text-white">通貨ペア選択</h3>
      </div>

      {/* タブ形式のセレクター */}
      <div className="flex flex-wrap gap-2">
        {displayPairs.map((pair) => {
          const isSelected = selectedPair === pair.pair;
          const pairData = pairs.find(p => p.pair === pair.pair);
          
          return (
            <button
              key={pair.pair}
              onClick={() => onPairChange(pair.pair)}
              disabled={loading}
              className={`relative px-4 py-3 rounded-lg border transition-all duration-200 min-w-[100px] ${
                isSelected 
                  ? 'bg-blue-500/20 border-blue-500/50 shadow-lg scale-105' 
                  : 'bg-gray-900/50 border-gray-800/50 hover:bg-gray-800/50 hover:border-gray-700/50'
              } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              {/* 通貨ペア表示 */}
              <div className="flex items-center justify-center space-x-1 mb-1">
                <span className="text-lg">{pair.flag1}</span>
                <span className="text-gray-500 text-sm">/</span>
                <span className="text-lg">{pair.flag2}</span>
              </div>
              
              <div className="text-sm font-medium text-white mb-1">
                {pair.pair}
              </div>
              
              {/* 価格と変動率 */}
              {pairData && (
                <div className="space-y-1">
                  <div className="text-xs text-gray-300">
                    {pairData.current?.toFixed(4)}
                  </div>
                  {pairData.changePercent !== undefined && (
                    <div className={`text-xs font-medium ${
                      pairData.changePercent > 0 ? 'text-green-400' : 
                      pairData.changePercent < 0 ? 'text-red-400' : 'text-gray-400'
                    }`}>
                      {pairData.changePercent > 0 ? '↑' : pairData.changePercent < 0 ? '↓' : '→'} 
                      {Math.abs(pairData.changePercent).toFixed(2)}%
                    </div>
                  )}
                </div>
              )}
              
              {/* 選択インジケーター */}
              {isSelected && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-400 rounded-full shadow-lg"></div>
              )}
            </button>
          );
        })}
      </div>

      {/* ドロップダウンメニュー（モバイル用） */}
      <div className="md:hidden">
        <select
          value={selectedPair}
          onChange={(e) => onPairChange(e.target.value)}
          disabled={loading}
          className="w-full px-3 py-2 bg-gray-900/50 border border-gray-800/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent"
        >
          {displayPairs.map((pair) => (
            <option key={pair.pair} value={pair.pair}>
              {pair.flag1} {pair.pair} {pair.flag2}
            </option>
          ))}
        </select>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-2">
          <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-400 border-t-transparent"></div>
          <span className="ml-2 text-sm text-gray-400">レート更新中...</span>
        </div>
      )}
    </div>
  );
}