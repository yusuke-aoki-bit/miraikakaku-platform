'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Search, 
  Filter, 
  TrendingUp, 
  TrendingDown, 
  Star, 
  Users, 
  ArrowRight,
  ChevronDown,
  Heart,
  HeartOff
} from 'lucide-react';

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

interface AllThemesProps {
  themes: Theme[];
  onThemeUpdate?: () => void;
}

type SortOption = 'popular' | 'performance' | 'newest' | 'name';

interface ThemeListItemProps {
  theme: Theme;
  isFollowing: boolean;
  onThemeClick: (themeId: string) => void;
  onFollowToggle: (themeId: string) => void;
}

function ThemeListItem({ theme, isFollowing, onThemeClick, onFollowToggle }: ThemeListItemProps) {
  const formatPerformance = (performance: number) => {
    const sign = performance >= 0 ? '+' : '';
    return `${sign}${performance.toFixed(1)}%`;
  };

  const getPerformanceColor = (performance: number) => {
    return performance >= 0 ? 'text-green-400' : 'text-red-400';
  };

  const PerformanceIcon = theme.performance_1m >= 0 ? TrendingUp : TrendingDown;

  return (
    <div className="group bg-gray-900/50 border border-gray-800/50 rounded-lg p-4 hover:border-purple-500/30 hover:bg-gray-900/70 transition-all">
      <div className="flex items-start justify-between">
        {/* 左側: テーマ情報 */}
        <div className="flex-1 cursor-pointer" onClick={() => onThemeClick(theme.id)}>
          <div className="flex items-center space-x-3 mb-2">
            <h3 className="text-lg font-semibold text-white group-hover:text-purple-300 transition-colors">
              {theme.name}
            </h3>
            
            {/* バッジ群 */}
            <div className="flex items-center space-x-2">
              {theme.is_featured && (
                <div className="flex items-center space-x-1 px-2 py-1 bg-yellow-900/30 text-yellow-400 text-xs rounded-full">
                  <Star className="w-3 h-3" />
                  <span>注目</span>
                </div>
              )}
              
              {theme.is_trending && (
                <div className="flex items-center space-x-1 px-2 py-1 bg-orange-900/30 text-orange-400 text-xs rounded-full">
                  <TrendingUp className="w-3 h-3" />
                  <span>トレンド</span>
                </div>
              )}
            </div>
          </div>

          <p className="text-sm text-gray-400 mb-3 leading-relaxed">
            {theme.description}
          </p>

          <div className="flex items-center space-x-6 text-sm">
            {/* カテゴリ */}
            <div className="text-gray-500">
              <span className="text-gray-400">カテゴリ:</span> {theme.category}
            </div>

            {/* 関連銘柄数 */}
            <div className="text-gray-300">
              <span className="text-gray-400">銘柄数:</span> <span className="font-medium">{theme.stock_count}</span>
            </div>

            {/* フォロワー数 */}
            <div className="flex items-center space-x-1 text-blue-400">
              <Users className="w-3 h-3" />
              <span className="font-medium">{theme.follow_count.toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* 右側: パフォーマンスとアクション */}
        <div className="flex items-center space-x-4 ml-4">
          {/* パフォーマンス */}
          <div className="text-right">
            <div className="text-xs text-gray-500 mb-1">直近1ヶ月</div>
            <div className={`flex items-center space-x-1 font-bold ${getPerformanceColor(theme.performance_1m)}`}>
              <PerformanceIcon className="w-4 h-4" />
              <span className="text-lg">{formatPerformance(theme.performance_1m)}</span>
            </div>
          </div>

          {/* フォローボタン */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onFollowToggle(theme.id);
            }}
            className={`flex items-center space-x-1 px-3 py-2 rounded-lg transition-colors ${
              isFollowing
                ? 'bg-pink-600/20 text-pink-400 hover:bg-pink-600/30'
                : 'bg-gray-700/50 text-gray-300 hover:bg-gray-700/70'
            }`}
            title={isFollowing ? 'フォロー中' : 'フォローする'}
          >
            {isFollowing ? (
              <Heart className="w-4 h-4 fill-current" />
            ) : (
              <HeartOff className="w-4 h-4" />
            )}
          </button>

          {/* 詳細リンク */}
          <button
            onClick={() => onThemeClick(theme.id)}
            className="flex items-center space-x-1 text-purple-400 hover:text-purple-300 transition-colors"
          >
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default function AllThemes({ themes, onThemeUpdate }: AllThemesProps) {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('popular');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [followingThemes, setFollowingThemes] = useState<Set<string>>(new Set());

  // カテゴリ一覧を抽出
  const categories = useMemo(() => {
    const categorySet = new Set(themes.map(theme => theme.category));
    return ['all', ...Array.from(categorySet)];
  }, [themes]);

  // フィルタリング・ソート済みのテーマリスト
  const filteredAndSortedThemes = useMemo(() => {
    let filtered = themes;

    // 検索フィルタ
    if (searchQuery) {
      filtered = filtered.filter(theme =>
        theme.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        theme.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        theme.category.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // カテゴリフィルタ
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(theme => theme.category === selectedCategory);
    }

    // ソート
    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'popular':
          return b.follow_count - a.follow_count;
        case 'performance':
          return b.performance_1m - a.performance_1m;
        case 'newest':
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
        case 'name':
          return a.name.localeCompare(b.name, 'ja');
        default:
          return 0;
      }
    });
  }, [themes, searchQuery, selectedCategory, sortBy]);

  const handleThemeClick = (themeId: string) => {
    router.push(`/themes/${themeId}`);
  };

  const handleFollowToggle = (themeId: string) => {
    const newFollowing = new Set(followingThemes);
    if (newFollowing.has(themeId)) {
      newFollowing.delete(themeId);
    } else {
      newFollowing.add(themeId);
    }
    setFollowingThemes(newFollowing);
    
    // TODO: API call to update follow status
    console.log('Toggle follow for theme:', themeId);
  };

  const getSortLabel = (option: SortOption) => {
    switch (option) {
      case 'popular': return '人気順';
      case 'performance': return 'パフォーマンス順';
      case 'newest': return '更新順';
      case 'name': return '名前順';
      default: return option;
    }
  };

  const getCategoryLabel = (category: string) => {
    return category === 'all' ? '全カテゴリ' : category;
  };

  return (
    <div className="space-y-6">
      {/* コントロールエリア */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* 検索バー */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="テーマ名やキーワードで検索..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500/50 transition-colors"
          />
        </div>

        {/* フィルタ・ソートエリア */}
        <div className="flex items-center space-x-4">
          {/* カテゴリフィルタ */}
          <div className="relative">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="appearance-none bg-gray-800/50 border border-gray-700/50 rounded-lg px-4 py-2 pr-8 text-white text-sm focus:outline-none focus:border-purple-500/50 transition-colors cursor-pointer"
            >
              {categories.map((category) => (
                <option key={category} value={category} className="bg-gray-800">
                  {getCategoryLabel(category)}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>

          {/* ソート */}
          <div className="relative">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="appearance-none bg-gray-800/50 border border-gray-700/50 rounded-lg px-4 py-2 pr-8 text-white text-sm focus:outline-none focus:border-purple-500/50 transition-colors cursor-pointer"
            >
              {(['popular', 'performance', 'newest', 'name'] as SortOption[]).map((option) => (
                <option key={option} value={option} className="bg-gray-800">
                  {getSortLabel(option)}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
        </div>
      </div>

      {/* 結果統計 */}
      <div className="flex items-center justify-between text-sm text-gray-400">
        <div>
          {filteredAndSortedThemes.length}件のテーマ
          {searchQuery && ` (「${searchQuery}」で検索)`}
          {selectedCategory !== 'all' && ` (${getCategoryLabel(selectedCategory)}カテゴリ)`}
        </div>
        <div>
          {getSortLabel(sortBy)}で表示
        </div>
      </div>

      {/* テーマリスト */}
      <div className="space-y-4">
        {filteredAndSortedThemes.length > 0 ? (
          filteredAndSortedThemes.map((theme) => (
            <ThemeListItem
              key={theme.id}
              theme={theme}
              isFollowing={followingThemes.has(theme.id)}
              onThemeClick={handleThemeClick}
              onFollowToggle={handleFollowToggle}
            />
          ))
        ) : (
          <div className="text-center py-12">
            <Filter className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-400 mb-2">
              条件に合うテーマが見つかりません
            </h3>
            <p className="text-gray-500 text-sm">
              検索条件やフィルタを変更してお試しください
            </p>
          </div>
        )}
      </div>
    </div>
  );
}