'use client';

import React, { useState, useMemo } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend,
  ReferenceLine
} from 'recharts';
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Calendar,
  BarChart3
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

interface PerformanceData {
  date: string;
  theme_index: number;
  market_index: number;
  outperformance: number;
}

interface ThemePerformanceChartProps {
  theme: ThemeDetail;
  performanceData: PerformanceData[];
}

type TimePeriod = '1M' | '3M' | '6M' | '1Y' | 'ALL';

export default function ThemePerformanceChart({ theme, performanceData }: ThemePerformanceChartProps) {
  const [selectedPeriod, setSelectedPeriod] = useState<TimePeriod>('1M');
  const [showComparison, setShowComparison] = useState(true);

  // データを期間でフィルタリング
  const filteredData = useMemo(() => {
    if (!performanceData || performanceData.length === 0) return [];

    const now = new Date();
    let startDate = new Date();

    switch (selectedPeriod) {
      case '1M':
        startDate.setMonth(now.getMonth() - 1);
        break;
      case '3M':
        startDate.setMonth(now.getMonth() - 3);
        break;
      case '6M':
        startDate.setMonth(now.getMonth() - 6);
        break;
      case '1Y':
        startDate.setFullYear(now.getFullYear() - 1);
        break;
      case 'ALL':
        return performanceData;
      default:
        startDate.setMonth(now.getMonth() - 1);
    }

    return performanceData.filter(item => new Date(item.date) >= startDate);
  }, [performanceData, selectedPeriod]);

  // パフォーマンス統計を計算
  const performanceStats = useMemo(() => {
    if (!filteredData || filteredData.length === 0) {
      return {
        themeReturn: 0,
        marketReturn: 0,
        outperformance: 0,
        volatility: 0,
        maxDrawdown: 0,
        sharpeRatio: 0
      };
    }

    const firstData = filteredData[0];
    const lastData = filteredData[filteredData.length - 1];

    const themeReturn = ((lastData.theme_index - firstData.theme_index) / firstData.theme_index) * 100;
    const marketReturn = ((lastData.market_index - firstData.market_index) / firstData.market_index) * 100;
    const outperformance = themeReturn - marketReturn;

    // 簡単なボラティリティ計算（日次リターンの標準偏差）
    const returns = filteredData.slice(1).map((item, index) => {
      return (item.theme_index - filteredData[index].theme_index) / filteredData[index].theme_index;
    });
    
    const avgReturn = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
    const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length;
    const volatility = Math.sqrt(variance) * Math.sqrt(252) * 100; // 年率換算

    // 最大ドローダウンの簡易計算
    let maxValue = firstData.theme_index;
    let maxDrawdown = 0;
    
    filteredData.forEach(item => {
      if (item.theme_index > maxValue) {
        maxValue = item.theme_index;
      } else {
        const drawdown = ((maxValue - item.theme_index) / maxValue) * 100;
        maxDrawdown = Math.max(maxDrawdown, drawdown);
      }
    });

    // シャープレシオの簡易計算（リスクフリーレートを0と仮定）
    const sharpeRatio = volatility > 0 ? (themeReturn / volatility) : 0;

    return {
      themeReturn,
      marketReturn,
      outperformance,
      volatility,
      maxDrawdown,
      sharpeRatio
    };
  }, [filteredData]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ja-JP', { 
      month: 'short', 
      day: 'numeric'
    });
  };

  const formatValue = (value: number) => {
    return value.toFixed(1);
  };

  const formatPerformance = (performance: number) => {
    const sign = performance >= 0 ? '+' : '';
    return `${sign}${performance.toFixed(2)}%`;
  };

  const getPerformanceColor = (performance: number) => {
    return performance >= 0 ? '#10b981' : '#ef4444';
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800/95 border border-gray-600/50 rounded-lg p-3 shadow-lg">
          <p className="text-gray-300 text-sm mb-2">{formatDate(label)}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {formatValue(entry.value)}
              {entry.dataKey !== 'outperformance' && (
                <span className="text-xs text-gray-400 ml-1">
                  ({formatPerformance((entry.value - 100))})
                </span>
              )}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
      {/* ヘッダー */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
        <div className="flex items-center">
          <Activity className="w-6 h-6 mr-3 text-blue-400" />
          <div>
            <h2 className="text-xl font-bold text-white">パフォーマンスチャート</h2>
            <p className="text-sm text-gray-400">テーマ指数と市場平均の比較</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* 比較表示切替 */}
          <button
            onClick={() => setShowComparison(!showComparison)}
            className={`flex items-center space-x-2 px-3 py-1 rounded-lg text-sm transition-colors ${
              showComparison 
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' 
                : 'bg-gray-700/50 text-gray-300 hover:bg-gray-700/70'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            <span>市場比較</span>
          </button>

          {/* 期間選択 */}
          <div className="flex items-center bg-gray-800/50 rounded-lg p-1">
            {(['1M', '3M', '6M', '1Y', 'ALL'] as TimePeriod[]).map((period) => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={`px-3 py-1 rounded-md text-sm transition-all ${
                  selectedPeriod === period
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                }`}
              >
                {period}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* パフォーマンス統計 */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
        <div className="bg-gray-800/30 rounded-lg p-3 text-center">
          <div className="text-xs text-gray-400 mb-1">テーマリターン</div>
          <div className={`font-bold ${getPerformanceColor(performanceStats.themeReturn) === '#10b981' ? 'text-green-400' : 'text-red-400'}`}>
            {formatPerformance(performanceStats.themeReturn)}
          </div>
        </div>

        <div className="bg-gray-800/30 rounded-lg p-3 text-center">
          <div className="text-xs text-gray-400 mb-1">市場リターン</div>
          <div className={`font-bold ${getPerformanceColor(performanceStats.marketReturn) === '#10b981' ? 'text-green-400' : 'text-red-400'}`}>
            {formatPerformance(performanceStats.marketReturn)}
          </div>
        </div>

        <div className="bg-gray-800/30 rounded-lg p-3 text-center">
          <div className="text-xs text-gray-400 mb-1">アウトパフォーム</div>
          <div className={`font-bold ${getPerformanceColor(performanceStats.outperformance) === '#10b981' ? 'text-green-400' : 'text-red-400'}`}>
            {formatPerformance(performanceStats.outperformance)}
          </div>
        </div>

        <div className="bg-gray-800/30 rounded-lg p-3 text-center">
          <div className="text-xs text-gray-400 mb-1">ボラティリティ</div>
          <div className="text-white font-bold">
            {formatPerformance(performanceStats.volatility)}
          </div>
        </div>

        <div className="bg-gray-800/30 rounded-lg p-3 text-center">
          <div className="text-xs text-gray-400 mb-1">最大ドローダウン</div>
          <div className="text-red-400 font-bold">
            -{formatPerformance(performanceStats.maxDrawdown).replace('-', '')}
          </div>
        </div>

        <div className="bg-gray-800/30 rounded-lg p-3 text-center">
          <div className="text-xs text-gray-400 mb-1">シャープレシオ</div>
          <div className="text-white font-bold">
            {performanceStats.sharpeRatio.toFixed(2)}
          </div>
        </div>
      </div>

      {/* チャート */}
      <div className="h-96">
        {filteredData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={filteredData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" strokeOpacity={0.3} />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12, fill: '#9CA3AF' }}
                tickFormatter={formatDate}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#9CA3AF' }}
                tickFormatter={formatValue}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <ReferenceLine y={100} stroke="#6B7280" strokeDasharray="2 2" strokeOpacity={0.5} />
              
              <Line
                type="monotone"
                dataKey="theme_index"
                stroke="#8B5CF6"
                strokeWidth={3}
                dot={false}
                name={`${theme.name}指数`}
                activeDot={{ r: 6, stroke: '#8B5CF6', strokeWidth: 2, fill: '#8B5CF6' }}
              />
              
              {showComparison && (
                <Line
                  type="monotone"
                  dataKey="market_index"
                  stroke="#6B7280"
                  strokeWidth={2}
                  dot={false}
                  name="市場平均"
                  strokeDasharray="5 5"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Activity className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-400 mb-2">
                データがありません
              </h3>
              <p className="text-gray-500 text-sm">
                パフォーマンスデータを取得中です
              </p>
            </div>
          </div>
        )}
      </div>

      {/* チャートの説明 */}
      <div className="mt-4 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
        <div className="flex items-start space-x-3">
          <Target className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-blue-400 mb-1">チャートについて</h4>
            <div className="text-sm text-gray-300 space-y-1">
              <p>• テーマ指数は関連銘柄を時価総額で加重平均した独自指数です</p>
              <p>• 市場平均にはTOPIX（東証株価指数）を使用しています</p>
              <p>• すべての指数は基準日を100として正規化されています</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}