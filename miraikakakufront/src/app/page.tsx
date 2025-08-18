'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, BarChart3, Brain, Activity, Star, Calculator } from 'lucide-react';
import StockSearch from '@/components/StockSearch';
import StockChart from '@/components/charts/StockChart';
import LoadingSpinner from '@/components/common/LoadingSpinner';

export default function Home() {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('');
  const [isPageLoading, setIsPageLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsPageLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  if (isPageLoading) {
    return (
      <div className="h-full bg-black text-white flex flex-col items-center justify-center">
        <div className="mb-8 animate-fade-in">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-red-500 to-pink-500 bg-clip-text text-transparent mb-4">
            Miraikakaku
          </h1>
          <p className="text-gray-400 text-center text-lg">
            AI駆動の株価予測プラットフォーム
          </p>
        </div>
        <LoadingSpinner 
          type="ai" 
          size="lg" 
          message="AI予測システムを初期化中..."
        />
      </div>
    );
  }

  return (
    <div className="p-8 min-h-full">
      {/* Hero Section with YouTube Music style */}
      <div className="mb-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-red-600/20 via-pink-600/10 to-purple-600/20 backdrop-blur-sm border border-gray-800/50">
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 to-pink-500/10"></div>
          <div className="relative p-8">
            <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              AI駆動の株価予測プラットフォーム
            </h2>
            <p className="text-xl text-gray-300 mb-6">
              機械学習とリアルタイムデータで未来の株価を予測
            </p>
            <div className="flex space-x-4">
              <button className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-full font-medium transition-all hover:scale-105">
                今すぐ開始
              </button>
              <button className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-full font-medium transition-all border border-white/20">
                詳細を見る
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div 
          onClick={() => window.location.href = '/analysis'}
          className="bg-gray-900/50 backdrop-blur-sm rounded-xl p-6 border border-gray-800/50 hover:border-red-500/30 transition-all group cursor-pointer"
        >
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">市場分析</h3>
          <p className="text-gray-400">リアルタイムチャートとテクニカル指標</p>
        </div>

        <div 
          onClick={() => window.location.href = '/predictions'}
          className="bg-gray-900/50 backdrop-blur-sm rounded-xl p-6 border border-gray-800/50 hover:border-red-500/30 transition-all group cursor-pointer"
        >
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">AI予測</h3>
          <p className="text-gray-400">機械学習による価格予測と分析</p>
        </div>

        <div 
          onClick={() => window.location.href = '/realtime'}
          className="bg-gray-900/50 backdrop-blur-sm rounded-xl p-6 border border-gray-800/50 hover:border-red-500/30 transition-all group cursor-pointer"
        >
          <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">リアルタイム</h3>
          <p className="text-gray-400">ライブデータとアラート機能</p>
        </div>

        <div 
          onClick={() => window.location.href = '/watchlist'}
          className="bg-gray-900/50 backdrop-blur-sm rounded-xl p-6 border border-gray-800/50 hover:border-red-500/30 transition-all group cursor-pointer"
        >
          <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <Star className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">ウォッチリスト</h3>
          <p className="text-gray-400">お気に入り銘柄の監視と追跡</p>
        </div>

        <div 
          onClick={() => window.location.href = '/tools'}
          className="bg-gray-900/50 backdrop-blur-sm rounded-xl p-6 border border-gray-800/50 hover:border-red-500/30 transition-all group cursor-pointer"
        >
          <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <Calculator className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">投資計算機</h3>
          <p className="text-gray-400">ポートフォリオとリスク計算</p>
        </div>

        <div 
          onClick={() => window.location.href = '/rankings'}
          className="bg-gray-900/50 backdrop-blur-sm rounded-xl p-6 border border-gray-800/50 hover:border-red-500/30 transition-all group cursor-pointer"
        >
          <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-red-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">ランキング</h3>
          <p className="text-gray-400">成長予測と予測精度ランキング</p>
        </div>
      </div>

      {/* Stock Search Section */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl p-8 border border-gray-800/50 mb-8">
        <h2 className="text-2xl font-bold text-white mb-6">
          株式検索
        </h2>
        <StockSearch onSymbolSelect={setSelectedSymbol} />
      </div>

      {/* Chart Section */}
      {selectedSymbol && (
        <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl p-8 border border-gray-800/50">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
            <TrendingUp className="w-6 h-6 mr-2 text-red-500" />
            {selectedSymbol} - 価格チャート
          </h2>
          <StockChart symbol={selectedSymbol} />
        </div>
      )}
    </div>
  )
}