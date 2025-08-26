'use client';

import HeroSection from '@/components/home/HeroSection';
import MarketIndexSummary from '@/components/home/MarketIndexSummary';
import MarketNews from '@/components/home/MarketNews';
import WatchlistWidget from '@/components/home/WatchlistWidget';
import TrendingStocksWidget from '@/components/home/TrendingStocksWidget';
import FeaturedPredictionWidget from '@/components/home/FeaturedPredictionWidget';
import EconomicEventBooksWidget from '@/components/books/EconomicEventBooksWidget';

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
        </div>
      </div>
    </div>
  );
}