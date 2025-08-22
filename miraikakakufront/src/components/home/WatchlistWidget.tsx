'use client';

import { useState, useEffect } from 'react';
import { Star, TrendingUp, TrendingDown, Eye } from 'lucide-react';
import Link from 'next/link';

interface WatchlistItem {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

export default function WatchlistWidget() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([
    { symbol: '7203', name: 'トヨタ自動車', price: 2543.0, change: 45.5, changePercent: 1.82 },
    { symbol: '6758', name: 'ソニーグループ', price: 3251.0, change: -23.0, changePercent: -0.70 },
    { symbol: '9984', name: 'ソフトバンクG', price: 6834.0, change: 156.0, changePercent: 2.34 },
  ]);

  const [isLoading, setIsLoading] = useState(false);

  // Load watchlist from localStorage
  useEffect(() => {
    const savedWatchlist = localStorage.getItem('watchlist');
    if (savedWatchlist) {
      try {
        const parsed = JSON.parse(savedWatchlist);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setWatchlist(parsed.slice(0, 5)); // Show only top 5
        }
      } catch (e) {
        console.error('Failed to load watchlist');
      }
    }
  }, []);

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-gray-800/50 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Star className="w-5 h-5 text-yellow-400" />
          <h3 className="text-xl font-bold text-white">ウォッチリスト</h3>
        </div>
        <Link 
          href="/watchlist"
          className="text-sm text-red-400 hover:text-red-300 transition-colors flex items-center space-x-1"
        >
          <span>すべて見る</span>
          <Eye className="w-4 h-4" />
        </Link>
      </div>

      {watchlist.length === 0 ? (
        <div className="text-center py-8">
          <Star className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400 mb-3">ウォッチリストは空です</p>
          <Link 
            href="/rankings"
            className="text-red-400 hover:text-red-300 text-sm"
          >
            銘柄を追加 →
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {watchlist.map((item) => (
            <Link 
              key={item.symbol}
              href={`/realtime?symbol=${item.symbol}`}
              className="flex items-center justify-between p-3 bg-black/30 rounded-lg hover:bg-black/50 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-white font-medium">{item.symbol}</span>
                  <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                </div>
                <div className="text-gray-400 text-sm truncate">{item.name}</div>
              </div>
              <div className="text-right">
                <div className="text-white font-medium">
                  ¥{item.price.toLocaleString()}
                </div>
                <div className={`flex items-center justify-end space-x-1 text-sm ${
                  item.change > 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {item.change > 0 ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                  <span>{item.changePercent > 0 ? '+' : ''}{item.changePercent}%</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {watchlist.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-800/50">
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">登録銘柄数</span>
            <span className="text-white font-medium">{watchlist.length} 銘柄</span>
          </div>
        </div>
      )}
    </div>
  );
}