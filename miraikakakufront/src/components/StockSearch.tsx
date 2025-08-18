'use client';

import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import LoadingSpinner from './common/LoadingSpinner';

interface Stock {
  symbol: string;
  company_name: string;
  exchange: string;
  sector?: string;
  industry?: string;
}

interface StockSearchProps {
  onSymbolSelect?: (symbol: string) => void;
}

export default function StockSearch({ onSymbolSelect }: StockSearchProps) {
  const [query, setQuery] = useState('');
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(false);

  const searchStocks = async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setStocks([]);
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/search?query=${encodeURIComponent(searchQuery)}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setStocks(data);
      } else {
        throw new Error(`API Error: ${response.status}`);
      }
    } catch (error) {
      console.error('株式検索エラー:', error);
      setStocks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchStocks(query);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleStockSelect = (symbol: string) => {
    onSymbolSelect?.(symbol);
    setQuery('');
    setStocks([]);
  };

  return (
    <div className="relative w-full max-w-lg mx-auto">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="株式シンボルまたは会社名で検索（例: AAPL, Apple）..."
          className="youtube-search w-full pl-10 pr-4 py-3"
        />
      </div>

      {/* 検索結果 */}
      {stocks.length > 0 && (
        <div className="absolute top-full left-0 right-0 z-10 mt-1 youtube-card max-h-60 overflow-y-auto">
          {stocks.map((stock) => (
            <button
              key={stock.symbol}
              onClick={() => handleStockSelect(stock.symbol)}
              className="w-full px-4 py-3 text-left hover:bg-gray-800/50 border-b border-gray-700/50 last:border-b-0 transition-all duration-150 group"
            >
              <div className="font-semibold text-white group-hover:text-red-400 transition-colors">{stock.symbol}</div>
              <div className="text-sm text-gray-300 truncate">{stock.company_name}</div>
              <div className="text-xs text-gray-500">
                {stock.exchange} {stock.sector && `• ${stock.sector}`}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* ローディング */}
      {loading && (
        <div className="absolute top-full left-0 right-0 z-10 mt-1 youtube-card p-4">
          <LoadingSpinner 
            type="chart" 
            size="sm" 
            message="株式データを検索中..."
          />
        </div>
      )}
    </div>
  );
}