'use client';

import React, { useState } from 'react';
import { 
  ChevronUp, 
  ChevronDown, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  ExternalLink,
  Trash2,
  CheckCircle,
  GripVertical
} from 'lucide-react';
import { SortOption, SortOrder } from './WatchlistToolbar';

interface WatchlistStock {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  volume?: number;
  market_cap?: number;
  per?: number;
  pbr?: number;
  dividend_yield?: number;
  ai_score?: number;
  last_updated?: string;
}

interface WatchlistListViewProps {
  stocks: WatchlistStock[];
  editMode: boolean;
  selectedStocks: string[];
  sortBy: SortOption;
  sortOrder: SortOrder;
  onSortChange: (sortBy: SortOption, sortOrder: SortOrder) => void;
  onStockSelect: (symbol: string) => void;
  onStockClick: (symbol: string) => void;
  onRemoveStock: (symbol: string) => void;
  onReorderStocks: (newOrder: WatchlistStock[]) => void;
  loading?: boolean;
}

const TABLE_COLUMNS = [
  { key: 'symbol' as SortOption, label: '銘柄', width: 'w-48' },
  { key: 'price' as SortOption, label: '株価', width: 'w-32' },
  { key: 'change' as SortOption, label: '変動率', width: 'w-32' },
  { key: 'volume' as SortOption, label: '出来高', width: 'w-32' },
  { key: 'marketCap' as SortOption, label: '時価総額', width: 'w-32' },
  { key: 'aiScore' as SortOption, label: 'AIスコア', width: 'w-32' },
  { key: 'per', label: 'PER', width: 'w-24' },
  { key: 'pbr', label: 'PBR', width: 'w-24' },
  { key: 'dividend', label: '配当利回り', width: 'w-32' }
];

