'use client';

import React, { useState } from 'react';
import { 
  Star, 
  StarOff, 
  TrendingUp, 
  TrendingDown, 
  Zap,
  ExternalLink,
  ChevronUp,
  ChevronDown
} from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip
);

interface RankingStock {
  rank: number;
  symbol: string;
  company_name: string;
  current_price: number;
  change?: number;
  change_percent?: number;
  volume_change?: number;
  ai_score?: number;
  growth_potential?: number;
  confidence?: number;
  sparkline_data?: number[];
}

interface RankingsTableProps {
  data: RankingStock[];
  loading: boolean;
  rankingType: string;
  onStockClick: (symbol: string) => void;
  onWatchlistToggle: (symbol: string, isWatched: boolean) => void;
}

type SortField = 'rank' | 'symbol' | 'current_price' | 'change_percent' | 'ai_score' | 'growth_potential';
type SortOrder = 'asc' | 'desc';

export default function RankingsTable({ 
  data, 
  loading, 
  rankingType, 
  onStockClick,
  onWatchlistToggle 
}: RankingsTableProps) {
  const [sortField, setSortField] = useState<SortField>('rank');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');
  const [watchlist, setWatchlist] = useState<Set<string>>(new Set());

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const sortedData = React.useMemo(() => {
    return [...data].sort((a, b) => {
      let aVal: any = a[sortField];
      let bVal: any = b[sortField];

      if (typeof aVal === 'string') {
        return sortOrder === 'asc' 
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
      }

      return 0;
    });
  }, [data, sortField, sortOrder]);

  const handleWatchlistClick = (e: React.MouseEvent, symbol: string) => {
    e.stopPropagation();
    const isCurrentlyWatched = watchlist.has(symbol);
    const newWatchlist = new Set(watchlist);
    
    if (isCurrentlyWatched) {
      newWatchlist.delete(symbol);
    } else {
      newWatchlist.add(symbol);
    }
    
    setWatchlist(newWatchlist);
    onWatchlistToggle(symbol, !isCurrentlyWatched);
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return rank.toString();
  };

  const getChangeDisplay = (stock: RankingStock) => {
    switch (rankingType) {
      case 'gainers':
      case 'losers':
        return {
          value: stock.change_percent || 0,
          suffix: '%',
          prefix: stock.change_percent && stock.change_percent >= 0 ? '+' : ''
        };
      case 'volume':
        return {
          value: stock.volume_change || 0,
          suffix: '%',
          prefix: '+'
        };
      case 'ai-score':
        return {
          value: stock.ai_score || 0,
          suffix: '',
          prefix: ''
        };
      case 'growth':
        return {
          value: stock.growth_potential || 0,
          suffix: '%',
          prefix: stock.growth_potential && stock.growth_potential >= 0 ? '+' : ''
        };
      default:
        return {
          value: stock.change_percent || 0,
          suffix: '%',
          prefix: stock.change_percent && stock.change_percent >= 0 ? '+' : ''
        };
    }
  };

  const SortButton = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center space-x-1 text-left hover:text-blue-400 transition-colors"
    >
      <span>{children}</span>
      {sortField === field && (
        sortOrder === 'asc' 
          ? <ChevronUp className="w-3 h-3" />
          : <ChevronDown className="w-3 h-3" />
      )}
    </button>
  );

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
        <div className="text-center py-12 text-gray-400">
          <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>表示するデータがありません</p>
          <p className="text-sm mt-2">フィルター条件を変更してお試しください</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-800/30 border-b border-gray-700/50">
            <tr>
              <th className="text-left p-4 text-sm font-medium text-gray-300">
                <SortButton field="rank">順位</SortButton>
              </th>
              <th className="text-left p-4 text-sm font-medium text-gray-300">
                <SortButton field="symbol">銘柄</SortButton>
              </th>
              <th className="text-right p-4 text-sm font-medium text-gray-300">
                <SortButton field="current_price">現在値</SortButton>
              </th>
              <th className="text-right p-4 text-sm font-medium text-gray-300">
                <SortButton field="change_percent">変動</SortButton>
              </th>
              <th className="text-right p-4 text-sm font-medium text-gray-300">
                <SortButton field="ai_score">AIスコア</SortButton>
              </th>
              <th className="text-center p-4 text-sm font-medium text-gray-300">
                チャート
              </th>
              <th className="text-center p-4 text-sm font-medium text-gray-300">
                アクション
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/30">
            {sortedData.map((stock) => (
              <RankingRow
                key={stock.symbol}
                stock={stock}
                rankingType={rankingType}
                isWatched={watchlist.has(stock.symbol)}
                onStockClick={() => onStockClick(stock.symbol)}
                onWatchlistClick={(e) => handleWatchlistClick(e, stock.symbol)}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

interface RankingRowProps {
  stock: RankingStock;
  rankingType: string;
  isWatched: boolean;
  onStockClick: () => void;
  onWatchlistClick: (e: React.MouseEvent) => void;
}

function RankingRow({ 
  stock, 
  rankingType, 
  isWatched, 
  onStockClick, 
  onWatchlistClick 
}: RankingRowProps) {
  const changeDisplay = getChangeDisplay(stock, rankingType);
  const isPositiveChange = changeDisplay.value >= 0;

  // スパークラインチャートデータ生成
  const sparklineData = stock.sparkline_data || generateSparklineData();
  
  const chartData = {
    labels: Array(24).fill(''),
    datasets: [{
      data: sparklineData,
      borderColor: isPositiveChange ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)',
      borderWidth: 1.5,
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
    <tr 
      className="hover:bg-gray-800/20 transition-all cursor-pointer group"
      onClick={onStockClick}
    >
      <td className="p-4">
        <div className="flex items-center">
          <span className="text-lg font-bold w-10 text-center">
            {getRankIcon(stock.rank)}
          </span>
        </div>
      </td>
      
      <td className="p-4">
        <div className="flex flex-col">
          <div className="font-medium text-white group-hover:text-blue-400 transition-colors flex items-center">
            {stock.symbol}
            <ExternalLink className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <div className="text-sm text-gray-400 truncate max-w-32">
            {stock.company_name}
          </div>
        </div>
      </td>

      <td className="p-4 text-right">
        <div className="font-medium text-white">
          {stock.symbol.match(/^[A-Z]+$/) ? '$' : '¥'}
          {stock.current_price.toLocaleString('ja-JP', {
            minimumFractionDigits: stock.symbol.match(/^[A-Z]+$/) ? 2 : 0,
            maximumFractionDigits: stock.symbol.match(/^[A-Z]+$/) ? 2 : 0
          })}
        </div>
      </td>

      <td className="p-4 text-right">
        <div className={`font-medium flex items-center justify-end ${
          isPositiveChange ? 'text-green-400' : 'text-red-400'
        }`}>
          {isPositiveChange ? (
            <TrendingUp className="w-3 h-3 mr-1" />
          ) : (
            <TrendingDown className="w-3 h-3 mr-1" />
          )}
          {changeDisplay.prefix}{changeDisplay.value.toFixed(1)}{changeDisplay.suffix}
        </div>
      </td>

      <td className="p-4 text-right">
        <div className="flex items-center justify-end space-x-1">
          <Zap className="w-3 h-3 text-yellow-400" />
          <span className="font-medium text-white">
            {(stock.ai_score || 75).toFixed(0)}
          </span>
        </div>
      </td>

      <td className="p-4">
        <div className="h-8 w-20">
          <Line data={chartData} options={chartOptions} />
        </div>
      </td>

      <td className="p-4">
        <div className="flex items-center justify-center space-x-2">
          <button
            onClick={onWatchlistClick}
            className={`p-1 rounded transition-colors ${
              isWatched 
                ? 'text-yellow-400 hover:text-yellow-300' 
                : 'text-gray-400 hover:text-yellow-400'
            }`}
            title={isWatched ? 'ウォッチリストから削除' : 'ウォッチリストに追加'}
          >
            {isWatched ? <Star className="w-4 h-4 fill-current" /> : <StarOff className="w-4 h-4" />}
          </button>
        </div>
      </td>
    </tr>
  );
}

function getChangeDisplay(stock: RankingStock, rankingType: string) {
  switch (rankingType) {
    case 'gainers':
    case 'losers':
      return {
        value: stock.change_percent || 0,
        suffix: '%',
        prefix: stock.change_percent && stock.change_percent >= 0 ? '+' : ''
      };
    case 'volume':
      return {
        value: stock.volume_change || 0,
        suffix: '%',
        prefix: '+'
      };
    case 'ai-score':
      return {
        value: stock.ai_score || 0,
        suffix: '',
        prefix: ''
      };
    case 'growth':
      return {
        value: stock.growth_potential || 0,
        suffix: '%',
        prefix: stock.growth_potential && stock.growth_potential >= 0 ? '+' : ''
      };
    default:
      return {
        value: stock.change_percent || 0,
        suffix: '%',
        prefix: stock.change_percent && stock.change_percent >= 0 ? '+' : ''
      };
  }
}

function getRankIcon(rank: number) {
  if (rank === 1) return '🥇';
  if (rank === 2) return '🥈';
  if (rank === 3) return '🥉';
  return rank.toString();
}

function generateSparklineData(): number[] {
  const data = [];
  let base = 100;
  for (let i = 0; i < 24; i++) {
    base += (Math.random() - 0.5) * 5;
    data.push(base);
  }
  return data;
}