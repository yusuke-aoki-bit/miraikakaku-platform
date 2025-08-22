'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, Zap } from 'lucide-react';

export default function HeroSection() {
  const [marketStatus, setMarketStatus] = useState('OPEN');
  const [animatedValue, setAnimatedValue] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setAnimatedValue(prev => (prev + 1) % 100);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-red-950/20 via-black to-pink-950/20 p-8 mb-6 border border-red-900/20">
      {/* Animated background effect */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-0 left-0 w-96 h-96 bg-red-500 rounded-full filter blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-pink-500 rounded-full filter blur-3xl animate-pulse animation-delay-2000" />
      </div>
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold mb-2">
              <span className="bg-gradient-to-r from-red-400 to-pink-400 bg-clip-text text-transparent">
                Miraikakaku
              </span>
            </h1>
            <p className="text-neutral-400 text-lg">
              AIが市場を24時間監視中
            </p>
          </div>
          
          <div className="hidden md:flex items-center space-x-2 px-4 py-2 bg-success/10 border border-success/30 rounded-full">
            <Activity className="w-4 h-4 text-success animate-pulse" />
            <span className="text-success font-medium">マーケット: {marketStatus}</span>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            title="日経平均"
            value="¥39,283.12"
            change="+1.23%"
            trend="up"
            icon={<TrendingUp className="w-5 h-5" />}
          />
          <StatCard
            title="TOPIX"
            value="2,781.45"
            change="-0.45%"
            trend="down"
            icon={<TrendingDown className="w-5 h-5" />}
          />
          <StatCard
            title="AI予測精度"
            value="87.3%"
            change="+2.1%"
            trend="up"
            icon={<Zap className="w-5 h-5" />}
          />
          <StatCard
            title="アクティブ予測"
            value="42"
            change="本日の予測"
            trend="neutral"
            icon={<Activity className="w-5 h-5" />}
          />
        </div>
      </div>
    </div>
  );
}

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down' | 'neutral';
  icon: React.ReactNode;
}

function StatCard({ title, value, change, trend, icon }: StatCardProps) {
  const trendColors = {
    up: 'text-success bg-success/10 border-success/30',
    down: 'text-danger bg-danger/10 border-danger/30',
    neutral: 'text-neutral-400 bg-neutral-400/10 border-neutral-400/30'
  };

  const trendTextColors = {
    up: 'text-success',
    down: 'text-danger',
    neutral: 'text-neutral-400'
  }

  return (
    <div className="bg-black/40 backdrop-blur-sm border border-neutral-800/50 rounded-xl p-4 hover:border-primary/30 transition-all duration-300 hover:transform hover:scale-105">
      <div className="flex items-center justify-between mb-2">
        <span className="text-neutral-400 text-sm">{title}</span>
        <div className={`p-1.5 rounded-lg ${trendColors[trend]}`}>
          {icon}
        </div>
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className={`text-sm ${trendTextColors[trend]}`}>
        {change}
      </div>
    </div>
  );
}