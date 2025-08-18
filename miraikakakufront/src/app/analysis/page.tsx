'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface MarketData {
  symbol: string;
  current_price: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  pe_ratio: number;
  recommendation: string;
  analyst_target: number;
}

export default function AnalysisPage() {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMarketData();
  }, []);

  const fetchMarketData = async () => {
    setLoading(true);
    try {
      const symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA'];
      const promises = symbols.map(symbol =>
        fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${symbol}/analysis`)
          .then(res => res.json())
      );
      const data = await Promise.all(promises);
      setMarketData(data);
    } catch (error) {
      console.error('市場データ取得エラー:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-96">
        <LoadingSpinner type="ai" size="lg" message="市場データを分析中..." />
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-6">市場分析</h1>
      
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {marketData.map((stock) => (
          <div key={stock.symbol} className="youtube-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">{stock.symbol}</h2>
              <div className={`flex items-center space-x-1 ${
                stock.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {stock.change_percent >= 0 ? 
                  <TrendingUp className="w-4 h-4" /> : 
                  <TrendingDown className="w-4 h-4" />
                }
                <span className="font-semibold">{stock.change_percent.toFixed(2)}%</span>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-400">現在価格</p>
                <p className="text-white font-semibold">${stock.current_price.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-gray-400">目標価格</p>
                <p className="text-white font-semibold">${stock.analyst_target.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-gray-400">P/E比</p>
                <p className="text-white font-semibold">{stock.pe_ratio}</p>
              </div>
              <div>
                <p className="text-gray-400">推奨</p>
                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                  stock.recommendation === 'BUY' ? 'bg-green-600 text-white' :
                  stock.recommendation === 'SELL' ? 'bg-red-600 text-white' :
                  'bg-yellow-600 text-white'
                }`}>
                  {stock.recommendation}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}