export default function WatchlistListView({
  stocks,
  editMode,
  selectedStocks,
  sortBy,
  sortOrder,
  onSortChange,
  onStockSelect,
  onStockClick,
  onRemoveStock,
  onReorderStocks,
  loading = false
}: WatchlistListViewProps) {
  const [draggedItem, setDraggedItem] = useState<WatchlistStock | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);

  const handleSort = (column: SortOption) => {
    if (sortBy === column) {
      onSortChange(column, sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      onSortChange(column, 'asc');
    }
  };

  const getSortIcon = (column: SortOption) => {
    if (sortBy !== column) {
      return <ChevronUp className="w-4 h-4 text-gray-500" />;
    }
    return sortOrder === 'asc' ? 
      <ChevronUp className="w-4 h-4 text-blue-400" /> : 
      <ChevronDown className="w-4 h-4 text-blue-400" />;
  };

  const formatMarketCap = (marketCap: number): string => {
    if (marketCap >= 1000000000000) {
      return `${(marketCap / 1000000000000).toFixed(1)}兆円`;
    } else if (marketCap >= 100000000) {
      return `${(marketCap / 100000000).toFixed(0)}億円`;
    } else {
      return `${(marketCap / 100000000).toFixed(1)}億円`;
    }
  };

  const formatVolume = (volume: number): string => {
    if (volume >= 100000000) {
      return `${(volume / 100000000).toFixed(1)}億`;
    } else if (volume >= 10000) {
      return `${(volume / 10000).toFixed(1)}万`;
    } else {
      return volume.toLocaleString();
    }
  };

  const handleDragStart = (e: React.DragEvent, stock: WatchlistStock) => {
    if (!editMode) return;
    setDraggedItem(stock);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    if (!editMode || !draggedItem) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverIndex(index);
  };

  const handleDrop = (e: React.DragEvent, dropIndex: number) => {
    if (!editMode || !draggedItem) return;
    e.preventDefault();
    
    const currentIndex = stocks.findIndex(stock => stock.symbol === draggedItem.symbol);
    if (currentIndex === dropIndex) {
      setDraggedItem(null);
      setDragOverIndex(null);
      return;
    }

    const newStocks = [...stocks];
    newStocks.splice(currentIndex, 1);
    newStocks.splice(dropIndex, 0, draggedItem);
    
    onReorderStocks(newStocks);
    setDraggedItem(null);
    setDragOverIndex(null);
  };

  const handleDragEnd = () => {
    setDraggedItem(null);
    setDragOverIndex(null);
  };

  const handleRowClick = (stock: WatchlistStock) => {
    if (editMode) {
      onStockSelect(stock.symbol);
    } else {
      onStockClick(stock.symbol);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl overflow-hidden">
        <div className="p-6">
          <div className="animate-pulse">
            <div className="h-12 bg-gray-700 rounded mb-4"></div>
            {Array.from({ length: 8 }).map((_, index) => (
              <div key={index} className="h-16 bg-gray-800 rounded mb-2"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (stocks.length === 0) {
    return (
      <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-12 text-center">
        <div className="w-24 h-24 mx-auto mb-6 bg-gray-800/50 rounded-full flex items-center justify-center">
          <span className="text-4xl text-gray-600">📊</span>
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">
          ウォッチリストは空です
        </h3>
        <p className="text-gray-400">
          銘柄を追加してリスト表示で詳細な比較を行いましょう
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl overflow-hidden">
      {/* テーブルヘッダー */}
      <div className="bg-gray-800/50 border-b border-gray-700/50">
        <div className="flex items-center px-6 py-4">
          {/* 編集モードの場合のチェックボックス列 */}
          {editMode && (
            <div className="w-12 flex items-center justify-center">
              <div className="w-6 h-6"></div> {/* 空のスペース */}
            </div>
          )}
          
          {/* ドラッグハンドル列 */}
          {editMode && (
            <div className="w-12"></div>
          )}

          {TABLE_COLUMNS.map((column) => {
            const isSortable = column.key && ['symbol', 'price', 'change', 'volume', 'marketCap', 'aiScore'].includes(column.key);
            
            return (
              <div
                key={column.key || column.label}
                className={`${column.width} flex items-center ${
                  isSortable ? 'cursor-pointer hover:text-blue-400' : ''
                } transition-colors`}
                onClick={() => isSortable && column.key && handleSort(column.key)}
              >
                <span className="text-sm font-medium text-gray-300">
                  {column.label}
                </span>
                {isSortable && column.key && (
                  <span className="ml-2">
                    {getSortIcon(column.key)}
                  </span>
                )}
              </div>
            );
          })}

          {/* アクション列 */}
          <div className="flex-1"></div>
          <div className="w-16"></div>
        </div>
      </div>

      {/* テーブルボディ */}
      <div className="divide-y divide-gray-800/50">
        {stocks.map((stock, index) => {
          const isSelected = selectedStocks.includes(stock.symbol);
          const isDraggedOver = dragOverIndex === index && draggedItem;
          const changePercent = stock.change_percent || 0;
          const isPositive = changePercent >= 0;

          return (
            <div
              key={stock.symbol}
              className={`
                flex items-center px-6 py-4 transition-all duration-200
                ${editMode ? 'cursor-pointer' : 'hover:bg-gray-800/30 cursor-pointer'}
                ${isSelected ? 'bg-blue-500/10 border-l-4 border-l-blue-500' : ''}
                ${isDraggedOver ? 'bg-blue-500/20' : ''}
                ${draggedItem?.symbol === stock.symbol ? 'opacity-50' : ''}
              `}
              onClick={() => handleRowClick(stock)}
              draggable={editMode}
              onDragStart={(e) => handleDragStart(e, stock)}
              onDragOver={(e) => handleDragOver(e, index)}
              onDrop={(e) => handleDrop(e, index)}
              onDragEnd={handleDragEnd}
            >
              {/* 選択チェックボックス */}
              {editMode && (
                <div className="w-12 flex items-center justify-center">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onStockSelect(stock.symbol);
                    }}
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                      isSelected
                        ? 'bg-blue-500 border-blue-500 text-white'
                        : 'border-gray-500 hover:border-blue-400'
                    }`}
                  >
                    {isSelected && <CheckCircle className="w-3 h-3" />}
                  </button>
                </div>
              )}

              {/* ドラッグハンドル */}
              {editMode && (
                <div className="w-12 flex items-center justify-center">
                  <div className="cursor-grab active:cursor-grabbing text-gray-500">
                    <GripVertical className="w-4 h-4" />
                  </div>
                </div>
              )}

              {/* 銘柄 */}
              <div className="w-48 min-w-0">
                <div className="flex items-center space-x-2">
                  <div className="min-w-0">
                    <div className="font-semibold text-white flex items-center">
                      {stock.symbol}
                      {!editMode && (
                        <ExternalLink className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                      )}
                    </div>
                    <div className="text-sm text-gray-400 truncate">
                      {stock.company_name}
                    </div>
                  </div>
                </div>
              </div>

              {/* 株価 */}
              <div className="w-32 text-right">
                <div className="text-white font-medium">
                  ¥{stock.current_price.toLocaleString()}
                </div>
              </div>

              {/* 変動率 */}
              <div className="w-32 text-right">
                <div className={`flex items-center justify-end space-x-1 ${
                  isPositive ? 'text-green-400' : changePercent < 0 ? 'text-red-400' : 'text-gray-400'
                }`}>
                  {isPositive ? <TrendingUp className="w-4 h-4" /> :
                   changePercent < 0 ? <TrendingDown className="w-4 h-4" /> :
                   <Minus className="w-4 h-4" />}
                  <span className="font-medium">
                    {isPositive ? '+' : ''}{changePercent.toFixed(2)}%
                  </span>
                </div>
              </div>

              {/* 出来高 */}
              <div className="w-32 text-right">
                <div className="text-white">
                  {stock.volume ? formatVolume(stock.volume) : '---'}
                </div>
              </div>

              {/* 時価総額 */}
              <div className="w-32 text-right">
                <div className="text-white">
                  {stock.market_cap ? formatMarketCap(stock.market_cap) : '---'}
                </div>
              </div>

              {/* AIスコア */}
              <div className="w-32 text-right">
                {stock.ai_score ? (
                  <div className={`inline-flex items-center px-2 py-1 rounded text-sm font-medium ${
                    stock.ai_score >= 80 ? 'bg-green-500/20 text-green-400' :
                    stock.ai_score >= 60 ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {stock.ai_score}
                  </div>
                ) : (
                  <div className="text-gray-500">---</div>
                )}
              </div>

              {/* PER */}
              <div className="w-24 text-right">
                <div className="text-white">
                  {stock.per ? stock.per.toFixed(1) : '---'}
                </div>
              </div>

              {/* PBR */}
              <div className="w-24 text-right">
                <div className="text-white">
                  {stock.pbr ? stock.pbr.toFixed(2) : '---'}
                </div>
              </div>

              {/* 配当利回り */}
              <div className="w-32 text-right">
                <div className="text-white">
                  {stock.dividend_yield ? `${stock.dividend_yield.toFixed(2)}%` : '---'}
                </div>
              </div>

              {/* 空のスペース */}
              <div className="flex-1"></div>

              {/* アクションボタン（編集モード時） */}
              <div className="w-16 flex justify-end">
                {editMode && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveStock(stock.symbol);
                    }}
                    className="w-8 h-8 bg-red-500/80 hover:bg-red-500 rounded-full flex items-center justify-center transition-colors"
                    title="削除"
                  >
                    <Trash2 className="w-4 h-4 text-white" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}