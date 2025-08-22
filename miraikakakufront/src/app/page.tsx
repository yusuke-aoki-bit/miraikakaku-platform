'use client';

import { useState, useEffect } from 'react';
import { TIME_PERIODS } from '@/config/constants';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import HeroSection from '@/components/home/HeroSection';
import MarketOverview from '@/components/home/MarketOverview';
import AIInsights from '@/components/home/AIInsights';
import AdvancedStockSearch from '@/components/search/AdvancedStockSearch';

import Link from 'next/link';

export default function Home() {
  const [isPageLoading, setIsPageLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsPageLoading(false);
    }, TIME_PERIODS.LOADING_DELAY);
    return () => clearTimeout(timer);
  }, []);

  if (isPageLoading) {
    return (
      <div className="page-container flex flex-col items-center justify-center">
        <div className="mb-8 animate-fade-in">
          <h1 className="text-5xl md:text-7xl font-bold gradient-text-primary mb-4">
            Miraikakaku
          </h1>
          <p className="text-neutral-400 text-center text-lg md:text-xl">
            AI駆動の株価予測プラットフォーム
          </p>
        </div>
        <LoadingSpinner 
          type="ai" 
          size="lg" 
          message="マーケットデータを読み込み中..."
        />
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-content">
        {/* Hero Section */}
        <HeroSection />
        
        {/* Stock Search */}
        <AdvancedStockSearch />
        
        {/* Main Content Grid */}
        <div className="grid-main mt-6">
          {/* Left Column - Market Overview (2 cols on lg) */}
          <div className="lg:col-span-2">
            <MarketOverview />
            <AIInsights />
          </div>
          
          {/* Right Column - News */}
          <div className="space-y-6">
            {/* Market News */}
            <div className="card-glass card-content">
              <h3 className="card-title mb-4">マーケットニュース</h3>
              <div className="space-y-4">
                <NewsItem
                  time="5分前"
                  title="日経平均、3万9000円台を回復"
                  category="市場"
                />
                <NewsItem
                  time="23分前"
                  title="トヨタ、EVバッテリー技術で新たな提携"
                  category="企業"
                />
                <NewsItem
                  time="1時間前"
                  title="米FRB、利下げ観測強まる"
                  category="海外"
                />
                <NewsItem
                  time="2時間前"
                  title="半導体関連株が軒並み上昇"
                  category="セクター"
                />
              </div>
              <Link href="/news" className="block w-full mt-4 btn-ghost btn-sm text-primary text-center">
                すべてのニュースを見る →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

interface NewsItemProps {
  time: string;
  title: string;
  category: string;
}

function NewsItem({ time, title, category }: NewsItemProps) {
  const categoryColors: { [key: string]: string } = {
    '市場': 'text-warning bg-warning/10 border-warning',
    '企業': 'text-success bg-success/10 border-success',
    '海外': 'text-primary bg-primary/10 border-primary',
    'セクター': 'text-danger bg-danger/10 border-danger'
  };

  return (
    <Link href="/news/1" className="block group hover:bg-neutral-800/20 p-2 rounded-lg transition-colors">
      <div className="flex items-start space-x-3">
        <span className="text-neutral-400 text-xs mt-1 whitespace-nowrap">{time}</span>
        <div className="flex-1">
          <h4 className="text-neutral-300 group-hover:text-white transition-colors text-sm font-medium">
            {title}
          </h4>
          <span className={`inline-block mt-1 px-2 py-0.5 text-xs rounded-full border ${categoryColors[category] || 'text-neutral-400 bg-neutral-400/10 border-neutral-400'}`}>
            {category}
          </span>
        </div>
      </div>
    </Link>
  );
}