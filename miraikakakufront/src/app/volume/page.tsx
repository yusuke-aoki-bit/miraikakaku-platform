'use client';

import React, { useState } from 'react';
import VolumeChart from '@/components/charts/VolumeChart';
import StockSearch from '@/components/StockSearch';
import { BarChart3, TrendingUp, Activity, Clock } from 'lucide-react';

export default function VolumePage() {
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [period, setPeriod] = useState<'day' | 'week' | 'month' | 'year'>('month');

  return (
    <div className="p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white flex items-center">
          <BarChart3 className="w-6 h-6 mr-2 text-green-400" />
          出来高分析
        </h1>
        
        {/* 期間選択 */}
        <div className="flex space-x-2">
          {(['day', 'week', 'month', 'year'] as const).map(p => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                period === p 
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
              }`}
            >
              {p === 'day' ? '1日' : p === 'week' ? '1週間' : p === 'month' ? '1ヶ月' : '1年'}
            </button>
          ))}
        </div>
      </div>

      {/* サマリーカード */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-green-900/20 to-emerald-900/20 border border-green-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <Activity className="w-5 h-5 text-green-400" />
            <span className="text-xs text-green-400">+12.5%</span>
          </div>
          <div className="text-2xl font-bold text-white">125.4M</div>
          <div className="text-sm text-gray-400">本日の出来高</div>
        </div>

        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            <span className="text-xs text-blue-400">標準</span>
          </div>
          <div className="text-2xl font-bold text-white">98.2M</div>
          <div className="text-sm text-gray-400">平均出来高</div>
        </div>

        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <BarChart3 className="w-5 h-5 text-purple-400" />
            <span className="text-xs text-purple-400">予測</span>
          </div>
          <div className="text-2xl font-bold text-white">132.8M</div>
          <div className="text-sm text-gray-400">明日の予測</div>
        </div>

        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <Clock className="w-5 h-5 text-yellow-400" />
            <span className="text-xs text-yellow-400">85%</span>
          </div>
          <div className="text-2xl font-bold text-white">14:30</div>
          <div className="text-sm text-gray-400">ピーク時刻</div>
        </div>
      </div>

      {/* 銘柄選択 */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">銘柄選択</h2>
        <StockSearch onSymbolSelect={setSelectedSymbol} />
        <div className="mt-2 text-sm text-gray-400">
          選択中: <span className="text-white font-medium">{selectedSymbol}</span>
        </div>
      </div>

      {/* 出来高チャート */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">
            {selectedSymbol} - 出来高チャート
          </h2>
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-400 rounded"></div>
              <span className="text-gray-400">実績</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-orange-400 rounded"></div>
              <span className="text-gray-400">予測</span>
            </div>
          </div>
        </div>
        
        <VolumeChart 
          symbol={selectedSymbol} 
          period={period}
          showPredictions={true}
        />
      </div>

      {/* 出来高パターン分析 */}
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">出来高パターン分析</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-3">時間帯別出来高</h3>
            <div className="space-y-2">
              {[
                { time: '09:00-10:00', volume: 85, color: 'bg-blue-500' },
                { time: '10:00-11:00', volume: 65, color: 'bg-blue-400' },
                { time: '11:00-12:00', volume: 45, color: 'bg-gray-500' },
                { time: '13:00-14:00', volume: 55, color: 'bg-gray-500' },
                { time: '14:00-15:00', volume: 95, color: 'bg-green-500' },
                { time: '15:00-16:00', volume: 100, color: 'bg-green-600' },
              ].map(item => (
                <div key={item.time} className="flex items-center space-x-3">
                  <span className="text-xs text-gray-400 w-24">{item.time}</span>
                  <div className="flex-1 bg-gray-800 rounded-full h-4 overflow-hidden">
                    <div 
                      className={`h-full ${item.color} transition-all duration-500`}
                      style={{ width: `${item.volume}%` }}
                    />
                  </div>
                  <span className="text-xs text-white w-12 text-right">{item.volume}%</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-3">曜日別平均出来高</h3>
            <div className="space-y-2">
              {[
                { day: '月曜日', volume: 88, trend: 'up' },
                { day: '火曜日', volume: 92, trend: 'up' },
                { day: '水曜日', volume: 95, trend: 'up' },
                { day: '木曜日', volume: 85, trend: 'down' },
                { day: '金曜日', volume: 78, trend: 'down' },
              ].map(item => (
                <div key={item.day} className="flex items-center space-x-3">
                  <span className="text-xs text-gray-400 w-24">{item.day}</span>
                  <div className="flex-1 bg-gray-800 rounded-full h-4 overflow-hidden">
                    <div 
                      className={`h-full ${item.trend === 'up' ? 'bg-green-500' : 'bg-red-500'} transition-all duration-500`}
                      style={{ width: `${item.volume}%` }}
                    />
                  </div>
                  <span className="text-xs text-white w-12 text-right">
                    {item.volume}M
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* AI分析 */}
      <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-xl p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Activity className="w-5 h-5 text-purple-400" />
          <h2 className="text-lg font-semibold text-white">AI出来高分析</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-black/30 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">異常検知</div>
            <div className="text-lg font-semibold text-yellow-400">注意</div>
            <div className="text-xs text-gray-400 mt-1">
              通常の1.5倍の出来高を検出
            </div>
          </div>
          
          <div className="bg-black/30 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">トレンド予測</div>
            <div className="text-lg font-semibold text-green-400">上昇</div>
            <div className="text-xs text-gray-400 mt-1">
              今後3日間で出来高増加予測
            </div>
          </div>
          
          <div className="bg-black/30 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">相関分析</div>
            <div className="text-lg font-semibold text-blue-400">0.82</div>
            <div className="text-xs text-gray-400 mt-1">
              価格と出来高の相関係数
            </div>
          </div>
        </div>
        
        <div className="mt-4 p-4 bg-black/30 rounded-lg">
          <div className="text-sm text-purple-400 font-medium mb-2">AIレポート</div>
          <p className="text-sm text-gray-300 leading-relaxed">
            {selectedSymbol}の出来高は過去30日間で平均を上回っており、特に午後の取引時間帯に集中しています。
            機関投資家の動きを示唆する大口取引が増加傾向にあり、今後の価格上昇の可能性が高いと予測されます。
            明日の予測出来高は132.8Mで、これは平均を35%上回る水準です。
          </p>
        </div>
      </div>
    </div>
  );
}