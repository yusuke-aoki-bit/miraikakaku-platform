'use client';

import React, { useState, useEffect, useMemo } from 'react';
import StockChart from './StockChart';
import { Brain, DollarSign } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { CHART_COLORS, getChartColors } from '@/config/chart-colors';

// データ型定義
interface HistoricalData {
  date: string;
  actual_price: number;
  volume: number;
}

interface PredictionData {
  date: string;
  lstm_prediction: number;
  vertexai_prediction: number;
  lstm_confidence: number;
  vertexai_confidence: number;
  actual_price?: number; // 過去予測の場合は実績値も含む
}

interface ModelPerformance {
  model: 'LSTM' | 'VertexAI';
  mae: number; // Mean Absolute Error
  rmse: number; // Root Mean Square Error
  accuracy_percentage: number;
  profit_potential: number;
  risk_level: 'Low' | 'Medium' | 'High';
}

interface EnhancedStockChartProps {
  symbol: string;
  timeframe?: string;
  showThumbnail?: boolean;
  chartType?: 'historical' | 'past-prediction' | 'future-prediction';
}

// MAS (Mean Absolute Error) 計算関数
const calculateMAS = (predictions: number[], actuals: number[]): number => {
  if (predictions.length !== actuals.length || predictions.length === 0) return 0;
  
  const absoluteErrors = predictions.map((pred, i) => Math.abs(pred - actuals[i]));
  return absoluteErrors.reduce((sum, error) => sum + error, 0) / absoluteErrors.length;
};

// RMSE 計算関数
const calculateRMSE = (predictions: number[], actuals: number[]): number => {
  if (predictions.length !== actuals.length || predictions.length === 0) return 0;
  
  const squaredErrors = predictions.map((pred, i) => Math.pow(pred - actuals[i], 2));
  return Math.sqrt(squaredErrors.reduce((sum, error) => sum + error, 0) / squaredErrors.length);
};

// 予測精度計算
const calculateAccuracy = (predictions: number[], actuals: number[]): number => {
  if (predictions.length !== actuals.length || predictions.length === 0) return 0;
  
  const accuracies = predictions.map((pred, i) => {
    const error = Math.abs(pred - actuals[i]) / actuals[i];
    return Math.max(0, 100 - (error * 100));
  });
  
  return accuracies.reduce((sum, acc) => sum + acc, 0) / accuracies.length;
};

