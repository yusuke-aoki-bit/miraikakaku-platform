'use client';

import React, { useState, useEffect } from 'react';
import { Activity, AlertCircle, TrendingUp, TrendingDown } from 'lucide-react';

interface RealtimeData {
  symbol: string;
  price: number;
  change: number;
  volume: number;
  timestamp: string;
}

export default function RealtimePage() {
  const [realtimeData, setRealtimeData] = useState<RealtimeData[]>([]);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    const interval = setInterval(() => {
      updateRealtimeData();
    }, 2000);

    updateRealtimeData();
    return () => clearInterval(interval);
  }, []);

  const updateRealtimeData = () => {
    const symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA'];
    const mockData = symbols.map(symbol => ({
      symbol,
      price: 150 + Math.random() * 50,
      change: (Math.random() - 0.5) * 10,
      volume: Math.floor(Math.random() * 10000000),
      timestamp: new Date().toLocaleTimeString()
    }));
    
    setRealtimeData(mockData);
    setLastUpdate(new Date().toLocaleTimeString());
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white flex items-center">
          <Activity className="w-6 h-6 mr-2 text-green-400 animate-pulse" />
          リアルタイム監視
        </h1>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-gray-400 text-sm">最終更新: {lastUpdate}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div className="youtube-card p-4">
          <div className="flex items-center mb-2">
            <AlertCircle className="w-5 h-5 text-orange-400 mr-2" />
            <h3 className="text-white font-semibold">アクティブアラート</h3>
          </div>
          <p className="text-2xl font-bold text-orange-400">3</p>
          <p className="text-gray-400 text-sm">価格変動アラート</p>
        </div>
        
        <div className="youtube-card p-4">
          <div className="flex items-center mb-2">
            <TrendingUp className="w-5 h-5 text-green-400 mr-2" />
            <h3 className="text-white font-semibold">上昇銘柄</h3>
          </div>
          <p className="text-2xl font-bold text-green-400">12</p>
          <p className="text-gray-400 text-sm">本日</p>
        </div>
        
        <div className="youtube-card p-4">
          <div className="flex items-center mb-2">
            <TrendingDown className="w-5 h-5 text-red-400 mr-2" />
            <h3 className="text-white font-semibold">下落銘柄</h3>
          </div>
          <p className="text-2xl font-bold text-red-400">8</p>
          <p className="text-gray-400 text-sm">本日</p>
        </div>
      </div>

      <div className="youtube-card p-6">
        <h2 className="text-lg font-semibold text-white mb-4">リアルタイム価格</h2>
        <div className="space-y-3">
          {realtimeData.map((stock) => (
            <div key={stock.symbol} className="flex items-center justify-between py-3 border-b border-gray-700/50 last:border-b-0">
              <div className="flex items-center space-x-3">
                <span className="text-white font-semibold w-16">{stock.symbol}</span>
                <span className="text-white font-bold">${stock.price.toFixed(2)}</span>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className={`flex items-center space-x-1 ${
                  stock.change >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {stock.change >= 0 ? 
                    <TrendingUp className="w-4 h-4" /> : 
                    <TrendingDown className="w-4 h-4" />
                  }
                  <span className="font-semibold">{stock.change.toFixed(2)}%</span>
                </div>
                <span className="text-gray-400 text-sm">{stock.timestamp}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}