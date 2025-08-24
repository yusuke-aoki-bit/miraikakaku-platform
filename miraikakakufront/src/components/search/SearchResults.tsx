'use client';

import React, { useState, useEffect } from 'react';
import { 
  Grid, 
  List, 
  ChevronLeft, 
  ChevronRight,
  Search,
  SortAsc,
  SortDesc
} from 'lucide-react';
import StockResultCard from './StockResultCard';

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

interface SearchResultsProps {
  results: SearchResult[];
  loading: boolean;
  query: string;
  totalCount?: number;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onStockClick: (symbol: string) => void;
  onWatchlistToggle: (symbol: string, isWatched: boolean) => void;
}

type ViewMode = 'card' | 'list';
type SortField = 'symbol' | 'current_price' | 'change_percent' | 'ai_score' | 'market_cap';
type SortOrder = 'asc' | 'desc';

export default function SearchResults({
  results,
  loading,
  query,
  totalCount = 0,
  currentPage,
  pageSize,
  onPageChange,
  onStockClick,
  onWatchlistToggle
}: SearchResultsProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('card');
  const [sortField, setSortField] = useState<SortField>('ai_score');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [watchlist, setWatchlist] = useState<Set<string>>(new Set());

  useEffect(() => {
    // ローカルストレージからウォッチリストを読み込み
    const saved = localStorage.getItem('user_watchlist');
    if (saved) {
      setWatchlist(new Set(JSON.parse(saved)));
    }
  }, []);

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc'); // 新しいフィールドはデフォルトで降順
    }
  };

  const handleWatchlistToggle = (symbol: string, isWatched: boolean) => {
    const newWatchlist = new Set(watchlist);
    if (isWatched) {
      newWatchlist.add(symbol);
    } else {
      newWatchlist.delete(symbol);
    }
    
    setWatchlist(newWatchlist);
    localStorage.setItem('user_watchlist', JSON.stringify(Array.from(newWatchlist)));
    onWatchlistToggle(symbol, isWatched);
  };

  const sortedResults = React.useMemo(() => {
    return [...results].sort((a, b) => {
      let aVal: any = a[sortField];
      let bVal: any = b[sortField];

      // undefinedやnullの場合のデフォルト値
      if (aVal === undefined || aVal === null) {
        aVal = sortField === 'current_price' ? 0 : sortField === 'ai_score' ? 0 : '';
      }
      if (bVal === undefined || bVal === null) {
        bVal = sortField === 'current_price' ? 0 : sortField === 'ai_score' ? 0 : '';
      }

      if (typeof aVal === 'string') {
        return sortOrder === 'asc' 
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
      }

      return 0;
    });
  }, [results, sortField, sortOrder]);

  const totalPages = Math.ceil(totalCount / pageSize);
  const startResult = (currentPage - 1) * pageSize + 1;
  const endResult = Math.min(currentPage * pageSize, totalCount);

  const SortButton = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center space-x-1 text-gray-400 hover:text-white transition-colors text-sm"
    >
      <span>{children}</span>
      {sortField === field && (
        sortOrder === 'asc' 
          ? <SortAsc className="w-3 h-3" />
          : <SortDesc className="w-3 h-3" />
      )}
    </button>
  );

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mb-4"></div>
        <p className="text-gray-400">検索中...</p>
      </div>
    );
  }

  if (results.length === 0 && query) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Search className="w-12 h-12 text-gray-600 mb-4" />
        <p className="text-gray-400 text-lg mb-2">検索結果が見つかりませんでした</p>
        <p className="text-gray-500 text-sm">
          「{query}」に一致する銘柄がありませんでした。<br />
          検索条件を変更してお試しください。
        </p>
      </div>
    );
  }

  if (results.length === 0 && !query) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Search className="w-12 h-12 text-gray-600 mb-4" />
        <p className="text-gray-400 text-lg mb-2">銘柄を検索してください</p>
        <p className="text-gray-500 text-sm">
          銘柄名やシンボルを入力するか、<br />
          左側のフィルターで条件を指定してください。
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="text-white">
            <span className="font-semibold">{totalCount.toLocaleString()}</span>
            <span className="text-gray-400 ml-2">件の検索結果</span>
            {query && (
              <span className="text-gray-400 ml-2">
                「<span className="text-blue-400">{query}</span>」
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* ソートメニュー */}
          <div className="flex items-center space-x-3 text-sm">
            <span className="text-gray-400">並び替え:</span>
            <SortButton field="ai_score">AIスコア</SortButton>
            <span className="text-gray-600">|</span>
            <SortButton field="current_price">価格</SortButton>
            <span className="text-gray-600">|</span>
            <SortButton field="change_percent">変動率</SortButton>
          </div>

          {/* 表示モード切り替え */}
          <div className="flex items-center bg-gray-800/50 rounded-lg p-1">
            <button
              onClick={() => setViewMode('card')}
              className={`p-2 rounded-md transition-colors ${
                viewMode === 'card' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:text-white'
              }`}
              title="カード表示"
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-md transition-colors ${
                viewMode === 'list' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:text-white'
              }`}
              title="リスト表示"
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* 検索結果 */}
      <div className={
        viewMode === 'card' 
          ? "grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
          : "space-y-3"
      }>
        {sortedResults.map((stock) => (
          <StockResultCard
            key={stock.symbol}
            stock={stock}
            onStockClick={onStockClick}
            onWatchlistToggle={handleWatchlistToggle}
            isWatched={watchlist.has(stock.symbol)}
            viewMode={viewMode}
          />
        ))}
      </div>

      {/* ページネーション */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-6 border-t border-gray-800/50">
          <div className="text-sm text-gray-400">
            {startResult}-{endResult} / {totalCount.toLocaleString()}件表示
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="flex items-center space-x-1 px-3 py-2 text-sm bg-gray-800/50 hover:bg-gray-700/50 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>前へ</span>
            </button>
            
            <div className="flex items-center space-x-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }
                
                return (
                  <button
                    key={pageNum}
                    onClick={() => onPageChange(pageNum)}
                    className={`px-3 py-2 text-sm rounded-lg transition-colors ${
                      pageNum === currentPage
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-800/50 hover:bg-gray-700/50 text-gray-300'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
            </div>
            
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="flex items-center space-x-1 px-3 py-2 text-sm bg-gray-800/50 hover:bg-gray-700/50 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
            >
              <span>次へ</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}