'use client';

import { useState, useEffect } from 'react';
import { TIME_PERIODS } from '@/config/constants';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import HeroSection from '@/components/home/HeroSection';
import MarketOverview from '@/components/home/MarketOverview';
import AIInsights from '@/components/home/AIInsights';
import AdvancedStockSearch from '@/components/search/AdvancedStockSearch';
import { Bell, BookOpen, TrendingUp, Users } from 'lucide-react';
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
          <p className="text-neutral text-center text-lg md:text-xl">
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
          
          {/* Right Column - Quick Actions & News */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="card-glass card-content">
              <h3 className="card-title mb-4">クイックアクション</h3>
              <div className="space-y-3">
                <QuickActionCard
                  icon={<TrendingUp className="w-5 h-5" />}
                  title="ポートフォリオ分析"
                  description="リスク評価とパフォーマンス"
                  color="from-base-blue-500 to-base-blue-400"
                  href="/dashboard"
                />
                <QuickActionCard
                  icon={<Bell className="w-5 h-5" />}
                  title="アラート設定"
                  description="価格変動の通知を管理"
                  color="from-base-blue-600 to-base-blue-500"
                  href="/watchlist"
                />
                <QuickActionCard
                  icon={<BookOpen className="w-5 h-5" />}
                  title="マーケットレポート"
                  description="日次分析レポートを確認"
                  color="from-icon-green to-icon-green/80"
                  href="/analysis"
                />
                <QuickActionCard
                  icon={<Users className="w-5 h-5" />}
                  title="AI予測"
                  description="AI による株価予測"
                  color="from-icon-red to-icon-red/80"
                  href="/predictions"
                />
              </div>
            </div>
            
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
              <button className="w-full mt-4 btn-ghost btn-sm text-primary">
                すべてのニュースを見る →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

interface QuickActionCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
  href: string;
}

function QuickActionCard({ icon, title, description, color, href }: QuickActionCardProps) {
  return (
    <Link href={href} className="block w-full">
      <div className="card-interactive group text-left">
        <div className="flex items-start space-x-3">
          <div className={`p-2 rounded-lg bg-gradient-to-r ${color} bg-opacity-20 group-hover:scale-110 transition-transform`}>
            <div className="text-text-white">{icon}</div>
          </div>
          <div className="flex-1">
            <h4 className="text-text-white font-medium group-hover:text-primary transition-colors">
              {title}
            </h4>
            <p className="text-neutral text-sm mt-1">{description}</p>
          </div>
        </div>
      </div>
    </Link>
  );
}

interface NewsItemProps {
  time: string;
  title: string;
  category: string;
}

function NewsItem({ time, title, category }: NewsItemProps) {
  const categoryColors: { [key: string]: string } = {
    '市場': 'status-warning',
    '企業': 'status-success',
    '海外': 'text-primary bg-base-blue-400/10',
    'セクター': 'status-danger'
  };

  return (
    <div className="group cursor-pointer hover:bg-base-gray-800/20 p-2 rounded-lg transition-colors">
      <div className="flex items-start space-x-3">
        <span className="text-neutral text-xs mt-1 whitespace-nowrap">{time}</span>
        <div className="flex-1">
          <h4 className="text-text-medium group-hover:text-text-white transition-colors text-sm font-medium">
            {title}
          </h4>
          <span className={`inline-block mt-1 px-2 py-0.5 text-xs rounded-full border ${categoryColors[category] || 'status-neutral'}`}>
            {category}
          </span>
        </div>
      </div>
    </div>
  );
}