'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';

interface StockRanking {
  symbol: string;
  name: string | null;
  exchange?: string;
  sector?: string;
  price: number;  // API returns 'price' not 'current_price'
  change: number; // API returns 'change' (percent) not 'price_change_percent'
  volume?: number;
  date?: string;
}

interface RealTimeRankingsProps {
  type: 'gainers' | 'losers' | 'actives';
  limit?: number;
  refreshInterval?: number;
  className?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://miraikakaku-api-465603676610.us-central1.run.app';

export default function RealTimeRankings({
  type,
  limit = 10,
  refreshInterval = 30000, // 30 seconds default
  className = ''
}: RealTimeRankingsProps) {
  const [rankings, setRankings] = useState<StockRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isLive, setIsLive] = useState(false);

  // Fetch rankings from API
  const fetchRankings = useCallback(async () => {
    try {
      setIsLive(true);
      const response = await fetch(
        `${API_BASE_URL}/api/home/rankings/${type}?limit=${limit}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setRankings(data);
      setLastUpdate(new Date());
      setError(null);
      setLoading(false);

      // Show live indicator briefly
      setTimeout(() => setIsLive(false), 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch rankings');
      setLoading(false);
      setIsLive(false);
    }
  }, [type, limit]);

  // Initial fetch
  useEffect(() => {
    fetchRankings();
  }, [fetchRankings]);

  // Auto-refresh
  useEffect(() => {
    const interval = setInterval(fetchRankings, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchRankings, refreshInterval]);

  // Get title based on type
  const getTitle = () => {
    switch (type) {
      case 'gainers':
        return 'トップゲイナー';
      case 'losers':
        return 'トップルーザー';
      case 'actives':
        return '出来高上位';
      default:
        return 'ランキング';
    }
  };

  // Format number with commas
  const formatNumber = (num: number) => {
    return num.toLocaleString('ja-JP');
  };

  // Format price change percent
  const formatPriceChange = (percent: number) => {
    const sign = percent >= 0 ? '+' : '';
    return `${sign}${percent.toFixed(2)}%`;
  };

  if (loading && rankings.length === 0) {
    return (
      <div className={`p-6 bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg shadow-sm ${className}`}>
        <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-white">{getTitle()}</h2>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400"></div>
        </div>
      </div>
    );
  }

  if (error && rankings.length === 0) {
    return (
      <div className={`p-6 bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg shadow-sm ${className}`}>
        <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-white">{getTitle()}</h2>
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded p-4">
          <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
          <button
            onClick={fetchRankings}
            className="mt-2 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 underline"
          >
            再試行
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`p-6 bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg shadow-sm ${className}`}>
      {/* Header with live indicator */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-800 dark:text-white">{getTitle()}</h2>
        <div className="flex items-center gap-2">
          {/* Live indicator */}
          <div className="flex items-center gap-1.5">
            <div
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                isLive
                  ? 'bg-green-500 animate-pulse'
                  : 'bg-gray-300'
              }`}
            ></div>
            <span className={`text-xs font-medium ${
              isLive ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'
            }`}>
              {isLive ? 'LIVE' : '待機中'}
            </span>
          </div>
          {/* Last update time */}
          {lastUpdate && (
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {lastUpdate.toLocaleTimeString('ja-JP', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
              })}
            </span>
          )}
        </div>
      </div>

      {/* Rankings table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-400">
              <th className="text-left py-2 px-2 font-medium">#</th>
              <th className="text-left py-2 px-2 font-medium">銘柄</th>
              <th className="text-right py-2 px-2 font-medium">現在値</th>
              <th className="text-right py-2 px-2 font-medium">変動</th>
              {type === 'actives' && (
                <th className="text-right py-2 px-2 font-medium">出来高</th>
              )}
            </tr>
          </thead>
          <tbody>
            {rankings.map((stock, index) => {
              const isPositive = stock.change >= 0;
              const changeColor = isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400';
              const bgColor = isPositive ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20';

              return (
                <tr
                  key={stock.symbol}
                  className={`border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                    isLive ? 'animate-pulse-subtle' : ''
                  }`}
                >
                  <td className="py-3 px-2 text-sm text-gray-600 dark:text-gray-400">
                    {index + 1}
                  </td>
                  <td className="py-3 px-2">
                    <Link
                      href={`/stock/${stock.symbol}`}
                      className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                    >
                      <div className="font-medium text-gray-900 dark:text-white">
                        {stock.symbol}
                      </div>
                      {stock.name && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 truncate max-w-[150px]">
                          {stock.name}
                        </div>
                      )}
                    </Link>
                  </td>
                  <td className="py-3 px-2 text-right">
                    <div className="font-semibold text-gray-900 dark:text-white">
                      ${formatNumber(stock.price)}
                    </div>
                  </td>
                  <td className="py-3 px-2 text-right">
                    <div className={`inline-block px-2 py-1 rounded text-sm font-medium ${bgColor} ${changeColor}`}>
                      {formatPriceChange(stock.change)}
                    </div>
                  </td>
                  {type === 'actives' && stock.volume && (
                    <td className="py-3 px-2 text-right text-sm text-gray-700 dark:text-gray-300">
                      {formatNumber(stock.volume)}
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Refresh button */}
      <div className="mt-4 flex items-center justify-between">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {refreshInterval / 1000}秒ごとに自動更新
        </p>
        <button
          onClick={fetchRankings}
          disabled={isLive}
          className="px-3 py-1.5 text-sm bg-blue-600 dark:bg-blue-500 text-white rounded hover:bg-blue-700 dark:hover:bg-blue-600 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
        >
          {isLive ? '更新中...' : '今すぐ更新'}
        </button>
      </div>
    </div>
  );
}
