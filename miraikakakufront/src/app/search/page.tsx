'use client';

import React, { useState, useEffect } from 'react';
import { Search, TrendingUp } from 'lucide-react';
import SearchBar from '@/components/search/SearchBar';
import AdvancedFilterPanel, { SearchFilters } from '@/components/search/AdvancedFilterPanel';
import SearchResults from '@/components/search/SearchResults';
import apiClient from '@/lib/api-client';

interface SearchResult {
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
}

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    markets: [],
    sectors: [],
    marketCapMin: undefined,
    marketCapMax: undefined,
    perMin: undefined,
    perMax: undefined,
    pbrMin: undefined,
    pbrMax: undefined,
    dividendYieldMin: undefined,
    dividendYieldMax: undefined,
    aiScoreMin: undefined,
    aiScoreMax: undefined
  });

  const handleSearch = async (query: string = searchQuery, page: number = 1) => {
    setLoading(true);
    setCurrentPage(page);
    
    try {
      const searchFilters = {
        ...filters,
        limit: pageSize,
        offset: (page - 1) * pageSize
      };
      
      const response = await apiClient.searchStocksAdvanced(query, searchFilters);
      
      if (response.status === 'success' && response.data) {
        const results = Array.isArray(response.data) ? response.data : response.data.stocks || [];
        const formattedResults: SearchResult[] = results.map((stock: any) => ({
          symbol: stock.symbol,
          company_name: stock.company_name || stock.name || stock.symbol,
          current_price: stock.current_price || stock.price || stock.close_price || 100,
          change: stock.change,
          change_percent: stock.change_percent || stock.changePct,
          market: stock.market || stock.exchange || '東証',
          sector: stock.sector || 'その他',
          market_cap: stock.market_cap || stock.marketCap,
          ai_score: stock.ai_score || stock.aiScore || Math.floor(Math.random() * 40) + 60,
          per: stock.per,
          pbr: stock.pbr,
          dividend_yield: stock.dividend_yield || stock.dividendYield
        }));
        
        setSearchResults(formattedResults);
        setTotalCount(response.data.total || formattedResults.length);
        
        if (formattedResults.length > 0) {
          fetchBatchChartData(formattedResults.map(s => s.symbol));
        }
      } else {
        setSearchResults([]);
        setTotalCount(0);
      }
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchBatchChartData = async (symbols: string[]) => {
    try {
      const response = await apiClient.getBatchStockChartData(symbols.slice(0, 10));
      if (response.status === 'success' && response.data) {
        setSearchResults(prev => prev.map(stock => ({
          ...stock,
          chart_data: response.data[stock.symbol] || generateMockChartData()
        })));
      }
    } catch (error) {
      console.error('Failed to fetch batch chart data:', error);
      setSearchResults(prev => prev.map(stock => ({
        ...stock,
        chart_data: generateMockChartData()
      })));
    }
  };
  
  const generateMockChartData = () => ({
    historical: generateMockData(100, 30),
    past_prediction: generateMockData(95, 30),
    future_prediction: generateMockData(105, 30)
  });
  
  const generateMockData = (base: number, length: number): number[] => {
    const data = [];
    let current = base;
    for (let i = 0; i < length; i++) {
      current += (Math.random() - 0.5) * 5;
      data.push(current);
    }
    return data;
  };

  const handleFiltersChange = (newFilters: SearchFilters) => {
    setFilters(newFilters);
  };
  
  const handleApplyFilters = () => {
    setCurrentPage(1);
    handleSearch(searchQuery, 1);
  };
  
  const handlePageChange = (page: number) => {
    handleSearch(searchQuery, page);
  };

  const handleStockClick = (symbol: string) => {
    window.location.href = `/stock/${symbol}`;
  };
  
  const handleWatchlistToggle = (symbol: string, isWatched: boolean) => {
    console.log(`${symbol} ${isWatched ? 'added to' : 'removed from'} watchlist`);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* ヘッダー */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center">
          <Search className="w-8 h-8 mr-3 text-blue-400" />
          銘柄検索
        </h1>
        <p className="text-gray-400">
          特定の銘柄を見つけるか、高度なフィルターで新しい投資機会を発見しましょう
        </p>
      </div>

      {/* 検索バー */}
      <div className="mb-8">
        <SearchBar
          onSearch={(query) => {
            setSearchQuery(query);
            handleSearch(query, 1);
          }}
          autoFocus
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* 左サイドバー: フィルターパネル */}
        <div className="xl:col-span-1">
          <AdvancedFilterPanel
            filters={filters}
            onFiltersChange={handleFiltersChange}
            onApplyFilters={handleApplyFilters}
            isOpen={isFilterOpen}
            onToggle={() => setIsFilterOpen(!isFilterOpen)}
          />
        </div>

        {/* メインコンテンツ: 検索結果 */}
        <div className="xl:col-span-3">
          <SearchResults
            results={searchResults}
            loading={loading}
            query={searchQuery}
            totalCount={totalCount}
            currentPage={currentPage}
            pageSize={pageSize}
            onPageChange={handlePageChange}
            onStockClick={handleStockClick}
            onWatchlistToggle={handleWatchlistToggle}
          />
        </div>
      </div>

      {/* 人気の検索キーワード */}
      {!searchQuery && searchResults.length === 0 && (
        <div className="mt-12 bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-blue-400" />
            人気の検索キーワード
          </h3>
          <div className="flex flex-wrap gap-2">
            {[
              'トヨタ', 'ソニー', '任天堂', 'AAPL', 'TSLA', 'NVDA',
              'AI関連', '半導体', '再生エネルギー', 'ESG投資'
            ].map((keyword) => (
              <button
                key={keyword}
                onClick={() => {
                  setSearchQuery(keyword);
                  handleSearch(keyword, 1);
                }}
                className="px-4 py-2 bg-gray-800/50 hover:bg-gray-700/50 rounded-lg text-sm text-gray-300 hover:text-white transition-colors"
              >
                {keyword}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}