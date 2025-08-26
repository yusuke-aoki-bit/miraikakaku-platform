'use client';

import React, { useState, useEffect } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';
import { 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Lightbulb,
  Calendar,
  BarChart3
} from 'lucide-react';
import apiClient from '@/lib/api-client';
import BookRecommendationSection from '@/components/books/BookRecommendationSection';
import { getBooksForSector } from '@/data/bookRecommendations';
import { BookSection } from '@/types/books';

interface SectorDetailsProps {
  sectorId: string | null;
  sectorName: string | null;
  timeframe: 'daily' | 'weekly' | 'monthly';
}

interface PerformanceData {
  date: string;
  value: number;
  change: number;
}

interface AISectorOutlook {
  ai_outlook: string;
  confidence_score: number;
  key_drivers: string[];
  risk_factors: string[];
}

interface HistoricalPerformance {
  performance_data: PerformanceData[];
  summary: {
    total_return: number;
    volatility: number;
    sharpe_ratio: number;
  };
}

export default function SectorDetails({ sectorId, sectorName, timeframe }: SectorDetailsProps) {
  const [historicalData, setHistoricalData] = useState<HistoricalPerformance | null>(null);
  const [aiOutlook, setAiOutlook] = useState<AISectorOutlook | null>(null);
  const [loading, setLoading] = useState(false);
  const [chartPeriod, setChartPeriod] = useState<'1M' | '6M' | '1Y'>('6M');

  useEffect(() => {
    if (sectorId) {
      fetchSectorDetails();
    }
  }, [sectorId, chartPeriod]);

  const fetchSectorDetails = async () => {
    if (!sectorId) return;
    
    setLoading(true);
    try {
      const [historicalResponse, outlookResponse] = await Promise.all([
        apiClient.getSectorHistoricalPerformance(sectorId, chartPeriod),
        apiClient.getAISectorOutlook(sectorId)
      ]);

      if (historicalResponse.success) {
        setHistoricalData(historicalResponse.data as any);
      }

      if (outlookResponse.success) {
        setAiOutlook(outlookResponse.data as any);
      }
    } catch (error) {
      console.error('Failed to fetch sector details:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    return (
      <div className="bg-black/90 border border-gray-600 rounded-lg p-3">
        <div className="text-gray-300 text-sm mb-1">{formatDate(label)}</div>
        <div className="text-white font-medium">
          インデックス値: {data.value.toFixed(2)}
        </div>
        <div className={`text-sm ${data.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          変動: {formatPercentage(data.change)}
        </div>
      </div>
    );
  };

  if (!sectorId) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-8">
        <div className="text-center">
          <BarChart3 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-400 mb-2">
            セクターを選択してください
          </h3>
          <p className="text-gray-500 text-sm">
            上のヒートマップからセクターをクリックして詳細情報を表示
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* セクター基本情報 */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white flex items-center">
            <BarChart3 className="w-6 h-6 mr-2 text-blue-400" />
            {sectorName}
          </h2>
          
          {historicalData && (
            <div className="flex items-center space-x-4 text-sm">
              <div className={`font-medium ${
                historicalData.summary.total_return >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {formatPercentage(historicalData.summary.total_return)}
              </div>
              <div className="text-gray-400">
                | ボラティリティ: {historicalData.summary.volatility.toFixed(1)}%
              </div>
              <div className="text-gray-400">
                | シャープ比: {historicalData.summary.sharpe_ratio.toFixed(2)}
              </div>
            </div>
          )}
        </div>

        {/* パフォーマンスチャート */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-md font-semibold text-white">パフォーマンス推移</h3>
            
            {/* 期間選択 */}
            <div className="flex items-center bg-gray-800/50 rounded-lg p-1">
              {(['1M', '6M', '1Y'] as const).map((period) => (
                <button
                  key={period}
                  onClick={() => setChartPeriod(period)}
                  className={`px-3 py-1 rounded-md text-sm transition-all ${
                    chartPeriod === period
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                  }`}
                >
                  {period}
                </button>
              ))}
            </div>
          </div>

          {loading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-400"></div>
            </div>
          ) : historicalData ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={historicalData.performance_data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                    stroke="#9CA3AF"
                    fontSize={12}
                  />
                  <YAxis 
                    stroke="#9CA3AF"
                    fontSize={12}
                    domain={['dataMin - 5', 'dataMax + 5']}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#3b82f6"
                    fill="url(#colorGradient)"
                    strokeWidth={2}
                  />
                  <defs>
                    <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-400">
              データを読み込めませんでした
            </div>
          )}
        </div>
      </div>

      {/* AI見通し */}
      {aiOutlook && (
        <div className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center">
              <Brain className="w-5 h-5 mr-2 text-purple-400" />
              AI セクター分析
            </h3>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-400">信頼度:</span>
              <span className="text-purple-400 font-medium">
                {aiOutlook.confidence_score.toFixed(0)}%
              </span>
            </div>
          </div>

          <div className="bg-black/30 rounded-lg p-4 mb-4">
            <p className="text-gray-200 leading-relaxed">
              {aiOutlook.ai_outlook}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 成長要因 */}
            <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
              <h4 className="text-green-400 font-medium mb-3 flex items-center">
                <TrendingUp className="w-4 h-4 mr-2" />
                主要な成長要因
              </h4>
              <ul className="space-y-2">
                {aiOutlook.key_drivers.map((driver, index) => (
                  <li key={index} className="text-gray-300 text-sm flex items-center">
                    <Lightbulb className="w-3 h-3 mr-2 text-green-400 flex-shrink-0" />
                    {driver}
                  </li>
                ))}
              </ul>
            </div>

            {/* リスク要因 */}
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
              <h4 className="text-red-400 font-medium mb-3 flex items-center">
                <AlertTriangle className="w-4 h-4 mr-2" />
                主要なリスク
              </h4>
              <ul className="space-y-2">
                {aiOutlook.risk_factors.map((risk, index) => (
                  <li key={index} className="text-gray-300 text-sm flex items-center">
                    <AlertTriangle className="w-3 h-3 mr-2 text-red-400 flex-shrink-0" />
                    {risk}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* セクター関連書籍推薦セクション */}
      {sectorName && (() => {
        const relatedBooks = getBooksForSector(sectorName, 3);
        if (relatedBooks.length > 0) {
          const bookSection: BookSection = {
            title: `${sectorName}セクター関連書籍`,
            subtitle: 'セクター理解を深める専門書をご紹介します',
            books: relatedBooks,
            displayType: 'grid',
            maxDisplay: 3
          };
          
          return (
            <BookRecommendationSection
              section={bookSection}
              contextTitle={`${sectorName}セクター分析`}
            />
          );
        }
        return null;
      })()}
    </div>
  );
}