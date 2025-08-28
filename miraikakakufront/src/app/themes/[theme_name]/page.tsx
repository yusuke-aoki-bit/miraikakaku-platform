'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Lightbulb } from 'lucide-react';
import ThemeHeader from '@/components/themes/ThemeHeader';
import ThemePerformanceChart from '@/components/themes/ThemePerformanceChart';
import ThemeStockTable from '@/components/themes/ThemeStockTable';
import ThemeInsightsPanel from '@/components/themes/ThemeInsightsPanel';
import { apiClient } from '@/lib/api-client';

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

interface Stock {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  market_cap: number;
  ai_score: number;
  theme_weight: number;
}

interface PerformanceData {
  date: string;
  theme_index: number;
  market_index: number;
  outperformance: number;
}

export default function ThemeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const themeId = params.theme_name as string;

  const [theme, setTheme] = useState<ThemeDetail | null>(null);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFollowing, setIsFollowing] = useState(false);

  const fetchThemeDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.getThemeDetails(themeId);
      
      if (response.success && response.data) {
        setTheme(response.data.theme);
        setStocks(response.data.stocks);
        setPerformanceData(response.data.performance_data);
        setIsFollowing(response.data.is_following || false);
      } else {
        setError('テーマデータが見つかりませんでした');
      }
    } catch (err) {
      console.error('Failed to fetch theme details:', err);
      setError('テーマデータの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  }, [themeId]);

  useEffect(() => {
    if (themeId) {
      fetchThemeDetails();
    }
  }, [themeId, fetchThemeDetails]);


  const handleFollowToggle = async () => {
    try {
      // TODO: API call to toggle follow status
      setIsFollowing(!isFollowing);
      
      if (theme) {
        setTheme({
          ...theme,
          follow_count: theme.follow_count + (isFollowing ? -1 : 1)
        });
      }
    } catch (error) {
      console.error('Failed to toggle follow status:', error);
    }
  };

  const handleBackToThemes = () => {
    router.push('/themes');
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

  if (error || !theme) {
    return (
      <div className="p-6 space-y-6">
        <button
          onClick={handleBackToThemes}
          className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>テーマ一覧に戻る</span>
        </button>
        
        <div className="text-center py-20">
          <Lightbulb className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-400 mb-3">
            テーマが見つかりません
          </h3>
          <p className="text-gray-500 max-w-md mx-auto leading-relaxed">
            指定されたテーマは存在しないか、<br />
            一時的にアクセスできません。
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 戻るボタン */}
      <button
        onClick={handleBackToThemes}
        className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>テーマ一覧に戻る</span>
      </button>

      {/* テーマヘッダー */}
      <ThemeHeader 
        theme={theme} 
        isFollowing={isFollowing}
        onFollowToggle={handleFollowToggle}
      />

      {/* パフォーマンスチャート */}
      <ThemePerformanceChart 
        theme={theme}
        performanceData={performanceData}
      />

      {/* 2カラムレイアウト: 関連銘柄テーブル & インサイトパネル */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* 関連銘柄テーブル */}
        <div className="xl:col-span-2">
          <ThemeStockTable 
            theme={theme}
            stocks={stocks}
          />
        </div>

        {/* インサイトパネル */}
        <div className="xl:col-span-1">
          <ThemeInsightsPanel 
            theme={theme}
          />
        </div>
      </div>

      {/* 投資判断に関する注意事項 */}
      <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-xl p-6">
        <div className="flex items-start space-x-3">
          <Lightbulb className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-yellow-400 mb-2">テーマ投資に関する重要な注意事項</h4>
            <div className="text-sm text-gray-300 space-y-2">
              <p>
                • テーマ投資は特定の成長分野に焦点を当てた投資手法ですが、市場環境や技術変化により大きく影響される可能性があります。
              </p>
              <p>
                • 新興テーマは高い成長ポテンシャルがある一方、ボラティリティも高く、投資リスクが伴います。
              </p>
              <p>
                • 各銘柄の財務状況、事業内容、競合環境なども個別に分析し、総合的に投資判断を行ってください。
              </p>
              <p>
                • 一つのテーマに集中せず、複数のテーマや資産クラスに分散投資することを強く推奨します。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}