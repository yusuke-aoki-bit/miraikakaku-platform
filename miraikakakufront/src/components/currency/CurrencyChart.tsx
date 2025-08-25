'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { TrendingUp, TrendingDown, Minus, BarChart3, Settings } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

// Chart.js登録
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface CurrencyChartProps {
  pair: string;
  timeframe?: '1H' | '4H' | '1D' | '1W';
  height?: number;
  showControls?: boolean;
  onTimeframeChange?: (timeframe: string) => void;
}

interface ChartData {
  labels: string[];
  historical: number[];
  predictions: number[];
  upperBound: number[];
  lowerBound: number[];
  supportLines: number[];
  resistanceLines: number[];
}

interface TechnicalLevel {
  level: number;
  type: 'support' | 'resistance';
  strength: number;
  description: string;
}

const TIMEFRAME_CONFIG = {
  '1H': { label: '1時間足', dataPoints: 60, interval: '1h' },
  '4H': { label: '4時間足', dataPoints: 72, interval: '4h' },
  '1D': { label: '日足', dataPoints: 30, interval: '1d' },
  '1W': { label: '週足', dataPoints: 12, interval: '1w' }
};

export default function CurrencyChart({
  pair,
  timeframe = '1D',
  height = 400,
  showControls = true,
  onTimeframeChange
}: CurrencyChartProps) {
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [technicalLevels, setTechnicalLevels] = useState<TechnicalLevel[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState(timeframe);
  const [showPredictions, setShowPredictions] = useState(true);
  const [showConfidenceBand, setShowConfidenceBand] = useState(true);
  const [showTechnicalLevels, setShowTechnicalLevels] = useState(true);
  const chartRef = useRef<any>(null);

  const fetchChartData = async () => {
    try {
      setLoading(true);
      
      const config = TIMEFRAME_CONFIG[selectedTimeframe];
      const [historyResponse, predictionsResponse] = await Promise.all([
        apiClient.getCurrencyHistory(pair, config.dataPoints),
        apiClient.getCurrencyPredictions(pair, selectedTimeframe, Math.floor(config.dataPoints * 0.3))
      ]);

      let historicalData: number[] = [];
      let labels: string[] = [];
      
      if (historyResponse.status === 'success' && historyResponse.data) {
        const historyArray = Array.isArray(historyResponse.data) ? historyResponse.data : [];
        historicalData = historyArray.map((d: any) => d.rate);
        labels = historyArray.map((d: any) => {
          const date = new Date(d.timestamp);
          if (selectedTimeframe === '1H' || selectedTimeframe === '4H') {
            return date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
          }
          return date.toLocaleDateString('ja-JP', { month: '2-digit', day: '2-digit' });
        });
      } else {
        // モックデータ生成
        const baseRate = pair === 'USD/JPY' ? 150 : 
                         pair === 'EUR/USD' ? 1.08 : 
                         pair === 'GBP/USD' ? 1.27 : 1.0;
        
        historicalData = [];
        labels = [];
        let current = baseRate;
        
        for (let i = 0; i < config.dataPoints; i++) {
          const volatility = 0.001 + Math.random() * 0.003; // 0.1%-0.4%の変動
          const change = (Math.random() - 0.5) * volatility * current;
          current = Math.max(current + change, baseRate * 0.95); // 最低でも5%以上は維持
          historicalData.push(current);
          
          // 時刻ラベル生成
          const time = new Date(Date.now() - (config.dataPoints - i) * (
            selectedTimeframe === '1H' ? 60000 :
            selectedTimeframe === '4H' ? 240000 :
            selectedTimeframe === '1D' ? 86400000 : 604800000
          ));
          
          if (selectedTimeframe === '1H' || selectedTimeframe === '4H') {
            labels.push(time.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }));
          } else {
            labels.push(time.toLocaleDateString('ja-JP', { month: '2-digit', day: '2-digit' }));
          }
        }
      }

      // 予測データ処理
      let predictionsData: number[] = [];
      let upperBoundData: number[] = [];
      let lowerBoundData: number[] = [];
      
      const predictionLength = Math.floor(config.dataPoints * 0.3);
      const lastHistoricalRate = historicalData[historicalData.length - 1];
      
      if (predictionsResponse.status === 'success' && predictionsResponse.data) {
        const predictionsArray = Array.isArray(predictionsResponse.data) ? predictionsResponse.data : [];
        predictionsData = predictionsArray.map((d: any) => d.predicted_rate);
        upperBoundData = predictionsArray.map((d: any) => d.upper_bound || d.predicted_rate * 1.002);
        lowerBoundData = predictionsArray.map((d: any) => d.lower_bound || d.predicted_rate * 0.998);
      } else {
        // モック予測データ
        const trendStrength = (Math.random() - 0.5) * 0.02; // -1% to +1% trend
        for (let i = 0; i < predictionLength; i++) {
          const progress = i / predictionLength;
          const trend = lastHistoricalRate * (1 + trendStrength * progress);
          const volatility = Math.random() * 0.001 * trend;
          const predicted = trend + (Math.random() - 0.5) * volatility;
          
          predictionsData.push(predicted);
          upperBoundData.push(predicted * (1 + 0.002 + Math.random() * 0.001));
          lowerBoundData.push(predicted * (1 - 0.002 - Math.random() * 0.001));
          
          // 予測期間のラベル追加
          const futureTime = new Date(Date.now() + i * (
            selectedTimeframe === '1H' ? 60000 :
            selectedTimeframe === '4H' ? 240000 :
            selectedTimeframe === '1D' ? 86400000 : 604800000
          ));
          
          if (selectedTimeframe === '1H' || selectedTimeframe === '4H') {
            labels.push(futureTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }));
          } else {
            labels.push(futureTime.toLocaleDateString('ja-JP', { month: '2-digit', day: '2-digit' }));
          }
        }
      }

      // テクニカルレベル計算
      const levels = calculateTechnicalLevels(historicalData, lastHistoricalRate);
      setTechnicalLevels(levels);

      // チャートデータ設定
      const fullHistorical = [...historicalData, ...new Array(predictionLength).fill(null)];
      const fullPredictions = [...new Array(historicalData.length).fill(null), ...predictionsData];
      const fullUpperBound = [...new Array(historicalData.length).fill(null), ...upperBoundData];
      const fullLowerBound = [...new Array(historicalData.length).fill(null), ...lowerBoundData];

      setChartData({
        labels,
        historical: fullHistorical,
        predictions: fullPredictions,
        upperBound: fullUpperBound,
        lowerBound: fullLowerBound,
        supportLines: levels.filter(l => l.type === 'support').map(l => l.level),
        resistanceLines: levels.filter(l => l.type === 'resistance').map(l => l.level)
      });

    } catch (error) {
      console.error('Failed to fetch chart data:', error);
    } finally {
      setLoading(false);
    }
  };

  // テクニカルレベル計算関数
  const calculateTechnicalLevels = (data: number[], currentRate: number): TechnicalLevel[] => {
    const levels: TechnicalLevel[] = [];
    const sortedData = [...data].sort((a, b) => a - b);
    const dataLength = data.length;
    
    // サポートレベル（下位20%、40%）
    const support1 = sortedData[Math.floor(dataLength * 0.2)];
    const support2 = sortedData[Math.floor(dataLength * 0.4)];
    
    // レジスタンスレベル（上位20%、40%）
    const resistance1 = sortedData[Math.floor(dataLength * 0.8)];
    const resistance2 = sortedData[Math.floor(dataLength * 0.6)];
    
    if (support1 < currentRate) {
      levels.push({
        level: support1,
        type: 'support',
        strength: 0.8,
        description: '強力なサポートライン'
      });
    }
    
    if (support2 < currentRate && Math.abs(support2 - support1) > currentRate * 0.01) {
      levels.push({
        level: support2,
        type: 'support',
        strength: 0.6,
        description: '中程度のサポートライン'
      });
    }
    
    if (resistance1 > currentRate) {
      levels.push({
        level: resistance1,
        type: 'resistance',
        strength: 0.8,
        description: '強力なレジスタンスライン'
      });
    }
    
    if (resistance2 > currentRate && Math.abs(resistance2 - resistance1) > currentRate * 0.01) {
      levels.push({
        level: resistance2,
        type: 'resistance',
        strength: 0.6,
        description: '中程度のレジスタンスライン'
      });
    }
    
    return levels;
  };

  useEffect(() => {
    fetchChartData();
  }, [pair, selectedTimeframe]);

  const handleTimeframeChange = (newTimeframe: keyof typeof TIMEFRAME_CONFIG) => {
    setSelectedTimeframe(newTimeframe);
    onTimeframeChange?.(newTimeframe);
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          color: 'white',
          font: { size: 12 },
          filter: (legendItem: any) => {
            // 設定に応じて表示/非表示を切り替え
            if (legendItem.text.includes('予測') && !showPredictions) return false;
            if (legendItem.text.includes('信頼区間') && !showConfidenceBand) return false;
            return true;
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(59, 130, 246, 0.5)',
        borderWidth: 1,
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            if (value === null) return '';
            
            const formattedValue = pair.includes('JPY') ? 
              value.toFixed(3) : value.toFixed(5);
            
            return `${label}: ${formattedValue}`;
          },
          afterBody: (tooltipItems: any[]) => {
            const index = tooltipItems[0]?.dataIndex;
            if (index !== undefined && chartData) {
              // 該当するテクニカルレベルがあるか確認
              const currentPrice = tooltipItems[0]?.parsed?.y;
              if (currentPrice) {
                const nearLevel = technicalLevels.find(level => 
                  Math.abs(level.level - currentPrice) < currentPrice * 0.002
                );
                if (nearLevel) {
                  return [`📍 ${nearLevel.description}`];
                }
              }
            }
            return [];
          }
        }
      }
    },
    scales: {
      x: {
        grid: { 
          color: 'rgba(255, 255, 255, 0.1)',
          drawOnChartArea: true 
        },
        ticks: { 
          color: 'gray', 
          maxTicksLimit: 8,
          font: { size: 11 }
        }
      },
      y: {
        grid: { 
          color: 'rgba(255, 255, 255, 0.1)',
          drawOnChartArea: true 
        },
        ticks: { 
          color: 'gray',
          callback: (value: any) => {
            return pair.includes('JPY') ? value.toFixed(2) : value.toFixed(4);
          },
          font: { size: 11 }
        }
      }
    },
    elements: {
      line: {
        tension: 0.1
      },
      point: {
        radius: 0,
        hoverRadius: 4
      }
    }
  };

  // チャートデータセット構築
  const buildDatasets = () => {
    if (!chartData) return [];
    
    const datasets: any[] = [
      {
        label: '実績レート',
        data: chartData.historical,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        borderWidth: 2,
        fill: false,
        pointRadius: 0,
        pointHoverRadius: 4,
      }
    ];

    if (showPredictions) {
      datasets.push({
        label: 'AI予測',
        data: chartData.predictions,
        borderColor: 'rgb(255, 159, 64)',
        backgroundColor: 'rgba(255, 159, 64, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5],
        fill: false,
        pointRadius: 0,
        pointHoverRadius: 4,
      });
    }

    if (showConfidenceBand && showPredictions) {
      datasets.push(
        {
          label: '信頼区間（上限）',
          data: chartData.upperBound,
          borderColor: 'rgba(255, 99, 132, 0.3)',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          borderWidth: 1,
          borderDash: [2, 2],
          fill: false,
          pointRadius: 0,
        },
        {
          label: '信頼区間（下限）',
          data: chartData.lowerBound,
          borderColor: 'rgba(54, 162, 235, 0.3)',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          borderWidth: 1,
          borderDash: [2, 2],
          fill: false,
          pointRadius: 0,
        }
      );
    }

    // テクニカルレベル線（サポート・レジスタンス）
    if (showTechnicalLevels) {
      technicalLevels.forEach((level, index) => {
        datasets.push({
          label: `${level.type === 'support' ? 'サポート' : 'レジスタンス'} ${level.level.toFixed(pair.includes('JPY') ? 2 : 4)}`,
          data: new Array(chartData.labels.length).fill(level.level),
          borderColor: level.type === 'support' ? 
            `rgba(34, 197, 94, ${level.strength})` : 
            `rgba(239, 68, 68, ${level.strength})`,
          backgroundColor: 'transparent',
          borderWidth: 1,
          borderDash: [10, 5],
          fill: false,
          pointRadius: 0,
          tension: 0
        });
      });
    }

    return datasets;
  };

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="flex items-center justify-center" style={{ height: height }}>
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-400 border-t-transparent"></div>
          <span className="ml-3 text-gray-400">チャートデータを読み込み中...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
      {/* チャートヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <BarChart3 className="w-6 h-6 text-blue-400" />
          <h3 className="text-lg font-semibold text-white">{pair} チャート</h3>
        </div>
        
        {showControls && (
          <div className="flex items-center space-x-4">
            {/* チャート設定 */}
            <div className="flex items-center space-x-2">
              <Settings className="w-4 h-4 text-gray-400" />
              <div className="flex space-x-1">
                <button
                  onClick={() => setShowPredictions(!showPredictions)}
                  className={`px-2 py-1 text-xs rounded ${
                    showPredictions ? 'bg-blue-500/20 text-blue-400' : 'bg-gray-800 text-gray-400'
                  }`}
                >
                  予測
                </button>
                <button
                  onClick={() => setShowConfidenceBand(!showConfidenceBand)}
                  className={`px-2 py-1 text-xs rounded ${
                    showConfidenceBand ? 'bg-purple-500/20 text-purple-400' : 'bg-gray-800 text-gray-400'
                  }`}
                >
                  信頼区間
                </button>
                <button
                  onClick={() => setShowTechnicalLevels(!showTechnicalLevels)}
                  className={`px-2 py-1 text-xs rounded ${
                    showTechnicalLevels ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-800 text-gray-400'
                  }`}
                >
                  テクニカル
                </button>
              </div>
            </div>
            
            {/* タイムフレーム選択 */}
            <div className="flex space-x-1">
              {(Object.keys(TIMEFRAME_CONFIG) as Array<keyof typeof TIMEFRAME_CONFIG>).map((tf) => (
                <button
                  key={tf}
                  onClick={() => handleTimeframeChange(tf)}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    selectedTimeframe === tf
                      ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* チャート */}
      <div style={{ height: height }}>
        {chartData ? (
          <Line
            ref={chartRef}
            data={{
              labels: chartData.labels,
              datasets: buildDatasets()
            }}
            options={chartOptions}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            チャートデータが利用できません
          </div>
        )}
      </div>

      {/* テクニカルレベル情報 */}
      {showTechnicalLevels && technicalLevels.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-800">
          <h4 className="text-sm font-medium text-white mb-2">主要テクニカルレベル</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
            {technicalLevels.map((level, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-800/30 rounded">
                <span className={level.type === 'support' ? 'text-green-400' : 'text-red-400'}>
                  {level.type === 'support' ? '📈' : '📉'} {level.description}
                </span>
                <span className="text-white font-mono">
                  {level.level.toFixed(pair.includes('JPY') ? 2 : 4)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}