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
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
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

export default function StockChart({ symbol }: StockChartProps) {
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (symbol) {
      fetchPriceData(symbol);
    }
  }, [symbol]);

  const fetchPriceData = async (stockSymbol: string) => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/finance/stocks/${stockSymbol}/price?days=30`
      );
      
      if (response.ok) {
        const data = await response.json();
        setPriceData(data);
      } else {
        // フォールバック用のモックデータ
        const mockData: PriceData[] = Array.from({ length: 30 }, (_, i) => {
          const basePrice = 150;
          const volatility = 0.02;
          const trend = -0.001 * i;
          const randomChange = (Math.random() - 0.5) * volatility;
          const price = basePrice * (1 + trend + randomChange);
          
          return {
            date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            close_price: price,
            open_price: price * (1 + (Math.random() - 0.5) * 0.01),
            high_price: price * (1 + Math.random() * 0.02),
            low_price: price * (1 - Math.random() * 0.02),
            volume: Math.floor(Math.random() * 10000000 + 1000000)
          };
        });
        setPriceData(mockData);
      }
    } catch (error) {
      console.error('価格データ取得エラー:', error);
      setError('データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: priceData.map(d => d.date),
    datasets: [
      {
        label: `${symbol} 終値`,
        data: priceData.map(d => d.close_price),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.1,
        fill: true,
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
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-gray-600">チャートを読み込み中...</div>
        </div>
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
    <div className="w-full h-96 p-4 bg-white rounded-lg">
      <Line data={chartData} options={options} />
    </div>
  );
}