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
        const response = await apiClient.getMarketIndices();
        
        if (response.success && response.data) {
          const marketData = Array.isArray(response.data) ? response.data : [];
          
          // APIデータを変換
          const transformedIndices: IndexData[] = marketData?.map((index: any) => ({
            name: getJapaneseName(index.index),
            value: index.current_value,
            change: index.daily_change,
            changePercent: index.daily_change_percent,
            sparklineData: index.sparkline_data || []
          })) || [];
          
          setIndices(transformedIndices);
        } else {
          // API失敗時は空配列
          setIndices([]);
        }
      } catch (error) {
        console.error('市場データ取得エラー:', error);
        setIndices([]);
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