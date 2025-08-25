'use client';

import React, { useState, useEffect } from 'react';
import { 
  Star, 
  StarOff, 
  TrendingUp, 
  TrendingDown, 
  Zap,
  ExternalLink,
  Building2,
  ChevronUp,
  ChevronDown,
  Filter
} from 'lucide-react';
import apiClient from '@/lib/api-client';

interface StockInSector {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  ai_score: number;
  market_cap?: number;
  volume?: number;
  isWatched: boolean;
}

interface TopStocksInSectorProps {
  sectorId: string | null;
  sectorName: string | null;
}

type SortField = 'symbol' | 'current_price' | 'change_percent' | 'ai_score' | 'market_cap';
type SortOrder = 'asc' | 'desc';

export default function TopStocksInSector({ sectorId, sectorName }: TopStocksInSectorProps) {
  const [stocks, setStocks] = useState<StockInSector[]>([]);
  const [loading, setLoading] = useState(false);
  const [sortField, setSortField] = useState<SortField>('ai_score');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [filterType, setFilterType] = useState<'all' | 'gainers' | 'losers'>('all');

  useEffect(() => {
    if (sectorId) {
      fetchSectorStocks();
    }
  }, [sectorId]);

  const fetchSectorStocks = async () => {
    if (!sectorId) return;
    
    setLoading(true);
    try {
      const response = await apiClient.getStocksBySector(sectorId, { limit: 50 });
      
      if (response.status === 'success' && Array.isArray(response.data)) {
        // ウォッチリスト情報を取得
        const watchlist = JSON.parse(localStorage.getItem('user_watchlist') || '[]');
        
        const enhancedStocks: StockInSector[] = response.data.map((stock: any) => ({
          symbol: stock.symbol,
          company_name: stock.company_name || stock.name || stock.symbol,
          current_price: stock.current_price || 1000,
          change_percent: stock.change_percent || 0,
          ai_score: stock.ai_score || 75,
          market_cap: stock.market_cap || 1000000000,
          volume: stock.volume || 1000000,
          isWatched: watchlist.includes(stock.symbol)
        }));

        setStocks(enhancedStocks);
      }
    } catch (error) {
      console.error('Failed to fetch sector stocks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const handleWatchlistToggle = (symbol: string) => {
    const watchlist = JSON.parse(localStorage.getItem('user_watchlist') || '[]');
    let updatedWatchlist;

    if (watchlist.includes(symbol)) {
      updatedWatchlist = watchlist.filter((item: string) => item !== symbol);
    } else {
      updatedWatchlist = [...watchlist, symbol];
    }

    localStorage.setItem('user_watchlist', JSON.stringify(updatedWatchlist));
    
    setStocks(prev => prev.map(stock => 
      stock.symbol === symbol 
        ? { ...stock, isWatched: !stock.isWatched }
        : stock
    ));
  };

  const handleStockClick = (symbol: string) => {
    window.location.href = `/stock/${symbol}`;
  };

  // フィルタリング
  const filteredStocks = stocks.filter(stock => {
    switch (filterType) {
      case 'gainers':
        return stock.change_percent > 0;
      case 'losers':
        return stock.change_percent < 0;
      default:
        return true;
    }
  });

  // ソート
  const sortedStocks = [...filteredStocks].sort((a, b) => {
    let aVal: any = a[sortField];
    let bVal: any = b[sortField];

    if (sortField === 'symbol') {
      return sortOrder === 'asc' 
        ? aVal.localeCompare(bVal)
        : bVal.localeCompare(aVal);
    }

    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
    }

    return 0;
  });

  const formatMarketCap = (marketCap: number): string => {
    if (marketCap >= 1000000000000) {
      return `${(marketCap / 1000000000000).toFixed(1)}兆円`;
    } else if (marketCap >= 100000000) {
      return `${(marketCap / 100000000).toFixed(0)}億円`;
    } else {
      return `${(marketCap / 100000000).toFixed(1)}億円`;
    }
  };

  const SortButton = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center space-x-1 text-left hover:text-blue-400 transition-colors"
    >
      <span>{children}</span>
      {sortField === field && (
        sortOrder === 'asc' 
          ? <ChevronUp className="w-3 h-3" />
          : <ChevronDown className="w-3 h-3" />
      )}
    </button>
  );

  if (!sectorId) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-8">
        <div className="text-center">
          <Building2 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-400 mb-2">
            セクターを選択してください
          </h3>
          <p className="text-gray-500 text-sm">
            ヒートマップからセクターをクリックして<br />
            そのセクター内の主要銘柄を表示
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center">
          <Building2 className="w-5 h-5 mr-2 text-green-400" />
          {sectorName} - 主要銘柄
          {stocks.length > 0 && (
            <span className="ml-2 text-sm text-gray-400">
              ({filteredStocks.length}/{stocks.length}社)
            </span>
          )}
        </h3>

        {/* フィルター */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center bg-gray-800/50 rounded-lg p-1">
            <button
              onClick={() => setFilterType('all')}
              className={`px-3 py-1 rounded-md text-sm transition-all ${
                filterType === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              すべて
            </button>
            <button
              onClick={() => setFilterType('gainers')}
              className={`px-3 py-1 rounded-md text-sm transition-all ${
                filterType === 'gainers'
                  ? 'bg-green-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              上昇
            </button>
            <button
              onClick={() => setFilterType('losers')}
              className={`px-3 py-1 rounded-md text-sm transition-all ${
                filterType === 'losers'
                  ? 'bg-red-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              下落
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-400"></div>
        </div>
      ) : sortedStocks.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-gray-700/50">
              <tr className="text-sm text-gray-300">
                <th className="text-left p-3">
                  <SortButton field="symbol">銘柄</SortButton>
                </th>
                <th className="text-right p-3">
                  <SortButton field="current_price">現在値</SortButton>
                </th>
                <th className="text-right p-3">
                  <SortButton field="change_percent">変動率</SortButton>
                </th>
                <th className="text-right p-3">
                  <SortButton field="ai_score">AIスコア</SortButton>
                </th>
                <th className="text-right p-3">
                  <SortButton field="market_cap">時価総額</SortButton>
                </th>
                <th className="text-center p-3">アクション</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/30">
              {sortedStocks.map((stock, index) => (
                <tr 
                  key={stock.symbol}
                  className="hover:bg-gray-800/20 transition-all group cursor-pointer"
                  onClick={() => handleStockClick(stock.symbol)}
                >
                  <td className="p-3">
                    <div className="flex items-center space-x-3">
                      <div className="text-sm font-bold text-gray-400 w-6">
                        {index + 1}
                      </div>
                      <div>
                        <div className="font-medium text-white group-hover:text-blue-400 transition-colors flex items-center">
                          {stock.symbol}
                          <ExternalLink className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                        <div className="text-xs text-gray-400 truncate max-w-32">
                          {stock.company_name}
                        </div>
                      </div>
                    </div>
                  </td>

                  <td className="p-3 text-right">
                    <div className="font-medium text-white">
                      {stock.symbol.match(/^[A-Z]+$/) ? '$' : '¥'}
                      {stock.current_price.toLocaleString('ja-JP', {
                        minimumFractionDigits: stock.symbol.match(/^[A-Z]+$/) ? 2 : 0,
                        maximumFractionDigits: stock.symbol.match(/^[A-Z]+$/) ? 2 : 0
                      })}
                    </div>
                  </td>

                  <td className="p-3 text-right">
                    <div className={`font-medium flex items-center justify-end ${
                      stock.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {stock.change_percent >= 0 ? (
                        <TrendingUp className="w-3 h-3 mr-1" />
                      ) : (
                        <TrendingDown className="w-3 h-3 mr-1" />
                      )}
                      {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                    </div>
                  </td>

                  <td className="p-3 text-right">
                    <div className="flex items-center justify-end space-x-1">
                      <Zap className="w-3 h-3 text-yellow-400" />
                      <span className="font-medium text-white">
                        {stock.ai_score.toFixed(0)}
                      </span>
                    </div>
                  </td>

                  <td className="p-3 text-right">
                    <div className="font-medium text-gray-300 text-sm">
                      {stock.market_cap ? formatMarketCap(stock.market_cap) : '-'}
                    </div>
                  </td>

                  <td className="p-3">
                    <div className="flex items-center justify-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleWatchlistToggle(stock.symbol);
                        }}
                        className={`p-1 rounded transition-colors ${
                          stock.isWatched 
                            ? 'text-yellow-400 hover:text-yellow-300' 
                            : 'text-gray-400 hover:text-yellow-400'
                        }`}
                        title={stock.isWatched ? 'ウォッチリストから削除' : 'ウォッチリストに追加'}
                      >
                        {stock.isWatched ? (
                          <Star className="w-4 h-4 fill-current" />
                        ) : (
                          <StarOff className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-400">
          <Filter className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <div>条件に該当する銘柄がありません</div>
          <div className="text-sm mt-1">フィルター条件を変更してください</div>
        </div>
      )}
    </div>
  );
}