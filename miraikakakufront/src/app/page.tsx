'use client';

import HeroSection from '@/components/home/HeroSection';
import MarketIndexSummary from '@/components/home/MarketIndexSummary';
import MarketNews from '@/components/home/MarketNews';
import WatchlistWidget from '@/components/home/WatchlistWidget';
import TrendingStocksWidget from '@/components/home/TrendingStocksWidget';
import FeaturedPredictionWidget from '@/components/home/FeaturedPredictionWidget';
import EconomicEventBooksWidget from '@/components/books/EconomicEventBooksWidget';
import AdSenseUnit from '@/components/monetization/AdSenseUnit';
import AmazonProductCard from '@/components/monetization/AmazonProductCard';
import amazonRecommendations from '@/data/amazon-recommendations.json';
import { BookOpen } from 'lucide-react';

export default function Home() {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* ヒーローセクション（全幅） */}
      <div className="mb-8">
        <HeroSection />
      </div>

      {/* 2カラムレイアウト */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 左カラム（メインコンテンツ、2/3幅） */}
        <div className="lg:col-span-2 space-y-8">
          {/* 主要指数サマリー */}
          <MarketIndexSummary />
          
          {/* マーケットニュース */}
          <MarketNews />
          
          {/* 経済指標関連書籍ウィジェット */}
          <EconomicEventBooksWidget />
        </div>

        {/* 右カラム（サイドコンテンツ、1/3幅） */}
        <div className="space-y-8">
          {/* ウォッチリスト・ウィジェット */}
          <WatchlistWidget />
          
          {/* トレンド銘柄ランキング */}
          <TrendingStocksWidget />
          
          {/* AI注目予測 */}
          <FeaturedPredictionWidget />
          
          {/* AdSense広告 */}
          <div className="mt-6">
            <AdSenseUnit
              adSlot="1234567894"
              style={{ display: 'block', textAlign: 'center', minHeight: '200px' }}
            />
          </div>
        </div>
      </div>

      {/* 全幅でAmazon商品推薦 */}
      <div className="mt-8 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <BookOpen className="w-6 h-6 text-blue-600 mr-2" />
          <h2 className="text-2xl font-semibold text-gray-800">
            {amazonRecommendations.general.title}
          </h2>
        </div>
        <p className="text-gray-600 mb-6">
          {amazonRecommendations.general.description}
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {amazonRecommendations.general.products.map((product) => (
            <AmazonProductCard
              key={product.id}
              product={product}
              compact={false}
            />
          ))}
        </div>
      </div>
    </div>
  );
}