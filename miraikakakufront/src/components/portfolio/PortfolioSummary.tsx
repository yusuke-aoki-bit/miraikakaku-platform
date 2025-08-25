'use client';

import { 
  CurrencyDollarIcon, 
  TrendingUpIcon, 
  TrendingDownIcon,
  GiftIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';

interface PortfolioSummaryProps {
  summary: {
    total_value: number;
    total_cost: number;
    total_profit_loss: number;
    total_profit_loss_percent: number;
    daily_change: number;
    daily_change_percent: number;
    annual_dividend_estimate: number;
  };
}

export default function PortfolioSummary({ summary }: PortfolioSummaryProps) {
  const formatCurrency = (amount: number) => {
    return `¥${amount.toLocaleString('ja-JP')}`;
  };

  const formatPercent = (percent: number) => {
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`;
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* 総資産額 */}
      <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-xl p-6">
        <div className="flex items-center justify-between mb-3">
          <div className="p-2 bg-blue-500/20 rounded-lg">
            <CurrencyDollarIcon className="w-6 h-6 text-blue-400" />
          </div>
          <span className="text-xs font-medium text-blue-400 uppercase tracking-wide">
            総資産額
          </span>
        </div>
        <div className="space-y-1">
          <div className="text-2xl font-bold text-text-primary">
            {formatCurrency(summary.total_value)}
          </div>
          <div className="text-sm text-text-secondary">
            取得総額: {formatCurrency(summary.total_cost)}
          </div>
        </div>
      </div>

      {/* 本日の損益 */}
      <div className={`bg-gradient-to-br ${
        summary.daily_change >= 0 
          ? 'from-green-500/10 to-emerald-500/10 border-green-500/20' 
          : 'from-red-500/10 to-pink-500/10 border-red-500/20'
      } border rounded-xl p-6`}>
        <div className="flex items-center justify-between mb-3">
          <div className={`p-2 ${
            summary.daily_change >= 0 ? 'bg-green-500/20' : 'bg-red-500/20'
          } rounded-lg`}>
            {summary.daily_change >= 0 ? (
              <TrendingUpIcon className="w-6 h-6 text-green-400" />
            ) : (
              <TrendingDownIcon className="w-6 h-6 text-red-400" />
            )}
          </div>
          <span className={`text-xs font-medium uppercase tracking-wide ${
            summary.daily_change >= 0 ? 'text-green-400' : 'text-red-400'
          }`}>
            本日の損益
          </span>
        </div>
        <div className="space-y-1">
          <div className={`text-2xl font-bold ${
            summary.daily_change >= 0 ? 'text-green-400' : 'text-red-400'
          }`}>
            {summary.daily_change >= 0 ? '+' : ''}{formatCurrency(summary.daily_change)}
          </div>
          <div className={`text-sm ${
            summary.daily_change >= 0 ? 'text-green-400' : 'text-red-400'
          }`}>
            {formatPercent(summary.daily_change_percent)}
          </div>
        </div>
      </div>

      {/* トータル損益 */}
      <div className={`bg-gradient-to-br ${
        summary.total_profit_loss >= 0 
          ? 'from-purple-500/10 to-indigo-500/10 border-purple-500/20' 
          : 'from-orange-500/10 to-red-500/10 border-orange-500/20'
      } border rounded-xl p-6`}>
        <div className="flex items-center justify-between mb-3">
          <div className={`p-2 ${
            summary.total_profit_loss >= 0 ? 'bg-purple-500/20' : 'bg-orange-500/20'
          } rounded-lg`}>
            {summary.total_profit_loss >= 0 ? (
              <TrendingUpIcon className="w-6 h-6 text-purple-400" />
            ) : (
              <TrendingDownIcon className="w-6 h-6 text-orange-400" />
            )}
          </div>
          <span className={`text-xs font-medium uppercase tracking-wide ${
            summary.total_profit_loss >= 0 ? 'text-purple-400' : 'text-orange-400'
          }`}>
            トータル損益
          </span>
        </div>
        <div className="space-y-1">
          <div className={`text-2xl font-bold ${
            summary.total_profit_loss >= 0 ? 'text-purple-400' : 'text-orange-400'
          }`}>
            {summary.total_profit_loss >= 0 ? '+' : ''}{formatCurrency(summary.total_profit_loss)}
          </div>
          <div className={`text-sm ${
            summary.total_profit_loss >= 0 ? 'text-purple-400' : 'text-orange-400'
          }`}>
            {formatPercent(summary.total_profit_loss_percent)}
          </div>
        </div>
      </div>

      {/* 年間配当額（予測） */}
      <div className="bg-gradient-to-br from-yellow-500/10 to-amber-500/10 border border-yellow-500/20 rounded-xl p-6">
        <div className="flex items-center justify-between mb-3">
          <div className="p-2 bg-yellow-500/20 rounded-lg">
            <GiftIcon className="w-6 h-6 text-yellow-400" />
          </div>
          <span className="text-xs font-medium text-yellow-400 uppercase tracking-wide">
            年間配当予測
          </span>
        </div>
        <div className="space-y-1">
          <div className="text-2xl font-bold text-text-primary">
            {formatCurrency(summary.annual_dividend_estimate)}
          </div>
          <div className="text-sm text-text-secondary flex items-center">
            <CalendarIcon className="w-4 h-4 mr-1" />
            年間予測額
          </div>
        </div>
      </div>
    </div>
  );
}