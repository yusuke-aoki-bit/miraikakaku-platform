'use client';

import React, { useState, useRef } from 'react';
import { Trash2, GripVertical, CheckCircle } from 'lucide-react';
import StockResultCard from '@/components/search/StockResultCard';
import TripleChart from '@/components/charts/TripleChart';

interface WatchlistStock {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  market?: string;
  sector?: string;
  market_cap?: number;
  ai_score?: number;
  per?: number;
  pbr?: number;
  dividend_yield?: number;
  chart_data?: {
    historical?: number[];
    past_prediction?: number[];
    future_prediction?: number[];
  };
}

interface WatchlistGridViewProps {
  stocks: WatchlistStock[];
  editMode: boolean;
  selectedStocks: string[];
  onStockSelect: (symbol: string) => void;
  onStockClick: (symbol: string) => void;
  onRemoveStock: (symbol: string) => void;
  onReorderStocks: (newOrder: WatchlistStock[]) => void;
  loading?: boolean;
}

export default function WatchlistGridView({
  stocks,
  editMode,
  selectedStocks,
  onStockSelect,
  onStockClick,
  onRemoveStock,
  onReorderStocks,
  loading = false
}: WatchlistGridViewProps) {
  const [draggedItem, setDraggedItem] = useState<WatchlistStock | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  const dragRef = useRef<HTMLDivElement>(null);

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

  const handleStockCardClick = (symbol: string) => {
    if (editMode) {
      onStockSelect(symbol);
    } else {
      onStockClick(symbol);
    }
  };

  const handleWatchlistToggle = (symbol: string, isWatched: boolean) => {
    if (!isWatched) {
      onRemoveStock(symbol);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="bg-gray-900/30 border border-gray-800/50 rounded-xl p-6 animate-pulse">
            <div className="flex items-start justify-between mb-4">
              <div className="space-y-2">
                <div className="h-6 bg-gray-700 rounded w-20"></div>
                <div className="h-4 bg-gray-700 rounded w-32"></div>
                <div className="h-3 bg-gray-700 rounded w-16"></div>
              </div>
              <div className="h-6 bg-gray-700 rounded w-16"></div>
            </div>
            <div className="h-32 bg-gray-700 rounded mb-4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-700 rounded w-24"></div>
              <div className="h-4 bg-gray-700 rounded w-20"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (stocks.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="w-24 h-24 mx-auto mb-6 bg-gray-800/50 rounded-full flex items-center justify-center">
          <span className="text-4xl text-gray-600">📈</span>
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">
          ウォッチリストは空です
        </h3>
        <p className="text-gray-400 mb-6">
          銘柄を追加して、AIによる分析と予測をチェックしましょう
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {stocks.map((stock, index) => {
        const isSelected = selectedStocks.includes(stock.symbol);
        const isDraggedOver = dragOverIndex === index && draggedItem;
        
        return (
          <div
            key={stock.symbol}
            className={`relative transition-all duration-200 ${
              isDraggedOver ? 'transform scale-105' : ''
            } ${
              draggedItem?.symbol === stock.symbol ? 'opacity-50' : ''
            }`}
            draggable={editMode}
            onDragStart={(e) => handleDragStart(e, stock)}
            onDragOver={(e) => handleDragOver(e, index)}
            onDrop={(e) => handleDrop(e, index)}
            onDragEnd={handleDragEnd}
          >
            {/* 編集モードのオーバーレイ */}
            {editMode && (
              <div className="absolute top-3 left-3 z-10 flex items-center space-x-2">
                {/* 選択チェックボックス */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onStockSelect(stock.symbol);
                  }}
                  className={`w-6 h-6 rounded border-2 flex items-center justify-center transition-colors ${
                    isSelected
                      ? 'bg-blue-500 border-blue-500 text-white'
                      : 'border-gray-500 hover:border-blue-400 bg-gray-900/80'
                  }`}
                >
                  {isSelected && <CheckCircle className="w-4 h-4" />}
                </button>
                
                {/* ドラッグハンドル */}
                <div className="w-6 h-6 flex items-center justify-center bg-gray-900/80 rounded border border-gray-600 cursor-grab active:cursor-grabbing">
                  <GripVertical className="w-4 h-4 text-gray-400" />
                </div>
              </div>
            )}

            {/* 削除ボタン（編集モード時） */}
            {editMode && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onRemoveStock(stock.symbol);
                }}
                className="absolute top-3 right-3 z-10 w-8 h-8 bg-red-500/80 hover:bg-red-500 rounded-full flex items-center justify-center transition-colors"
                title="削除"
              >
                <Trash2 className="w-4 h-4 text-white" />
              </button>
            )}

            {/* 選択状態のボーダー */}
            <div className={`
              bg-gray-900/30 border-2 rounded-xl transition-all duration-200 overflow-hidden
              ${editMode ? 'cursor-pointer' : ''}
              ${isSelected ? 'border-blue-500 bg-blue-500/5' : 'border-gray-800/50'}
              ${!editMode && 'hover:border-gray-700/50 hover:bg-gray-800/40'}
            `}>
              {/* カスタムストックカード */}
              <div 
                className="p-6"
                onClick={() => handleStockCardClick(stock.symbol)}
              >
                {/* ヘッダー情報 */}
                <div className="flex items-start justify-between mb-4">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-bold text-white text-lg">{stock.symbol}</h3>
                      {stock.ai_score && (
                        <div className={`px-2 py-1 rounded text-xs font-medium ${
                          stock.ai_score >= 80 ? 'bg-green-500/20 text-green-400' :
                          stock.ai_score >= 60 ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          AI {stock.ai_score}
                        </div>
                      )}
                    </div>
                    <p className="text-sm text-gray-400 truncate mt-1">
                      {stock.company_name}
                    </p>
                    {stock.market && stock.sector && (
                      <p className="text-xs text-gray-500 mt-1">
                        {stock.market} • {stock.sector}
                      </p>
                    )}
                  </div>
                  
                  <div className="text-right">
                    <div className="text-lg font-bold text-white">
                      ¥{stock.current_price.toLocaleString()}
                    </div>
                    <div className={`text-sm font-medium ${
                      stock.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                    </div>
                  </div>
                </div>

                {/* TripleChart */}
                {stock.chart_data && (
                  <div className="mb-4 text-gray-500 text-sm">
                    {/* チャートコンポーネントは型定義修正後に有効化 */}
                    チャートデータ利用可能
                  </div>
                )}

                {/* 財務指標 */}
                <div className="grid grid-cols-2 gap-4 text-xs">
                  {stock.market_cap && (
                    <div>
                      <span className="text-gray-400">時価総額</span>
                      <div className="text-white font-medium">
                        {stock.market_cap >= 1000000000000 
                          ? `${(stock.market_cap / 1000000000000).toFixed(1)}兆円`
                          : `${(stock.market_cap / 100000000).toFixed(0)}億円`
                        }
                      </div>
                    </div>
                  )}
                  {stock.per && (
                    <div>
                      <span className="text-gray-400">PER</span>
                      <div className="text-white font-medium">{stock.per.toFixed(1)}</div>
                    </div>
                  )}
                  {stock.pbr && (
                    <div>
                      <span className="text-gray-400">PBR</span>
                      <div className="text-white font-medium">{stock.pbr.toFixed(2)}</div>
                    </div>
                  )}
                  {stock.dividend_yield && (
                    <div>
                      <span className="text-gray-400">配当利回り</span>
                      <div className="text-white font-medium">{stock.dividend_yield.toFixed(2)}%</div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* ドラッグオーバーインジケーター */}
            {isDraggedOver && (
              <div className="absolute inset-0 border-2 border-dashed border-blue-400 rounded-xl pointer-events-none" />
            )}
          </div>
        );
      })}
    </div>
  );
}