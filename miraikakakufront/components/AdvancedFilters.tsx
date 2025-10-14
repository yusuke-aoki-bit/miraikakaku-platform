'use client';

import { useState } from 'react';

/**
 * 高度なフィルタリング・ソートシステム
 * ランキングページや検索ページで使用
 */

export interface FilterOptions {
  // 価格フィルター
  priceMin?: number;
  priceMax?: number;

  // 変動率フィルター
  changeMin?: number;
  changeMax?: number;

  // 予測精度フィルター
  accuracyMin?: number;

  // 市場フィルター
  exchange?: string[];

  // セクターフィルター
  sector?: string[];

  // データ可用性フィルター
  hasPrice?: boolean;
  hasPrediction?: boolean;

  // 検索クエリ
  searchQuery?: string;
}

export interface SortOption {
  field: 'price' | 'change' | 'prediction' | 'accuracy' | 'volume' | 'marketCap' | 'name';
  direction: 'asc' | 'desc';
}

interface AdvancedFiltersProps {
  filters: FilterOptions;
  onFiltersChange: (filters: FilterOptions) => void;
  sortOption: SortOption;
  onSortChange: (sort: SortOption) => void;
  resultCount?: number;
}

export function AdvancedFilters({
  filters,
  onFiltersChange,
  sortOption,
  onSortChange,
  resultCount
}: AdvancedFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const exchanges = [
    { id: 'tse', name: '東京証券取引所' },
    { id: 'nasdaq', name: 'NASDAQ' },
    { id: 'nyse', name: 'NYSE' },
    { id: 'crypto', name: '暗号通貨' },
  ];

  const sectors = [
    { id: 'tech', name: 'テクノロジー' },
    { id: 'finance', name: '金融' },
    { id: 'healthcare', name: 'ヘルスケア' },
    { id: 'consumer', name: '消費財' },
    { id: 'energy', name: 'エネルギー' },
    { id: 'industrial', name: '工業' },
  ];

  const sortOptions = [
    { field: 'change' as const, name: '変動率', icon: '📈' },
    { field: 'price' as const, name: '価格', icon: '💰' },
    { field: 'prediction' as const, name: '予測値', icon: '🔮' },
    { field: 'accuracy' as const, name: '精度', icon: '🎯' },
    { field: 'volume' as const, name: '出来高', icon: '📊' },
    { field: 'marketCap' as const, name: '時価総額', icon: '💎' },
    { field: 'name' as const, name: '銘柄名', icon: '🔤' },
  ];

  const updateFilter = (key: keyof FilterOptions, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const toggleArrayFilter = (key: 'exchange' | 'sector', value: string) => {
    const current = filters[key] || [];
    const updated = current.includes(value)
      ? current.filter(v => v !== value)
      : [...current, value];
    updateFilter(key, updated.length > 0 ? updated : undefined);
  };

  const resetFilters = () => {
    onFiltersChange({});
  };

  const activeFilterCount = Object.values(filters).filter(v =>
    v !== undefined && v !== null && (Array.isArray(v) ? v.length > 0 : true)
  ).length;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            フィルター & ソート
          </h2>
          {activeFilterCount > 0 && (
            <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm font-semibold rounded-full">
              {activeFilterCount} 個適用中
            </span>
          )}
          {resultCount !== undefined && (
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {resultCount.toLocaleString()} 件の結果
            </span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {activeFilterCount > 0 && (
            <button
              onClick={resetFilters}
              className="px-3 py-1.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
            >
              リセット
            </button>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
            aria-label={isExpanded ? '折りたたむ' : '展開'}
          >
            <svg
              className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      {/* ソートオプション（常に表示） */}
      <div className="flex flex-wrap gap-2 mb-4">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 self-center">
          並び替え:
        </span>
        {sortOptions.map(option => (
          <button
            key={option.field}
            onClick={() => {
              if (sortOption.field === option.field) {
                onSortChange({
                  field: option.field,
                  direction: sortOption.direction === 'asc' ? 'desc' : 'asc'
                });
              } else {
                onSortChange({ field: option.field, direction: 'desc' });
              }
            }}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1 ${
              sortOption.field === option.field
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            <span>{option.icon}</span>
            <span>{option.name}</span>
            {sortOption.field === option.field && (
              <svg
                className={`w-4 h-4 transition-transform ${sortOption.direction === 'asc' ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            )}
          </button>
        ))}
      </div>

      {/* 詳細フィルター（展開時のみ） */}
      {isExpanded && (
        <div className="space-y-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          {/* 価格範囲 */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              💰 価格範囲
            </label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">最小価格</label>
                <input
                  type="number"
                  value={filters.priceMin || ''}
                  onChange={(e) => updateFilter('priceMin', e.target.value ? Number(e.target.value) : undefined)}
                  placeholder="0"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">最大価格</label>
                <input
                  type="number"
                  value={filters.priceMax || ''}
                  onChange={(e) => updateFilter('priceMax', e.target.value ? Number(e.target.value) : undefined)}
                  placeholder="∞"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
          </div>

          {/* 変動率範囲 */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              📈 変動率範囲 (%)
            </label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">最小変動率</label>
                <input
                  type="number"
                  value={filters.changeMin || ''}
                  onChange={(e) => updateFilter('changeMin', e.target.value ? Number(e.target.value) : undefined)}
                  placeholder="-100"
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">最大変動率</label>
                <input
                  type="number"
                  value={filters.changeMax || ''}
                  onChange={(e) => updateFilter('changeMax', e.target.value ? Number(e.target.value) : undefined)}
                  placeholder="100"
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
          </div>

          {/* 予測精度 */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              🎯 最小予測精度 (%)
            </label>
            <input
              type="number"
              value={filters.accuracyMin || ''}
              onChange={(e) => updateFilter('accuracyMin', e.target.value ? Number(e.target.value) : undefined)}
              placeholder="0"
              min="0"
              max="100"
              step="1"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* 取引所 */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              🏛️ 取引所
            </label>
            <div className="flex flex-wrap gap-2">
              {exchanges.map(exchange => (
                <button
                  key={exchange.id}
                  onClick={() => toggleArrayFilter('exchange', exchange.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filters.exchange?.includes(exchange.id)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {exchange.name}
                </button>
              ))}
            </div>
          </div>

          {/* セクター */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              🏢 セクター
            </label>
            <div className="flex flex-wrap gap-2">
              {sectors.map(sector => (
                <button
                  key={sector.id}
                  onClick={() => toggleArrayFilter('sector', sector.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filters.sector?.includes(sector.id)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {sector.name}
                </button>
              ))}
            </div>
          </div>

          {/* データ可用性 */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              📊 データ可用性
            </label>
            <div className="space-y-2">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.hasPrice || false}
                  onChange={(e) => updateFilter('hasPrice', e.target.checked || undefined)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">価格データあり</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.hasPrediction || false}
                  onChange={(e) => updateFilter('hasPrediction', e.target.checked || undefined)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">予測データあり</span>
              </label>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * フィルタリング関数
 */
export function applyFilters<T extends Record<string, any>>(
  data: T[],
  filters: FilterOptions,
  sort: SortOption
): T[] {
  let filtered = [...data];

  // 価格フィルター
  if (filters.priceMin !== undefined) {
    filtered = filtered.filter(item => (item.price || item.close_price || 0) >= filters.priceMin!);
  }
  if (filters.priceMax !== undefined) {
    filtered = filtered.filter(item => (item.price || item.close_price || 0) <= filters.priceMax!);
  }

  // 変動率フィルター
  if (filters.changeMin !== undefined) {
    filtered = filtered.filter(item => (item.change_percent || item.change || 0) >= filters.changeMin!);
  }
  if (filters.changeMax !== undefined) {
    filtered = filtered.filter(item => (item.change_percent || item.change || 0) <= filters.changeMax!);
  }

  // 精度フィルター
  if (filters.accuracyMin !== undefined) {
    filtered = filtered.filter(item => (item.accuracy || 0) >= filters.accuracyMin!);
  }

  // 取引所フィルター
  if (filters.exchange && filters.exchange.length > 0) {
    filtered = filtered.filter(item => filters.exchange!.includes(item.exchange || item.market));
  }

  // セクターフィルター
  if (filters.sector && filters.sector.length > 0) {
    filtered = filtered.filter(item => filters.sector!.includes(item.sector));
  }

  // データ可用性フィルター
  if (filters.hasPrice) {
    filtered = filtered.filter(item => item.price || item.close_price);
  }
  if (filters.hasPrediction) {
    filtered = filtered.filter(item => item.prediction || item.predicted_price);
  }

  // 検索クエリ
  if (filters.searchQuery) {
    const query = filters.searchQuery.toLowerCase();
    filtered = filtered.filter(item =>
      (item.symbol || '').toLowerCase().includes(query) ||
      (item.name || '').toLowerCase().includes(query) ||
      (item.company_name || '').toLowerCase().includes(query)
    );
  }

  // ソート
  filtered.sort((a, b) => {
    let aValue, bValue;

    switch (sort.field) {
      case 'price':
        aValue = a.price || a.close_price || 0;
        bValue = b.price || b.close_price || 0;
        break;
      case 'change':
        aValue = a.change_percent || a.change || 0;
        bValue = b.change_percent || b.change || 0;
        break;
      case 'prediction':
        aValue = a.prediction || a.predicted_price || 0;
        bValue = b.prediction || b.predicted_price || 0;
        break;
      case 'accuracy':
        aValue = a.accuracy || 0;
        bValue = b.accuracy || 0;
        break;
      case 'volume':
        aValue = a.volume || 0;
        bValue = b.volume || 0;
        break;
      case 'marketCap':
        aValue = a.market_cap || 0;
        bValue = b.market_cap || 0;
        break;
      case 'name':
        aValue = a.name || a.company_name || a.symbol || '';
        bValue = b.name || b.company_name || b.symbol || '';
        return sort.direction === 'asc'
          ? aValue.localeCompare(bValue, 'ja')
          : bValue.localeCompare(aValue, 'ja');
      default:
        return 0;
    }

    return sort.direction === 'asc' ? aValue - bValue : bValue - aValue;
  });

  return filtered;
}
