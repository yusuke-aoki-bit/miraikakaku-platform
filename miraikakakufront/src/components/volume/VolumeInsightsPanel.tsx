'use client';

import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  BarChart3, 
  TrendingUp,
  TrendingDown,
  Calendar,
  AlertTriangle,
  Zap,
  Target,
  Clock,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react';
import apiClient from '@/lib/api-client';

interface Stock {
  symbol: string;
  company_name: string;
}

interface VolumeInsight {
  symbol: string;
  current_analysis: {
    current_volume: number;
    average_volume_20d: number;
    deviation_percent: number;
    deviation_ratio: number;
    trend: string;
    analysis_date: string;
  };
  ai_insights: string[];
  future_predictions: {
    date: string;
    predicted_volume: number;
    change_percent: number;
    confidence: number;
    day_name: string;
  }[];
  risk_factors: string[];
  confidence_score: number;
}

interface VolumeInsightsPanelProps {
  stock: Stock | null;
}

export default function VolumeInsightsPanel({ stock }: VolumeInsightsPanelProps) {
  const [insights, setInsights] = useState<VolumeInsight | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (stock) {
      fetchVolumeInsights();
    }
  }, [stock]);

  const fetchVolumeInsights = async () => {
    if (!stock) return;

    setLoading(true);
    try {
      const response = await apiClient.getAIVolumeInsights(stock.symbol);
      if (response.success && response.data) {
        setInsights(response.data as any);
      }
    } catch (error) {
      console.error('Failed to fetch volume insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatVolume = (volume: number): string => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M株`;
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(0)}K株`;
    }
    return `${volume.toLocaleString()}株`;
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case '急増トレンド':
        return <ArrowUp className="w-4 h-4 text-green-400" />;
      case '減少傾向':
        return <ArrowDown className="w-4 h-4 text-red-400" />;
      case '安定推移':
        return <Minus className="w-4 h-4 text-blue-400" />;
      default:
        return <BarChart3 className="w-4 h-4 text-gray-400" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case '急増トレンド':
        return 'text-green-400 bg-green-900/20 border-green-500/30';
      case '減少傾向':
        return 'text-red-400 bg-red-900/20 border-red-500/30';
      case '安定推移':
        return 'text-blue-400 bg-blue-900/20 border-blue-500/30';
      default:
        return 'text-gray-400 bg-gray-800/30 border-gray-700/50';
    }
  };

  const getDeviationColor = (deviation: number) => {
    if (Math.abs(deviation) > 50) return 'text-red-400';
    if (Math.abs(deviation) > 25) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getChangeIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="w-3 h-3 text-green-400" />;
    if (change < 0) return <TrendingDown className="w-3 h-3 text-red-400" />;
    return <Minus className="w-3 h-3 text-gray-400" />;
  };

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-green-400';
    if (change < 0) return 'text-red-400';
    return 'text-gray-400';
  };

  if (!stock) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="text-center">
          <Brain className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <h3 className="text-md font-semibold text-gray-400 mb-2">
            AI出来高分析
          </h3>
          <p className="text-gray-500 text-sm">
            銘柄を選択すると<br />
            AI分析結果が表示されます
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-400"></div>
        </div>
      </div>
    );
  }

  if (!insights) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="text-center text-gray-400">
          分析データを読み込めませんでした
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* ヘッダー */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
        <h2 className="text-lg font-bold text-white flex items-center mb-2">
          <Brain className="w-5 h-5 mr-2 text-purple-400" />
          AI出来高分析
        </h2>
        <div className="text-sm text-gray-400">
          {stock.company_name} ({stock.symbol})
        </div>
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-gray-500">信頼度</span>
          <span className="text-purple-400 font-medium">
            {insights.confidence_score.toFixed(0)}%
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-1 mt-1">
          <div 
            className="bg-purple-400 h-1 rounded-full transition-all"
            style={{ width: `${insights.confidence_score}%` }}
          />
        </div>
      </div>

      {/* 現在の出来高サマリー */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
        <h3 className="text-md font-semibold text-white mb-3 flex items-center">
          <Target className="w-4 h-4 mr-2 text-blue-400" />
          現在の出来高状況
        </h3>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">本日出来高</span>
            <span className="text-white font-medium">
              {formatVolume(insights.current_analysis.current_volume)}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">20日平均</span>
            <span className="text-gray-300">
              {formatVolume(insights.current_analysis.average_volume_20d)}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">平均との乖離</span>
            <span className={`font-medium ${getDeviationColor(insights.current_analysis.deviation_percent)}`}>
              {insights.current_analysis.deviation_percent > 0 ? '+' : ''}
              {insights.current_analysis.deviation_percent.toFixed(1)}%
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">平均倍率</span>
            <span className={`font-medium ${getDeviationColor(insights.current_analysis.deviation_percent)}`}>
              {insights.current_analysis.deviation_ratio.toFixed(1)}倍
            </span>
          </div>

          <div className="pt-2 border-t border-gray-700/50">
            <div className={`flex items-center justify-center p-2 rounded-lg border ${getTrendColor(insights.current_analysis.trend)}`}>
              {getTrendIcon(insights.current_analysis.trend)}
              <span className="ml-2 font-medium">{insights.current_analysis.trend}</span>
            </div>
          </div>
        </div>
      </div>

      {/* AI分析インサイト */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
        <h3 className="text-md font-semibold text-white mb-3 flex items-center">
          <Zap className="w-4 h-4 mr-2 text-yellow-400" />
          AI分析コメント
        </h3>

        <div className="space-y-3">
          {insights.ai_insights.map((insight, index) => (
            <div 
              key={index}
              className="bg-gray-800/30 rounded-lg p-3 border-l-2 border-yellow-400"
            >
              <p className="text-sm text-gray-300 leading-relaxed">
                {insight}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* 未来の出来高予測 */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
        <h3 className="text-md font-semibold text-white mb-3 flex items-center">
          <Calendar className="w-4 h-4 mr-2 text-green-400" />
          出来高予測
        </h3>

        <div className="space-y-2">
          {insights.future_predictions.slice(0, 5).map((prediction, index) => (
            <div 
              key={prediction.date}
              className="flex items-center justify-between p-2 bg-gray-800/20 rounded-md"
            >
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-400 w-12">
                  {prediction.day_name}
                </span>
                {getChangeIcon(prediction.change_percent)}
              </div>
              
              <div className="text-right">
                <div className="text-sm font-medium text-white">
                  {formatVolume(prediction.predicted_volume)}
                </div>
                <div className={`text-xs ${getChangeColor(prediction.change_percent)}`}>
                  {prediction.change_percent > 0 ? '+' : ''}
                  {prediction.change_percent.toFixed(1)}%
                </div>
              </div>
              
              <div className="text-xs text-gray-500 w-8 text-right">
                {prediction.confidence.toFixed(0)}%
              </div>
            </div>
          ))}
        </div>

        {/* 予測サマリー */}
        <div className="mt-4 pt-3 border-t border-gray-700/50">
          <div className="grid grid-cols-2 gap-3 text-center">
            <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-2">
              <div className="text-green-400 text-lg font-bold">
                {insights.future_predictions.filter(p => p.change_percent > 0).length}
              </div>
              <div className="text-xs text-gray-400">増加予測日</div>
            </div>
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-2">
              <div className="text-red-400 text-lg font-bold">
                {insights.future_predictions.filter(p => p.change_percent < 0).length}
              </div>
              <div className="text-xs text-gray-400">減少予測日</div>
            </div>
          </div>
        </div>
      </div>

      {/* リスク要因 */}
      {insights.risk_factors.length > 0 && (
        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
          <h3 className="text-md font-semibold text-white mb-3 flex items-center">
            <AlertTriangle className="w-4 h-4 mr-2 text-orange-400" />
            注意すべき要因
          </h3>

          <div className="space-y-2">
            {insights.risk_factors.map((factor, index) => (
              <div 
                key={index}
                className="flex items-center space-x-2 text-sm text-gray-300"
              >
                <AlertTriangle className="w-3 h-3 text-orange-400 flex-shrink-0" />
                <span>{factor}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 更新情報 */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center">
            <Clock className="w-3 h-3 mr-1" />
            最終更新
          </div>
          <div>
            {new Date(insights.current_analysis.analysis_date).toLocaleString('ja-JP')}
          </div>
        </div>
      </div>
    </div>
  );
}