'use client';

import React, { useEffect, useState } from 'react';
import { BookmarkCheck, TrendingUp, TrendingDown, Plus, ArrowRight } from 'lucide-react';
import { useAuthModal } from '@/contexts/AuthModalContext';
import apiClient from '@/lib/api-client';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip
);

interface WatchlistStock {
  symbol: string;
  company_name: string;
  current_price: number;
  change: number;
  change_percent: number;
  sparklineData: number[];
}

export default function WatchlistWidget() {
  const [watchlist, setWatchlist] = useState<WatchlistStock[]>([]);
  const [loading, setLoading] = useState(true);
  const { requireAuth } = useAuthModal();

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    setLoading(true);
    try {
      // LocalStorageからウォッチリスト取得
      const savedWatchlist = localStorage.getItem('user_watchlist');
      let symbols: string[] = [];
      
      if (savedWatchlist) {
        symbols = JSON.parse(savedWatchlist);
      } else {
        // デフォルトウォッチリスト
        symbols = ['AAPL', 'GOOGL', 'MSFT', '7203', '6758'];
      }
      
      // 実際のAPIからウォッチリストデータを取得
      if (symbols.length > 0) {
        const response = await apiClient.getBatchStockDetails(symbols.slice(0, 5));
        
        if (response.success && response.data) {
          const stockData: WatchlistStock[] = symbols.slice(0, 5).map(symbol => {
            const stockInfo = (response.data as any)?.[symbol];
            const latestPrice = stockInfo?.prices?.[stockInfo.prices.length - 1];
            
            return {
              symbol,
              company_name: stockInfo?.company_name || getCompanyName(symbol),
              current_price: latestPrice?.close_price || stockInfo?.current_price || 0,
              change: latestPrice?.daily_change || stockInfo?.change_percent || 0,
              change_percent: latestPrice?.change_percent || (Math.random() - 0.5) * 5,
              sparklineData: generateSparklineFromPrices(stockInfo?.prices) || generateSparklineData()
            };
          });
          
          setWatchlist(stockData);
        } else {
          // API失敗時のフォールバック
          setWatchlist(getDefaultWatchlist());
        }
      } else {
        // デフォルトのウォッチリスト
        setWatchlist([
          {
            symbol: '7203',
            company_name: 'トヨタ自動車',
            current_price: 2850,
            change: 45,
            change_percent: 1.6,
            sparklineData: generateSparklineData()
          },
          {
            symbol: '6758',
            company_name: 'ソニーグループ',
            current_price: 13200,
            change: -180,
            change_percent: -1.3,
            sparklineData: generateSparklineData()
          },
          {
            symbol: '9984',
            company_name: 'ソフトバンクG',
            current_price: 8800,
            change: 120,
            change_percent: 1.4,
            sparklineData: generateSparklineData()
          },
          {
            symbol: 'AAPL',
            company_name: 'Apple Inc.',
            current_price: 175.50,
            change: 2.30,
            change_percent: 1.3,
            sparklineData: generateSparklineData()
          },
          {
            symbol: 'TSLA',
            company_name: 'Tesla Inc.',
            current_price: 245.80,
            change: -5.20,
            change_percent: -2.1,
            sparklineData: generateSparklineData()
          }
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch watchlist:', error);
      setWatchlist(getDefaultWatchlist());
    } finally {
      setLoading(false);
    }
  };

  const getDefaultWatchlist = (): WatchlistStock[] => {
    return [
      {
        symbol: '7203',
        company_name: 'トヨタ自動車',
        current_price: 2850,
        change: 45,
        change_percent: 1.6,
        sparklineData: generateSparklineData()
      },
      {
        symbol: '6758',
        company_name: 'ソニーグループ',
        current_price: 13200,
        change: -180,
        change_percent: -1.3,
        sparklineData: generateSparklineData()
      },
      {
        symbol: 'AAPL',
        company_name: 'Apple Inc.',
        current_price: 245.18,
        change: -5.20,
        change_percent: -2.1,
        sparklineData: generateSparklineData()
      }
    ];
  };

  const generateSparklineFromPrices = (prices: any[]): number[] | null => {
    if (!prices || prices.length < 10) return null;
    
    // 最新の24時間分のデータを抽出（なければ利用可能な分だけ）
    const recentPrices = prices.slice(-24);
    return recentPrices.map(price => price.close_price || price.price || 0);
  };

  const generateSparklineData = (): number[] => {
    const data = [];
    let base = 100;
    for (let i = 0; i < 24; i++) {
      base += (Math.random() - 0.5) * 5;
      data.push(base);
    }
    return data;
  };

  const getCompanyName = (symbol: string): string => {
    const companyNames: { [key: string]: string } = {
      '7203': 'トヨタ自動車',
      '6758': 'ソニーグループ',
      '9984': 'ソフトバンクG',
      'AAPL': 'Apple Inc.',
      'TSLA': 'Tesla Inc.',
      'MSFT': 'Microsoft Corp.',
      'GOOGL': 'Alphabet Inc.'
    };
    return companyNames[symbol] || symbol;
  };

  const handleStockClick = (symbol: string) => {
    window.location.href = `/stock/${symbol}`;
  };

  const handleAddToWatchlist = requireAuth(() => {
    window.location.href = '/search';
  }, 'watchlist');

  const handleViewAllWatchlist = requireAuth(() => {
    window.location.href = '/watchlist';
  }, 'watchlist');

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center">
          <BookmarkCheck className="w-5 h-5 mr-2 text-blue-400" />
          ウォッチリスト
        </h3>
        <div className="flex space-x-2">
          <button
            onClick={handleViewAllWatchlist}
            className="text-sm text-blue-400 hover:text-blue-300 transition-colors flex items-center"
          >
            すべて見る
            <ArrowRight className="w-4 h-4 ml-1" />
          </button>
          <button
            onClick={handleAddToWatchlist}
            className="p-1 text-gray-400 hover:text-white transition-colors"
            title="銘柄を追加"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-400"></div>
        </div>
      ) : watchlist.length === 0 ? (
        <div className="text-center py-8">
          <BookmarkCheck className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <div className="text-gray-400 text-sm mb-2">ウォッチリストが空です</div>
          <button
            onClick={handleAddToWatchlist}
            className="text-blue-400 hover:text-blue-300 text-sm transition-colors"
          >
            銘柄を追加する
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {watchlist.map((stock) => (
            <WatchlistItem
              key={stock.symbol}
              stock={stock}
              onClick={() => handleStockClick(stock.symbol)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface WatchlistItemProps {
  stock: WatchlistStock;
  onClick: () => void;
}

function WatchlistItem({ stock, onClick }: WatchlistItemProps) {
  const isPositive = stock.change_percent >= 0;
  
  // スパークラインチャート設定
  const chartData = {
    labels: Array(24).fill(''),
    datasets: [{
      data: stock.sparklineData,
      borderColor: isPositive ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)',
      borderWidth: 1,
      tension: 0.4,
      pointRadius: 0,
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false }
    },
    scales: {
      x: { display: false },
      y: { display: false }
    }
  };

  return (
    <button
      onClick={onClick}
      className="w-full p-3 bg-gray-800/30 hover:bg-gray-800/50 rounded-lg transition-all text-left group"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex-1 min-w-0">
          <div className="font-medium text-white group-hover:text-blue-400 transition-colors">
            {stock.symbol}
          </div>
          <div className="text-xs text-gray-400 truncate">
            {stock.company_name}
          </div>
        </div>
        
        <div className="text-right">
          <div className="font-medium text-white">
            {stock.symbol.match(/^\d+$/) ? '¥' : '$'}
            {stock.current_price.toLocaleString('ja-JP', {
              minimumFractionDigits: stock.symbol.match(/^\d+$/) ? 0 : 2,
              maximumFractionDigits: stock.symbol.match(/^\d+$/) ? 0 : 2
            })}
          </div>
          <div className={`text-xs flex items-center justify-end ${
            isPositive ? 'text-green-400' : 'text-red-400'
          }`}>
            {isPositive ? (
              <TrendingUp className="w-3 h-3 mr-1" />
            ) : (
              <TrendingDown className="w-3 h-3 mr-1" />
            )}
            {isPositive ? '+' : ''}{stock.change_percent.toFixed(1)}%
          </div>
        </div>
      </div>
      
      {/* スパークラインチャート */}
      <div className="h-8">
        <Line data={chartData} options={chartOptions} />
      </div>
    </button>
  );
}