'use client';

import React, { useState, useEffect } from 'react';
import { User, TrendingUp, DollarSign, Eye, Star, BookOpen } from 'lucide-react';
import AdSenseUnit from '@/components/monetization/AdSenseUnit';
import AmazonProductCard from '@/components/monetization/AmazonProductCard';
import WatchlistWidget from '@/components/home/WatchlistWidget';
import { motion } from 'framer-motion';
import { apiClient } from '@/lib/api-client';
import amazonRecommendations from '@/data/amazon-recommendations.json';

interface DashboardData {
  user: {
    name: string;
    email: string;
  } | null;
  portfolioValue: number;
  portfolioChange: number;
  portfolioChangePercent: number;
  watchlistCount: number;
  watchlistTopMover: {
    symbol: string;
    name: string;
    change: number;
  } | null;
  recentActivity: {
    type: 'prediction' | 'contest' | 'watchlist';
    description: string;
    timestamp: string;
  }[];
}

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    user: null,
    portfolioValue: 0,
    portfolioChange: 0,
    portfolioChangePercent: 0,
    watchlistCount: 0,
    watchlistTopMover: null,
    recentActivity: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch user profile
        const userResponse = await apiClient.getCurrentUser();
        
        // Fetch portfolio summary
        const portfolioResponse = await apiClient.getPortfolioSummary();
        
        // Fetch watchlist summary
        const watchlistResponse = await apiClient.getWatchlist();

        setDashboardData({
          user: userResponse.success ? userResponse.data : null,
          portfolioValue: portfolioResponse.success ? portfolioResponse.data?.totalValue || 0 : 0,
          portfolioChange: portfolioResponse.success ? portfolioResponse.data?.todayChange || 0 : 0,
          portfolioChangePercent: portfolioResponse.success ? portfolioResponse.data?.todayChangePercent || 0 : 0,
          watchlistCount: watchlistResponse.success && Array.isArray(watchlistResponse.data) ? watchlistResponse.data.length : 0,
          watchlistTopMover: watchlistResponse.success && Array.isArray(watchlistResponse.data) && watchlistResponse.data.length > 0 
            ? watchlistResponse.data[0] 
            : null,
          recentActivity: [] // TODO: Implement activity feed API
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded w-64 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-32 bg-gray-800 rounded-xl"></div>
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-6">
                <div className="h-96 bg-gray-800 rounded-xl"></div>
                <div className="h-96 bg-gray-800 rounded-xl"></div>
              </div>
              <div className="space-y-6">
                <div className="h-64 bg-gray-800 rounded-xl"></div>
                <div className="h-96 bg-gray-800 rounded-xl"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Page Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-white flex items-center">
            <User className="w-8 h-8 mr-3 text-blue-400" />
            こんにちは、{dashboardData.user?.name || 'ゲスト'}さん
          </h1>
          <p className="text-gray-400 mt-2">
            あなたのポートフォリオと投資状況をひと目で確認
          </p>
        </motion.div>

        {/* Summary Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          {/* Portfolio Value Card */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-300">ポートフォリオ評価額</h3>
              <DollarSign className="w-6 h-6 text-green-400" />
            </div>
            <div className="space-y-2">
              <div className="text-2xl font-bold text-white">
                ¥{dashboardData.portfolioValue.toLocaleString()}
              </div>
              <div className={`flex items-center text-sm ${
                dashboardData.portfolioChange >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                <TrendingUp className={`w-4 h-4 mr-1 ${
                  dashboardData.portfolioChange < 0 ? 'rotate-180' : ''
                }`} />
                {dashboardData.portfolioChange >= 0 ? '+' : ''}
                ¥{Math.abs(dashboardData.portfolioChange).toLocaleString()} 
                ({dashboardData.portfolioChangePercent >= 0 ? '+' : ''}
                {dashboardData.portfolioChangePercent.toFixed(2)}%)
              </div>
            </div>
          </div>

          {/* Watchlist Card */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-300">ウォッチリスト</h3>
              <Eye className="w-6 h-6 text-blue-400" />
            </div>
            <div className="space-y-2">
              <div className="text-2xl font-bold text-white">
                {dashboardData.watchlistCount}銘柄
              </div>
              {dashboardData.watchlistTopMover && (
                <div className="text-sm text-gray-400">
                  注目: {dashboardData.watchlistTopMover.symbol} 
                  <span className={dashboardData.watchlistTopMover.change >= 0 ? 'text-green-400' : 'text-red-400'}>
                    {dashboardData.watchlistTopMover.change >= 0 ? '+' : ''}
                    {dashboardData.watchlistTopMover.change.toFixed(2)}%
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Activity Card */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-300">最近のアクティビティ</h3>
              <Star className="w-6 h-6 text-yellow-400" />
            </div>
            <div className="space-y-2">
              <div className="text-sm text-gray-400">
                {dashboardData.recentActivity.length > 0 
                  ? `${dashboardData.recentActivity.length}件の新しい活動`
                  : '新しい予測を開始しましょう'
                }
              </div>
            </div>
          </div>
        </motion.div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Area (Left 2/3) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Watchlist Preview */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <WatchlistWidget />
            </motion.div>

            {/* Portfolio Preview */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-gray-900/50 border border-gray-800 rounded-xl p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white">ポートフォリオ概要</h2>
                <button className="text-blue-400 hover:text-blue-300 text-sm font-medium">
                  詳細を見る →
                </button>
              </div>

              {dashboardData.portfolioValue > 0 ? (
                <div className="space-y-4">
                  {/* Portfolio Chart Placeholder */}
                  <div className="h-64 bg-gray-800/50 rounded-lg flex items-center justify-center">
                    <div className="text-center text-gray-400">
                      <DollarSign className="w-12 h-12 mx-auto mb-2" />
                      <p>ポートフォリオチャートを表示</p>
                      <p className="text-sm">（実装予定）</p>
                    </div>
                  </div>
                  
                  {/* Quick Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-lg font-semibold text-white">0</div>
                      <div className="text-xs text-gray-400">保有銘柄数</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-green-400">0%</div>
                      <div className="text-xs text-gray-400">今年のリターン</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-blue-400">0%</div>
                      <div className="text-xs text-gray-400">配当利回り</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-purple-400">0%</div>
                      <div className="text-xs text-gray-400">リスク指標</div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <DollarSign className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                  <h3 className="text-lg font-semibold text-gray-400 mb-2">
                    ポートフォリオを開始しましょう
                  </h3>
                  <p className="text-gray-500 mb-4">
                    興味のある銘柄をウォッチリストに追加して投資を始めましょう
                  </p>
                  <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    銘柄を探す
                  </button>
                </div>
              )}
            </motion.div>
          </div>

          {/* Sidebar (Right 1/3) */}
          <div className="space-y-6">
            {/* AdSense Unit */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <AdSenseUnit
                adSlot="1234567890"
                className="w-full"
                style={{ minHeight: '600px' }}
              />
            </motion.div>

            {/* Recommendations */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-gray-900/50 border border-gray-800 rounded-xl p-6"
            >
              <div className="flex items-center mb-4">
                <BookOpen className="w-5 h-5 mr-2 text-blue-400" />
                <h3 className="text-lg font-semibold text-white">あなたへのおすすめ</h3>
              </div>
              
              <div className="space-y-4 mb-6">
                <div className="p-4 bg-blue-900/20 border border-blue-800/30 rounded-lg">
                  <h4 className="font-medium text-blue-300 mb-2">📈 成長株テーマ</h4>
                  <p className="text-sm text-gray-400">
                    あなたのウォッチリストの傾向から、テクノロジー株への関心が高いようです
                  </p>
                </div>
                
                <div className="p-4 bg-green-900/20 border border-green-800/30 rounded-lg">
                  <h4 className="font-medium text-green-300 mb-2">💡 分散投資のススメ</h4>
                  <p className="text-sm text-gray-400">
                    リスク分散のため、異なるセクターの銘柄も検討してみましょう
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Amazon Product Recommendations */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="flex items-center mb-4">
                  <BookOpen className="w-6 h-6 text-blue-600 mr-2" />
                  <h3 className="text-xl font-semibold text-gray-800">
                    {amazonRecommendations.dashboard.title}
                  </h3>
                </div>
                <p className="text-gray-600 mb-4">{amazonRecommendations.dashboard.description}</p>
                <div className="grid grid-cols-1 gap-4">
                  {amazonRecommendations.dashboard.products.slice(0, 2).map((product) => (
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
  );
}