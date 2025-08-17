'use client';

import { useState } from 'react';
import { Search, TrendingUp, BarChart3, Brain } from 'lucide-react';
import StockSearch from '@/components/StockSearch';
import StockChart from '@/components/charts/StockChart';

export default function Home() {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('');

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* ヘッダー */}
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Miraikakaku
            </span>
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            AI駆動の株価予測プラットフォーム
          </p>
          
          {/* 機能紹介 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="bg-white rounded-lg shadow-md p-6">
              <Search className="w-8 h-8 text-blue-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">株式検索</h3>
              <p className="text-gray-600">リアルタイムで株式データを検索・分析</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <BarChart3 className="w-8 h-8 text-green-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">価格チャート</h3>
              <p className="text-gray-600">インタラクティブな価格推移チャート</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <Brain className="w-8 h-8 text-purple-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">AI予測</h3>
              <p className="text-gray-600">機械学習による価格予測分析</p>
            </div>
          </div>
        </div>

        {/* 株式検索セクション */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <Search className="w-6 h-6 mr-2 text-blue-600" />
            株式検索
          </h2>
          <StockSearch onSymbolSelect={setSelectedSymbol} />
        </div>

        {/* チャート表示セクション */}
        {selectedSymbol && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <TrendingUp className="w-6 h-6 mr-2 text-green-600" />
              {selectedSymbol} - 価格チャート
            </h2>
            <StockChart symbol={selectedSymbol} />
          </div>
        )}
      </div>
    </main>
  )
}