export default function EnhancedStockChart({ symbol, timeframe = '1M', showThumbnail = false, chartType = 'historical' }: EnhancedStockChartProps) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<{
    historical: HistoricalData[];
    pastPredictions: PredictionData[];
    futurePredictions: PredictionData[];
  } | null>(null);

  // モデルパフォーマンス計算
  const modelPerformance = useMemo((): ModelPerformance[] => {
    if (!data || data.pastPredictions.length === 0) return [];

    const lstmPreds = data.pastPredictions.map(p => p.lstm_prediction);
    const vertexPreds = data.pastPredictions.map(p => p.vertexai_prediction);
    const actuals = data.pastPredictions.map(p => p.actual_price!);

    const lstmMAE = calculateMAS(lstmPreds, actuals);
    const vertexMAE = calculateMAS(vertexPreds, actuals);
    
    const lstmRMSE = calculateRMSE(lstmPreds, actuals);
    const vertexRMSE = calculateRMSE(vertexPreds, actuals);
    
    const lstmAccuracy = calculateAccuracy(lstmPreds, actuals);
    const vertexAccuracy = calculateAccuracy(vertexPreds, actuals);

    return [
      {
        model: 'LSTM',
        mae: lstmMAE,
        rmse: lstmRMSE,
        accuracy_percentage: lstmAccuracy,
        profit_potential: lstmAccuracy * 0.1, // 精度に基づく収益ポテンシャル
        risk_level: lstmMAE < 2 ? 'Low' : lstmMAE < 5 ? 'Medium' : 'High'
      },
      {
        model: 'VertexAI',
        mae: vertexMAE,
        rmse: vertexRMSE,
        accuracy_percentage: vertexAccuracy,
        profit_potential: vertexAccuracy * 0.12,
        risk_level: vertexMAE < 2 ? 'Low' : vertexMAE < 5 ? 'Medium' : 'High'
      }
    ];
  }, [data]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      
      try {
        const [historicalRes, pastPredictionsRes, futurePredictionsRes] = await Promise.all([
          apiClient.getStockPrice(symbol, 30),
          apiClient.getHistoricalPredictions(symbol, 15),
          apiClient.getStockPredictions(symbol, undefined, 15)
        ]);

        const historical = historicalRes.success && Array.isArray(historicalRes.data) ? (historicalRes.data as any[]).map(d => ({...d, date: d.date.split('T')[0], actual_price: d.close_price, volume: d.volume || 0})) : [];
        const pastPredictions = pastPredictionsRes.success && Array.isArray(pastPredictionsRes.data) ? (pastPredictionsRes.data as any[]).map(d => ({...d, date: d.target_date})) : [];
        const futurePredictions = futurePredictionsRes.success && Array.isArray(futurePredictionsRes.data) ? (futurePredictionsRes.data as any[]).map(d => ({...d, date: d.target_date})) : [];

        setData({
          historical,
          pastPredictions,
          futurePredictions,
        });
      } catch (error) {
        console.error("Failed to fetch chart data", error);
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [symbol, timeframe]);

  // Chart.js用データ準備
  const chartData = useMemo(() => {
    if (!data) return null;

    const allDates = [
      ...data.historical.map(h => h.date),
      ...data.futurePredictions.map(f => f.date)
    ].sort();

    const datasets = [];

    if (chartType === 'historical' || !showThumbnail) {
        datasets.push({
          label: '実績価格',
          data: allDates.map(date => {
            const historical = data.historical.find(h => h.date === date);
            return historical ? { x: date, y: historical.actual_price } : null;
          }).filter(Boolean),
          borderColor: CHART_COLORS.PRICE.UP,
          backgroundColor: CHART_COLORS.PRICE.UP + '20',
          borderWidth: 3,
          pointRadius: 2,
          pointHoverRadius: 6,
          fill: false,
        });
    }

    if (chartType === 'past-prediction' || !showThumbnail) {
        datasets.push({
          label: 'LSTM過去予測',
          data: allDates.map(date => {
            const pastPred = data.pastPredictions.find(p => p.date === date);
            return pastPred ? { x: date, y: pastPred.lstm_prediction } : null;
          }).filter(Boolean),
          borderColor: getChartColors.prediction('lstm'),
          backgroundColor: getChartColors.prediction('lstm') + '20',
          borderWidth: 2,
          pointRadius: 3,
          borderDash: [5, 5],
          fill: false,
        },
        {
          label: 'VertexAI過去予測',
          data: allDates.map(date => {
            const pastPred = data.pastPredictions.find(p => p.date === date);
            return pastPred ? { x: date, y: pastPred.vertexai_prediction } : null;
          }).filter(Boolean),
          borderColor: getChartColors.prediction('vertexai'),
          backgroundColor: getChartColors.prediction('vertexai') + '20',
          borderWidth: 2,
          pointRadius: 3,
          borderDash: [5, 5],
          fill: false,
        });
    }

    if (chartType === 'future-prediction' || !showThumbnail) {
        datasets.push({
          label: 'LSTM未来予測',
          data: allDates.map(date => {
            const futurePred = data.futurePredictions.find(f => f.date === date);
            return futurePred ? { x: date, y: futurePred.lstm_prediction } : null;
          }).filter(Boolean),
          borderColor: CHART_COLORS.PREDICTIONS.ENSEMBLE,
          backgroundColor: CHART_COLORS.PREDICTIONS.ENSEMBLE + '30',
          borderWidth: 3,
          pointRadius: 4,
          fill: false,
        },
        {
          label: 'VertexAI未来予測',
          data: allDates.map(date => {
            const futurePred = data.futurePredictions.find(f => f.date === date);
            return futurePred ? { x: date, y: futurePred.vertexai_prediction } : null;
          }).filter(Boolean),
          borderColor: getChartColors.prediction('vertexai'),
          backgroundColor: getChartColors.prediction('vertexai') + '30',
          borderWidth: 3,
          pointRadius: 4,
          fill: false,
        });
    }

    return {
      labels: allDates,
      datasets,
    };
  }, [data, chartType, showThumbnail]);

  const chartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#ffffff',
          usePointStyle: true,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#374151',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: 'day' as const,
        },
        ticks: {
          color: '#9ca3af',
        },
        grid: {
          color: 'rgba(75, 85, 99, 0.3)',
        },
      },
      y: {
        ticks: {
          color: '#9ca3af',
          callback: function(value: any) {
            return '¥' + value.toLocaleString();
          },
        },
        grid: {
          color: 'rgba(75, 85, 99, 0.3)',
        },
      },
    },
  }), []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Brain className="w-8 h-8 text-purple-400 animate-spin mx-auto mb-2" />
          <p className="text-gray-400">AI予測を分析中...</p>
        </div>
      </div>
    );
  }

  if (showThumbnail) {
    return (
      <div className="h-24 relative">
        {chartData && (
          <StockChart data={chartData} options={{
            ...chartOptions,
            plugins: { ...chartOptions.plugins, legend: { display: false } },
            scales: {
              x: { display: false },
              y: { display: false }
            }
          }} />
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* パフォーマンス比較カード */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {modelPerformance.map((perf) => (
          <div key={perf.model} className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Brain className="w-5 h-5 text-blue-400" />
                <h3 className="text-white font-semibold">{perf.model}</h3>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                perf.risk_level === 'Low' ? 'bg-green-500/20 text-green-400' :
                perf.risk_level === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-red-500/20 text-red-400'
              }`}>
                {perf.risk_level} Risk
              </span>
            </div>
            
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <div className="text-gray-400">精度</div>
                <div className="text-white font-bold">{perf.accuracy_percentage.toFixed(1)}%</div>
              </div>
              <div>
                <div className="text-gray-400">MAS誤差</div>
                <div className="text-white font-bold">{perf.mae.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-gray-400">収益期待</div>
                <div className="text-green-400 font-bold">+{perf.profit_potential.toFixed(1)}%</div>
              </div>
              <div>
                <div className="text-gray-400">RMSE</div>
                <div className="text-white font-bold">{perf.rmse.toFixed(2)}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* メインチャート */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="h-96">
          {chartData && <StockChart data={chartData} options={chartOptions} />}
        </div>
      </div>

      {/* 投資推奨サマリー */}
      <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 border border-green-500/30 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <DollarSign className="w-6 h-6 text-green-400" />
          <h3 className="text-xl font-bold text-white">投資推奨</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">
              {modelPerformance.length > 0 ? modelPerformance[0].accuracy_percentage > modelPerformance[1]?.accuracy_percentage ? 'LSTM' : 'VertexAI' : 'AI'}
            </div>
            <div className="text-gray-400 text-sm">推奨モデル</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {modelPerformance.length > 0 ? Math.max(...modelPerformance.map(p => p.profit_potential)).toFixed(1) : '0'}%
            </div>
            <div className="text-gray-400 text-sm">期待収益</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">
              {modelPerformance.length > 0 ? (modelPerformance.reduce((sum, p) => sum + p.accuracy_percentage, 0) / modelPerformance.length).toFixed(1) : '0'}%
            </div>
            <div className="text-gray-400 text-sm">総合精度</div>
          </div>
        </div>
      </div>
    </div>
  );
}