'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  TrendingUp, 
  TrendingDown, 
  Building2,
  X,
  ChevronDown
} from 'lucide-react';
import apiClient from '@/lib/api-client';

interface Stock {
  symbol: string;
  company_name: string;
  market: string;
  current_price: number;
  change_percent: number;
}

interface StockSelectorProps {
  selectedStock: Stock | null;
  onStockSelect: (stock: Stock) => void;
}

export default function StockSelector({ selectedStock, onStockSelect }: StockSelectorProps) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Stock[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [recentSearches, setRecentSearches] = useState<Stock[]>([]);
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // ローカルストレージから最近の検索を読み込み
    const saved = localStorage.getItem('recent_stock_searches');
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved));
      } catch (error) {
        console.error('Failed to parse recent searches:', error);
      }
    }
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (query.length > 0) {
      const timeoutId = setTimeout(() => {
        searchStocks();
      }, 300);

      return () => clearTimeout(timeoutId);
    } else {
      setSuggestions([]);
    }
  }, [query]);

  const searchStocks = async () => {
    if (query.length < 1) return;
    
    setLoading(true);
    try {
      const response = await apiClient.searchStocksAutocomplete(query, 10);
      if (response.success && response.data) {
        setSuggestions(response.data as any);
        setIsOpen(true);
      }
    } catch (error) {
      console.error('Stock search failed:', error);
      // モックデータでフォールバック
      const mockSuggestions: Stock[] = [
        { symbol: '7203', company_name: 'トヨタ自動車', market: 'TSE', current_price: 2500, change_percent: 1.2 },
        { symbol: '6758', company_name: 'ソニーグループ', market: 'TSE', current_price: 12000, change_percent: -0.5 },
        { symbol: 'AAPL', company_name: 'Apple Inc.', market: 'NASDAQ', current_price: 185.50, change_percent: 2.1 },
        { symbol: 'GOOGL', company_name: 'Alphabet Inc.', market: 'NASDAQ', current_price: 2800.75, change_percent: -1.3 }
      ].filter(stock => 
        stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
        stock.company_name.toLowerCase().includes(query.toLowerCase())
      );
      setSuggestions(mockSuggestions);
      setIsOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const handleStockSelect = (stock: Stock) => {
    onStockSelect(stock);
    setQuery('');
    setIsOpen(false);
    
    // 最近の検索履歴に追加
    const updatedRecents = [stock, ...recentSearches.filter(s => s.symbol !== stock.symbol)].slice(0, 5);
    setRecentSearches(updatedRecents);
    localStorage.setItem('recent_stock_searches', JSON.stringify(updatedRecents));
  };

  const handleInputFocus = () => {
    setIsOpen(true);
  };

  const clearSelection = () => {
    onStockSelect(null as any);
  };

  const formatPrice = (price: number, isUSStock: boolean) => {
    if (isUSStock) {
      return `$${price.toFixed(2)}`;
    }
    return `¥${price.toLocaleString('ja-JP')}`;
  };

  return (
    <div className="relative" ref={searchRef}>
      {/* メインの検索エリア */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white flex items-center">
            <Search className="w-5 h-5 mr-2 text-blue-400" />
            銘柄選択
          </h2>
          {selectedStock && (
            <button
              onClick={clearSelection}
              className="text-sm text-gray-400 hover:text-red-400 transition-colors"
            >
              選択解除
            </button>
          )}
        </div>

        {/* 選択中の銘柄表示 */}
        {selectedStock ? (
          <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Building2 className="w-5 h-5 text-blue-400" />
                <div>
                  <div className="font-semibold text-white text-lg">
                    {selectedStock.symbol}
                  </div>
                  <div className="text-sm text-gray-300">
                    {selectedStock.company_name}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {selectedStock.market}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-white">
                  {formatPrice(selectedStock.current_price, selectedStock.symbol.match(/^[A-Z]+$/) !== null)}
                </div>
                <div className={`text-sm font-medium flex items-center justify-end ${
                  selectedStock.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {selectedStock.change_percent >= 0 ? (
                    <TrendingUp className="w-3 h-3 mr-1" />
                  ) : (
                    <TrendingDown className="w-3 h-3 mr-1" />
                  )}
                  {selectedStock.change_percent >= 0 ? '+' : ''}{selectedStock.change_percent.toFixed(2)}%
                </div>
              </div>
            </div>
            
            <button
              onClick={clearSelection}
              className="mt-3 w-full py-2 text-sm text-gray-300 hover:text-white transition-colors border border-gray-600/50 hover:border-gray-500/50 rounded-md"
            >
              別の銘柄を選択
            </button>
          </div>
        ) : (
          <>
            {/* 検索入力フィールド */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="w-4 h-4 text-gray-400" />
              </div>
              <input
                ref={inputRef}
                type="text"
                placeholder="銘柄コードまたは企業名で検索 (例: AAPL, 7203, トヨタ)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={handleInputFocus}
                className="w-full pl-10 pr-10 py-3 bg-gray-800/50 border border-gray-700/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500/50 transition-colors"
              />
              {query && (
                <button
                  onClick={() => setQuery('')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              <div className="absolute inset-y-0 right-8 flex items-center pointer-events-none">
                <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
              </div>
            </div>

            {/* 最近の検索 */}
            {!query && recentSearches.length > 0 && !isOpen && (
              <div className="mt-4">
                <div className="text-sm text-gray-400 mb-2">最近の検索</div>
                <div className="flex flex-wrap gap-2">
                  {recentSearches.slice(0, 3).map((stock) => (
                    <button
                      key={stock.symbol}
                      onClick={() => handleStockSelect(stock)}
                      className="px-3 py-1 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700/50 rounded-md text-sm text-gray-300 hover:text-white transition-colors"
                    >
                      {stock.symbol}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {/* 検索結果ドロップダウン */}
        {isOpen && (query.length > 0 || recentSearches.length > 0) && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-gray-900 border border-gray-700 rounded-xl shadow-xl z-50 max-h-80 overflow-y-auto">
            {loading && (
              <div className="p-4 text-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-400 mx-auto"></div>
              </div>
            )}

            {/* 検索結果 */}
            {query.length > 0 && suggestions.length > 0 && (
              <div>
                <div className="px-4 py-2 text-xs text-gray-400 border-b border-gray-800">
                  検索結果
                </div>
                {suggestions.map((stock) => (
                  <button
                    key={stock.symbol}
                    onClick={() => handleStockSelect(stock)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-800/50 transition-colors border-b border-gray-800/30 last:border-b-0"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div>
                          <div className="font-medium text-white">
                            {stock.symbol}
                          </div>
                          <div className="text-sm text-gray-400 truncate max-w-48">
                            {stock.company_name}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {stock.market}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-white">
                          {formatPrice(stock.current_price, stock.symbol.match(/^[A-Z]+$/) !== null)}
                        </div>
                        <div className={`text-xs flex items-center ${
                          stock.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {stock.change_percent >= 0 ? (
                            <TrendingUp className="w-2 h-2 mr-1" />
                          ) : (
                            <TrendingDown className="w-2 h-2 mr-1" />
                          )}
                          {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* 最近の検索履歴 */}
            {query.length === 0 && recentSearches.length > 0 && (
              <div>
                <div className="px-4 py-2 text-xs text-gray-400 border-b border-gray-800">
                  最近の検索履歴
                </div>
                {recentSearches.map((stock) => (
                  <button
                    key={`recent-${stock.symbol}`}
                    onClick={() => handleStockSelect(stock)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-800/50 transition-colors border-b border-gray-800/30 last:border-b-0"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div>
                          <div className="font-medium text-white">
                            {stock.symbol}
                          </div>
                          <div className="text-sm text-gray-400 truncate max-w-48">
                            {stock.company_name}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-white">
                          {formatPrice(stock.current_price, stock.symbol.match(/^[A-Z]+$/) !== null)}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* 検索結果なし */}
            {query.length > 0 && !loading && suggestions.length === 0 && (
              <div className="p-4 text-center text-gray-400">
                <Search className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <div className="text-sm">「{query}」の検索結果が見つかりませんでした</div>
                <div className="text-xs mt-1">銘柄コードまたは企業名で検索してください</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}