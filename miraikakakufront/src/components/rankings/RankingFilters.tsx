'use client';

import React, { useState, useEffect } from 'react';
import { Filter, X, Check } from 'lucide-react';
import apiClient from '@/lib/api-client';

export interface RankingFilters {
  market: string[];
  sectors: string[];
  marketCap: string[];
  period: string;
}

interface RankingFiltersProps {
  filters: RankingFilters;
  onFiltersChange: (filters: RankingFilters) => void;
  onApplyFilters: () => void;
}

export const MARKET_OPTIONS = [
  { id: 'jp', label: '日本株', count: 0 },
  { id: 'us', label: '米国株', count: 0 },
  { id: 'all', label: 'すべて', count: 0 }
];

export const MARKET_CAP_OPTIONS = [
  { id: 'large', label: '大型株', description: '時価総額 > 3000億円' },
  { id: 'mid', label: '中型株', description: '300億円 - 3000億円' },
  { id: 'small', label: '小型株', description: '< 300億円' }
];

export const PERIOD_OPTIONS = [
  { id: 'daily', label: 'デイリー', description: '1日の変動' },
  { id: 'weekly', label: '週間', description: '1週間の変動' },
  { id: 'monthly', label: '月間', description: '1ヶ月の変動' }
];

export default function RankingFilters({ 
  filters, 
  onFiltersChange, 
  onApplyFilters 
}: RankingFiltersProps) {
  const [sectors, setSectors] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    fetchSectors();
  }, []);

  const fetchSectors = async () => {
    setLoading(true);
    try {
      const response = await apiClient.getSectors();
      if (response.status === 'success' && Array.isArray(response.data)) {
        setSectors(response.data);
      } else {
        // API失敗時は空配列
        setSectors([]);
      }
    } catch (error) {
      console.error('Failed to fetch sectors:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarketChange = (marketId: string) => {
    const newMarkets = filters.market.includes(marketId)
      ? filters.market.filter(m => m !== marketId)
      : [...filters.market, marketId];
    
    onFiltersChange({
      ...filters,
      market: newMarkets
    });
  };

  const handleSectorChange = (sectorId: string) => {
    const newSectors = filters.sectors.includes(sectorId)
      ? filters.sectors.filter(s => s !== sectorId)
      : [...filters.sectors, sectorId];
    
    onFiltersChange({
      ...filters,
      sectors: newSectors
    });
  };

  const handleMarketCapChange = (capId: string) => {
    const newCaps = filters.marketCap.includes(capId)
      ? filters.marketCap.filter(c => c !== capId)
      : [...filters.marketCap, capId];
    
    onFiltersChange({
      ...filters,
      marketCap: newCaps
    });
  };

  const handlePeriodChange = (period: string) => {
    onFiltersChange({
      ...filters,
      period
    });
  };

  const clearAllFilters = () => {
    onFiltersChange({
      market: [],
      sectors: [],
      marketCap: [],
      period: 'daily'
    });
  };

  const hasActiveFilters = filters.market.length > 0 || 
                          filters.sectors.length > 0 || 
                          filters.marketCap.length > 0 || 
                          filters.period !== 'daily';

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center">
          <Filter className="w-5 h-5 mr-2 text-blue-400" />
          フィルター
        </h3>
        <div className="flex items-center space-x-2">
          {hasActiveFilters && (
            <button
              onClick={clearAllFilters}
              className="text-sm text-gray-400 hover:text-white transition-colors flex items-center"
            >
              <X className="w-4 h-4 mr-1" />
              クリア
            </button>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            {isExpanded ? '簡易表示' : '詳細表示'}
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {/* 集計期間 - 常に表示 */}
        <div>
          <label className="text-sm font-medium text-gray-300 mb-2 block">
            集計期間
          </label>
          <div className="flex flex-wrap gap-2">
            {PERIOD_OPTIONS.map((option) => (
              <button
                key={option.id}
                onClick={() => handlePeriodChange(option.id)}
                className={`px-3 py-1 rounded-md text-sm transition-all ${
                  filters.period === option.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50'
                }`}
                title={option.description}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* 市場選択 - 常に表示 */}
        <div>
          <label className="text-sm font-medium text-gray-300 mb-2 block">
            市場
          </label>
          <div className="flex flex-wrap gap-2">
            {MARKET_OPTIONS.map((option) => (
              <button
                key={option.id}
                onClick={() => handleMarketChange(option.id)}
                className={`px-3 py-1 rounded-md text-sm transition-all flex items-center space-x-1 ${
                  filters.market.includes(option.id)
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50'
                }`}
              >
                {filters.market.includes(option.id) && (
                  <Check className="w-3 h-3" />
                )}
                <span>{option.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 詳細フィルター - 展開時のみ表示 */}
        {isExpanded && (
          <>
            {/* セクター選択 */}
            <div>
              <label className="text-sm font-medium text-gray-300 mb-2 block">
                セクター
                {filters.sectors.length > 0 && (
                  <span className="ml-1 text-xs text-blue-400">
                    ({filters.sectors.length}選択中)
                  </span>
                )}
              </label>
              <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                {sectors.map((sector) => (
                  <button
                    key={sector.id}
                    onClick={() => handleSectorChange(sector.id)}
                    className={`px-3 py-1 rounded-md text-sm transition-all flex items-center space-x-1 ${
                      filters.sectors.includes(sector.id)
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50'
                    }`}
                  >
                    {filters.sectors.includes(sector.id) && (
                      <Check className="w-3 h-3" />
                    )}
                    <span>{sector.name}</span>
                    {sector.count && (
                      <span className="text-xs opacity-75">({sector.count})</span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* 時価総額 */}
            <div>
              <label className="text-sm font-medium text-gray-300 mb-2 block">
                時価総額
              </label>
              <div className="flex flex-wrap gap-2">
                {MARKET_CAP_OPTIONS.map((option) => (
                  <button
                    key={option.id}
                    onClick={() => handleMarketCapChange(option.id)}
                    className={`px-3 py-1 rounded-md text-sm transition-all flex items-center space-x-1 ${
                      filters.marketCap.includes(option.id)
                        ? 'bg-orange-600 text-white'
                        : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50'
                    }`}
                    title={option.description}
                  >
                    {filters.marketCap.includes(option.id) && (
                      <Check className="w-3 h-3" />
                    )}
                    <span>{option.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}
      </div>

      {/* 適用ボタン */}
      <div className="mt-4 pt-4 border-t border-gray-800/50">
        <button
          onClick={onApplyFilters}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-2 px-4 rounded-lg transition-all font-medium"
        >
          {loading ? '読み込み中...' : 'フィルターを適用'}
        </button>
        
        {hasActiveFilters && (
          <div className="mt-2 text-center">
            <span className="text-xs text-gray-400">
              {[
                filters.market.length > 0 ? `市場: ${filters.market.length}` : null,
                filters.sectors.length > 0 ? `セクター: ${filters.sectors.length}` : null,
                filters.marketCap.length > 0 ? `時価総額: ${filters.marketCap.length}` : null,
                filters.period !== 'daily' ? `期間: ${PERIOD_OPTIONS.find(p => p.id === filters.period)?.label}` : null
              ].filter(Boolean).join(' | ')}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}