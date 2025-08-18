'use client';

import React, { useState } from 'react';
import StockSearch from '@/components/StockSearch';
import StockChart from '@/components/charts/StockChart';
import { Brain, Target, TrendingUp } from 'lucide-react';

export default function PredictionsPage() {
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-6 flex items-center">
        <Brain className="w-6 h-6 mr-2 text-purple-400" />
        AI予測
      </h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="youtube-card p-4">
          <div className="flex items-center mb-2">
            <Target className="w-5 h-5 text-green-400 mr-2" />
            <h3 className="text-white font-semibold">予測精度</h3>
          </div>
          <p className="text-2xl font-bold text-green-400">87.3%</p>
          <p className="text-gray-400 text-sm">過去30日平均</p>
        </div>
        
        <div className="youtube-card p-4">
          <div className="flex items-center mb-2">
            <TrendingUp className="w-5 h-5 text-blue-400 mr-2" />
            <h3 className="text-white font-semibold">予測トレンド</h3>
          </div>
          <p className="text-2xl font-bold text-blue-400">上昇</p>
          <p className="text-gray-400 text-sm">次の7日間</p>
        </div>
        
        <div className="youtube-card p-4">
          <div className="flex items-center mb-2">
            <Brain className="w-5 h-5 text-purple-400 mr-2" />
            <h3 className="text-white font-semibold">信頼度</h3>
          </div>
          <p className="text-2xl font-bold text-purple-400">92%</p>
          <p className="text-gray-400 text-sm">最新予測</p>
        </div>
      </div>

      <div className="youtube-card p-6 mb-6">
        <h2 className="text-lg font-semibold text-white mb-4">銘柄選択</h2>
        <StockSearch onSymbolSelect={setSelectedSymbol} />
      </div>

      <div className="youtube-card p-6">
        <h2 className="text-lg font-semibold text-white mb-4">
          {selectedSymbol} - AI予測チャート
        </h2>
        <StockChart symbol={selectedSymbol} />
      </div>
    </div>
  );
}