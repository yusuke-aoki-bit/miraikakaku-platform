'use client';

import React, { useState, useEffect } from 'react';
import { Star, RefreshCw } from 'lucide-react';
import { useRouter } from 'next/navigation';
import WatchlistToolbar, { ViewMode, SortOption, SortOrder } from '@/components/watchlist/WatchlistToolbar';
import WatchlistGridView from '@/components/watchlist/WatchlistGridView';
import WatchlistListView from '@/components/watchlist/WatchlistListView';
import WatchlistHeatmapView from '@/components/watchlist/WatchlistHeatmapView';
import { apiClient } from '@/lib/api-client';

interface WatchlistStock {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  market?: string;
  sector?: string;
  market_cap?: number;
  volume?: number;
  per?: number;
  pbr?: number;
  dividend_yield?: number;
  ai_score?: number;
  chart_data?: {
    historical?: number[];
    past_prediction?: number[];
    future_prediction?: number[];
  };
  last_updated?: string;
}

export default function WatchlistPage() {
  const router = useRouter();
  const [watchlist, setWatchlist] = useState<WatchlistStock[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  // UI状態
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [editMode, setEditMode] = useState(false);
  const [selectedStocks, setSelectedStocks] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<SortOption>('symbol');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');

  useEffect(() => {
    loadWatchlist();
  }, []);

  const loadWatchlist = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      
      // localStorageからウォッチリスト取得
      const watchlistResponse = await apiClient.getWatchlist();
      if (watchlistResponse.status !== 'success' || !watchlistResponse.data || watchlistResponse.data.length === 0) {
        // デフォルトのウォッチリスト設定
        const defaultStocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', '7203'];
        localStorage.setItem('watchlist', JSON.stringify(defaultStocks));
        await loadStockData(defaultStocks);
        return;
      }

      await loadStockData(watchlistResponse.data);
    } catch (error) {
      console.error('ウォッチリスト読み込みエラー:', error);
      setWatchlist([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const loadStockData = async (symbols: string[]) => {
    if (symbols.length === 0) {
      setWatchlist([]);
      return;
    }

    try {
      // バッチで株式データを取得
      const batchResponse = await apiClient.getBatchStockDetails(symbols);
      if (batchResponse.status === 'success') {
        const stocksData: WatchlistStock[] = symbols.map(symbol => {
          const data = batchResponse.data[symbol];
          if (data) {
            return {
              symbol: data.symbol,
              company_name: data.company_name,
              current_price: data.current_price || Math.random() * 200 + 50,
              change_percent: data.change_percent || (Math.random() - 0.5) * 10,
              market: data.market || (symbol.match(/^\d/) ? 'TSE' : 'NASDAQ'),
              sector: data.sector || 'Technology',
              market_cap: data.market_cap,
              volume: data.volume,
              per: data.per,
              pbr: data.pbr,
              dividend_yield: data.dividend_yield,
              ai_score: data.ai_score,
              chart_data: {
                historical: data.prices?.slice(-30).map((p: any) => p.close_price) || generateMockChart(30),
                past_prediction: data.predictions?.slice(-15).map((p: any) => p.predicted_price) || generateMockChart(15),
                future_prediction: data.predictions?.slice(0, 15).map((p: any) => p.predicted_price) || generateMockChart(15)
              },
              last_updated: new Date().toLocaleTimeString()
            };
          }
          // フォールバックデータ
          return {
            symbol,
            company_name: `${symbol} Corporation`,
            current_price: Math.random() * 200 + 50,
            change_percent: (Math.random() - 0.5) * 10,
            market: symbol.match(/^\d/) ? 'TSE' : 'NASDAQ',
            sector: 'Technology',
            market_cap: Math.random() * 1000000000000,
            ai_score: Math.floor(Math.random() * 40) + 60,
            chart_data: {
              historical: generateMockChart(30),
              past_prediction: generateMockChart(15),
              future_prediction: generateMockChart(15)
            },
            last_updated: new Date().toLocaleTimeString()
          };
        });

        setWatchlist(stocksData);
      }
    } catch (error) {
      console.error('株式データ取得エラー:', error);
    }
  };

  const generateMockChart = (length: number): number[] => {
    const data = [];
    let current = 100;
    for (let i = 0; i < length; i++) {
      current += (Math.random() - 0.5) * 5;
      data.push(Math.max(current, 10));
    }
    return data;
  };

  const handleAddStock = async (symbol: string) => {
    try {
      await apiClient.addToWatchlist(symbol.toUpperCase());
      await loadWatchlist(false);
    } catch (error) {
      console.error('銘柄追加エラー:', error);
    }
  };

  const handleRemoveStock = async (symbol: string) => {
    try {
      await apiClient.removeFromWatchlist(symbol);
      setWatchlist(prev => prev.filter(stock => stock.symbol !== symbol));
      setSelectedStocks(prev => prev.filter(s => s !== symbol));
    } catch (error) {
      console.error('銘柄削除エラー:', error);
    }
  };

  const handleStockSelect = (symbol: string) => {
    setSelectedStocks(prev => {
      if (prev.includes(symbol)) {
        return prev.filter(s => s !== symbol);
      } else {
        return [...prev, symbol];
      }
    });
  };

  const handleDeleteSelected = async () => {
    try {
      for (const symbol of selectedStocks) {
        await apiClient.removeFromWatchlist(symbol);
      }
      setWatchlist(prev => prev.filter(stock => !selectedStocks.includes(stock.symbol)));
      setSelectedStocks([]);
    } catch (error) {
      console.error('選択銘柄削除エラー:', error);
    }
  };

  const handleSelectAll = () => {
    setSelectedStocks(watchlist.map(stock => stock.symbol));
  };

  const handleClearSelection = () => {
    setSelectedStocks([]);
  };

  const handleReorderStocks = async (newOrder: WatchlistStock[]) => {
    setWatchlist(newOrder);
    const symbols = newOrder.map(stock => stock.symbol);
    try {
      await apiClient.updateWatchlistOrder(symbols);
    } catch (error) {
      console.error('順序更新エラー:', error);
    }
  };

  const handleStockClick = (symbol: string) => {
    router.push(`/stock/${symbol}`);
  };

  const handleSortChange = (newSortBy: SortOption, newSortOrder: SortOrder) => {
    setSortBy(newSortBy);
    setSortOrder(newSortOrder);
    
    const sortedWatchlist = [...watchlist].sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (newSortBy) {
        case 'symbol':
          aValue = a.symbol;
          bValue = b.symbol;
          break;
        case 'price':
          aValue = a.current_price;
          bValue = b.current_price;
          break;
        case 'change':
          aValue = a.change_percent;
          bValue = b.change_percent;
          break;
        case 'volume':
          aValue = a.volume || 0;
          bValue = b.volume || 0;
          break;
        case 'marketCap':
          aValue = a.market_cap || 0;
          bValue = b.market_cap || 0;
          break;
        case 'aiScore':
          aValue = a.ai_score || 0;
          bValue = b.ai_score || 0;
          break;
        default:
          return 0;
      }

      if (typeof aValue === 'string') {
        return newSortOrder === 'asc' 
          ? aValue.localeCompare(bValue) 
          : bValue.localeCompare(aValue);
      } else {
        return newSortOrder === 'asc' ? aValue - bValue : bValue - aValue;
      }
    });

    setWatchlist(sortedWatchlist);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadWatchlist(false);
  };

  const handleEditModeToggle = () => {
    setEditMode(!editMode);
    if (editMode) {
      setSelectedStocks([]);
    }
  };

  const renderMainView = () => {
    const commonProps = {
      stocks: watchlist,
      editMode,
      selectedStocks,
      onStockSelect: handleStockSelect,
      onStockClick: handleStockClick,
      onRemoveStock: handleRemoveStock,
      onReorderStocks: handleReorderStocks,
      loading
    };

    switch (viewMode) {
      case 'list':
        return (
          <WatchlistListView
            {...commonProps}
            sortBy={sortBy}
            sortOrder={sortOrder}
            onSortChange={handleSortChange}
          />
        );
      case 'heatmap':
        return (
          <WatchlistHeatmapView
            stocks={watchlist}
            onStockClick={handleStockClick}
            loading={loading}
          />
        );
      case 'grid':
      default:
        return <WatchlistGridView {...commonProps} />;
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* ページヘッダー */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white flex items-center">
          <Star className="w-6 h-6 mr-2 text-yellow-400" />
          ウォッチリスト
        </h1>
        
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center space-x-2 px-3 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-gray-300 hover:text-white hover:bg-gray-700/50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span className="text-sm">更新</span>
        </button>
      </div>

      {/* ツールバー */}
      <WatchlistToolbar
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        editMode={editMode}
        onEditModeToggle={handleEditModeToggle}
        onAddStock={handleAddStock}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={handleSortChange}
        watchlistCount={watchlist.length}
        selectedCount={selectedStocks.length}
        onDeleteSelected={handleDeleteSelected}
        onSelectAll={handleSelectAll}
        onClearSelection={handleClearSelection}
      />

      {/* メインビュー */}
      {renderMainView()}
    </div>
  );
}