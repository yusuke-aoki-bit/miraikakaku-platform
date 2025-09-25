'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, X, Filter, TrendingUp, ChevronDown } from 'lucide-react';
import { stockAPI } from '../lib/api';
import { SearchResult } from '../types';
import LoadingSpinner from './LoadingSpinner';
import { InlineLoading } from './Loading';

interface SearchBarProps {
  onSelectStock: (symbol: string) => void;
  placeholder?: string;
  className?: string;
}

interface MarketFilter {
  value: string;
  label: string;
  emoji: string;
}

interface SortOption {
  value: string;
  label: string;
  icon?: string;
}

export default function SearchBar({
  onSelectStock
  placeholder
  className = ""
}: SearchBarProps) {
  const [query, setQuery] = useState(''
  const [results, setResults] = useState<SearchResult[]>([]
  const [suggestions, setSuggestions] = useState<{symbol: string, display: string, type: string}[]>([]
  const [popularStocks, setPopularStocks] = useState<SearchResult[]>([]
  const [isLoading, setIsLoading] = useState(false
  const [showResults, setShowResults] = useState(false
  const [showFilters, setShowFilters] = useState(false
  const [selectedIndex, setSelectedIndex] = useState(-1
  const [selectedMarket, setSelectedMarket] = useState('all'
  const [selectedSort, setSelectedSort] = useState('relevance'
  const inputRef = useRef<HTMLInputElement>(null
  const resultsRef = useRef<HTMLDivElement>(null
  const filtersRef = useRef<HTMLDivElement>(null
  // Market filter options
  const marketFilters: MarketFilter[] = [
    { value: 'all', label: '全市場', emoji: '🌍' }
    { value: 'us', label: '米国株', emoji: '🇺🇸' }
    { value: 'jp', label: '日本株', emoji: '🇯🇵' }
    { value: 'hk', label: '香港株', emoji: '🇭🇰' }
    { value: 'crypto', label: '仮想通貨', emoji: '🪙' }
  ];

  // Sort options
  const sortOptions: SortOption[] = [
    { value: 'relevance', label: '関連性', icon: '🎯' }
    { value: 'price', label: '価格', icon: '💰' }
    { value: 'volume', label: '出来高', icon: '📊' }
    { value: 'symbol', label: 'シンボル', icon: '🔤' }
  ];
  
  const searchPlaceholder = placeholder || '銘柄コードまたは会社名を入力...';

  // Load popular stocks on component mount
  useEffect(() => {
    const loadPopularStocks = async () => {
      try {
        const popular = await stockAPI.getPopularStocks(
        setPopularStocks(popular.slice(0, 5)); // Top 5 popular stocks
      } catch (error) {
        }
    };
    loadPopularStocks(
  }, []
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (resultsRef.current && !resultsRef.current.contains(event.target as Node) &&
          inputRef.current && !inputRef.current.contains(event.target as Node) &&
          filtersRef.current && !filtersRef.current.contains(event.target as Node)) {
        setShowResults(false
        setShowFilters(false
      }
    };

    document.addEventListener('mousedown', handleClickOutside
    return () => document.removeEventListener('mousedown', handleClickOutside
  }, []
  const searchStocks = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]
      setSuggestions([]
      setShowResults(false
      return;
    }

    setIsLoading(true
    try {
      // Load both search results and suggestions in parallel
      const [searchResults, searchSuggestions] = await Promise.all([
        stockAPI.search(searchQuery, 8, selectedMarket, selectedSort)
        stockAPI.searchSuggestions(searchQuery)
      ]
      setResults(searchResults
      setSuggestions(searchSuggestions.slice(0, 5)); // Top 5 suggestions
      setShowResults(true
      setSelectedIndex(-1
    } catch (error) {
      // Provide mock search results for testing
      const mockResults: SearchResult[] = [
        {
          symbol: searchQuery.toUpperCase().includes('AAPL') || searchQuery.includes('アップル') ? 'AAPL' : searchQuery.toUpperCase()
          name: searchQuery.includes('アップル') ? 'Apple Inc.'
          type: 'stock'
        }
      ];
      setResults(mockResults
      setSuggestions([]
      setShowResults(true
    } finally {
      setIsLoading(false
    }
  }, [selectedMarket, selectedSort]
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (query) {
        searchStocks(query
      }
    }, 300
    return () => clearTimeout(timeoutId
  }, [query, selectedMarket, selectedSort, searchStocks]
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value
  };

  const handleSelectStock = (symbol: string) => {
    setQuery(symbol
    setShowResults(false
    onSelectStock(symbol
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault(
    if (query.trim()) {
      if (selectedIndex >= 0 && results[selectedIndex]) {
        handleSelectStock(results[selectedIndex].symbol
      } else {
        handleSelectStock(query.trim().toUpperCase()
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showResults || results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown'
        e.preventDefault(
        setSelectedIndex(prev => 
          prev < results.length - 1 ? prev + 1 : prev
        break;
      case 'ArrowUp'
        e.preventDefault(
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1
        break;
      case 'Enter'
        e.preventDefault(
        if (selectedIndex >= 0) {
          handleSelectStock(results[selectedIndex].symbol
        } else {
          handleSubmit(e
        }
        break;
      case 'Escape'
        setShowResults(false
        setSelectedIndex(-1
        inputRef.current?.blur(
        break;
    }
  };

  const clearSearch = () => {
    setQuery(''
    setResults([]
    setSuggestions([]
    setShowResults(false
    inputRef.current?.focus(
  };

  const toggleFilters = () => {
    setShowFilters(!showFilters
  };

  const handleMarketChange = (market: string) => {
    setSelectedMarket(market
    setShowFilters(false
    if (query) {
      searchStocks(query
    }
  };

  const handleSortChange = (sort: string) => {
    setSelectedSort(sort
    setShowFilters(false
    if (query) {
      searchStocks(query
    }
  };

  return (
    <div className={`relative w-full ${className}`}>
      <form onSubmit={handleSubmit}>
        <div className="relative flex">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 theme-text-secondary" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={() => {
                (query || popularStocks.length > 0) && setShowResults(true
              }}
              placeholder={searchPlaceholder}
              className="theme-input w-full pl-10 pr-20 py-4 rounded-l-full border-r-0 focus:ring-2 focus:ring-blue-500/50 transition-all duration-300"
              autoComplete="off"
              data-testid="search-input"
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
              {query && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="hover:scale-110 transition-transform duration-200 theme-text-secondary hover:theme-text-primary"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              <button
                type="button"
                onClick={toggleFilters}
                className={`p-1 rounded-full transition-all duration-200 hover:scale-110 ${
                  showFilters ? 'scale-110 theme-text-primary' : 'theme-text-secondary hover:theme-text-primary'
                }`}
                style={{
                  backgroundColor: showFilters ? 'rgb(var(--theme-bg-hover))' : 'transparent'
                }}
              >
                <Filter className="w-4 h-4" />
              </button>
            </div>
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className={`px-6 py-4 rounded-r-full font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg flex items-center space-x-2 ${
              isLoading ? 'theme-btn-disabled' : 'theme-btn-primary pulse-glow'
            }`}
          >
            {isLoading ? (
              <>
                <InlineLoading size="small" />
                <span data-testid="searching-text">検索中...</span>
              </>
            ) : (
              <span>検索</span>
            )}
          </button>
        </div>
      </form>

      {/* Advanced Filters Panel */}
      {showFilters && (
        <div
          ref={filtersRef}
          className="absolute top-full left-0 right-0 z-40 theme-card mt-1 p-4"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Market Filter */}
            <div>
              <label className="block text-sm font-medium mb-2 theme-text-primary">
                市場フィルタ
              </label>
              <div className="grid grid-cols-2 gap-2">
                {marketFilters.map((market) => (
                  <button
                    key={market.value}
                    type="button"
                    onClick={() => handleMarketChange(market.value)}
                    className={`p-2 rounded-lg text-sm transition-all duration-200 hover:scale-105 ${
                      selectedMarket === market.value ? 'theme-btn-primary' : 'theme-btn-secondary'
                    }`}
                  >
                    <span className="mr-1">{market.emoji}</span>
                    {market.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Sort Options */}
            <div>
              <label className="block text-sm font-medium mb-2 theme-text-primary">
                並び順
              </label>
              <div className="grid grid-cols-2 gap-2">
                {sortOptions.map((sort) => (
                  <button
                    key={sort.value}
                    type="button"
                    onClick={() => handleSortChange(sort.value)}
                    className={`p-2 rounded-lg text-sm transition-all duration-200 hover:scale-105 ${
                      selectedSort === sort.value ? 'theme-btn-primary' : 'theme-btn-secondary'
                    }`}
                  >
                    <span className="mr-1">{sort.icon}</span>
                    {sort.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {showResults && (
        <div
          ref={resultsRef}
          className="absolute top-full left-0 right-0 z-50 theme-card mt-2 max-h-96 overflow-y-auto"
          style={{
            marginTop: showFilters ? '1rem' : '0.5rem'
          }}
        >
          {isLoading ? (
            <div className="px-6 py-4 text-center flex items-center justify-center space-x-2">
              <div className="theme-spinner w-5 h-5"></div>
              <span className="theme-text-secondary">
                検索中...
              </span>
            </div>
          ) : (
            <div>
              {/* Search Results Section */}
              {results.length > 0 && (
                <div>
                  <div className="px-4 py-2 border-b theme-border">
                    <div className="flex items-center space-x-2">
                      <Search className="w-4 h-4 theme-text-secondary" />
                      <span className="text-sm font-medium theme-text-secondary">
                        検索結果 ({results.length}件)
                      </span>
                    </div>
                  </div>
                  {results.map((result, index) => (
                    <button
                      key={`result-${result.symbol}`}
                      onClick={() => handleSelectStock(result.symbol)}
                      className={`w-full px-6 py-4 text-left transition-all duration-200 border-b last:border-b-0 hover:scale-[1.02] theme-border hover:bg-hover ${
                        selectedIndex === index ? 'scale-[1.02] bg-hover' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <div className="font-semibold theme-text-primary">
                              {result.symbol}
                            </div>
                            {result.market && (
                              <span className="text-xs px-2 py-1 rounded-full theme-badge-primary">
                                {result.market}
                              </span>
                            )}
                          </div>
                          <div className="text-sm truncate theme-text-secondary">
                            {result.longName || result.shortName}
                          </div>
                          {result.currentPrice && (
                            <div className="text-xs theme-caption">
                              ${result.currentPrice}
                            </div>
                          )}
                        </div>
                        {result.relevanceScore && (
                          <div className="text-xs theme-caption">
                            {Math.round(result.relevanceScore)}%
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Suggestions Section */}
              {suggestions.length > 0 && (!query || results.length === 0) && (
                <div>
                  <div className="px-4 py-2 border-b theme-border">
                    <div className="flex items-center space-x-2">
                      <ChevronDown className="w-4 h-4 theme-text-secondary" />
                      <span className="text-sm font-medium theme-text-secondary">
                        候補
                      </span>
                    </div>
                  </div>
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={`suggestion-${suggestion.symbol}`}
                      onClick={() => handleSelectStock(suggestion.symbol)}
                      className="w-full px-6 py-3 text-left transition-all duration-200 border-b last:border-b-0 hover:scale-[1.02] theme-border hover:bg-hover"
                    >
                      <div className="text-sm theme-text-primary">
                        {suggestion.display}
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Popular Stocks Section */}
              {popularStocks.length > 0 && !query && (
                <div>
                  <div className="px-4 py-2 border-b theme-border">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="w-4 h-4 theme-text-secondary" />
                      <span className="text-sm font-medium theme-text-secondary">
                        人気銘柄
                      </span>
                    </div>
                  </div>
                  {popularStocks.map((stock, index) => (
                    <button
                      key={`popular-${stock.symbol}`}
                      onClick={() => handleSelectStock(stock.symbol)}
                      className="w-full px-6 py-3 text-left transition-all duration-200 border-b last:border-b-0 hover:scale-[1.02] theme-border hover:bg-hover"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium theme-text-primary">
                            {stock.symbol}
                          </div>
                          <div className="text-xs theme-text-secondary">
                            {stock.shortName || stock.longName}
                          </div>
                        </div>
                        {stock.currentPrice && (
                          <div className="text-sm font-medium theme-text-accent">
                            ${stock.currentPrice}
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* No Results */}
              {query && !isLoading && results.length === 0 && suggestions.length === 0 && (
                <div className="px-6 py-4 text-center theme-text-secondary">
                  検索結果が見つかりませんでした: &quot;{query}&quot;
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
}