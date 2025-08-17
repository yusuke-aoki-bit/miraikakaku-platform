'use client';

import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

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
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/search?query=${encodeURIComponent(searchQuery)}&limit=10`
      );
      
      if (response.ok) {
        const data = await response.json();
        setStocks(data);
      } else {
        // フォールバック用のモックデータ
        const mockStocks: Stock[] = [
          { symbol: 'AAPL', company_name: 'Apple Inc.', exchange: 'NASDAQ', sector: 'Technology' },
          { symbol: 'GOOGL', company_name: 'Alphabet Inc.', exchange: 'NASDAQ', sector: 'Technology' },
          { symbol: 'MSFT', company_name: 'Microsoft Corporation', exchange: 'NASDAQ', sector: 'Technology' },
          { symbol: 'TSLA', company_name: 'Tesla Inc.', exchange: 'NASDAQ', sector: 'Automotive' },
          { symbol: 'AMZN', company_name: 'Amazon.com Inc.', exchange: 'NASDAQ', sector: 'E-commerce' },
        ].filter(stock => 
          stock.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
          stock.company_name.toLowerCase().includes(searchQuery.toLowerCase())
        );
        setStocks(mockStocks);
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
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
        />
      </div>

      {/* 検索結果 */}
      {stocks.length > 0 && (
        <div className="absolute top-full left-0 right-0 z-10 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {stocks.map((stock) => (
            <button
              key={stock.symbol}
              onClick={() => handleStockSelect(stock.symbol)}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors duration-150"
            >
              <div className="font-semibold text-gray-900">{stock.symbol}</div>
              <div className="text-sm text-gray-600 truncate">{stock.company_name}</div>
              <div className="text-xs text-gray-500">
                {stock.exchange} {stock.sector && `• ${stock.sector}`}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* ローディング */}
      {loading && (
        <div className="absolute top-full left-0 right-0 z-10 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
          <div className="text-center text-gray-600 flex items-center justify-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            検索中...
          </div>
        </div>
      )}
    </div>
  );
}