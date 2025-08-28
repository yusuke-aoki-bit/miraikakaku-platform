'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Lightbulb, Search, TrendingUp, Star } from 'lucide-react';
import FeaturedThemes from '@/components/themes/FeaturedThemes';
import AllThemes from '@/components/themes/AllThemes';
import { apiClient } from '@/lib/api-client';

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

export default function ThemesPage() {
  const [themes, setThemes] = useState<Theme[]>([]);
  const [featuredThemes, setFeaturedThemes] = useState<Theme[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchThemes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.getThemes();
      
      if (response.success && response.data) {
        const allThemes = response.data;
        setThemes(allThemes);
        setFeaturedThemes(allThemes.filter((theme: Theme) => theme.is_featured));
      } else {
        setThemes([]);
        setFeaturedThemes([]);
      }
    } catch (err) {
      console.error('Failed to fetch themes:', err);
      setThemes([]);
      setFeaturedThemes([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchThemes();
  }, [fetchThemes]);


  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      {/* ページヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Lightbulb className="w-8 h-8 mr-3 text-yellow-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">テーマ別分析</h1>
            <p className="text-sm text-gray-400 mt-1">
              市場で注目される投資テーマと関連銘柄を発見
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-400">
            総テーマ数: <span className="text-white font-medium">{themes.length}</span>
          </div>
          <div className="text-sm text-gray-400">
            注目テーマ: <span className="text-yellow-400 font-medium">{featuredThemes.length}</span>
          </div>
        </div>
      </div>

      {/* 機能説明パネル */}
      <div className="bg-gradient-to-r from-yellow-900/20 to-orange-900/20 border border-yellow-500/30 rounded-xl p-6">
        <div className="flex items-start space-x-4">
          <Lightbulb className="w-6 h-6 text-yellow-400 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">
              テーマ投資の特徴
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-gray-300">
              <div>
                <div className="flex items-center mb-2">
                  <TrendingUp className="w-4 h-4 text-green-400 mr-2" />
                  <span className="font-medium">成長分野発見</span>
                </div>
                <p>AI、再生可能エネルギー、宇宙産業など、将来有望な成長分野を特定し、関連銘柄を体系的に分析</p>
              </div>
              <div>
                <div className="flex items-center mb-2">
                  <Search className="w-4 h-4 text-blue-400 mr-2" />
                  <span className="font-medium">銘柄スクリーニング</span>
                </div>
                <p>テーマ別に厳選された銘柄群から、投資対象を効率的に絞り込み。個別分析では見つけにくい優良株を発見</p>
              </div>
              <div>
                <div className="flex items-center mb-2">
                  <Star className="w-4 h-4 text-yellow-400 mr-2" />
                  <span className="font-medium">トレンド追跡</span>
                </div>
                <p>市場動向とテーマ別パフォーマンスをリアルタイム追跡。タイムリーな投資機会を見逃さない</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 特集テーマセクション */}
      {featuredThemes.length > 0 && (
        <div>
          <div className="flex items-center mb-6">
            <Star className="w-6 h-6 text-yellow-400 mr-2" />
            <h2 className="text-xl font-bold text-white">注目テーマ特集</h2>
            <div className="ml-3 px-2 py-1 bg-yellow-900/30 text-yellow-400 text-xs rounded-full">
              HOT
            </div>
          </div>
          <FeaturedThemes themes={featuredThemes} />
        </div>
      )}

      {/* 全テーマ一覧セクション */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white flex items-center">
            <Search className="w-6 h-6 mr-2 text-blue-400" />
            全テーマ一覧
          </h2>
          <div className="text-sm text-gray-400">
            {themes.length}件のテーマ
          </div>
        </div>
        <AllThemes themes={themes} onThemeUpdate={fetchThemes} />
      </div>

      {/* 投資判断に関する注意事項 */}
      <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-xl p-6">
        <div className="flex items-start space-x-3">
          <Lightbulb className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-yellow-400 mb-2">テーマ投資に関する重要な注意事項</h4>
            <div className="text-sm text-gray-300 space-y-2">
              <p>
                • テーマ投資は成長性の高い分野に投資する手法ですが、市場のトレンドや政策変更により大きく影響される場合があります。
              </p>
              <p>
                • 新興テーマは高いリターンの可能性がある一方、ボラティリティも高く、リスクが伴います。
              </p>
              <p>
                • 投資判断は、テーマの将来性だけでなく、個別銘柄の財務状況や事業内容も総合的に検討してください。
              </p>
              <p>
                • 一つのテーマに集中投資するのではなく、分散投資によるリスク管理を心がけてください。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}