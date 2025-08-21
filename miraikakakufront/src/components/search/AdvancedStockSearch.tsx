'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Filter, Globe, Building2, TrendingUp, X } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface Stock {
  symbol: string;
  company_name: string;
  sector: string;
  industry: string;
  exchange: string;
  currency: string;
  relevance_score?: number;
}

interface Sector {
  sector: string;
  company_count: number;
  jpy_count: number;
  usd_count: number;
}

export default function AdvancedStockSearch() {
  const [query, setQuery] = useState('');
  const [currency, setCurrency] = useState<string>('');
  const [selectedSector, setSelectedSector] = useState<string>('');
  const [searchResults, setSearchResults] = useState<Stock[]>([]);
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // セクター一覧を取得
  useEffect(() => {
    const fetchSectors = async () => {
      try {
        const response = await apiClient.getSectors();
        if (response.status === 'success' && response.data) {
          setSectors(Array.isArray(response.data) ? response.data : []);
        }
      } catch (error) {
        console.error('セクター取得エラー:', error);
      }
    };

    fetchSectors();
  }, []);

  // 検索実行のデバウンス処理
  const debounce = (func: Function, wait: number) => {
    let timeout: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(null, args), wait);
    };
  };

  // 検索処理
  const performSearch = useCallback(async (searchQuery: string, currencyFilter?: string) => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.searchStocks(
        searchQuery,
        20,
        currencyFilter
      );

      if (response.status === 'success' && response.data) {
        setSearchResults(Array.isArray(response.data) ? response.data : []);
      } else {
        setSearchResults([]);
      }
    } catch (error) {
      console.error('検索エラー:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // セクター別検索
  const searchBySector = useCallback(async (sectorId: string, currencyFilter: string = 'JPY') => {
    if (!sectorId) return;

    setLoading(true);
    try {
      const response = await apiClient.getStocksBySector(sectorId, 20, currencyFilter);
      if (response.status === 'success' && response.data) {
        setSearchResults(Array.isArray(response.data) ? response.data : []);
      } else {
        setSearchResults([]);
      }
    } catch (error) {
      console.error('セクター検索エラー:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const debouncedSearch = useCallback(debounce(performSearch, 300), [performSearch]);

  // クエリ変更時の処理
  useEffect(() => {
    if (query) {
      debouncedSearch(query, currency);
    } else {
      setSearchResults([]);
    }
  }, [query, currency, debouncedSearch]);

  // セクター選択時の処理
  useEffect(() => {
    if (selectedSector) {
      searchBySector(selectedSector, currency || 'JPY');
      setQuery(''); // クエリをクリア
    }
  }, [selectedSector, currency, searchBySector]);

  const handleStockSelect = (stock: Stock) => {
    // 銘柄詳細ページに遷移
    window.location.href = `/stock/${stock.symbol}`;
  };

  const clearFilters = () => {
    setCurrency('');
    setSelectedSector('');
    setQuery('');
    setSearchResults([]);
  };

  const getSectorDisplayName = (sectorCode: string) => {
    // 数字セクターの場合は簡略表示
    if (/^\d+$/.test(sectorCode)) {
      return `セクター ${sectorCode}`;
    }
    return sectorCode;
  };

  const formatMarketCap = (count: number) => {
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-gray-800/50 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <Search className="w-6 h-6 mr-3 text-red-400" />
          日本株検索
        </h2>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
            showFilters
              ? 'bg-red-500/20 text-red-400 border border-red-500/30'
              : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 border border-gray-700/50'
          }`}
        >
          <Filter className="w-4 h-4" />
          <span>フィルター</span>
        </button>
      </div>

      {/* 検索フォーム */}
      <div className="space-y-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="企業名、銘柄コード、セクターで検索..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-red-500 focus:outline-none"
          />
        </div>

        {/* フィルター */}
        {showFilters && (
          <div className="bg-gray-800/30 rounded-lg p-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* 通貨フィルター */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Globe className="w-4 h-4 inline mr-2" />
                  通貨
                </label>
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-red-500 focus:outline-none"
                >
                  <option value="">全て</option>
                  <option value="JPY">日本円 (JPY)</option>
                  <option value="USD">米ドル (USD)</option>
                </select>
              </div>

              {/* セクターフィルター */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Building2 className="w-4 h-4 inline mr-2" />
                  セクター
                </label>
                <select
                  value={selectedSector}
                  onChange={(e) => setSelectedSector(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-red-500 focus:outline-none"
                >
                  <option value="">全セクター</option>
                  {sectors.slice(0, 20).map((sector) => (
                    <option key={sector.sector} value={sector.sector}>
                      {getSectorDisplayName(sector.sector)} ({formatMarketCap(sector.jpy_count)}社)
                    </option>
                  ))}
                </select>
              </div>

              {/* クリアボタン */}
              <div className="flex items-end">
                <button
                  onClick={clearFilters}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-600/50 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors"
                >
                  <X className="w-4 h-4" />
                  <span>クリア</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 検索結果 */}
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-400"></div>
        </div>
      ) : searchResults.length > 0 ? (
        <div className="space-y-2">
          <div className="text-sm text-gray-400 mb-4">
            {searchResults.length}件の結果
          </div>
          {searchResults.map((stock, index) => (
            <div
              key={`${stock.symbol}-${index}`}
              onClick={() => handleStockSelect(stock)}
              className="flex items-center justify-between p-4 bg-gray-800/30 rounded-lg hover:bg-gray-800/50 cursor-pointer transition-colors group"
            >
              <div className="flex items-center space-x-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-medium text-white group-hover:text-red-400 transition-colors">
                      {stock.symbol}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded ${
                      stock.currency === 'JPY' 
                        ? 'bg-green-500/20 text-green-400' 
                        : 'bg-blue-500/20 text-blue-400'
                    }`}>
                      {stock.currency}
                    </span>
                  </div>
                  <div className="text-sm text-gray-300 mt-1">{stock.company_name}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {getSectorDisplayName(stock.sector)} • {stock.exchange}
                  </div>
                </div>
              </div>
              <div className="text-gray-400">
                <TrendingUp className="w-5 h-5" />
              </div>
            </div>
          ))}
        </div>
      ) : query && !loading ? (
        <div className="text-center py-8 text-gray-400">
          <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>検索結果が見つかりませんでした</p>
          <p className="text-sm mt-2">別のキーワードをお試しください</p>
        </div>
      ) : null}
    </div>
  );
}