'use client';

import { useState, useMemo } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

/**
 * 高度な分析ダッシュボード
 * プロフェッショナル投資家向けの詳細分析機能
 */

interface StockData {
  symbol: string;
  name: string;
  price: number;
  change_percent: number;
  volume: number;
  market_cap?: number;
  sector?: string;
  beta?: number;
  pe_ratio?: number;
  dividend_yield?: number;
}

interface AnalyticsDashboardProps {
  stocks: StockData[];
  portfolioValue?: number;
}

export function AdvancedAnalyticsDashboard({ stocks, portfolioValue }: AnalyticsDashboardProps) {
  const [selectedMetric, setSelectedMetric] = useState<'performance' | 'risk' | 'sector' | 'valuation'>('performance');
  const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | '3M' | '1Y'>('1M');

  // パフォーマンス分析
  const performanceMetrics = useMemo(() => {
    if (stocks.length === 0) return null;

    const gainers = stocks.filter(s => s.change_percent > 0);
    const losers = stocks.filter(s => s.change_percent < 0);
    const avgChange = stocks.reduce((sum, s) => sum + s.change_percent, 0) / stocks.length;
    const totalVolume = stocks.reduce((sum, s) => sum + (s.volume || 0), 0);

    return {
      totalStocks: stocks.length,
      gainers: gainers.length,
      losers: losers.length,
      unchanged: stocks.length - gainers.length - losers.length,
      avgChange: avgChange,
      totalVolume: totalVolume,
      topGainer: stocks.sort((a, b) => b.change_percent - a.change_percent)[0],
      topLoser: stocks.sort((a, b) => a.change_percent - b.change_percent)[0],
    };
  }, [stocks]);

  // セクター分析
  const sectorAnalysis = useMemo(() => {
    const sectorMap = new Map<string, { count: number; avgChange: number; totalVolume: number }>();

    stocks.forEach(stock => {
      const sector = stock.sector || 'その他';
      const existing = sectorMap.get(sector) || { count: 0, avgChange: 0, totalVolume: 0 };

      existing.count += 1;
      existing.avgChange += stock.change_percent;
      existing.totalVolume += stock.volume || 0;

      sectorMap.set(sector, existing);
    });

    return Array.from(sectorMap.entries()).map(([name, data]) => ({
      name,
      count: data.count,
      avgChange: data.avgChange / data.count,
      totalVolume: data.totalVolume,
      percentage: (data.count / stocks.length) * 100
    })).sort((a, b) => b.count - a.count);
  }, [stocks]);

  // リスク分析
  const riskMetrics = useMemo(() => {
    const changes = stocks.map(s => s.change_percent);
    const mean = changes.reduce((sum, c) => sum + c, 0) / changes.length;
    const variance = changes.reduce((sum, c) => sum + Math.pow(c - mean, 2), 0) / changes.length;
    const stdDev = Math.sqrt(variance);

    const sortedChanges = [...changes].sort((a, b) => a - b);
    const q1Index = Math.floor(sortedChanges.length * 0.25);
    const q3Index = Math.floor(sortedChanges.length * 0.75);

    return {
      volatility: stdDev,
      sharpeRatio: mean / stdDev || 0,
      maxDrawdown: Math.min(...changes),
      maxGain: Math.max(...changes),
      q1: sortedChanges[q1Index],
      median: sortedChanges[Math.floor(sortedChanges.length / 2)],
      q3: sortedChanges[q3Index],
    };
  }, [stocks]);

  // バリュエーション分析
  const valuationMetrics = useMemo(() => {
    const withPE = stocks.filter(s => s.pe_ratio);
    const avgPE = withPE.length > 0
      ? withPE.reduce((sum, s) => sum + (s.pe_ratio || 0), 0) / withPE.length
      : 0;

    const withDividend = stocks.filter(s => s.dividend_yield);
    const avgDividend = withDividend.length > 0
      ? withDividend.reduce((sum, s) => sum + (s.dividend_yield || 0), 0) / withDividend.length
      : 0;

    return {
      avgPE,
      avgDividend,
      undervaluedCount: withPE.filter(s => (s.pe_ratio || 0) < avgPE).length,
      overvaluedCount: withPE.filter(s => (s.pe_ratio || 0) > avgPE).length,
    };
  }, [stocks]);

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

  if (!performanceMetrics) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center">
        <p className="text-gray-600 dark:text-gray-400">分析するデータがありません</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">📊 高度な分析ダッシュボード</h1>
        <p className="text-blue-100">プロフェッショナル投資家向け詳細分析</p>
      </div>

      {/* タイムフレーム選択 */}
      <div className="flex space-x-2">
        {(['1D', '1W', '1M', '3M', '1Y'] as const).map(tf => (
          <button
            key={tf}
            onClick={() => setTimeframe(tf)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              timeframe === tf
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            {tf}
          </button>
        ))}
      </div>

      {/* メトリック選択タブ */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          {[
            { key: 'performance' as const, label: 'パフォーマンス' },
            { key: 'risk' as const, label: 'リスク分析' },
            { key: 'sector' as const, label: 'セクター分析' },
            { key: 'valuation' as const, label: 'バリュエーション' },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setSelectedMetric(tab.key)}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                selectedMetric === tab.key
                  ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-b-2 border-blue-600'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {/* パフォーマンス分析 */}
          {selectedMetric === 'performance' && (
            <div className="space-y-6">
              {/* サマリーカード */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border-l-4 border-green-500">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">上昇銘柄</p>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {performanceMetrics.gainers}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {((performanceMetrics.gainers / performanceMetrics.totalStocks) * 100).toFixed(1)}%
                  </p>
                </div>

                <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border-l-4 border-red-500">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">下落銘柄</p>
                  <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {performanceMetrics.losers}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {((performanceMetrics.losers / performanceMetrics.totalStocks) * 100).toFixed(1)}%
                  </p>
                </div>

                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border-l-4 border-blue-500">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">平均変動率</p>
                  <p className={`text-2xl font-bold ${
                    performanceMetrics.avgChange >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                  }`}>
                    {performanceMetrics.avgChange >= 0 ? '+' : ''}
                    {performanceMetrics.avgChange.toFixed(2)}%
                  </p>
                </div>

                <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg border-l-4 border-purple-500">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">総出来高</p>
                  <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                    {(performanceMetrics.totalVolume / 1000000).toFixed(1)}M
                  </p>
                </div>
              </div>

              {/* トップパフォーマー */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-green-50 dark:bg-green-900/20 p-6 rounded-lg">
                  <h3 className="font-semibold text-green-800 dark:text-green-200 mb-3 flex items-center">
                    <span className="text-2xl mr-2">🏆</span>
                    トップゲイナー
                  </h3>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">
                    {performanceMetrics.topGainer.symbol}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {performanceMetrics.topGainer.name}
                  </p>
                  <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                    +{performanceMetrics.topGainer.change_percent.toFixed(2)}%
                  </p>
                </div>

                <div className="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg">
                  <h3 className="font-semibold text-red-800 dark:text-red-200 mb-3 flex items-center">
                    <span className="text-2xl mr-2">📉</span>
                    トップルーザー
                  </h3>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">
                    {performanceMetrics.topLoser.symbol}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {performanceMetrics.topLoser.name}
                  </p>
                  <p className="text-3xl font-bold text-red-600 dark:text-red-400">
                    {performanceMetrics.topLoser.change_percent.toFixed(2)}%
                  </p>
                </div>
              </div>

              {/* パフォーマンス分布 */}
              <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-4">パフォーマンス分布</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: '上昇', value: performanceMetrics.gainers, color: '#10B981' },
                        { name: '下落', value: performanceMetrics.losers, color: '#EF4444' },
                        { name: '変動なし', value: performanceMetrics.unchanged, color: '#6B7280' },
                      ]}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {[
                        { name: '上昇', value: performanceMetrics.gainers, color: '#10B981' },
                        { name: '下落', value: performanceMetrics.losers, color: '#EF4444' },
                        { name: '変動なし', value: performanceMetrics.unchanged, color: '#6B7280' },
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* リスク分析 */}
          {selectedMetric === 'risk' && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">ボラティリティ</p>
                  <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                    {riskMetrics.volatility.toFixed(2)}%
                  </p>
                </div>

                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">シャープレシオ</p>
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {riskMetrics.sharpeRatio.toFixed(2)}
                  </p>
                </div>

                <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">最大ドローダウン</p>
                  <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {riskMetrics.maxDrawdown.toFixed(2)}%
                  </p>
                </div>

                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">最大ゲイン</p>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    +{riskMetrics.maxGain.toFixed(2)}%
                  </p>
                </div>
              </div>

              {/* ボックスプロット風の表示 */}
              <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-4">リターン分布</h3>
                <div className="space-y-3">
                  <div className="flex items-center">
                    <span className="w-32 text-sm text-gray-600 dark:text-gray-400">最大値</span>
                    <div className="flex-1 h-8 bg-gray-200 dark:bg-gray-700 rounded relative">
                      <div
                        className="absolute h-full bg-green-500 rounded"
                        style={{ width: `${Math.abs(riskMetrics.maxGain) / Math.abs(riskMetrics.maxDrawdown) * 50}%`, right: 0 }}
                      />
                      <span className="absolute right-2 top-1 text-sm font-semibold text-white">
                        {riskMetrics.maxGain.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="w-32 text-sm text-gray-600 dark:text-gray-400">第3四分位</span>
                    <div className="flex-1 h-8 bg-gray-200 dark:bg-gray-700 rounded relative">
                      <div
                        className="absolute h-full bg-blue-400 rounded"
                        style={{ width: '40%', right: '30%' }}
                      />
                      <span className="absolute left-1/2 top-1 text-sm font-semibold">
                        {riskMetrics.q3.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="w-32 text-sm text-gray-600 dark:text-gray-400">中央値</span>
                    <div className="flex-1 h-8 bg-gray-200 dark:bg-gray-700 rounded relative">
                      <div className="absolute h-full w-1 bg-purple-500 left-1/2 transform -translate-x-1/2" />
                      <span className="absolute left-1/2 top-1 text-sm font-semibold transform -translate-x-1/2">
                        {riskMetrics.median.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="w-32 text-sm text-gray-600 dark:text-gray-400">第1四分位</span>
                    <div className="flex-1 h-8 bg-gray-200 dark:bg-gray-700 rounded relative">
                      <div
                        className="absolute h-full bg-orange-400 rounded"
                        style={{ width: '40%', left: '10%' }}
                      />
                      <span className="absolute left-1/3 top-1 text-sm font-semibold">
                        {riskMetrics.q1.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="w-32 text-sm text-gray-600 dark:text-gray-400">最小値</span>
                    <div className="flex-1 h-8 bg-gray-200 dark:bg-gray-700 rounded relative">
                      <div
                        className="absolute h-full bg-red-500 rounded"
                        style={{ width: `${Math.abs(riskMetrics.maxDrawdown) / Math.abs(riskMetrics.maxGain) * 50}%`, left: 0 }}
                      />
                      <span className="absolute left-2 top-1 text-sm font-semibold text-white">
                        {riskMetrics.maxDrawdown.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* セクター分析 */}
          {selectedMetric === 'sector' && (
            <div className="space-y-6">
              <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-4">セクター別構成</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={sectorAnalysis}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percentage }) => `${name} ${percentage.toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {sectorAnalysis.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="space-y-3">
                <h3 className="font-semibold text-gray-900 dark:text-white">セクター別パフォーマンス</h3>
                {sectorAnalysis.map((sector, index) => (
                  <div key={sector.name} className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <div
                          className="w-4 h-4 rounded"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <span className="font-semibold text-gray-900 dark:text-white">
                          {sector.name}
                        </span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          ({sector.count} 銘柄)
                        </span>
                      </div>
                      <span className={`font-bold ${
                        sector.avgChange >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                      }`}>
                        {sector.avgChange >= 0 ? '+' : ''}
                        {sector.avgChange.toFixed(2)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          sector.avgChange >= 0 ? 'bg-green-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(Math.abs(sector.avgChange) * 10, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* バリュエーション分析 */}
          {selectedMetric === 'valuation' && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">平均PER</p>
                  <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                    {valuationMetrics.avgPE.toFixed(2)}x
                  </p>
                </div>

                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">平均配当利回り</p>
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {valuationMetrics.avgDividend.toFixed(2)}%
                  </p>
                </div>

                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">割安銘柄</p>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {valuationMetrics.undervaluedCount}
                  </p>
                </div>

                <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">割高銘柄</p>
                  <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {valuationMetrics.overvaluedCount}
                  </p>
                </div>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-lg border-l-4 border-blue-500">
                <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">💡 バリュエーションインサイト</h4>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  平均PER {valuationMetrics.avgPE.toFixed(2)}xは
                  {valuationMetrics.avgPE < 15 ? '割安' : valuationMetrics.avgPE < 25 ? '適正' : '割高'}
                  な水準です。
                  {valuationMetrics.undervaluedCount > valuationMetrics.overvaluedCount
                    ? '市場全体として割安な銘柄が多い状況です。'
                    : '市場全体として割高な銘柄が多い状況です。'}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
