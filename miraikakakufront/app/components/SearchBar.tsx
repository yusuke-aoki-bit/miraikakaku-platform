'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Search, X } from 'lucide-react';
import { stockAPI } from '../lib/api';
import { SearchResult } from '../types';
import LoadingSpinner from './LoadingSpinner';

interface SearchBarProps {
  onSelectStock: (symbol: string) => void;
  placeholder?: string;
  className?: string;
}

export default function SearchBar({ 
  onSelectStock, 
  placeholder,
  className = ""
}: SearchBarProps) {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  
  const searchPlaceholder = placeholder || t('search.placeholder');

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (resultsRef.current && !resultsRef.current.contains(event.target as Node) &&
          inputRef.current && !inputRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const searchStocks = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setShowResults(false);
      return;
    }

    setIsLoading(true);
    try {
      // Try API call first
      const searchResults = await stockAPI.search(searchQuery, 8);
      setResults(searchResults);
      setShowResults(true);
      setSelectedIndex(-1);
    } catch (error) {
      console.error('Search error:', error);
      // Provide mock search results for testing
      const mockResults: SearchResult[] = [
        {
          symbol: searchQuery.toUpperCase().includes('AAPL') || searchQuery.includes('アップル') ? 'AAPL' : searchQuery.toUpperCase(),
          name: searchQuery.includes('アップル') ? 'Apple Inc.' : `${searchQuery} Company`,
          type: 'stock'
        }
      ];
      setResults(mockResults);
      setShowResults(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (query) {
        searchStocks(query);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleSelectStock = (symbol: string) => {
    setQuery(symbol);
    setShowResults(false);
    onSelectStock(symbol);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (query.trim()) {
      if (selectedIndex >= 0 && results[selectedIndex]) {
        handleSelectStock(results[selectedIndex].symbol);
      } else {
        handleSelectStock(query.trim().toUpperCase());
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showResults || results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < results.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0) {
          handleSelectStock(results[selectedIndex].symbol);
        } else {
          handleSubmit(e);
        }
        break;
      case 'Escape':
        setShowResults(false);
        setSelectedIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };

  const clearSearch = () => {
    setQuery('');
    setResults([]);
    setShowResults(false);
    inputRef.current?.focus();
  };

  return (
    <div className={`relative w-full ${className}`}>
      <form onSubmit={handleSubmit}>
        <div className="relative flex">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: 'var(--yt-music-text-disabled)' }} />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={() => query && setShowResults(true)}
              placeholder={searchPlaceholder}
              className="w-full pl-10 pr-10 py-4 rounded-l-full focus:outline-none transition-all duration-200"
              style={{
                backgroundColor: 'var(--yt-music-surface-variant)',
                border: '1px solid var(--yt-music-border)',
                borderRight: 'none',
                color: 'var(--yt-music-text-primary)',
                fontSize: '16px'
              }}
              autoComplete="off"
              onFocus={(e) => {
                e.currentTarget.style.borderColor = 'var(--yt-music-accent)';
                e.currentTarget.style.boxShadow = '0 0 0 2px rgba(62, 166, 255, 0.2)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = 'var(--yt-music-border)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            />
            {query && (
              <button
                type="button"
                onClick={clearSearch}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 hover:scale-110 transition-transform duration-200"
                style={{ color: 'var(--yt-music-text-disabled)' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = 'var(--yt-music-text-primary)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = 'var(--yt-music-text-disabled)';
                }}
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="px-6 py-4 rounded-r-full font-medium transition-all duration-200 hover:scale-105 flex items-center space-x-2"
            style={{
              backgroundColor: isLoading ? 'var(--yt-music-border)' : 'var(--yt-music-primary)',
              border: `1px solid ${isLoading ? 'var(--yt-music-border)' : 'var(--yt-music-primary)'}`,
              color: 'white',
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                e.currentTarget.style.backgroundColor = 'var(--yt-music-primary-hover)';
                e.currentTarget.style.transform = 'scale(1.05)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading) {
                e.currentTarget.style.backgroundColor = 'var(--yt-music-primary)';
                e.currentTarget.style.transform = 'scale(1)';
              }
            }}
          >
            {isLoading ? (
              <>
                <LoadingSpinner size="sm" />
                <span>検索中...</span>
              </>
            ) : (
              <span>{t('search.button')}</span>
            )}
          </button>
        </div>
        <style jsx>{`
          input::placeholder {
            color: var(--yt-music-text-disabled);
          }
        `}</style>
      </form>

      {showResults && (
        <div 
          ref={resultsRef}
          className="absolute top-full left-0 right-0 z-50 rounded-xl shadow-2xl mt-2 max-h-80 overflow-y-auto glass-effect"
          style={{
            border: '1px solid var(--yt-music-border)'
          }}
        >
          {isLoading ? (
            <div className="px-6 py-4 text-center flex items-center justify-center space-x-2">
              <LoadingSpinner size="sm" />
              <span style={{ color: 'var(--yt-music-text-secondary)' }}>
                {t('search.searching')}
              </span>
            </div>
          ) : results.length > 0 ? (
            <div>
              {results.map((result, index) => (
                <button
                  key={result.symbol}
                  onClick={() => handleSelectStock(result.symbol)}
                  className={`w-full px-6 py-4 text-left transition-all duration-200 border-b last:border-b-0 ${
                    selectedIndex === index ? 'scale-105' : ''
                  }`}
                  style={{
                    backgroundColor: selectedIndex === index ? 'var(--yt-music-surface-hover)' : 'transparent',
                    borderColor: 'var(--yt-music-border)'
                  }}
                  onMouseEnter={(e) => {
                    if (selectedIndex !== index) {
                      e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-hover)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedIndex !== index) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold" style={{ color: 'var(--yt-music-text-primary)' }}>
                        {result.symbol}
                      </div>
                      <div className="text-sm truncate" style={{ color: 'var(--yt-music-text-secondary)' }}>
                        {result.longName || result.shortName}
                      </div>
                      {result.sector && (
                        <div className="text-xs" style={{ color: 'var(--yt-music-text-disabled)' }}>
                          {result.sector}
                        </div>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          ) : query && !isLoading ? (
            <div className="px-6 py-4 text-center" style={{ color: 'var(--yt-music-text-secondary)' }}>
              {t('search.noResults', { query })}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}