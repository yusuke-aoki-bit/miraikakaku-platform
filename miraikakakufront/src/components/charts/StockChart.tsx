'use client';

import React, { useState, useEffect } from 'react';
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
  TimeScale,
  Filler,
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import LoadingSpinner from '../common/LoadingSpinner';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler
);

interface StockChartProps {
  symbol: string;
}

interface PriceData {
  date: string;
  open_price?: number;
  high_price?: number;
  low_price?: number;
  close_price: number;
  volume?: number;
}

interface PredictionData {
  date: string;
  predicted_price: number;
  confidence: number;
  upper_bound: number;
  lower_bound: number;
}

interface HistoricalPredictionData {
  date: string;
  predicted_price: number;
  actual_price: number;
  accuracy: number;
  confidence: number;
}

export default function StockChart({ symbol }: StockChartProps) {
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [predictionData, setPredictionData] = useState<PredictionData[]>([]);
  const [historicalPredictions, setHistoricalPredictions] = useState<HistoricalPredictionData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (symbol) {
      fetchPriceData(symbol);
      fetchPredictionData(symbol);
      fetchHistoricalPredictions(symbol);
    }
  }, [symbol]);

  const fetchPriceData = async (stockSymbol: string) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_DATAFEED_URL}/price/${stockSymbol}?days=30`
      );
      
      if (response.ok) {
        const data = await response.json();
        setPriceData(data);
      } else {
        throw new Error(`API Error: ${response.status}`);
      }
    } catch (error) {
      console.error('価格データ取得エラー:', error);
      setError('データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const fetchPredictionData = async (stockSymbol: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_DATAFEED_URL}/api/finance/stocks/${stockSymbol}/predictions?days=7`
      );
      
      if (response.ok) {
        const data = await response.json();
        setPredictionData(data);
      }
    } catch (error) {
      console.error('予測データ取得エラー:', error);
    }
  };

  const fetchHistoricalPredictions = async (stockSymbol: string) => {
    try {
      // For now, generate mock historical data since the endpoint is not ready
      const mockHistoricalData = Array.from({length: 7}, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (7 - i));
        return {
          date: date.toISOString().split('T')[0],
          predicted_price: 230 + Math.random() * 20 - 10,
          actual_price: 230 + Math.random() * 20 - 10,
          accuracy: 0.7 + Math.random() * 0.2,
          confidence: 0.6 + Math.random() * 0.3
        };
      });
      setHistoricalPredictions(mockHistoricalData);
    } catch (error) {
      console.error('過去予測データ取得エラー:', error);
      setHistoricalPredictions([]); // Fallback to empty array
    }
  };

  const allDates = [
    ...priceData.map(d => d.date), 
    ...predictionData.map(d => d.date),
    ...historicalPredictions.map(d => d.date)
  ];
  const uniqueDates = [...new Set(allDates)].sort();

  const chartData = {
    labels: uniqueDates,
    datasets: [
      {
        label: `${symbol} 実測値`,
        data: uniqueDates.map(date => {
          const pricePoint = priceData.find(d => d.date === date);
          return pricePoint ? pricePoint.close_price : null;
        }),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.1,
        fill: false,
        pointRadius: 3,
      },
      {
        label: `${symbol} AI予測`,
        data: uniqueDates.map(date => {
          const predPoint = predictionData.find(d => d.date === date);
          return predPoint ? predPoint.predicted_price : null;
        }),
        borderColor: 'rgb(255, 99, 71)',
        backgroundColor: 'rgba(255, 99, 71, 0.1)',
        tension: 0.1,
        fill: false,
        borderDash: [5, 5],
        pointRadius: 3,
      },
      {
        label: `${symbol} 予測上限`,
        data: uniqueDates.map(date => {
          const predPoint = predictionData.find(d => d.date === date);
          return predPoint ? predPoint.upper_bound : null;
        }),
        borderColor: 'rgba(255, 99, 71, 0.3)',
        backgroundColor: 'rgba(255, 99, 71, 0.05)',
        tension: 0.1,
        fill: '+1',
        pointRadius: 0,
        borderWidth: 1,
      },
      {
        label: `${symbol} 予測下限`,
        data: uniqueDates.map(date => {
          const predPoint = predictionData.find(d => d.date === date);
          return predPoint ? predPoint.lower_bound : null;
        }),
        borderColor: 'rgba(255, 99, 71, 0.3)',
        backgroundColor: 'rgba(255, 99, 71, 0.05)',
        tension: 0.1,
        fill: false,
        pointRadius: 0,
        borderWidth: 1,
      },
      {
        label: `${symbol} 過去予測`,
        data: uniqueDates.map(date => {
          const histPred = historicalPredictions.find(d => d.date === date);
          return histPred ? histPred.predicted_price : null;
        }),
        borderColor: 'rgb(147, 51, 234)',
        backgroundColor: 'rgba(147, 51, 234, 0.1)',
        tension: 0.1,
        fill: false,
        borderDash: [3, 3],
        pointRadius: 2,
        pointBackgroundColor: function(context: any) {
          const date = uniqueDates[context.dataIndex];
          const histPred = historicalPredictions.find(d => d.date === date);
          if (histPred && histPred.accuracy > 0.8) return 'rgb(34, 197, 94)';
          if (histPred && histPred.accuracy > 0.6) return 'rgb(234, 179, 8)';
          return 'rgb(239, 68, 68)';
        },
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `${symbol} 株価チャート (30日間)`,
        font: {
          size: 16,
          weight: 'bold' as const,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `終値: $${context.parsed.y.toFixed(2)}`;
          },
        },
      },
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: 'day' as const,
          displayFormats: {
            day: 'MM/dd',
          },
        },
        title: {
          display: true,
          text: '日付',
        },
      },
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: '価格 ($)',
        },
        ticks: {
          callback: function(value: any) {
            return '$' + value.toFixed(2);
          },
        },
      },
    },
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 youtube-card">
        <LoadingSpinner 
          type="chart" 
          size="lg" 
          message="株価チャートを読み込み中..."
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96 bg-red-50 rounded-lg">
        <div className="text-center text-red-600">
          <div className="text-lg font-semibold mb-2">エラー</div>
          <div>{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-96 p-4 youtube-card">
      <Line data={chartData} options={options} />
    </div>
  );
}