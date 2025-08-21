'use client';

import { useState, useEffect } from 'react';
import { Widget } from '@/types/dashboard';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  PieChart,
  Target,
  AlertCircle,
  Plus
} from 'lucide-react';

interface PortfolioSummaryProps {
  widget: Widget;
}

interface PortfolioData {
  total_value: number;
  daily_change: number;
  daily_change_percent: number;
  total_return: number;
  total_return_percent: number;
  cash_balance: number;
  positions_count: number;
  top_holdings: {
    symbol: string;
    name: string;
    weight: number;
    value: number;
    change_percent: number;
  }[];
  performance_metrics: {
    sharpe_ratio: number;
    max_drawdown: number;
    volatility: number;
    beta: number;
  };
  allocation: {
    stocks: number;
    bonds: number;
    cash: number;
    alternatives: number;
  };
}

const mockPortfolioData: PortfolioData = {
  total_value: 15250000,
  daily_change: 125600,
  daily_change_percent: 0.83,
  total_return: 2150000,
  total_return_percent: 16.4,
  cash_balance: 850000,
  positions_count: 12,
  top_holdings: [
    { symbol: '7203', name: 'トヨタ自動車', weight: 15.2, value: 2318000, change_percent: 1.24 },
    { symbol: '9984', name: 'ソフトバンクグループ', weight: 12.8, value: 1952000, change_percent: -0.87 },
    { symbol: '6758', name: 'ソニーグループ', weight: 10.5, value: 1601250, change_percent: 2.15 },
    { symbol: '7974', name: '任天堂', weight: 8.9, value: 1357250, change_percent: 0.45 },
    { symbol: '8058', name: '三菱商事', weight: 7.6, value: 1159000, change_percent: 1.67 }
  ],
  performance_metrics: {
    sharpe_ratio: 1.35,
    max_drawdown: -12.4,
    volatility: 18.7,
    beta: 1.08
  },
  allocation: {
    stocks: 85.5,
    bonds: 8.2,
    cash: 5.6,
    alternatives: 0.7
  }
};

