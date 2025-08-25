'use client';

import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';
import apiClient from '@/lib/api-client';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip
);

interface IndexData {
  name: string;
  value: number;
  change: number;
  changePercent: number;
  sparklineData: number[];
}

export default function MarketIndexSummary() {
  const [indices, setIndices] = useState<IndexData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        setLoading(true);
        const response = await apiClient.request('/api/analytics/market-overview');
        
        if (response.status === 'success' && response.data) {
          const marketData = response.data;
          
          // APIデータを変換
          const transformedIndices: IndexData[] = marketData.market_indices?.map((index: any) => ({
            name: getJapaneseName(index.index),
            value: index.current_value,
            change: index.daily_change,
            changePercent: index.daily_change_percent,
            sparklineData: generateSparklineData(index.current_value, index.daily_change_percent)
          })) || [];
          
          setIndices(transformedIndices);
        } else {
          // API失敗時のフォールバック
          setIndices(getFallbackData());
        }
      } catch (error) {
        console.error('市場データ取得エラー:', error);
        setIndices(getFallbackData());
      } finally {
        setLoading(false);
      }
    };
    
    fetchMarketData();
  }, []);

  function getJapaneseName(indexSymbol: string): string {
    const nameMap: { [key: string]: string } = {
      'SP500': 'S&P 500',
      'NASDAQ': 'NASDAQ',
      'DOW': 'NYダウ',
      'NIKKEI': '日経平均225',
      'FTSE': 'FTSE 100'
    };
    return nameMap[indexSymbol] || indexSymbol;
  }

  function getFallbackData(): IndexData[] {
    return [
      {
        name: '日経平均225',
        value: 39123.45,
        change: 123.45,
        changePercent: 0.32,
        sparklineData: generateSparklineData(39000, 0.32)
      },
      {
        name: 'TOPIX',
        value: 2781.45,
        change: -12.34,
        changePercent: -0.44,
        sparklineData: generateSparklineData(2780, -0.44)
      },
      {
        name: 'NYダウ',
        value: 38456.78,
        change: 234.56,
        changePercent: 0.61,
        sparklineData: generateSparklineData(38400, 0.61)
      },
      {
        name: 'NASDAQ',
        value: 15234.12,
        change: 45.67,
        changePercent: 0.30,
        sparklineData: generateSparklineData(15200, 0.30)
      }
    ];
  }

  function generateSparklineData(base: number, changePercent: number): number[] {
    const data = [];
    let current = base * (1 - Math.abs(changePercent) / 100);
    for (let i = 0; i < 24; i++) {
      current += (Math.random() - 0.5) * base * 0.001;
      data.push(current);
    }
    // 最終値を現在値に設定
    data[data.length - 1] = base;
    return data;
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-white flex items-center">
        <Activity className="w-5 h-5 mr-2 text-blue-400" />
        主要指数サマリー
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading ? (
          <div className="col-span-full flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
          </div>
        ) : (
          indices.map((index) => (
            <IndexCard key={index.name} data={index} />
          ))
        )}
      </div>
    </div>
  );
}

interface IndexCardProps {
  data: IndexData;
}

function IndexCard({ data }: IndexCardProps) {
  const isPositive = data.changePercent >= 0;
  
  // スパークラインチャート設定
  const chartData = {
    labels: Array(24).fill(''),
    datasets: [{
      data: data.sparklineData,
      borderColor: isPositive ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)',
      backgroundColor: isPositive ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
      borderWidth: 1.5,
      fill: true,
      tension: 0.4,
      pointRadius: 0,
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false }
    },
    scales: {
      x: { display: false },
      y: { display: false }
    }
  };

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4 hover:border-blue-500/30 transition-all">
      <div className="mb-3">
        <div className="text-sm text-gray-400 mb-1">{data.name}</div>
        <div className="text-2xl font-bold text-white">
          {data.value.toLocaleString('ja-JP', { 
            minimumFractionDigits: 2,
            maximumFractionDigits: 2 
          })}
        </div>
        <div className={`flex items-center space-x-1 text-sm ${
          isPositive ? 'text-green-400' : 'text-red-400'
        }`}>
          {isPositive ? (
            <TrendingUp className="w-4 h-4" />
          ) : (
            <TrendingDown className="w-4 h-4" />
          )}
          <span>
            {isPositive ? '+' : ''}{data.change.toFixed(2)}
            ({isPositive ? '+' : ''}{data.changePercent.toFixed(2)}%)
          </span>
        </div>
      </div>
      
      {/* スパークラインチャート */}
      <div className="h-12">
        <Line data={chartData} options={chartOptions} />
      </div>
    </div>
  );
}