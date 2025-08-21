'use client';

import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import { SEARCH_CONFIG, UI_CONFIG } from '@/config/constants';
import SkeletonLoader from './common/SkeletonLoader';

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
    if (searchQuery.length < SEARCH_CONFIG.MIN_QUERY_LENGTH) {
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
    }, SEARCH_CONFIG.DEBOUNCE_DELAY);

    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleStockSelect = (symbol: string) => {
    onSymbolSelect?.(symbol);
    setQuery('');
    setStocks([]);
  };

  return (
    <div className="relative w-full max-w-lg mx-auto" data-testid="stock-search">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-medium w-5 h-5" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="株式シンボルまたは会社名で検索（例: AAPL, Apple）..."
          className="bg-dark-card border border-dark-border rounded-md w-full pl-10 pr-4 py-3 text-text-light focus:outline-none focus:ring-2 focus:ring-brand-primary"
          data-testid="stock-search-input"
        />
      </div>

      {/* 検索結果 */}
      {stocks.length > 0 && (
        <div className="absolute top-full left-0 right-0 z-10 mt-1 bg-dark-card rounded-md max-h-60 overflow-y-auto shadow-lg border border-dark-border" data-testid="search-suggestions">
          {stocks.map((stock) => (
            <button
              key={stock.symbol}
              onClick={() => handleStockSelect(stock.symbol)}
              className="w-full px-4 py-3 text-left hover:bg-dark-border transition-all duration-150 group"
            >
              <div className="font-semibold text-text-light group-hover:text-brand-primary transition-colors">{stock.symbol}</div>
              <div className="text-sm text-text-medium truncate">{stock.company_name}</div>
              <div className="text-xs text-text-dark">
                {stock.exchange} {stock.sector && `• ${stock.sector}`}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* ローディングスケルトン */}
      {loading && (
        <div className="absolute top-full left-0 right-0 z-10 mt-1 bg-dark-card rounded-md p-4 shadow-lg border border-dark-border">
          {[...Array(UI_CONFIG.SKELETON_ITEMS)].map((_, i) => (
            <div key={i} className="mb-3 last:mb-0">
              <SkeletonLoader width="80%" height="18px" className="mb-1" />
              <SkeletonLoader width="60%" height="14px" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
