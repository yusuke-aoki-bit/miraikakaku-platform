'use client';

import { useState, useEffect } from 'react';
import { ArrowUp, ArrowDown, Minus, AlertCircle, TrendingUp, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api-client';

interface MarketData {
  symbol: string;
  company_name?: string;
  name?: string;
  current_price?: number;
  predicted_price?: number;
  growth_potential?: number;
  confidence?: number;
  prediction_count?: number;
  // Legacy format support
  price?: number;
  change?: number;
  changePercent?: number;
  volume?: string;
  high?: number;
  low?: number;
}

export default function MarketOverview() {
  const [selectedTab, setSelectedTab] = useState('trending');
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const tabs = [
    { id: 'trending', label: 'トレンド', icon: <TrendingUp className="w-4 h-4" /> },
    { id: 'gainers', label: '値上がり', icon: <ArrowUp className="w-4 h-4" /> },
    { id: 'losers', label: '値下がり', icon: <ArrowDown className="w-4 h-4" /> },
    { id: 'volume', label: '総合', icon: <AlertCircle className="w-4 h-4" /> },
  ];

  // リアルデータ取得
  const fetchMarketData = async (tabId: string) => {
    setLoading(true);
    setError(null);
    try {
      let response;
      switch (tabId) {
        case 'trending':
          response = await apiClient.getTrendingStocks(10);
          break;
        case 'gainers':
          response = await apiClient.getGainersRankings(10);
          break;
        case 'losers':
          response = await apiClient.getLosersRankings(10);
          break;
        case 'volume':
          response = await apiClient.getCompositeRankings(10);
          break;
        default:
          response = await apiClient.getTrendingStocks(10);
      }

      if (response.status === 'success' && response.data) {
        setMarketData(Array.isArray(response.data) ? response.data : []);
      } else {
        setError(response.error || 'データの取得に失敗しました');
        // フォールバックデータ
        setMarketData([
          { symbol: '7203', name: 'トヨタ自動車', price: 2543.0, change: 45.5, changePercent: 1.82, volume: '12.3M', high: 2555, low: 2498 },
          { symbol: '6758', name: 'ソニーグループ', price: 3251.0, change: -23.0, changePercent: -0.70, volume: '8.5M', high: 3280, low: 3225 },
          { symbol: 'AAPL', name: 'Apple Inc.', price: 175.50, change: 2.30, changePercent: 1.33, volume: '45.2M', high: 177.20, low: 174.10 },
          { symbol: 'TSLA', name: 'Tesla Inc.', price: 243.84, change: -5.67, changePercent: -2.27, volume: '78.5M', high: 248.90, low: 241.20 },
          { symbol: 'NVDA', name: 'NVIDIA Corp.', price: 421.13, change: 12.45, changePercent: 3.05, volume: '92.1M', high: 425.67, low: 416.78 },
        ]);
      }
    } catch (error) {
      console.error('Market data fetch error:', error);
      setError('ネットワークエラーが発生しました');
      // フォールバックデータ
      setMarketData([
        { symbol: '7203', name: 'トヨタ自動車', price: 2543.0, change: 45.5, changePercent: 1.82, volume: '12.3M', high: 2555, low: 2498 },
        { symbol: 'AAPL', name: 'Apple Inc.', price: 175.50, change: 2.30, changePercent: 1.33, volume: '45.2M', high: 177.20, low: 174.10 },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarketData(selectedTab);
  }, [selectedTab]);

  // データの正規化（新旧フォーマット対応）
  const normalizeStockData = (stock: MarketData) => {
    const symbol = stock.symbol;
    const name = stock.company_name || stock.name || symbol;
    const price = stock.current_price || stock.price || 0;
    
    // 成長ポテンシャルから変化量を計算
    let change = 0;
    let changePercent = stock.growth_potential || 0;
    
    if (stock.current_price && stock.predicted_price) {
      change = stock.predicted_price - stock.current_price;
      changePercent = ((stock.predicted_price - stock.current_price) / stock.current_price) * 100;
    } else if (stock.change !== undefined) {
      change = stock.change;
      changePercent = stock.changePercent || 0;
    }

    const volume = stock.volume || `${stock.prediction_count || 0}`;
    const high = stock.high || (price * 1.05);
    const low = stock.low || (price * 0.95);

    return { symbol, name, price, change, changePercent, volume, high, low };
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-gray-800/50 p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">マーケット概況</h2>
        <div className="flex space-x-2">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                selectedTab === tab.id
                  ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 border border-gray-700/50'
              }`}
            >
              {tab.icon}
              <span className="hidden md:inline">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-red-400" />
          <span className="ml-2 text-gray-400">マーケットデータを読み込み中...</span>
        </div>
      ) : error ? (
        <div className="flex justify-center items-center py-12">
          <AlertCircle className="w-6 h-6 text-yellow-400 mr-2" />
          <span className="text-yellow-400">{error}</span>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400 text-sm border-b border-gray-800">
                <th className="pb-3 font-medium">銘柄</th>
                <th className="pb-3 text-right font-medium">現在値</th>
                <th className="pb-3 text-right font-medium">予測変化</th>
                <th className="pb-3 text-right font-medium hidden md:table-cell">信頼度</th>
                <th className="pb-3 text-right font-medium hidden lg:table-cell">高値</th>
                <th className="pb-3 text-right font-medium hidden lg:table-cell">安値</th>
              </tr>
            </thead>
            <tbody>
              {marketData.map((stock, index) => {
                const normalized = normalizeStockData(stock);
                const isUSD = /^[A-Z]{1,5}$/.test(normalized.symbol) && !normalized.symbol.match(/^\d/);
                const currencySymbol = isUSD ? '$' : '¥';
                
                return (
                  <tr 
                    key={normalized.symbol}
                    className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors group"
                  >
                    <td className="py-4">
                      <Link href={`/stock/${normalized.symbol}`} className="block">
                        <div className="text-white font-medium group-hover:text-red-400 transition-colors">
                          {normalized.symbol}
                          {isUSD && <span className="text-xs text-blue-400 ml-1">USD</span>}
                          {!isUSD && normalized.symbol.match(/^\d/) && <span className="text-xs text-green-400 ml-1">JPY</span>}
                        </div>
                        <div className="text-gray-400 text-sm">{normalized.name}</div>
                      </Link>
                    </td>
                    <td className="py-4 text-right">
                      <div className="text-white font-medium">
                        {currencySymbol}{normalized.price.toLocaleString(undefined, {
                          minimumFractionDigits: isUSD ? 2 : 0,
                          maximumFractionDigits: isUSD ? 2 : 0
                        })}
                      </div>
                    </td>
                    <td className="py-4 text-right">
                      <div className={`flex items-center justify-end space-x-1 ${
                        normalized.changePercent > 0 ? 'text-green-400' : normalized.changePercent < 0 ? 'text-red-400' : 'text-gray-400'
                      }`}>
                        {normalized.changePercent > 0 ? <ArrowUp className="w-4 h-4" /> : normalized.changePercent < 0 ? <ArrowDown className="w-4 h-4" /> : <Minus className="w-4 h-4" />}
                        <span className="text-sm font-medium">
                          {normalized.changePercent > 0 ? '+' : ''}{normalized.changePercent.toFixed(2)}%
                        </span>
                      </div>
                    </td>
                    <td className="py-4 text-right hidden md:table-cell">
                      <div className="text-gray-300">
                        {stock.confidence ? `${(stock.confidence * 100).toFixed(0)}%` : normalized.volume}
                      </div>
                    </td>
                    <td className="py-4 text-right hidden lg:table-cell">
                      <div className="text-gray-300">
                        {currencySymbol}{normalized.high.toLocaleString(undefined, {
                          minimumFractionDigits: isUSD ? 2 : 0,
                          maximumFractionDigits: isUSD ? 2 : 0
                        })}
                      </div>
                    </td>
                    <td className="py-4 text-right hidden lg:table-cell">
                      <div className="text-gray-300">
                        {currencySymbol}{normalized.low.toLocaleString(undefined, {
                          minimumFractionDigits: isUSD ? 2 : 0,
                          maximumFractionDigits: isUSD ? 2 : 0
                        })}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-4 flex justify-center">
        <Link 
          href="/rankings"
          className="px-6 py-2 bg-red-500/10 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/20 transition-all duration-200"
        >
          すべて表示
        </Link>
      </div>
    </div>
  );
}