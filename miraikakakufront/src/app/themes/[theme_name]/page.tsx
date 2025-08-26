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
        // Generate mock data for development
        generateMockThemeData();
      }
    } catch (err) {
      console.error('Failed to fetch theme details:', err);
      generateMockThemeData();
    } finally {
      setLoading(false);
    }
  }, [themeId]);

  useEffect(() => {
    if (themeId) {
      fetchThemeDetails();
    }
  }, [themeId, fetchThemeDetails]);

  const generateMockThemeData = () => {
    // Create mock theme based on theme ID
    const mockThemes: Record<string, Partial<ThemeDetail>> = {
      'next-gen-semiconductors': {
        id: 'next-gen-semiconductors',
        name: '次世代半導体',
        description: 'AIの進化を支える、演算能力の飛躍的向上に関連する企業群',
        overview: 'AI、自動運転、IoTの普及により半導体需要が急成長。特に高性能チップ、メモリ技術、製造装置メーカーに注目',
        detailed_description: '次世代半導体テーマは、AI処理に特化したGPU、高効率メモリ（HBM）、先端プロセス技術（3nm以下）、パッケージング技術、製造装置などを含む包括的な投資テーマです。データセンターの拡張、エッジAI、自動運転車の普及により、従来の半導体を大幅に上回る性能が求められています。',
        category: 'Technology',
        risk_level: 'High' as const,
        growth_stage: 'Growth' as const
      },
      'renewable-energy': {
        id: 'renewable-energy',
        name: '再生可能エネルギー',
        description: '脱炭素社会実現に向けた、次世代エネルギー関連企業',
        overview: '太陽光、風力、水素などの再生可能エネルギー技術とインフラ企業群。政府政策による後押しも強い',
        detailed_description: '再生可能エネルギーテーマは、太陽光発電、風力発電、水素エネルギー、蓄電池技術、スマートグリッド、エネルギー管理システムなどを含む総合的なエネルギー転換投資テーマです。世界的な脱炭素政策により長期的な成長が期待されています。',
        category: 'Energy',
        risk_level: 'Medium' as const,
        growth_stage: 'Growth' as const
      }
    };

    const baseTheme = mockThemes[themeId] || mockThemes['next-gen-semiconductors'];
    
    const mockTheme: ThemeDetail = {
      ...baseTheme,
      stock_count: 42,
      performance_1m: 8.5,
      performance_3m: 15.2,
      performance_1y: 45.8,
      is_featured: true,
      is_trending: true,
      follow_count: 1247,
      market_cap_total: 2500000000000, // 2.5兆円
      top_stocks: ['NVDA', '7203', 'TSMC', 'ASML'],
      created_at: '2024-01-15',
      updated_at: '2024-02-20'
    } as ThemeDetail;

    const mockStocks: Stock[] = [
      {
        symbol: 'NVDA',
        company_name: 'NVIDIA Corporation',
        current_price: 875.25,
        change_percent: 3.4,
        market_cap: 2100000000000,
        ai_score: 95,
        theme_weight: 15.2
      },
      {
        symbol: '7203',
        company_name: 'トヨタ自動車',
        current_price: 2845,
        change_percent: 1.8,
        market_cap: 45000000000000,
        ai_score: 78,
        theme_weight: 8.7
      },
      {
        symbol: 'TSMC',
        company_name: 'Taiwan Semiconductor',
        current_price: 142.50,
        change_percent: 2.1,
        market_cap: 740000000000,
        ai_score: 92,
        theme_weight: 12.4
      }
    ];

    const mockPerformanceData: PerformanceData[] = [];
    const baseDate = new Date();
    for (let i = 30; i >= 0; i--) {
      const date = new Date(baseDate);
      date.setDate(date.getDate() - i);
      
      const themeReturn = 1 + (Math.random() - 0.4) * 0.02; // Slight upward bias
      const marketReturn = 1 + (Math.random() - 0.5) * 0.015;
      
      mockPerformanceData.push({
        date: date.toISOString().split('T')[0],
        theme_index: 100 * Math.pow(themeReturn, 30 - i),
        market_index: 100 * Math.pow(marketReturn, 30 - i),
        outperformance: 0
      });
    }

    // Calculate outperformance
    mockPerformanceData.forEach((item, index) => {
      item.outperformance = item.theme_index - item.market_index;
    });

    setTheme(mockTheme);
    setStocks(mockStocks);
    setPerformanceData(mockPerformanceData);
  };

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