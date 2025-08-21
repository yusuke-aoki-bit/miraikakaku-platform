'use client';

import { useState, useEffect } from 'react';
import { Widget } from '@/types/dashboard';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Activity, Globe } from 'lucide-react';

interface MarketOverviewProps {
  widget: Widget;
}

interface MarketIndex {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap?: number;
  region: 'domestic' | 'us' | 'asia' | 'europe';
}

const mockIndices: MarketIndex[] = [
  {
    symbol: 'N225',
    name: '日経平均',
    price: 33125.05,
    change: -128.45,
    change_percent: -0.39,
    volume: 1240000000,
    region: 'domestic'
  },
  {
    symbol: 'TPX',
    name: 'TOPIX',
    price: 2420.18,
    change: 15.22,
    change_percent: 0.63,
    volume: 2100000000,
    region: 'domestic'
  },
  {
    symbol: 'SPX',
    name: 'S&P 500',
    price: 4721.12,
    change: 24.85,
    change_percent: 0.53,
    volume: 3850000000,
    region: 'us'
  },
  {
    symbol: 'NDX',
    name: 'ナスダック',
    price: 14855.32,
    change: -41.23,
    change_percent: -0.28,
    volume: 4120000000,
    region: 'us'
  },
  {
    symbol: 'HSI',
    name: 'ハンセン',
    price: 18420.56,
    change: 112.34,
    change_percent: 0.61,
    volume: 1680000000,
    region: 'asia'
  },
  {
    symbol: 'SX5E',
    name: 'ユーロ・ストックス50',
    price: 4320.78,
    change: -8.92,
    change_percent: -0.21,
    volume: 980000000,
    region: 'europe'
  }
];

const regionColors = {
  domestic: 'bg-brand-primary/20 text-brand-primary',
  us: 'bg-blue-500/20 text-blue-400',
  asia: 'bg-green-500/20 text-green-400',
  europe: 'bg-purple-500/20 text-purple-400'
};

const regionLabels = {
  domestic: '国内',
  us: '米国',
  asia: 'アジア',
  europe: '欧州'
};

export default function MarketOverview({ widget }: MarketOverviewProps) {
  const [indices, setIndices] = useState<MarketIndex[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedRegion, setSelectedRegion] = useState<string>('all');

  useEffect(() => {
    // Simulate API call
    const loadData = async () => {
      setIsLoading(true);
      
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Add some randomness to mock live updates
      const updatedIndices = mockIndices.map(index => ({
        ...index,
        price: index.price + (Math.random() - 0.5) * 10,
        change: index.change + (Math.random() - 0.5) * 5,
        change_percent: index.change_percent + (Math.random() - 0.5) * 0.2
      }));
      
      setIndices(updatedIndices);
      setIsLoading(false);
    };

    loadData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const filteredIndices = selectedRegion === 'all' 
    ? indices 
    : indices.filter(index => index.region === selectedRegion);

  const marketSentiment = () => {
    const positive = indices.filter(i => i.change_percent > 0).length;
    const total = indices.length;
    const ratio = positive / total;
    
    if (ratio >= 0.7) return { label: '楽観的', color: 'text-status-success', icon: TrendingUp };
    if (ratio >= 0.4) return { label: '中立', color: 'text-status-warning', icon: Minus };
    return { label: '悲観的', color: 'text-status-danger', icon: TrendingDown };
  };

  const sentiment = marketSentiment();
  const SentimentIcon = sentiment.icon;

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-pulse space-y-4 w-full">
          <div className="h-4 bg-surface-elevated rounded w-3/4"></div>
          <div className="h-4 bg-surface-elevated rounded w-1/2"></div>
          <div className="h-4 bg-surface-elevated rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Market Sentiment Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Globe size={18} className="text-text-secondary" />
          <h4 className="font-medium text-text-primary">マーケット概況</h4>
        </div>
        <div className={`flex items-center space-x-1 text-sm font-medium ${sentiment.color}`}>
          <SentimentIcon size={16} />
          <span>{sentiment.label}</span>
        </div>
      </div>

      {/* Region Filter */}
      <div className="flex space-x-1 p-1 bg-surface-elevated rounded-lg">
        <button
          onClick={() => setSelectedRegion('all')}
          className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
            selectedRegion === 'all'
              ? 'bg-brand-primary text-white'
              : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          すべて
        </button>
        {Object.entries(regionLabels).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setSelectedRegion(key)}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
              selectedRegion === key
                ? 'bg-brand-primary text-white'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Indices List */}
      <div className="flex-1 overflow-y-auto space-y-2">
        {filteredIndices.map((index, i) => (
          <motion.div
            key={index.symbol}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex items-center justify-between p-3 bg-surface-elevated rounded-lg hover:bg-surface-elevated/80 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className={`px-2 py-1 rounded text-xs font-medium ${regionColors[index.region]}`}>
                {regionLabels[index.region]}
              </div>
              <div>
                <div className="font-medium text-text-primary text-sm">
                  {index.name}
                </div>
                <div className="text-xs text-text-tertiary font-mono">
                  {index.symbol}
                </div>
              </div>
            </div>

            <div className="text-right">
              <div className="font-mono text-sm text-text-primary">
                {index.price.toLocaleString('ja-JP', { 
                  maximumFractionDigits: 2,
                  minimumFractionDigits: 2 
                })}
              </div>
              <div className={`flex items-center text-xs font-medium ${
                index.change_percent >= 0 ? 'text-status-success' : 'text-status-danger'
              }`}>
                {index.change_percent >= 0 ? (
                  <TrendingUp size={12} className="mr-1" />
                ) : (
                  <TrendingDown size={12} className="mr-1" />
                )}
                {index.change_percent >= 0 ? '+' : ''}
                {index.change_percent.toFixed(2)}%
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Market Activity Indicator */}
      <div className="flex items-center justify-between p-2 bg-surface-elevated/50 rounded-lg">
        <div className="flex items-center space-x-2 text-xs text-text-secondary">
          <Activity size={12} />
          <span>市場活動</span>
        </div>
        <div className="text-xs text-text-primary font-medium">
          {indices.filter(i => Math.abs(i.change_percent) > 0.5).length}/{indices.length} が活発
        </div>
      </div>
    </div>
  );
}