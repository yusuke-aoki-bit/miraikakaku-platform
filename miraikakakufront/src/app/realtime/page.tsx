'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Activity, AlertCircle, TrendingUp, TrendingDown, Zap, Clock, RefreshCw, Pause, Play, Volume2, VolumeX } from 'lucide-react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import AdSenseUnit from '@/components/monetization/AdSenseUnit';
import AmazonProductCard from '@/components/monetization/AmazonProductCard';
import { apiClient } from '@/lib/api-client';
import amazonRecommendations from '@/data/amazon-recommendations.json';

interface RealtimeStock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  marketCap?: number;
  lastUpdate: string;
  sector?: string;
}

interface MarketStatus {
  isOpen: boolean;
  nextOpen: string;
  nextClose: string;
  timezone: string;
}

interface Alert {
  id: string;
  symbol: string;
  type: 'price' | 'volume' | 'change';
  message: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high';
}

export default function RealtimePage() {
  const [stocks, setStocks] = useState<RealtimeStock[]>([]);
  const [marketStatus, setMarketStatus] = useState<MarketStatus>({
    isOpen: false,
    nextOpen: '',
    nextClose: '',
    timezone: 'JST'
  });
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'change' | 'volume' | 'price' | 'name'>('change');
  const [isAutoUpdate, setIsAutoUpdate] = useState(true);
  const [isSoundEnabled, setIsSoundEnabled] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [loading, setLoading] = useState(true);
  const tickerRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const categories = [
    { id: 'all', label: 'すべて' },
    { id: 'nikkei225', label: '日経225' },
    { id: 'topix', label: 'TOPIX' },
    { id: 'growth', label: 'グロース' },
    { id: 'value', label: 'バリュー' },
    { id: 'us', label: '米国株' }
  ];

  // Fetch realtime data
  const fetchRealtimeData = async () => {
    try {
      const [stocksResponse, statusResponse, alertsResponse] = await Promise.all([
        apiClient.getRealtimeStocks({
          category: selectedCategory === 'all' ? undefined : selectedCategory,
          limit: 50
        }),
        apiClient.getMarketStatus(),
        apiClient.getRealtimeAlerts({ limit: 10 })
      ]);

      if (stocksResponse.success && stocksResponse.data) {
        setStocks(stocksResponse.data);
      }

      if (statusResponse.success && statusResponse.data) {
        setMarketStatus(statusResponse.data);
      }

      if (alertsResponse.success && alertsResponse.data) {
        setAlerts(alertsResponse.data);
      }

      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching realtime data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Auto update effect
  useEffect(() => {
    fetchRealtimeData();

    if (isAutoUpdate) {
      intervalRef.current = setInterval(fetchRealtimeData, 3000); // Update every 3 seconds
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [selectedCategory, isAutoUpdate]);

  // Sort stocks
  const sortedStocks = [...stocks].sort((a, b) => {
    switch (sortBy) {
      case 'change':
        return b.changePercent - a.changePercent;
      case 'volume':
        return b.volume - a.volume;
      case 'price':
        return b.price - a.price;
      case 'name':
        return a.name.localeCompare(b.name);
      default:
        return 0;
    }
  });

  const toggleAutoUpdate = () => {
    setIsAutoUpdate(!isAutoUpdate);
    if (!isAutoUpdate && intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ja-JP', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  const formatCurrency = (value: number, currency = '¥') => {
    return `${currency}${value.toLocaleString()}`;
  };

  const getAlertSeverityColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'high': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded w-64 mb-8"></div>
            <div className="h-16 bg-gray-800 rounded-xl mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-32 bg-gray-800 rounded-xl"></div>
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 h-96 bg-gray-800 rounded-xl"></div>
              <div className="h-96 bg-gray-800 rounded-xl"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Ticker Tape */}
      <div className="bg-gray-900 border-b border-gray-800 py-3 overflow-hidden">
        <div 
          ref={tickerRef}
          className="flex animate-scroll whitespace-nowrap"
          style={{
            animation: 'scroll-left 60s linear infinite'
          }}
        >
          {[...sortedStocks, ...sortedStocks].map((stock, index) => (
            <div key={`${stock.symbol}-${index}`} className="flex items-center mx-8">
              <span className="text-white font-semibold mr-2">{stock.symbol}</span>
              <span className="text-white mr-2">{formatCurrency(stock.price)}</span>
              <span className={`flex items-center ${
                stock.changePercent >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {stock.changePercent >= 0 ? '▲' : '▼'}
                {Math.abs(stock.changePercent).toFixed(2)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between mb-8"
          >
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center mb-2">
                <Activity className="w-8 h-8 mr-3 text-green-400 animate-pulse" />
                リアルタイム市場監視
              </h1>
              <p className="text-gray-400">
                市場の動きを即座にキャッチし、投資機会を逃しません
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Market Status */}
              <div className={`flex items-center px-4 py-2 rounded-lg ${
                marketStatus.isOpen 
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                  : 'bg-red-500/20 text-red-400 border border-red-500/30'
              }`}>
                <div className={`w-2 h-2 rounded-full mr-2 ${
                  marketStatus.isOpen ? 'bg-green-400 animate-pulse' : 'bg-red-400'
                }`}></div>
                <span className="text-sm font-medium">
                  {marketStatus.isOpen ? '取引中' : '取引終了'}
                </span>
              </div>

              {/* Controls */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={toggleAutoUpdate}
                  className={`p-2 rounded-lg transition-colors ${
                    isAutoUpdate 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-800 text-gray-400 hover:text-white'
                  }`}
                  title={isAutoUpdate ? '自動更新を停止' : '自動更新を開始'}
                >
                  {isAutoUpdate ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                </button>

                <button
                  onClick={() => setIsSoundEnabled(!isSoundEnabled)}
                  className={`p-2 rounded-lg transition-colors ${
                    isSoundEnabled 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-800 text-gray-400 hover:text-white'
                  }`}
                  title={isSoundEnabled ? '音を無効化' : '音を有効化'}
                >
                  {isSoundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
                </button>

                <button
                  onClick={() => fetchRealtimeData()}
                  className="p-2 bg-gray-800 text-gray-400 hover:text-white rounded-lg transition-colors"
                  title="手動更新"
                >
                  <RefreshCw className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>

          {/* Summary Cards */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
          >
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center mb-4">
                <AlertCircle className="w-6 h-6 text-orange-400 mr-3" />
                <h3 className="text-lg font-semibold text-gray-300">アクティブアラート</h3>
              </div>
              <div className="text-3xl font-bold text-orange-400 mb-2">
                {alerts.length}
              </div>
              <p className="text-gray-400 text-sm">件の通知</p>
            </div>

            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center mb-4">
                <TrendingUp className="w-6 h-6 text-green-400 mr-3" />
                <h3 className="text-lg font-semibold text-gray-300">上昇銘柄</h3>
              </div>
              <div className="text-3xl font-bold text-green-400 mb-2">
                {stocks.filter(s => s.changePercent > 0).length}
              </div>
              <p className="text-gray-400 text-sm">本日プラス</p>
            </div>

            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center mb-4">
                <TrendingDown className="w-6 h-6 text-red-400 mr-3" />
                <h3 className="text-lg font-semibold text-gray-300">下落銘柄</h3>
              </div>
              <div className="text-3xl font-bold text-red-400 mb-2">
                {stocks.filter(s => s.changePercent < 0).length}
              </div>
              <p className="text-gray-400 text-sm">本日マイナス</p>
            </div>

            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center mb-4">
                <Clock className="w-6 h-6 text-blue-400 mr-3" />
                <h3 className="text-lg font-semibold text-gray-300">最終更新</h3>
              </div>
              <div className="text-xl font-bold text-white mb-2">
                {formatTime(lastUpdate)}
              </div>
              <p className="text-gray-400 text-sm">
                {isAutoUpdate ? '3秒毎' : '手動更新'}
              </p>
            </div>
          </motion.div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content Area (2/3) */}
            <div className="lg:col-span-2 space-y-6">
              {/* Filters */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-gray-900/50 border border-gray-800 rounded-xl p-6"
              >
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-400 mb-2">カテゴリ</label>
                    <div className="flex flex-wrap gap-2">
                      {categories.map((category) => (
                        <button
                          key={category.id}
                          onClick={() => setSelectedCategory(category.id)}
                          className={`px-4 py-2 rounded-lg transition-colors ${
                            selectedCategory === category.id
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                          }`}
                        >
                          {category.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">並び順</label>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value as any)}
                      className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="change">変動率順</option>
                      <option value="volume">出来高順</option>
                      <option value="price">価格順</option>
                      <option value="name">銘柄名順</option>
                    </select>
                  </div>
                </div>
              </motion.div>

              {/* Stocks Table */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden"
              >
                <div className="p-6 border-b border-gray-800">
                  <h2 className="text-xl font-bold text-white flex items-center">
                    <Zap className="w-6 h-6 mr-2 text-yellow-400" />
                    リアルタイム株価
                  </h2>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-800/50">
                      <tr>
                        <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">銘柄</th>
                        <th className="px-6 py-4 text-right text-sm font-medium text-gray-400">現在値</th>
                        <th className="px-6 py-4 text-right text-sm font-medium text-gray-400">変動</th>
                        <th className="px-6 py-4 text-right text-sm font-medium text-gray-400">変動率</th>
                        <th className="px-6 py-4 text-right text-sm font-medium text-gray-400">出来高</th>
                        <th className="px-6 py-4 text-center text-sm font-medium text-gray-400">更新</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                      {sortedStocks.map((stock, index) => (
                        <motion.tr
                          key={stock.symbol}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.4 + index * 0.02 }}
                          className="hover:bg-gray-800/30 transition-colors"
                        >
                          <td className="px-6 py-4">
                            <Link 
                              href={`/stock/${stock.symbol}`}
                              className="block hover:text-blue-400 transition-colors"
                            >
                              <div>
                                <div className="font-medium text-white">{stock.symbol}</div>
                                <div className="text-sm text-gray-400">{stock.name}</div>
                              </div>
                            </Link>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <span className="text-white font-semibold">
                              {formatCurrency(stock.price)}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <span className={`font-semibold ${
                              stock.change >= 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                              {stock.change >= 0 ? '+' : ''}{formatCurrency(stock.change)}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <span className={`flex items-center justify-end font-semibold ${
                              stock.changePercent >= 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                              {stock.changePercent >= 0 ? 
                                <TrendingUp className="w-4 h-4 mr-1" /> : 
                                <TrendingDown className="w-4 h-4 mr-1" />
                              }
                              {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                            </span>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <span className="text-gray-300">
                              {(stock.volume / 1000).toFixed(0)}K
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className="text-xs text-gray-500">
                              {new Date(stock.lastUpdate).toLocaleTimeString('ja-JP', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </span>
                          </td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            </div>

            {/* Sidebar (1/3) */}
            <div className="space-y-6">
              {/* AdSense Unit */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <AdSenseUnit
                  adSlot="1234567892"
                  className="w-full"
                  style={{ minHeight: '600px' }}
                />
              </motion.div>

              {/* Alerts */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="bg-gray-900/50 border border-gray-800 rounded-xl p-6"
              >
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2 text-orange-400" />
                  最新アラート
                </h3>
                
                {alerts.length > 0 ? (
                  <div className="space-y-3">
                    {alerts.slice(0, 5).map((alert) => (
                      <div 
                        key={alert.id}
                        className={`p-3 rounded-lg border ${getAlertSeverityColor(alert.severity)}`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">{alert.symbol}</span>
                          <span className="text-xs">
                            {new Date(alert.timestamp).toLocaleTimeString('ja-JP', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                        <p className="text-sm">{alert.message}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400 text-center py-8">
                    現在アラートはありません
                  </p>
                )}
              </motion.div>

              {/* Amazon Product Recommendations */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <div className="bg-gray-50 rounded-lg p-6">
                  <div className="flex items-center mb-4">
                    <Activity className="w-6 h-6 text-blue-600 mr-2" />
                    <h3 className="text-xl font-semibold text-gray-800">
                      {amazonRecommendations.realtime.title}
                    </h3>
                  </div>
                  <p className="text-gray-600 mb-4">{amazonRecommendations.realtime.description}</p>
                  <div className="grid grid-cols-1 gap-4">
                    {amazonRecommendations.realtime.products.slice(0, 2).map((product) => (
                      <AmazonProductCard
                        key={product.id}
                        product={product}
                        compact={true}
                      />
                    ))}
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes scroll-left {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-100%); }
        }
      `}</style>
    </div>
  );
}