'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { TrendingUp, TrendingDown, Users, Calendar, ArrowRight } from 'lucide-react';

interface Theme {
  id: string;
  name: string;
  description: string;
  overview: string;
  category: string;
  stock_count: number;
  performance_1m: number;
  performance_3m: number;
  performance_1y: number;
  is_featured: boolean;
  is_trending: boolean;
  background_image?: string;
  follow_count: number;
  created_at: string;
  updated_at: string;
}

interface FeaturedThemesProps {
  themes: Theme[];
}

interface ThemeCardProps {
  theme: Theme;
  onClick: (themeId: string) => void;
}

function ThemeCard({ theme, onClick }: ThemeCardProps) {
  const formatPerformance = (performance: number) => {
    const sign = performance >= 0 ? '+' : '';
    return `${sign}${performance.toFixed(1)}%`;
  };

  const getPerformanceColor = (performance: number) => {
    return performance >= 0 ? 'text-green-400' : 'text-red-400';
  };

  const getPerformanceIcon = (performance: number) => {
    return performance >= 0 ? TrendingUp : TrendingDown;
  };

  const PerformanceIcon = getPerformanceIcon(theme.performance_1m);

  return (
    <div 
      onClick={() => onClick(theme.id)}
      className="group relative bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-gray-700/50 rounded-xl overflow-hidden cursor-pointer transition-all duration-300 hover:border-purple-500/50 hover:shadow-xl hover:scale-105"
    >
      {/* 背景画像オーバーレイ */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 to-blue-900/20 opacity-70"></div>
      
      {/* トレンディングバッジ */}
      {theme.is_trending && (
        <div className="absolute top-4 right-4 z-10">
          <div className="flex items-center space-x-1 px-2 py-1 bg-orange-500/90 text-white text-xs rounded-full">
            <TrendingUp className="w-3 h-3" />
            <span>トレンド</span>
          </div>
        </div>
      )}

      <div className="relative p-6 h-full flex flex-col">
        {/* カテゴリー */}
        <div className="mb-3">
          <span className="inline-block px-2 py-1 bg-gray-700/50 text-gray-300 text-xs rounded-full">
            {theme.category}
          </span>
        </div>

        {/* テーマ名 */}
        <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-purple-300 transition-colors">
          {theme.name}
        </h3>

        {/* 説明文 */}
        <p className="text-gray-300 text-sm leading-relaxed mb-4 flex-grow">
          {theme.description}
        </p>

        {/* 統計情報 */}
        <div className="space-y-3 mb-4">
          {/* パフォーマンス */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">直近1ヶ月のリターン</span>
            <div className={`flex items-center space-x-1 font-bold ${getPerformanceColor(theme.performance_1m)}`}>
              <PerformanceIcon className="w-4 h-4" />
              <span>{formatPerformance(theme.performance_1m)}</span>
            </div>
          </div>

          {/* 関連銘柄数 */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">関連銘柄数</span>
            <span className="text-white font-medium">{theme.stock_count}銘柄</span>
          </div>

          {/* フォロワー数 */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">フォロワー</span>
            <div className="flex items-center space-x-1 text-blue-400">
              <Users className="w-3 h-3" />
              <span className="font-medium">{theme.follow_count.toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* アクションエリア */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-700/50">
          <div className="flex items-center space-x-2 text-xs text-gray-500">
            <Calendar className="w-3 h-3" />
            <span>更新: {new Date(theme.updated_at).toLocaleDateString('ja-JP')}</span>
          </div>
          
          <div className="flex items-center space-x-1 text-purple-400 text-sm font-medium group-hover:text-purple-300 transition-colors">
            <span>詳細を見る</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>
      </div>

      {/* ホバーエフェクト */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-blue-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
    </div>
  );
}

export default function FeaturedThemes({ themes }: FeaturedThemesProps) {
  const router = useRouter();

  const handleThemeClick = (themeId: string) => {
    router.push(`/themes/${themeId}`);
  };

  if (!themes || themes.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 mb-2">特集テーマがありません</div>
        <div className="text-sm text-gray-500">しばらく後にもう一度確認してください</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      {themes.map((theme) => (
        <ThemeCard 
          key={theme.id} 
          theme={theme} 
          onClick={handleThemeClick}
        />
      ))}
    </div>
  );
}