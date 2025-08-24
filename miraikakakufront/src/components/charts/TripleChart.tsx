'use client';

import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
);

interface TripleChartProps {
  symbol: string;
  historicalData?: number[];
  pastPredictionData?: number[];
  futurePredictionData?: number[];
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

interface ChartData {
  data: number[];
  label: string;
  color: string;
  borderColor: string;
  backgroundColor?: string;
}

export default function TripleChart({ 
  symbol, 
  historicalData, 
  pastPredictionData, 
  futurePredictionData,
  className = '',
  size = 'md'
}: TripleChartProps) {
  // デフォルトデータを生成（APIからのデータが無い場合）
  const generateMockData = (baseValue: number, trend: 'up' | 'down' | 'flat' = 'flat', length: number = 30): number[] => {
    const data = [];
    let current = baseValue;
    
    for (let i = 0; i < length; i++) {
      const trendFactor = trend === 'up' ? 0.001 : trend === 'down' ? -0.001 : 0;
      const randomFactor = (Math.random() - 0.5) * 0.05;
      current = current * (1 + trendFactor + randomFactor);
      data.push(current);
    }
    
    return data;
  };

  const basePrice = 100; // 基準価格
  
  const charts: ChartData[] = [
    {
      data: historicalData || generateMockData(basePrice, 'up', 30),
      label: '実績',
      color: 'rgba(34, 197, 94, 0.8)', // green
      borderColor: 'rgba(34, 197, 94, 1)',
      backgroundColor: 'rgba(34, 197, 94, 0.1)'
    },
    {
      data: pastPredictionData || generateMockData(basePrice * 0.95, 'up', 30),
      label: '過去予測',
      color: 'rgba(59, 130, 246, 0.8)', // blue
      borderColor: 'rgba(59, 130, 246, 1)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)'
    },
    {
      data: futurePredictionData || generateMockData(basePrice * 1.05, 'up', 30),
      label: '未来予測',
      color: 'rgba(147, 51, 234, 0.8)', // purple
      borderColor: 'rgba(147, 51, 234, 1)',
      backgroundColor: 'rgba(147, 51, 234, 0.1)'
    }
  ];

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'h-16 w-20';
      case 'md':
        return 'h-20 w-24';
      case 'lg':
        return 'h-24 w-32';
      default:
        return 'h-20 w-24';
    }
  };

  const getMiniChart = (chartData: ChartData, index: number) => {
    const data = {
      labels: chartData.data.map((_, i) => ''),
      datasets: [{
        data: chartData.data,
        borderColor: chartData.borderColor,
        backgroundColor: chartData.backgroundColor,
        borderWidth: 1.5,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 3,
        fill: true
      }]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: 'white',
          bodyColor: 'white',
          borderColor: chartData.borderColor,
          borderWidth: 1,
          displayColors: false,
          callbacks: {
            title: () => chartData.label,
            label: (context: any) => {
              const value = context.parsed.y;
              return symbol.match(/^[A-Z]+$/) 
                ? `$${value.toFixed(2)}`
                : `¥${Math.round(value).toLocaleString()}`;
            }
          }
        }
      },
      scales: {
        x: { display: false },
        y: { display: false }
      },
      interaction: {
        intersect: false,
        mode: 'index' as const
      }
    };

    return (
      <div key={index} className="flex flex-col items-center space-y-2">
        <div className={`${getSizeClasses()} relative`}>
          <Line data={data} options={options} />
        </div>
        <div className="text-center">
          <div className={`text-xs font-medium text-white ${size === 'sm' ? 'text-[10px]' : ''}`}>
            {chartData.label}
          </div>
          <div 
            className={`text-xs opacity-75 ${size === 'sm' ? 'text-[9px]' : ''}`}
            style={{ color: chartData.borderColor }}
          >
            {getPerformanceIndicator(chartData.data)}
          </div>
        </div>
      </div>
    );
  };

  const getPerformanceIndicator = (data: number[]): string => {
    if (data.length < 2) return '';
    
    const start = data[0];
    const end = data[data.length - 1];
    const change = ((end - start) / start) * 100;
    
    return `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`;
  };

  return (
    <div className={`flex items-center space-x-4 ${className}`}>
      {charts.map((chart, index) => getMiniChart(chart, index))}
    </div>
  );
}

// スタンドアロン版のTripleChart（単一チャート表示用）
export function SingleChart({ 
  data, 
  label, 
  color, 
  symbol, 
  className = '',
  height = 100 
}: {
  data: number[];
  label: string;
  color: string;
  symbol: string;
  className?: string;
  height?: number;
}) {
  const chartData = {
    labels: data.map((_, i) => ''),
    datasets: [{
      data,
      borderColor: color,
      backgroundColor: color.replace('1)', '0.1)'),
      borderWidth: 2,
      tension: 0.4,
      pointRadius: 0,
      pointHoverRadius: 4,
      fill: true
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        enabled: true,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: color,
        borderWidth: 1,
        displayColors: false,
        callbacks: {
          title: () => label,
          label: (context: any) => {
            const value = context.parsed.y;
            return symbol.match(/^[A-Z]+$/) 
              ? `$${value.toFixed(2)}`
              : `¥${Math.round(value).toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      x: { display: false },
      y: { display: false }
    },
    interaction: {
      intersect: false,
      mode: 'index' as const
    }
  };

  return (
    <div className={`relative ${className}`} style={{ height }}>
      <Line data={chartData} options={options} />
      <div className="absolute top-2 left-2 text-xs font-medium text-white bg-black/50 px-2 py-1 rounded">
        {label}
      </div>
    </div>
  );
}