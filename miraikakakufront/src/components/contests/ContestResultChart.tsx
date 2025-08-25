'use client';

import React from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine,
  Cell
} from 'recharts';
import { Target, TrendingUp, Users } from 'lucide-react';

interface PredictionDistribution {
  range: string;
  count: number;
  percentage: number;
}

interface ContestResultChartProps {
  actualResult: number;
  distribution: PredictionDistribution[];
  userPrediction?: number;
}

export default function ContestResultChart({ 
  actualResult, 
  distribution, 
  userPrediction 
}: ContestResultChartProps) {
  
  // データを可視化用に変換
  const chartData = distribution.map(item => ({
    ...item,
    rangeMidpoint: parseFloat(item.range.split('-')[0]) + 
                   (parseFloat(item.range.split('-')[1]) - parseFloat(item.range.split('-')[0])) / 2
  }));

  // ユーザーの予測がどの範囲に入るかを計算
  const getUserPredictionRange = () => {
    if (!userPrediction) return null;
    
    return distribution.find(item => {
      const [min, max] = item.range.split('-').map(parseFloat);
      return userPrediction >= min && userPrediction < max;
    });
  };

  const userRange = getUserPredictionRange();

  // カスタムツールチップ
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-gray-800 border border-gray-600 rounded-lg p-3 shadow-lg">
          <p className="text-white font-medium mb-1">
            予測範囲: {data.range}
          </p>
          <p className="text-blue-400">
            参加者数: {data.count}人
          </p>
          <p className="text-gray-300">
            割合: {data.percentage.toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  // 最大値を取得してY軸の範囲を設定
  const maxCount = Math.max(...distribution.map(d => d.count));

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-white flex items-center">
          <BarChart className="w-6 h-6 mr-2 text-blue-400" />
          予測分布分析
        </h3>
        
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded"></div>
            <span className="text-gray-300">実際の結果</span>
          </div>
          {userPrediction && (
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-purple-400 rounded"></div>
              <span className="text-gray-300">あなたの予測</span>
            </div>
          )}
        </div>
      </div>

      {/* チャート */}
      <div className="h-80 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" strokeOpacity={0.3} />
            <XAxis 
              dataKey="range"
              tick={{ fontSize: 12, fill: '#9CA3AF' }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis 
              tick={{ fontSize: 12, fill: '#9CA3AF' }}
              label={{ value: '参加者数', angle: -90, position: 'insideLeft', style: { fill: '#9CA3AF' } }}
            />
            <Tooltip content={<CustomTooltip />} />
            
            {/* 実際の結果を示す縦線 */}
            <ReferenceLine 
              x={actualResult} 
              stroke="#10b981" 
              strokeWidth={3}
              strokeDasharray="none"
              label={{ value: "実際の結果", position: "top" }}
            />
            
            {/* ユーザーの予測を示す縦線 */}
            {userPrediction && (
              <ReferenceLine 
                x={userPrediction} 
                stroke="#8b5cf6" 
                strokeWidth={2}
                strokeDasharray="5 5"
                label={{ value: "あなたの予測", position: "top" }}
              />
            )}
            
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => {
                // ユーザーの予測範囲を強調表示
                const isUserRange = userRange && entry.range === userRange.range;
                return (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={isUserRange ? '#8b5cf6' : '#3b82f6'}
                  />
                );
              })}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 統計サマリー */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800/30 rounded-lg p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            <Target className="w-5 h-5 text-green-400 mr-2" />
            <span className="text-sm text-gray-400">実際の結果</span>
          </div>
          <div className="text-xl font-bold text-green-400">
            {actualResult.toLocaleString()}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            最も近い予測との差: {Math.abs(actualResult - parseFloat(distribution.find(d => d.count === Math.max(...distribution.map(d => d.count)))?.range.split('-')[0] || '0')).toFixed(1)}
          </div>
        </div>

        <div className="bg-gray-800/30 rounded-lg p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            <Users className="w-5 h-5 text-blue-400 mr-2" />
            <span className="text-sm text-gray-400">最多予測範囲</span>
          </div>
          <div className="text-lg font-bold text-blue-400">
            {distribution.reduce((max, current) => current.count > max.count ? current : max).range}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {distribution.reduce((max, current) => current.count > max.count ? current : max).count}人 
            ({distribution.reduce((max, current) => current.count > max.count ? current : max).percentage.toFixed(1)}%)
          </div>
        </div>

        {userPrediction && userRange && (
          <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <TrendingUp className="w-5 h-5 text-purple-400 mr-2" />
              <span className="text-sm text-gray-400">あなたの予測</span>
            </div>
            <div className="text-lg font-bold text-purple-400">
              {userPrediction.toLocaleString()}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              同じ範囲の予測者: {userRange.count}人 ({userRange.percentage.toFixed(1)}%)
            </div>
          </div>
        )}
      </div>

      {/* 分析コメント */}
      <div className="mt-6 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
        <div className="flex items-start space-x-3">
          <Target className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-blue-400 mb-1">分析結果</h4>
            <div className="text-sm text-gray-300 space-y-1">
              <p>
                • 参加者の{distribution.reduce((max, current) => current.count > max.count ? current : max).percentage.toFixed(1)}%が
                {distribution.reduce((max, current) => current.count > max.count ? current : max).range}の範囲で予測
              </p>
              <p>
                • 予測の標準偏差は{((Math.max(...distribution.map(d => parseFloat(d.range.split('-')[1]))) - 
                Math.min(...distribution.map(d => parseFloat(d.range.split('-')[0])))) / 6).toFixed(1)}程度
              </p>
              {userPrediction && (
                <p>
                  • あなたの予測は実際の結果から{Math.abs(userPrediction - actualResult).toFixed(1)}の差
                  （的中率: {(100 - Math.abs(userPrediction - actualResult) / actualResult * 100).toFixed(2)}%）
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}