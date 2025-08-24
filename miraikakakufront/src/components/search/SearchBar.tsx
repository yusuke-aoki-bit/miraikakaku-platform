'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Search, X, Clock, TrendingUp } from 'lucide-react';
import apiClient from '@/lib/api-client';

interface SearchSuggestion {
  symbol: string;
  company_name: string;
  market: string;
  current_price?: number;
  change_percent?: number;
}

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  autoFocus?: boolean;
}

export default function SearchBar({ 
  onSearch, 
  placeholder = "銘柄名またはシンボルを入力...",
  autoFocus = false 
}: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // ローカルストレージから最近の検索履歴を取得
    const saved = localStorage.getItem('recent_searches');
    if (saved) {
      setRecentSearches(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      if (query.trim() && query.length >= 2) {
        fetchSuggestions(query.trim());
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 300); // 300msのデバウンス

    return () => clearTimeout(delayedSearch);
  }, [query]);

  const fetchSuggestions = async (searchQuery: string) => {
    setLoading(true);
    try {
      const response = await apiClient.searchStocksAutocomplete(searchQuery, 8);
      if (response.status === 'success' && response.data) {
        setSuggestions(response.data);
        setShowSuggestions(true);
        setSelectedIndex(-1);
      } else {
        // フォールバック用のモックデータ
        const mockSuggestions: SearchSuggestion[] = [
          {
            symbol: '7203',
            company_name: 'トヨタ自動車',
            market: '東証プライム',
            current_price: 2850,
            change_percent: 1.2
          },
          {
            symbol: 'AAPL',
            company_name: 'Apple Inc.',
            market: 'NASDAQ',
            current_price: 175.50,
            change_percent: -0.8
          },
          {
            symbol: '6758',
            company_name: 'ソニーグループ',
            market: '東証プライム',
            current_price: 13200,
            change_percent: 2.1
          }
        ].filter(item => 
          item.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.company_name.toLowerCase().includes(searchQuery.toLowerCase())
        );
        
        setSuggestions(mockSuggestions);
        setShowSuggestions(mockSuggestions.length > 0);
        setSelectedIndex(-1);
      }
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleInputFocus = () => {
    if (query.trim() && suggestions.length > 0) {
      setShowSuggestions(true);
    } else if (!query.trim() && recentSearches.length > 0) {
      setShowSuggestions(true);
    }
  };

  const handleInputBlur = () => {
    // 少し遅延させてクリックイベントを処理できるようにする
    setTimeout(() => {
      setShowSuggestions(false);
      setSelectedIndex(-1);
    }, 200);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions) return;

    const itemCount = query.trim() ? suggestions.length : recentSearches.length;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => (prev + 1) % itemCount);
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev <= 0 ? itemCount - 1 : prev - 1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0) {
          if (query.trim()) {
            const selected = suggestions[selectedIndex];
            handleSuggestionClick(selected);
          } else {
            const recent = recentSearches[selectedIndex];
            handleRecentSearchClick(recent);
          }
        } else if (query.trim()) {
          handleSearch();
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    setQuery(`${suggestion.symbol} ${suggestion.company_name}`);
    setShowSuggestions(false);
    addToRecentSearches(suggestion.symbol);
    onSearch(suggestion.symbol);
  };

  const handleRecentSearchClick = (searchTerm: string) => {
    setQuery(searchTerm);
    setShowSuggestions(false);
    onSearch(searchTerm);
  };

  const handleSearch = () => {
    if (query.trim()) {
      const searchTerm = query.trim();
      addToRecentSearches(searchTerm);
      setShowSuggestions(false);
      onSearch(searchTerm);
    }
  };

  const addToRecentSearches = (searchTerm: string) => {
    const updated = [
      searchTerm,
      ...recentSearches.filter(item => item !== searchTerm)
    ].slice(0, 5); // 最新5件まで保持
    
    setRecentSearches(updated);
    localStorage.setItem('recent_searches', JSON.stringify(updated));
  };

  const clearQuery = () => {
    setQuery('');
    setSuggestions([]);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const clearRecentSearches = () => {
    setRecentSearches([]);
    localStorage.removeItem('recent_searches');
    setShowSuggestions(false);
  };

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      {/* 検索バー */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full pl-12 pr-12 py-4 bg-gray-900/50 border border-gray-700/50 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
        />
        
        {query && (
          <button
            onClick={clearQuery}
            className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        )}
        
        {loading && (
          <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-400 border-t-transparent"></div>
          </div>
        )}
      </div>

      {/* サジェストドロップダウン */}
      {showSuggestions && (
        <div 
          ref={suggestionsRef}
          className="absolute top-full left-0 right-0 mt-2 bg-gray-900/95 border border-gray-700/50 rounded-xl shadow-xl backdrop-blur-sm z-50"
        >
          {query.trim() ? (
            // 検索候補
            <>
              {suggestions.length > 0 ? (
                <div className="py-2">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={`${suggestion.symbol}-${index}`}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className={`w-full px-4 py-3 text-left hover:bg-gray-800/50 transition-colors ${
                        index === selectedIndex ? 'bg-gray-800/50' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-white">
                            {suggestion.symbol}
                          </div>
                          <div className="text-sm text-gray-400">
                            {suggestion.company_name}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {suggestion.market}
                          </div>
                        </div>
                        
                        {suggestion.current_price && (
                          <div className="text-right">
                            <div className="text-white font-medium">
                              {suggestion.symbol.match(/^[A-Z]+$/) ? '$' : '¥'}
                              {suggestion.current_price.toLocaleString()}
                            </div>
                            {suggestion.change_percent !== undefined && (
                              <div className={`text-sm flex items-center ${
                                suggestion.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
                              }`}>
                                <TrendingUp className="w-3 h-3 mr-1" />
                                {suggestion.change_percent >= 0 ? '+' : ''}
                                {suggestion.change_percent.toFixed(1)}%
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              ) : !loading && (
                <div className="py-4 px-4 text-center text-gray-400">
                  検索結果が見つかりませんでした
                </div>
              )}
            </>
          ) : (
            // 最近の検索履歴
            recentSearches.length > 0 && (
              <div className="py-2">
                <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800/50">
                  <div className="text-sm text-gray-400 flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    最近の検索
                  </div>
                  <button
                    onClick={clearRecentSearches}
                    className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
                  >
                    クリア
                  </button>
                </div>
                
                {recentSearches.map((searchTerm, index) => (
                  <button
                    key={`recent-${index}`}
                    onClick={() => handleRecentSearchClick(searchTerm)}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-800/50 transition-colors ${
                      index === selectedIndex ? 'bg-gray-800/50' : ''
                    }`}
                  >
                    <div className="text-white">{searchTerm}</div>
                  </button>
                ))}
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}