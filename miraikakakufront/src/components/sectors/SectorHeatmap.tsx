'use client';

import React, { useState, useEffect } from 'react';
import { 
  Treemap, 
  ResponsiveContainer, 
  Cell, 
  Tooltip,
  Legend
} from 'recharts';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface SectorData {
  id: string;
  name: string;
  market_cap: number;
  daily_change: number;
  weekly_change: number;
  monthly_change: number;
  stock_count: number;
  top_performers: number;
  color_intensity: number;
}

interface SectorHeatmapProps {
  sectors: SectorData[];
  selectedSector: string | null;
  onSectorSelect: (sectorId: string) => void;
  timeframe: 'daily' | 'weekly' | 'monthly';
  onTimeframeChange: (timeframe: 'daily' | 'weekly' | 'monthly') => void;
}

export default function SectorHeatmap({
  sectors,
  selectedSector,
  onSectorSelect,
  timeframe,
  onTimeframeChange
}: SectorHeatmapProps) {
  const [hoveredSector, setHoveredSector] = useState<string | null>(null);

  // ツリーマップ用のデータ変換
  const treemapData = sectors.map(sector => {
    const change = timeframe === 'daily' ? sector.daily_change 
                  : timeframe === 'weekly' ? sector.weekly_change 
                  : sector.monthly_change;

    return {
      name: sector.name,
      id: sector.id,
      size: sector.market_cap,
      change: change,
      stock_count: sector.stock_count,
      top_performers: sector.top_performers,
      // 色の強度を変動率に基づいて計算
      fill: getColorForChange(change),
      opacity: selectedSector === sector.id ? 1 : 0.8
    };
  });

  // 変動率に基づいて色を決定
  function getColorForChange(change: number): string {
    if (change > 3) return '#16a34a'; // 強い上昇 - 濃い緑
    if (change > 1) return '#22c55e'; // 中程度の上昇 - 緑
    if (change > 0) return '#84cc16'; // 軽微な上昇 - 薄い緑
    if (change > -1) return '#fbbf24'; // 軽微な下落 - 黄色
    if (change > -3) return '#f97316'; // 中程度の下落 - オレンジ
    return '#dc2626'; // 強い下落 - 赤
  }

  // ツールチップコンポーネント
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    
    return (
      <div className="bg-black/90 border border-gray-600 rounded-lg p-4 shadow-xl">
        <div className="text-white font-semibold mb-2">{data.name}</div>
        <div className="space-y-1 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-gray-300">変動率 ({timeframe === 'daily' ? '日次' : timeframe === 'weekly' ? '週次' : '月次'}):</span>
            <span className={`font-medium ${data.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {data.change >= 0 ? '+' : ''}{data.change.toFixed(2)}%
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-300">時価総額:</span>
            <span className="text-white">
              {(data.size / 1000000000000).toFixed(1)}兆円
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-300">銘柄数:</span>
            <span className="text-white">{data.stock_count}社</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-300">注目銘柄:</span>
            <span className="text-blue-400">{data.top_performers}社</span>
          </div>
        </div>
      </div>
    );
  };

  // セル描画コンポーネント
  const CustomCell = ({ x, y, width, height, payload }: any) => {
    const isSelected = selectedSector === payload.id;
    const isHovered = hoveredSector === payload.id;
    
    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          fill={payload.fill}
          stroke={isSelected ? '#3b82f6' : isHovered ? '#64748b' : '#374151'}
          strokeWidth={isSelected ? 3 : isHovered ? 2 : 1}
          className="cursor-pointer transition-all duration-200"
          onClick={() => onSectorSelect(payload.id)}
          onMouseEnter={() => setHoveredSector(payload.id)}
          onMouseLeave={() => setHoveredSector(null)}
        />
        
        {/* セクター名とパフォーマンス */}
        {width > 120 && height > 60 && (
          <>
            <text
              x={x + width / 2}
              y={y + height / 2 - 10}
              textAnchor="middle"
              className="fill-white text-sm font-medium pointer-events-none"
              style={{ textShadow: '1px 1px 1px rgba(0,0,0,0.7)' }}
            >
              {payload.name}
            </text>
            <text
              x={x + width / 2}
              y={y + height / 2 + 10}
              textAnchor="middle"
              className={`text-sm font-bold pointer-events-none ${
                payload.change >= 0 ? 'fill-green-100' : 'fill-red-100'
              }`}
              style={{ textShadow: '1px 1px 1px rgba(0,0,0,0.7)' }}
            >
              {payload.change >= 0 ? '+' : ''}{payload.change.toFixed(1)}%
            </text>
          </>
        )}
        
        {/* 小さいセルの場合はシンボルのみ */}
        {(width <= 120 || height <= 60) && width > 40 && height > 40 && (
          <text
            x={x + width / 2}
            y={y + height / 2}
            textAnchor="middle"
            className="fill-white text-xs font-medium pointer-events-none"
            style={{ textShadow: '1px 1px 1px rgba(0,0,0,0.7)' }}
          >
            {payload.name.substring(0, 4)}
          </text>
        )}
      </g>
    );
  };

  const getTimeframeIcon = (tf: string) => {
    switch (tf) {
      case 'daily': return <Activity className="w-4 h-4" />;
      case 'weekly': return <TrendingUp className="w-4 h-4" />;
      case 'monthly': return <TrendingDown className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getTimeframeLabel = (tf: string) => {
    switch (tf) {
      case 'daily': return '日次';
      case 'weekly': return '週次'; 
      case 'monthly': return '月次';
      default: return '日次';
    }
  };

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white">セクターヒートマップ</h2>
        
        {/* タイムフレーム切り替え */}
        <div className="flex items-center bg-gray-800/50 rounded-lg p-1">
          {(['daily', 'weekly', 'monthly'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => onTimeframeChange(tf)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm transition-all ${
                timeframe === tf
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
              }`}
            >
              {getTimeframeIcon(tf)}
              <span>{getTimeframeLabel(tf)}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ヒートマップ */}
      <div className="h-96 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <Treemap
            data={treemapData}
            dataKey="size"
            aspectRatio={1}
            stroke="#374151"
            content={<CustomCell />}
          >
            <Tooltip content={<CustomTooltip />} />
          </Treemap>
        </ResponsiveContainer>
      </div>

      {/* 凡例 */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-400">
          クリックでセクター詳細を表示 • サイズ = 時価総額、色 = パフォーマンス
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded"></div>
            <span className="text-sm text-gray-400">上昇</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-yellow-500 rounded"></div>
            <span className="text-sm text-gray-400">横ばい</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded"></div>
            <span className="text-sm text-gray-400">下落</span>
          </div>
        </div>
      </div>

      {/* 選択中のセクター表示 */}
      {selectedSector && (
        <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
          <div className="text-sm text-blue-400">
            選択中: {sectors.find(s => s.id === selectedSector)?.name}
          </div>
        </div>
      )}
    </div>
  );
}