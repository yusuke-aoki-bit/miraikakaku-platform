'use client';

import { useStockWebSocket } from '@/hooks/useStockWebSocket';
import { useEffect, useState } from 'react';
import { safeToFixed } from '@/lib/formatters';

interface RealTimeStockPriceProps {
  symbol: string;
  showDetails?: boolean;
  className?: string;
}

export default function RealTimeStockPrice({
  symbol,
  showDetails = true,
  className = ''
}: RealTimeStockPriceProps) {
  const { data, connected, error, getLatest } = useStockWebSocket(symbol);
  const [priceChange, setPriceChange] = useState<number | null>(null);
  const [priceChangePercent, setPriceChangePercent] = useState<number | null>(null);

  // Calculate price change when data updates
  useEffect(() => {
    if (data) {
      const change = data.close_price - data.open_price;
      const changePercent = (change / data.open_price) * 100;
      setPriceChange(change);
      setPriceChangePercent(changePercent);
    }
  }, [data]);

  // Refresh price every 30 seconds
  useEffect(() => {
    if (connected) {
      const interval = setInterval(() => {
        getLatest();
      }, 30000);

      return () => clearInterval(interval);
    }
  }, [connected, getLatest]);

  if (error) {
    return (
      <div className={`p-4 bg-red-50 border border-red-200 rounded-lg ${className}`}>
        <p className="text-red-600 text-sm">Error: {error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className={`p-4 bg-gray-50 border border-gray-200 rounded-lg ${className}`}>
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <p className="text-gray-600 text-sm">Loading {symbol}...</p>
        </div>
      </div>
    );
  }

  const isPositive = (priceChange ?? 0) >= 0;

  return (
    <div className={`p-4 bg-white border rounded-lg shadow-sm ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <h3 className="text-lg font-semibold text-gray-900">{data.symbol}</h3>
          {connected && (
            <span className="flex items-center">
              <span className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="ml-1 text-xs text-gray-500">Live</span>
            </span>
          )}
        </div>
        <span className="text-xs text-gray-500">{data.date}</span>
      </div>

      {/* Current Price */}
      <div className="mb-3">
        <div className="text-3xl font-bold text-gray-900">
          ${safeToFixed(data.close_price, 2, '0.00')}
        </div>
        {priceChange !== null && priceChangePercent !== null && (
          <div className={`flex items-center space-x-2 mt-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            <span className="font-medium">
              {isPositive ? '+' : ''}{safeToFixed(priceChange, 2, '0.00')}
            </span>
            <span className="font-medium">
              ({isPositive ? '+' : ''}{safeToFixed(priceChangePercent, 2, '0.00')}%)
            </span>
          </div>
        )}
      </div>

      {/* Details */}
      {showDetails && (
        <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-200">
          <div>
            <p className="text-xs text-gray-500">Open</p>
            <p className="text-sm font-medium text-gray-900">
              ${safeToFixed(data.open_price, 2, '0.00')}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">High</p>
            <p className="text-sm font-medium text-gray-900">
              ${safeToFixed(data.high_price, 2, '0.00')}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Low</p>
            <p className="text-sm font-medium text-gray-900">
              ${safeToFixed(data.low_price, 2, '0.00')}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Volume</p>
            <p className="text-sm font-medium text-gray-900">
              {data.volume.toLocaleString()}
            </p>
          </div>
        </div>
      )}

      {/* Data Source */}
      <div className="mt-3 pt-3 border-t border-gray-200">
        <p className="text-xs text-gray-400">
          Source: {data.data_source} • Updates every 30s
        </p>
      </div>
    </div>
  );
}
