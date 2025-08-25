'use client';

import React, { useState, useEffect } from 'react';
import { Lightbulb, Search, Filter, TrendingUp, Star } from 'lucide-react';
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

  useEffect(() => {
    fetchThemes();
  }, []);

  const fetchThemes = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.getThemes();
      
      if (response.success && response.data) {
        const allThemes = response.data;
        setThemes(allThemes);
        setFeaturedThemes(allThemes.filter((theme: Theme) => theme.is_featured));
      } else {
        // Generate mock data for development
        generateMockThemes();
      }
    } catch (err) {
      console.error('Failed to fetch themes:', err);
      generateMockThemes();
    } finally {
      setLoading(false);
    }
  };

  const generateMockThemes = () => {
    const mockThemes: Theme[] = [
      {
        id: 'next-gen-semiconductors',
        name: '次世代半導体',
        description: 'AIの進化を支える、演算能力の飛躍的向上に関連する企業群',
        overview: 'AI、自動運転、IoTの普及により半導体需要が急成長。特に高性能チップ、メモリ技術、製造装置メーカーに注目',
        category: 'Technology',
        stock_count: 42,
        performance_1m: 8.5,
        performance_3m: 15.2,
        performance_1y: 45.8,
        is_featured: true,
        is_trending: true,
        background_image: '/themes/semiconductors.jpg',
        follow_count: 1247,
        created_at: '2024-01-15',
        updated_at: '2024-02-20'
      },
      {
        id: 'renewable-energy',
        name: '再生可能エネルギー',
        description: '脱炭素社会実現に向けた、次世代エネルギー関連企業',
        overview: '太陽光、風力、水素などの再生可能エネルギー技術とインフラ企業群。政府政策による後押しも強い',
        category: 'Energy',
        stock_count: 38,
        performance_1m: 12.3,
        performance_3m: 8.7,
        performance_1y: 28.9,
        is_featured: true,
        is_trending: true,
        background_image: '/themes/renewable-energy.jpg',
        follow_count: 982,
        created_at: '2024-01-20',
        updated_at: '2024-02-18'
      },
      {
        id: 'digital-transformation',
        name: 'デジタル変革',
        description: '企業のDX推進を支援するソフトウェア・サービス企業群',
        overview: 'クラウド、AI、IoT、ビッグデータ解析など、企業のデジタル化を支える技術・サービス提供企業',
        category: 'Technology',
        stock_count: 55,
        performance_1m: 6.8,
        performance_3m: 11.4,
        performance_1y: 32.1,
        is_featured: true,
        is_trending: false,
        background_image: '/themes/digital-transformation.jpg',
        follow_count: 1156,
        created_at: '2024-01-10',
        updated_at: '2024-02-15'
      },
      {
        id: 'healthcare-innovation',
        name: 'ヘルスケア・イノベーション',
        description: '医療技術革新と高齢化社会対応企業群',
        overview: 'バイオテクノロジー、医療機器、デジタルヘルス、創薬支援など次世代医療技術企業',
        category: 'Healthcare',
        stock_count: 29,
        performance_1m: 4.2,
        performance_3m: 9.8,
        performance_1y: 18.6,
        is_featured: false,
        is_trending: true,
        follow_count: 734,
        created_at: '2024-01-25',
        updated_at: '2024-02-12'
      },
      {
        id: 'fintech',
        name: 'フィンテック',
        description: '金融業界のデジタル革命を推進する企業群',
        overview: 'デジタル決済、ブロックチェーン、暗号資産、オンライン証券・保険など金融×技術企業',
        category: 'Financial Services',
        stock_count: 33,
        performance_1m: 7.9,
        performance_3m: 13.5,
        performance_1y: 25.4,
        is_featured: false,
        is_trending: false,
        follow_count: 891,
        created_at: '2024-01-18',
        updated_at: '2024-02-10'
      },
      {
        id: 'space-economy',
        name: '宇宙産業',
        description: '商業宇宙開発と衛星サービス関連企業群',
        overview: '衛星打ち上げ、宇宙旅行、衛星通信・観測、宇宙資源開発など新興宇宙産業',
        category: 'Aerospace',
        stock_count: 18,
        performance_1m: 15.7,
        performance_3m: 22.1,
        performance_1y: 67.3,
        is_featured: false,
        is_trending: true,
        follow_count: 542,
        created_at: '2024-02-01',
        updated_at: '2024-02-19'
      }
    ];

    setThemes(mockThemes);
    setFeaturedThemes(mockThemes.filter(theme => theme.is_featured));
  };

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