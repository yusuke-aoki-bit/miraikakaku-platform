'use client';

import React from 'react';
import { 
  Star, 
  Users, 
  TrendingUp, 
  TrendingDown, 
  Building2, 
  Target,
  Activity,
  AlertTriangle,
  Calendar,
  Heart,
  HeartOff
} from 'lucide-react';

interface ThemeDetail {
  id: string;
  name: string;
  description: string;
  overview: string;
  detailed_description: string;
  category: string;
  stock_count: number;
  performance_1m: number;
  performance_3m: number;
  performance_1y: number;
  is_featured: boolean;
  is_trending: boolean;
  background_image?: string;
  follow_count: number;
  market_cap_total: number;
  top_stocks: string[];
  risk_level: 'Low' | 'Medium' | 'High';
  growth_stage: 'Early' | 'Growth' | 'Mature';
  created_at: string;
  updated_at: string;
}

interface ThemeHeaderProps {
  theme: ThemeDetail;
  isFollowing: boolean;
  onFollowToggle: () => void;
}

export default function ThemeHeader({ theme, isFollowing, onFollowToggle }: ThemeHeaderProps) {
  const formatPerformance = (performance: number) => {
    const sign = performance >= 0 ? '+' : '';
    return `${sign}${performance.toFixed(1)}%`;
  };

  const getPerformanceColor = (performance: number) => {
    return performance >= 0 ? 'text-green-400' : 'text-red-400';
  };

  const getRiskLevelColor = (risk: string) => {
    switch (risk) {
      case 'Low': return 'text-green-400 bg-green-900/20';
      case 'Medium': return 'text-yellow-400 bg-yellow-900/20';
      case 'High': return 'text-red-400 bg-red-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getGrowthStageColor = (stage: string) => {
    switch (stage) {
      case 'Early': return 'text-purple-400 bg-purple-900/20';
      case 'Growth': return 'text-blue-400 bg-blue-900/20';
      case 'Mature': return 'text-gray-400 bg-gray-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getRiskLevelLabel = (risk: string) => {
    switch (risk) {
      case 'Low': return '低リスク';
      case 'Medium': return '中リスク';
      case 'High': return '高リスク';
      default: return risk;
    }
  };

  const getGrowthStageLabel = (stage: string) => {
    switch (stage) {
      case 'Early': return '初期成長';
      case 'Growth': return '成長期';
      case 'Mature': return '成熟期';
      default: return stage;
    }
  };

  const formatMarketCap = (value: number) => {
    if (value >= 1000000000000) {
      return `${(value / 1000000000000).toFixed(1)}兆円`;
    } else if (value >= 100000000) {
      return `${(value / 100000000).toFixed(0)}億円`;
    } else {
      return `${value.toLocaleString()}円`;
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-gray-700/50 rounded-xl p-8">
      {/* 上部: タイトルエリア */}
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6 mb-8">
        {/* 左側: テーマ情報 */}
        <div className="flex-1">
          <div className="flex items-center space-x-4 mb-4">
            <h1 className="text-3xl font-bold text-white">{theme.name}</h1>
            
            {/* バッジ群 */}
            <div className="flex items-center space-x-2">
              {theme.is_featured && (
                <div className="flex items-center space-x-1 px-3 py-1 bg-yellow-900/30 text-yellow-400 rounded-full text-sm">
                  <Star className="w-4 h-4" />
                  <span>注目</span>
                </div>
              )}
              
              {theme.is_trending && (
                <div className="flex items-center space-x-1 px-3 py-1 bg-orange-900/30 text-orange-400 rounded-full text-sm">
                  <TrendingUp className="w-4 h-4" />
                  <span>トレンド</span>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <p className="text-lg text-gray-300 leading-relaxed">
              {theme.description}
            </p>
            
            <p className="text-gray-400 leading-relaxed">
              {theme.detailed_description}
            </p>
          </div>
        </div>

        {/* 右側: アクションエリア */}
        <div className="flex flex-col items-end space-y-4">
          {/* フォローボタン */}
          <button
            onClick={onFollowToggle}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
              isFollowing
                ? 'bg-pink-600/20 text-pink-400 hover:bg-pink-600/30 border border-pink-500/30'
                : 'bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 border border-purple-500/30'
            }`}
          >
            {isFollowing ? (
              <>
                <Heart className="w-5 h-5 fill-current" />
                <span>フォロー中</span>
              </>
            ) : (
              <>
                <HeartOff className="w-5 h-5" />
                <span>フォローする</span>
              </>
            )}
          </button>

          {/* フォロワー数 */}
          <div className="flex items-center space-x-2 text-blue-400">
            <Users className="w-4 h-4" />
            <span className="font-medium">{theme.follow_count.toLocaleString()}人がフォロー</span>
          </div>
        </div>
      </div>

      {/* 下部: 統計エリア */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* パフォーマンス */}
        <div className="bg-gray-800/30 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">1ヶ月リターン</span>
            {theme.performance_1m >= 0 ? (
              <TrendingUp className="w-4 h-4 text-green-400" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-400" />
            )}
          </div>
          <div className={`text-2xl font-bold ${getPerformanceColor(theme.performance_1m)}`}>
            {formatPerformance(theme.performance_1m)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            3ヶ月: {formatPerformance(theme.performance_3m)} | 1年: {formatPerformance(theme.performance_1y)}
          </div>
        </div>

        {/* 関連銘柄・時価総額 */}
        <div className="bg-gray-800/30 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">関連銘柄</span>
            <Building2 className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {theme.stock_count}銘柄
          </div>
          <div className="text-xs text-gray-500 mt-1">
            総時価総額: {formatMarketCap(theme.market_cap_total)}
          </div>
        </div>

        {/* リスクレベル */}
        <div className="bg-gray-800/30 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">リスクレベル</span>
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
          </div>
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRiskLevelColor(theme.risk_level)}`}>
            {getRiskLevelLabel(theme.risk_level)}
          </div>
          <div className="text-xs text-gray-500 mt-2">
            成長段階: <span className={`px-2 py-1 rounded-full text-xs ${getGrowthStageColor(theme.growth_stage)}`}>
              {getGrowthStageLabel(theme.growth_stage)}
            </span>
          </div>
        </div>

        {/* その他情報 */}
        <div className="bg-gray-800/30 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">カテゴリ</span>
            <Target className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-lg font-bold text-white mb-1">
            {theme.category}
          </div>
          <div className="flex items-center text-xs text-gray-500">
            <Calendar className="w-3 h-3 mr-1" />
            <span>更新: {new Date(theme.updated_at).toLocaleDateString('ja-JP')}</span>
          </div>
        </div>
      </div>

      {/* 主要銘柄プレビュー */}
      {theme.top_stocks && theme.top_stocks.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-700/50">
          <h3 className="text-sm text-gray-400 mb-3">主要構成銘柄</h3>
          <div className="flex flex-wrap gap-2">
            {theme.top_stocks.slice(0, 6).map((stock, index) => (
              <span 
                key={index}
                className="px-3 py-1 bg-blue-900/20 text-blue-400 rounded-full text-sm font-medium border border-blue-500/30"
              >
                {stock}
              </span>
            ))}
            {theme.top_stocks.length > 6 && (
              <span className="px-3 py-1 bg-gray-700/30 text-gray-400 rounded-full text-sm">
                +{theme.top_stocks.length - 6}銘柄
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}