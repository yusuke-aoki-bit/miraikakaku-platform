'use client';

import React, { useState, useEffect } from 'react';
import { Star, TrendingUp, TrendingDown, Plus } from 'lucide-react';
import StockSearch from '@/components/StockSearch';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface WatchlistStock {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  last_updated: string;
}

export default function WatchlistPage() {
  const [watchlist, setWatchlist] = useState<WatchlistStock[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddStock, setShowAddStock] = useState(false);

  useEffect(() => {
    loadWatchlist();
  }, []);

  const loadWatchlist = async () => {
    setLoading(true);
    // デフォルトのウォッチリスト
    const defaultStocks = ['AAPL', 'GOOGL', 'TSLA'];
    try {
      const promises = defaultStocks.map(async (symbol) => {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${symbol}/analysis`);
        const data = await response.json();
        return {
          symbol: data.symbol,
          company_name: symbol === 'AAPL' ? 'Apple Inc.' : symbol === 'GOOGL' ? 'Alphabet Inc.' : 'Tesla, Inc.',
          current_price: data.current_price,
          change_percent: data.change_percent,
          last_updated: new Date().toLocaleTimeString()
        };
      });
      const stocks = await Promise.all(promises);
      setWatchlist(stocks);
    } catch (error) {
      console.error('ウォッチリスト取得エラー:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToWatchlist = (symbol: string) => {
    // 実際の実装では銘柄データを取得して追加
    setShowAddStock(false);
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-96">
        <LoadingSpinner type="default" size="lg" message="ウォッチリストを読み込み中..." />
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white flex items-center">
          <Star className="w-6 h-6 mr-2 text-yellow-400" />
          ウォッチリスト
        </h1>
        <button
          onClick={() => setShowAddStock(!showAddStock)}
          className="youtube-button flex items-center space-x-2 px-4 py-2"
        >
          <Plus className="w-4 h-4" />
          <span>銘柄追加</span>
        </button>
      </div>

      {showAddStock && (
        <div className="youtube-card p-6 mb-6">
          <h2 className="text-lg font-semibold text-white mb-4">銘柄を追加</h2>
          <StockSearch onSymbolSelect={addToWatchlist} />
        </div>
      )}

      <div className="space-y-4">
        {watchlist.map((stock) => (
          <div key={stock.symbol} className="youtube-card p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">{stock.symbol.slice(0, 2)}</span>
                </div>
                <div>
                  <h3 className="text-white font-semibold">{stock.symbol}</h3>
                  <p className="text-gray-400 text-sm">{stock.company_name}</p>
                </div>
              </div>
              
              <div className="text-right">
                <p className="text-white font-semibold text-lg">${stock.current_price.toFixed(2)}</p>
                <div className={`flex items-center space-x-1 ${
                  stock.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {stock.change_percent >= 0 ? 
                    <TrendingUp className="w-4 h-4" /> : 
                    <TrendingDown className="w-4 h-4" />
                  }
                  <span className="text-sm font-semibold">{stock.change_percent.toFixed(2)}%</span>
                </div>
                <p className="text-gray-500 text-xs">更新: {stock.last_updated}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}