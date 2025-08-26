'use client';

import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  TrendingUp, 
  Target,
  Award,
  BarChart3,
  Clock,
  Database
} from 'lucide-react';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';
import apiClient from '@/lib/api-client';

interface Stock {
  symbol: string;
  company_name: string;
}

interface ModelPerformance {
  model_name: string;
  accuracy: number;
  mae: number;
  rmse: number;
  ai_evaluation: string;
  backtest_data: {
    date: string;
    actual_price: number;
    predicted_price: number;
    error: number;
  }[];
  last_updated: string;
  training_samples: number;
}

interface ModelPerformanceData {
  symbol: string;
  models: ModelPerformance[];
  overall_performance: {
    best_accuracy: number;
    best_model: string;
    average_accuracy: number;
  };
}

interface ModelPerformanceDashboardProps {
  stock: Stock | null;
}

function ModelPerformanceCard({ model }: { model: ModelPerformance }) {
  const getModelColor = (modelName: string) => {
    const colors: { [key: string]: string } = {
      'LSTM': '#3b82f6',
      'VertexAI': '#10b981',
      'RandomForest': '#f59e0b',
      'XGBoost': '#ef4444'
    };
    return colors[modelName] || '#6b7280';
  };

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 85) return 'text-green-400';
    if (accuracy >= 75) return 'text-blue-400';
    if (accuracy >= 65) return 'text-yellow-400';
    return 'text-red-400';
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    return (
      <div className="bg-black/90 border border-gray-600 rounded-lg p-3">
        <div className="text-gray-300 text-sm mb-1">{formatDate(label)}</div>
        <div className="text-white">実績: ¥{data.actual_price.toLocaleString()}</div>
        <div style={{ color: getModelColor(model.model_name) }}>
          予測: ¥{data.predicted_price.toLocaleString()}
        </div>
        <div className="text-red-300">誤差: ¥{Math.abs(data.error).toLocaleString()}</div>
      </div>
    );
  };

  return (
    <div className="bg-gray-900/30 border border-gray-800/50 rounded-xl p-6 hover:bg-gray-900/40 transition-colors">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div 
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: getModelColor(model.model_name) }}
          />
          <h3 className="text-lg font-semibold text-white">
            {model.model_name}モデル
          </h3>
        </div>
        <div className={`text-right ${getAccuracyColor(model.accuracy)}`}>
          <div className="text-2xl font-bold">
            {model.accuracy.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-400">精度</div>
        </div>
      </div>

      {/* 主要指標 */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <Target className="w-4 h-4 text-blue-400 mr-1" />
            <span className="text-xs text-gray-400">MAE</span>
          </div>
          <div className="text-lg font-bold text-white">
            ¥{model.mae.toFixed(0)}
          </div>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <BarChart3 className="w-4 h-4 text-green-400 mr-1" />
            <span className="text-xs text-gray-400">RMSE</span>
          </div>
          <div className="text-lg font-bold text-white">
            ¥{model.rmse.toFixed(0)}
          </div>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <Database className="w-4 h-4 text-purple-400 mr-1" />
            <span className="text-xs text-gray-400">データ数</span>
          </div>
          <div className="text-lg font-bold text-white">
            {(model.training_samples / 1000).toFixed(1)}k
          </div>
        </div>
      </div>

      {/* AI評価 */}
      <div className="mb-4">
        <div className="flex items-center mb-2">
          <Brain className="w-4 h-4 text-purple-400 mr-2" />
          <span className="text-sm font-medium text-gray-300">AI評価</span>
        </div>
        <div className="text-sm text-gray-400 leading-relaxed bg-gray-800/30 rounded-lg p-3">
          {model.ai_evaluation}
        </div>
      </div>

      {/* バックテストチャート */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-300">バックテスト結果</span>
          <span className="text-xs text-gray-400">過去30日</span>
        </div>
        <div className="h-24">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={model.backtest_data}>
              <XAxis 
                dataKey="date" 
                hide
              />
              <YAxis hide />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="actual_price"
                stroke="#ffffff"
                strokeWidth={1}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="predicted_price"
                stroke={getModelColor(model.model_name)}
                strokeWidth={1}
                strokeDasharray="2 2"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="flex items-center justify-center space-x-4 text-xs text-gray-400 mt-1">
          <div className="flex items-center">
            <div className="w-3 h-0.5 bg-white mr-1"></div>
            実績
          </div>
          <div className="flex items-center">
            <div 
              className="w-3 h-0.5 mr-1 border-t border-dashed"
              style={{ borderColor: getModelColor(model.model_name) }}
            ></div>
            予測
          </div>
        </div>
      </div>

      {/* 更新情報 */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center">
          <Clock className="w-3 h-3 mr-1" />
          最終更新: {new Date(model.last_updated).toLocaleDateString('ja-JP')}
        </div>
        <div className="flex items-center">
          <Award className="w-3 h-3 mr-1" />
          {model.model_name === 'VertexAI' ? 'おすすめ' : '標準'}
        </div>
      </div>
    </div>
  );
}

export default function ModelPerformanceDashboard({ stock }: ModelPerformanceDashboardProps) {
  const [performanceData, setPerformanceData] = useState<ModelPerformanceData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (stock) {
      fetchModelPerformance();
    }
  }, [stock]);

  const fetchModelPerformance = async () => {
    if (!stock) return;

    setLoading(true);
    try {
      const response = await apiClient.getModelPerformance(stock.symbol);
      if (response.success && response.data) {
        setPerformanceData(response.data as ModelPerformanceData);
      }
    } catch (error) {
      console.error('Failed to fetch model performance:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!stock) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-8">
        <div className="text-center">
          <Brain className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-400 mb-2">
            銘柄を選択してください
          </h3>
          <p className="text-gray-500 text-sm">
            銘柄を選択すると各AIモデルの<br />
            パフォーマンス比較が表示されます
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
        </div>
      </div>
    );
  }

  if (!performanceData) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-8">
        <div className="text-center text-gray-400">
          モデルパフォーマンスデータを読み込めませんでした
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white flex items-center">
            <Brain className="w-6 h-6 mr-2 text-purple-400" />
            AIモデル パフォーマンス比較
          </h2>
          <div className="text-sm text-gray-400">
            {stock.symbol} - {stock.company_name}
          </div>
        </div>

        {/* 総合パフォーマンス */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-green-900/20 border border-green-500/30 rounded-lg">
            <div className="text-green-400 text-2xl font-bold">
              {performanceData.overall_performance.best_accuracy.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-300 mt-1">最高精度</div>
            <div className="text-xs text-green-400 mt-1">
              {performanceData.overall_performance.best_model}
            </div>
          </div>

          <div className="text-center p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
            <div className="text-blue-400 text-2xl font-bold">
              {performanceData.overall_performance.average_accuracy.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-300 mt-1">平均精度</div>
            <div className="text-xs text-blue-400 mt-1">
              全{performanceData.models.length}モデル
            </div>
          </div>

          <div className="text-center p-4 bg-purple-900/20 border border-purple-500/30 rounded-lg">
            <div className="text-purple-400 text-2xl font-bold">
              {performanceData.models.length}
            </div>
            <div className="text-sm text-gray-300 mt-1">利用可能モデル</div>
            <div className="text-xs text-purple-400 mt-1">
              マルチモデル予測
            </div>
          </div>
        </div>
      </div>

      {/* モデルカード一覧 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {performanceData.models.map((model) => (
          <ModelPerformanceCard
            key={model.model_name}
            model={model}
          />
        ))}
      </div>

      {/* パフォーマンス比較チャート */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2 text-blue-400" />
          精度比較
        </h3>
        
        <div className="space-y-3">
          {performanceData.models
            .sort((a, b) => b.accuracy - a.accuracy)
            .map((model, index) => (
              <div key={model.model_name} className="flex items-center space-x-4">
                <div className="flex items-center w-24">
                  <div className="text-sm font-medium text-gray-300">
                    #{index + 1}
                  </div>
                  <div 
                    className="w-3 h-3 rounded-full ml-2"
                    style={{ backgroundColor: getModelColor(model.model_name) }}
                  />
                  <div className="text-sm text-gray-300 ml-2">
                    {model.model_name}
                  </div>
                </div>
                
                <div className="flex-1 bg-gray-800 rounded-full h-4 overflow-hidden">
                  <div
                    className="h-full transition-all duration-500 bg-gradient-to-r from-blue-500 to-green-500"
                    style={{ width: `${model.accuracy}%` }}
                  />
                </div>
                
                <div className="text-sm font-medium text-white w-16 text-right">
                  {model.accuracy.toFixed(1)}%
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

function getModelColor(modelName: string): string {
  const colors: { [key: string]: string } = {
    'LSTM': '#3b82f6',
    'VertexAI': '#10b981',
    'RandomForest': '#f59e0b',
    'XGBoost': '#ef4444'
  };
  return colors[modelName] || '#6b7280';
}