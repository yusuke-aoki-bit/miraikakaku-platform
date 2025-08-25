'use client';

import React, { memo } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface ChartDataPoint {
  date: string;
  value: number;
  type: 'actual' | 'historical_prediction' | 'future_prediction';
}

interface IndexChartProps {
  data: ChartDataPoint[];
}

const IndexChart = memo(function IndexChart({ data }: IndexChartProps) {
  // データを種類別に分離
  const actualData = data.filter(d => d.type === 'actual');
  const historicalPredictions = data.filter(d => d.type === 'historical_prediction');
  const futurePredictions = data.filter(d => d.type === 'future_prediction');
  
  // すべてのデータを日付順にソート
  const sortedData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  
  // 各データポイントに対応する値を設定
  const chartData = sortedData.map(point => {
    const actual = actualData.find(d => d.date === point.date);
    const historical = historicalPredictions.find(d => d.date === point.date);
    const future = futurePredictions.find(d => d.date === point.date);
    
    return {
      date: point.date,
      actual: actual?.value || null,
      historical: historical?.value || null,
      future: future?.value || null,
    };
  });

  // データの最小値と最大値を計算してY軸のドメインを設定
  const values = data.map(d => d.value);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const padding = (maxValue - minValue) * 0.1; // 10%のパディング
  const yDomain = [minValue - padding, maxValue + padding];

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis 
          dataKey="date" 
          tick={{ fontSize: 12, fill: '#9CA3AF' }}
          tickFormatter={(value) => {
            const date = new Date(value);
            return `${date.getMonth() + 1}/${date.getDate()}`;
          }}
        />
        <YAxis 
          domain={yDomain}
          tick={{ fontSize: 12, fill: '#9CA3AF' }}
          tickFormatter={(value) => value.toLocaleString()}
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: '#1F2937',
            border: '1px solid #374151',
            borderRadius: '8px',
            color: '#F9FAFB'
          }}
          formatter={(value: any, name: string) => {
            if (value === null) return ['---', name];
            const labels = {
              actual: '実測値',
              historical: '過去予測',
              future: '未来予測'
            };
            return [value.toLocaleString(), labels[name as keyof typeof labels] || name];
          }}
          labelFormatter={(label) => `日付: ${label}`}
        />
        
        {/* 実測値 */}
        <Area
          type="monotone"
          dataKey="actual"
          stroke="#2196F3"
          fill="url(#actualGradient)"
          strokeWidth={2}
          connectNulls={false}
        />
        
        {/* 過去予測 */}
        <Area
          type="monotone"
          dataKey="historical"
          stroke="#10B981"
          fill="url(#historicalGradient)"
          strokeWidth={2}
          strokeDasharray="5 5"
          connectNulls={false}
        />
        
        {/* 未来予測 */}
        <Area
          type="monotone"
          dataKey="future"
          stroke="#8B5CF6"
          fill="url(#futureGradient)"
          strokeWidth={2}
          strokeDasharray="3 3"
          connectNulls={false}
        />
        
        <defs>
          <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#2196F3" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#2196F3" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="historicalGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10B981" stopOpacity={0.2}/>
            <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="futureGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.2}/>
            <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
          </linearGradient>
        </defs>
      </AreaChart>
    </ResponsiveContainer>
  );
});

export default IndexChart;