'use client';

import React, { useState } from 'react';
import { Plus, Grid, List, Map, Edit3, MoreHorizontal, ArrowUpDown, Filter } from 'lucide-react';
import StockSearch from '@/components/StockSearch';

export type ViewMode = 'grid' | 'list' | 'heatmap';
export type SortOption = 'symbol' | 'price' | 'change' | 'volume' | 'marketCap' | 'aiScore';
export type SortOrder = 'asc' | 'desc';

interface WatchlistToolbarProps {
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
  editMode: boolean;
  onEditModeToggle: () => void;
  onAddStock: (symbol: string) => void;
  sortBy?: SortOption;
  sortOrder?: SortOrder;
  onSortChange?: (sortBy: SortOption, sortOrder: SortOrder) => void;
  watchlistCount: number;
  selectedCount?: number;
  onDeleteSelected?: () => void;
  onSelectAll?: () => void;
  onClearSelection?: () => void;
}

const VIEW_MODES = [
  { mode: 'grid' as ViewMode, label: 'グリッド', icon: Grid },
  { mode: 'list' as ViewMode, label: 'リスト', icon: List },
  { mode: 'heatmap' as ViewMode, label: 'ヒートマップ', icon: Map }
];

const SORT_OPTIONS = [
  { value: 'symbol' as SortOption, label: 'シンボル' },
  { value: 'price' as SortOption, label: '株価' },
  { value: 'change' as SortOption, label: '変動率' },
  { value: 'volume' as SortOption, label: '出来高' },
  { value: 'marketCap' as SortOption, label: '時価総額' },
  { value: 'aiScore' as SortOption, label: 'AIスコア' }
];

export default function WatchlistToolbar({
  viewMode,
  onViewModeChange,
  editMode,
  onEditModeToggle,
  onAddStock,
  sortBy = 'symbol',
  sortOrder = 'asc',
  onSortChange,
  watchlistCount,
  selectedCount = 0,
  onDeleteSelected,
  onSelectAll,
  onClearSelection
}: WatchlistToolbarProps) {
  const [showAddStock, setShowAddStock] = useState(false);
  const [showSortMenu, setShowSortMenu] = useState(false);

  const handleAddStock = (symbol: string) => {
    onAddStock(symbol);
    setShowAddStock(false);
  };

  const handleSortChange = (newSortBy: SortOption) => {
    if (onSortChange) {
      const newOrder = sortBy === newSortBy && sortOrder === 'asc' ? 'desc' : 'asc';
      onSortChange(newSortBy, newOrder);
    }
    setShowSortMenu(false);
  };

  return (
    <div className="space-y-4">
      {/* メインツールバー */}
      <div className="flex items-center justify-between bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
        {/* 左側: カウントと表示モード */}
        <div className="flex items-center space-x-6">
          <div className="text-white">
            <span className="text-lg font-semibold">{watchlistCount}</span>
            <span className="text-sm text-gray-400 ml-1">銘柄</span>
            {editMode && selectedCount > 0 && (
              <span className="ml-2 text-sm text-blue-400">
                ({selectedCount}選択中)
              </span>
            )}
          </div>

          {/* 表示モード切替 */}
          <div className="flex items-center space-x-1 bg-gray-800/50 rounded-lg p-1">
            {VIEW_MODES.map(({ mode, label, icon: Icon }) => (
              <button
                key={mode}
                onClick={() => onViewModeChange(mode)}
                className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === mode
                    ? 'bg-blue-500/20 text-blue-400'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                }`}
                title={label}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 右側: アクションボタン */}
        <div className="flex items-center space-x-2">
          {/* 編集モード時のアクション */}
          {editMode && selectedCount > 0 && (
            <div className="flex items-center space-x-2 mr-4">
              <button
                onClick={onSelectAll}
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                すべて選択
              </button>
              <button
                onClick={onClearSelection}
                className="text-sm text-gray-400 hover:text-white transition-colors"
              >
                選択解除
              </button>
              <button
                onClick={onDeleteSelected}
                className="px-3 py-1 bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg text-sm font-medium hover:bg-red-500/30 transition-colors"
              >
                削除 ({selectedCount})
              </button>
            </div>
          )}

          {/* ソートメニュー */}
          {viewMode === 'list' && onSortChange && (
            <div className="relative">
              <button
                onClick={() => setShowSortMenu(!showSortMenu)}
                className="flex items-center space-x-1 px-3 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-sm text-gray-300 hover:text-white transition-colors"
              >
                <ArrowUpDown className="w-4 h-4" />
                <span>ソート</span>
              </button>
              
              {showSortMenu && (
                <div className="absolute top-full right-0 mt-1 w-40 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50">
                  {SORT_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handleSortChange(option.value)}
                      className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-800 transition-colors flex items-center justify-between ${
                        sortBy === option.value ? 'text-blue-400' : 'text-gray-300'
                      }`}
                    >
                      <span>{option.label}</span>
                      {sortBy === option.value && (
                        <span className="text-xs">
                          {sortOrder === 'asc' ? '↑' : '↓'}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 編集モード切替 */}
          <button
            onClick={onEditModeToggle}
            className={`flex items-center space-x-1 px-3 py-2 border rounded-lg text-sm font-medium transition-colors ${
              editMode
                ? 'bg-orange-500/20 text-orange-400 border-orange-500/30 hover:bg-orange-500/30'
                : 'bg-gray-800/50 text-gray-300 border-gray-700/50 hover:text-white hover:bg-gray-700/50'
            }`}
          >
            <Edit3 className="w-4 h-4" />
            <span>{editMode ? '編集完了' : '編集'}</span>
          </button>

          {/* 銘柄追加ボタン */}
          <button
            onClick={() => setShowAddStock(!showAddStock)}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all font-medium"
          >
            <Plus className="w-4 h-4" />
            <span>銘柄追加</span>
          </button>
        </div>
      </div>

      {/* 銘柄追加パネル */}
      {showAddStock && (
        <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">銘柄を追加</h3>
            <button
              onClick={() => setShowAddStock(false)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>
          
          <StockSearch 
            onSymbolSelect={handleAddStock}
          />
        </div>
      )}

      {/* 編集モード時のヘルプテキスト */}
      {editMode && (
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
          <p className="text-sm text-blue-300">
            📝 編集モード: 銘柄をドラッグして並べ替えたり、チェックボックスで選択して削除できます。
          </p>
        </div>
      )}

      {/* クリック外しでメニューを閉じる */}
      {showSortMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowSortMenu(false)}
        />
      )}
    </div>
  );
}