export default function PortfolioSummary({ widget }: PortfolioSummaryProps) {
  const [portfolioData, setPortfolioData] = useState<PortfolioData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState<'value' | 'return' | 'allocation'>('value');

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Add some randomness for demo
      const randomizedData = {
        ...mockPortfolioData,
        daily_change: mockPortfolioData.daily_change + (Math.random() - 0.5) * 50000,
        daily_change_percent: mockPortfolioData.daily_change_percent + (Math.random() - 0.5) * 0.5,
        top_holdings: mockPortfolioData.top_holdings.map(holding => ({
          ...holding,
          change_percent: holding.change_percent + (Math.random() - 0.5) * 1
        }))
      };
      
      setPortfolioData(randomizedData);
      setIsLoading(false);
    };

    loadData();
    
    // Auto-refresh every minute
    const interval = setInterval(loadData, 60000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading || !portfolioData) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-pulse space-y-4 w-full">
          <div className="h-6 bg-surface-elevated rounded w-2/3"></div>
          <div className="h-4 bg-surface-elevated rounded w-1/2"></div>
          <div className="space-y-2">
            <div className="h-3 bg-surface-elevated rounded"></div>
            <div className="h-3 bg-surface-elevated rounded w-5/6"></div>
            <div className="h-3 bg-surface-elevated rounded w-4/6"></div>
          </div>
        </div>
      </div>
    );
  }

  const allocationData = [
    { label: '株式', value: portfolioData.allocation.stocks, color: '#2196f3' },
    { label: '債券', value: portfolioData.allocation.bonds, color: '#10b981' },
    { label: '現金', value: portfolioData.allocation.cash, color: '#f59e0b' },
    { label: 'オルタナティブ', value: portfolioData.allocation.alternatives, color: '#8b5cf6' }
  ];

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Header with Total Value */}
      <div className="text-center">
        <div className="text-2xl font-bold text-text-primary">
          ¥{portfolioData.total_value.toLocaleString()}
        </div>
        <div className={`flex items-center justify-center space-x-1 text-sm font-medium ${
          portfolioData.daily_change_percent >= 0 ? 'text-status-success' : 'text-status-danger'
        }`}>
          {portfolioData.daily_change_percent >= 0 ? (
            <TrendingUp size={14} />
          ) : (
            <TrendingDown size={14} />
          )}
          <span>
            {portfolioData.daily_change_percent >= 0 ? '+' : ''}
            ¥{portfolioData.daily_change.toLocaleString()}
          </span>
          <span>
            ({portfolioData.daily_change_percent >= 0 ? '+' : ''}
            {portfolioData.daily_change_percent.toFixed(2)}%)
          </span>
        </div>
        <div className="text-xs text-text-secondary mt-1">
          本日
        </div>
      </div>

      {/* Metric Tabs */}
      <div className="flex bg-surface-elevated rounded-lg p-1">
        {[
          { key: 'value', label: '価値', icon: DollarSign },
          { key: 'return', label: 'リターン', icon: TrendingUp },
          { key: 'allocation', label: '配分', icon: PieChart }
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setSelectedMetric(key as any)}
            className={`flex-1 flex items-center justify-center space-x-1 py-2 px-3 rounded-md text-sm font-medium transition-all ${
              selectedMetric === key
                ? 'bg-brand-primary text-white'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            <Icon size={14} />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* Content based on selected metric */}
      <div className="flex-1 overflow-hidden">
        {selectedMetric === 'value' && (
          <motion.div
            key="value"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="h-full flex flex-col space-y-3"
          >
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-surface-elevated p-3 rounded-lg text-center">
                <div className="text-lg font-semibold text-text-primary">
                  {portfolioData.positions_count}
                </div>
                <div className="text-xs text-text-secondary">銘柄数</div>
              </div>
              <div className="bg-surface-elevated p-3 rounded-lg text-center">
                <div className="text-lg font-semibold text-text-primary">
                  ¥{portfolioData.cash_balance.toLocaleString()}
                </div>
                <div className="text-xs text-text-secondary">現金残高</div>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto">
              <h4 className="text-sm font-medium text-text-primary mb-2">主要保有銘柄</h4>
              <div className="space-y-2">
                {portfolioData.top_holdings.map((holding, i) => (
                  <motion.div
                    key={holding.symbol}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="flex items-center justify-between p-2 bg-surface-elevated rounded-lg"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-text-primary truncate">
                        {holding.name}
                      </div>
                      <div className="text-xs text-text-secondary font-mono">
                        {holding.symbol} • {holding.weight.toFixed(1)}%
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-mono text-text-primary">
                        ¥{(holding.value / 1000).toFixed(0)}K
                      </div>
                      <div className={`text-xs font-medium ${
                        holding.change_percent >= 0 ? 'text-status-success' : 'text-status-danger'
                      }`}>
                        {holding.change_percent >= 0 ? '+' : ''}
                        {holding.change_percent.toFixed(2)}%
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {selectedMetric === 'return' && (
          <motion.div
            key="return"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="h-full flex flex-col space-y-3"
          >
            <div className="bg-surface-elevated p-4 rounded-lg text-center">
              <div className="text-xl font-bold text-status-success">
                +{portfolioData.total_return_percent.toFixed(1)}%
              </div>
              <div className="text-sm text-text-secondary mb-1">総合リターン</div>
              <div className="text-lg font-semibold text-text-primary">
                +¥{portfolioData.total_return.toLocaleString()}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'シャープレシオ', value: portfolioData.performance_metrics.sharpe_ratio.toFixed(2), good: portfolioData.performance_metrics.sharpe_ratio > 1 },
                { label: '最大ドローダウン', value: `${portfolioData.performance_metrics.max_drawdown.toFixed(1)}%`, good: portfolioData.performance_metrics.max_drawdown > -15 },
                { label: 'ボラティリティ', value: `${portfolioData.performance_metrics.volatility.toFixed(1)}%`, good: portfolioData.performance_metrics.volatility < 20 },
                { label: 'ベータ', value: portfolioData.performance_metrics.beta.toFixed(2), good: Math.abs(portfolioData.performance_metrics.beta - 1) < 0.2 }
              ].map((metric, i) => (
                <motion.div
                  key={metric.label}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-surface-elevated p-3 rounded-lg text-center"
                >
                  <div className={`text-lg font-semibold ${
                    metric.good ? 'text-status-success' : 'text-status-warning'
                  }`}>
                    {metric.value}
                  </div>
                  <div className="text-xs text-text-secondary">{metric.label}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {selectedMetric === 'allocation' && (
          <motion.div
            key="allocation"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="h-full flex flex-col space-y-3"
          >
            {/* Allocation Chart (Simple bars for now) */}
            <div className="space-y-2">
              {allocationData.map((item, i) => (
                <motion.div
                  key={item.label}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex items-center space-x-3"
                >
                  <div 
                    className="w-3 h-3 rounded-full flex-shrink-0"
                    style={{ backgroundColor: item.color }}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-text-primary">{item.label}</span>
                      <span className="text-sm font-medium text-text-primary">
                        {item.value.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-surface-elevated rounded-full h-2">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${item.value}%` }}
                        transition={{ delay: i * 0.1 + 0.3, duration: 0.5 }}
                        className="h-2 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Rebalancing Suggestions */}
            <div className="mt-4 p-3 bg-status-warning/10 border border-status-warning/30 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <Target size={14} className="text-status-warning" />
                <span className="text-sm font-medium text-status-warning">リバランス推奨</span>
              </div>
              <p className="text-xs text-text-secondary">
                株式の比重が目標配分より5%高くなっています。
                一部売却を検討することをお勧めします。
              </p>
            </div>
          </motion.div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="flex space-x-2">
        <button className="flex-1 flex items-center justify-center space-x-1 py-2 px-3 bg-brand-primary text-white rounded-lg text-sm font-medium hover:bg-brand-primary-hover transition-colors">
          <Plus size={14} />
          <span>追加投資</span>
        </button>
        <button className="flex-1 py-2 px-3 border border-border-default text-text-secondary rounded-lg text-sm font-medium hover:text-text-primary hover:border-border-strong transition-colors">
          詳細を見る
        </button>
      </div>
    </div>
  );
}