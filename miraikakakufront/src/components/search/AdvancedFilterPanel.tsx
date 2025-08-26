'use client';

import React, { useState, useEffect } from 'react';
import { 
  Filter, 
  ChevronDown, 
  ChevronUp, 
  X, 
  DollarSign,
  BarChart3,
  TrendingUp,
  Zap
} from 'lucide-react';
import apiClient from '@/lib/api-client';

export interface SearchFilters {
  markets: string[];
  sectors: string[];
  marketCapMin?: number;
  marketCapMax?: number;
  perMin?: number;
  perMax?: number;
  pbrMin?: number;
  pbrMax?: number;
  dividendYieldMin?: number;
  dividendYieldMax?: number;
  aiScoreMin?: number;
  aiScoreMax?: number;
}

interface AdvancedFilterPanelProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  onApplyFilters: () => void;
  isOpen: boolean;
  onToggle: () => void;
}

export const MARKET_OPTIONS = [
  { id: 'jp', label: '日本株', description: '東証・マザーズ等' },
  { id: 'us', label: '米国株', description: 'NYSE・NASDAQ等' }
];

export const MARKET_CAP_RANGES = [
  { label: '小型株', min: 0, max: 30000000000 }, // 300億円
  { label: '中型株', min: 30000000000, max: 300000000000 }, // 300億円-3000億円
  { label: '大型株', min: 300000000000, max: undefined } // 3000億円以上
];

export default function AdvancedFilterPanel({
  filters,
  onFiltersChange,
  onApplyFilters,
  isOpen,
  onToggle
}: AdvancedFilterPanelProps) {
  const [sectors, setSectors] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    basic: true,
    financial: false,
    ai: false
  });

  useEffect(() => {
    fetchSectors();
  }, []);

  const fetchSectors = async () => {
    try {
      const response = await apiClient.getSectors();
      if (response.success && Array.isArray(response.data)) {
        setSectors(response.data);
      } else {
        // API失敗時は空配列
        setSectors([]);
      }
    } catch (error) {
      console.error('Failed to fetch sectors:', error);
    }
  };

  const handleMarketChange = (marketId: string) => {
    const newMarkets = filters.markets.includes(marketId)
      ? filters.markets.filter(m => m !== marketId)
      : [...filters.markets, marketId];
    
    onFiltersChange({ ...filters, markets: newMarkets });
  };

  const handleSectorChange = (sectorId: string) => {
    const newSectors = filters.sectors.includes(sectorId)
      ? filters.sectors.filter(s => s !== sectorId)
      : [...filters.sectors, sectorId];
    
    onFiltersChange({ ...filters, sectors: newSectors });
  };

  const handleRangeChange = (field: keyof SearchFilters, value: number | undefined, isMin: boolean) => {
    const minField = `${field.replace('Max', '').replace('Min', '')}Min` as keyof SearchFilters;
    const maxField = `${field.replace('Max', '').replace('Min', '')}Max` as keyof SearchFilters;
    
    onFiltersChange({
      ...filters,
      [isMin ? minField : maxField]: value
    });
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const clearAllFilters = () => {
    onFiltersChange({
      markets: [],
      sectors: [],
      marketCapMin: undefined,
      marketCapMax: undefined,
      perMin: undefined,
      perMax: undefined,
      pbrMin: undefined,
      pbrMax: undefined,
      dividendYieldMin: undefined,
      dividendYieldMax: undefined,
      aiScoreMin: undefined,
      aiScoreMax: undefined
    });
  };

  const hasActiveFilters = filters.markets.length > 0 || 
                          filters.sectors.length > 0 ||
                          filters.marketCapMin !== undefined ||
                          filters.marketCapMax !== undefined ||
                          filters.perMin !== undefined ||
                          filters.perMax !== undefined ||
                          filters.pbrMin !== undefined ||
                          filters.pbrMax !== undefined ||
                          filters.dividendYieldMin !== undefined ||
                          filters.dividendYieldMax !== undefined ||
                          filters.aiScoreMin !== undefined ||
                          filters.aiScoreMax !== undefined;

  const RangeSlider = ({ 
    label, 
    min, 
    max, 
    step = 1, 
    valueMin, 
    valueMax, 
    onMinChange, 
    onMaxChange,
    unit = '',
    icon
  }: {
    label: string;
    min: number;
    max: number;
    step?: number;
    valueMin?: number;
    valueMax?: number;
    onMinChange: (value: number | undefined) => void;
    onMaxChange: (value: number | undefined) => void;
    unit?: string;
    icon?: React.ReactNode;
  }) => (
    <div className="space-y-3">
      <label className="text-sm font-medium text-gray-300 flex items-center">
        {icon && <span className="mr-2">{icon}</span>}
        {label}
      </label>
      <div className="space-y-2">
        <div className="flex items-center space-x-2">
          <input
            type="number"
            value={valueMin ?? ''}
            onChange={(e) => onMinChange(e.target.value ? Number(e.target.value) : undefined)}
            placeholder={`最小${unit}`}
            className="w-20 px-2 py-1 bg-gray-800/50 border border-gray-700/50 rounded text-white text-sm"
            min={min}
            max={max}
            step={step}
          />
          <span className="text-gray-400 text-sm">〜</span>
          <input
            type="number"
            value={valueMax ?? ''}
            onChange={(e) => onMaxChange(e.target.value ? Number(e.target.value) : undefined)}
            placeholder={`最大${unit}`}
            className="w-20 px-2 py-1 bg-gray-800/50 border border-gray-700/50 rounded text-white text-sm"
            min={min}
            max={max}
            step={step}
          />
          {unit && <span className="text-gray-400 text-sm">{unit}</span>}
        </div>
        
        {/* プリセットボタン */}
        {label === '時価総額' && (
          <div className="flex flex-wrap gap-1">
            {MARKET_CAP_RANGES.map((range) => (
              <button
                key={range.label}
                onClick={() => {
                  onMinChange(range.min);
                  onMaxChange(range.max);
                }}
                className="px-2 py-1 bg-gray-700/50 hover:bg-gray-600/50 rounded text-xs text-gray-300 transition-colors"
              >
                {range.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className="flex items-center space-x-2 px-4 py-2 bg-gray-900/50 border border-gray-800/50 rounded-lg text-gray-300 hover:text-white transition-colors"
      >
        <Filter className="w-4 h-4" />
        <span>高度な検索</span>
        {hasActiveFilters && (
          <span className="bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">
            {[
              filters.markets.length,
              filters.sectors.length,
              filters.marketCapMin !== undefined || filters.marketCapMax !== undefined ? 1 : 0,
              filters.perMin !== undefined || filters.perMax !== undefined ? 1 : 0,
              filters.pbrMin !== undefined || filters.pbrMax !== undefined ? 1 : 0,
              filters.dividendYieldMin !== undefined || filters.dividendYieldMax !== undefined ? 1 : 0,
              filters.aiScoreMin !== undefined || filters.aiScoreMax !== undefined ? 1 : 0
            ].reduce((a, b) => a + b, 0)}
          </span>
        )}
      </button>
    );
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white flex items-center">
          <Filter className="w-5 h-5 mr-2 text-blue-400" />
          高度な検索フィルター
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
            onClick={onToggle}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <ChevronUp className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {/* 基本情報セクション */}
        <div>
          <button
            onClick={() => toggleSection('basic')}
            className="flex items-center justify-between w-full text-left mb-4"
          >
            <h4 className="text-md font-medium text-white">基本情報</h4>
            {expandedSections.basic ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          
          {expandedSections.basic && (
            <div className="space-y-4 pl-4">
              {/* 市場選択 */}
              <div>
                <label className="text-sm font-medium text-gray-300 mb-2 block">
                  市場
                </label>
                <div className="flex flex-wrap gap-2">
                  {MARKET_OPTIONS.map((option) => (
                    <button
                      key={option.id}
                      onClick={() => handleMarketChange(option.id)}
                      className={`px-3 py-2 rounded-lg text-sm transition-all ${
                        filters.markets.includes(option.id)
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
                      className={`px-3 py-1 rounded-md text-sm transition-all ${
                        filters.sectors.includes(sector.id)
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50'
                      }`}
                    >
                      {sector.name}
                      {sector.count && (
                        <span className="text-xs opacity-75 ml-1">({sector.count})</span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 財務指標セクション */}
        <div>
          <button
            onClick={() => toggleSection('financial')}
            className="flex items-center justify-between w-full text-left mb-4"
          >
            <h4 className="text-md font-medium text-white flex items-center">
              <BarChart3 className="w-4 h-4 mr-2 text-green-400" />
              財務指標
            </h4>
            {expandedSections.financial ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          
          {expandedSections.financial && (
            <div className="space-y-4 pl-4">
              <RangeSlider
                label="時価総額"
                min={0}
                max={50000000000000}
                step={10000000000}
                valueMin={filters.marketCapMin}
                valueMax={filters.marketCapMax}
                onMinChange={(value) => handleRangeChange('marketCapMin', value, true)}
                onMaxChange={(value) => handleRangeChange('marketCapMax', value, false)}
                unit="円"
                icon={<DollarSign className="w-3 h-3 text-green-400" />}
              />
              
              <RangeSlider
                label="PER（株価収益率）"
                min={0}
                max={100}
                step={0.1}
                valueMin={filters.perMin}
                valueMax={filters.perMax}
                onMinChange={(value) => handleRangeChange('perMin', value, true)}
                onMaxChange={(value) => handleRangeChange('perMax', value, false)}
                unit="倍"
                icon={<TrendingUp className="w-3 h-3 text-blue-400" />}
              />
              
              <RangeSlider
                label="PBR（株価純資産倍率）"
                min={0}
                max={10}
                step={0.1}
                valueMin={filters.pbrMin}
                valueMax={filters.pbrMax}
                onMinChange={(value) => handleRangeChange('pbrMin', value, true)}
                onMaxChange={(value) => handleRangeChange('pbrMax', value, false)}
                unit="倍"
                icon={<BarChart3 className="w-3 h-3 text-purple-400" />}
              />
              
              <RangeSlider
                label="配当利回り"
                min={0}
                max={10}
                step={0.1}
                valueMin={filters.dividendYieldMin}
                valueMax={filters.dividendYieldMax}
                onMinChange={(value) => handleRangeChange('dividendYieldMin', value, true)}
                onMaxChange={(value) => handleRangeChange('dividendYieldMax', value, false)}
                unit="%"
                icon={<DollarSign className="w-3 h-3 text-orange-400" />}
              />
            </div>
          )}
        </div>

        {/* AI指標セクション */}
        <div>
          <button
            onClick={() => toggleSection('ai')}
            className="flex items-center justify-between w-full text-left mb-4"
          >
            <h4 className="text-md font-medium text-white flex items-center">
              <Zap className="w-4 h-4 mr-2 text-yellow-400" />
              AI指標
            </h4>
            {expandedSections.ai ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          
          {expandedSections.ai && (
            <div className="space-y-4 pl-4">
              <RangeSlider
                label="AIスコア"
                min={0}
                max={100}
                step={1}
                valueMin={filters.aiScoreMin}
                valueMax={filters.aiScoreMax}
                onMinChange={(value) => handleRangeChange('aiScoreMin', value, true)}
                onMaxChange={(value) => handleRangeChange('aiScoreMax', value, false)}
                unit="点"
                icon={<Zap className="w-3 h-3 text-yellow-400" />}
              />
            </div>
          )}
        </div>
      </div>

      {/* 適用ボタン */}
      <div className="mt-6 pt-6 border-t border-gray-800/50">
        <button
          onClick={onApplyFilters}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-3 px-4 rounded-lg transition-all font-medium"
        >
          {loading ? '検索中...' : 'フィルターを適用'}
        </button>
        
        {hasActiveFilters && (
          <div className="mt-2 text-center">
            <span className="text-xs text-gray-400">
              アクティブなフィルター: {[
                filters.markets.length > 0 ? `市場: ${filters.markets.length}` : null,
                filters.sectors.length > 0 ? `セクター: ${filters.sectors.length}` : null,
                filters.marketCapMin !== undefined || filters.marketCapMax !== undefined ? '時価総額' : null,
                filters.perMin !== undefined || filters.perMax !== undefined ? 'PER' : null,
                filters.pbrMin !== undefined || filters.pbrMax !== undefined ? 'PBR' : null,
                filters.dividendYieldMin !== undefined || filters.dividendYieldMax !== undefined ? '配当利回り' : null,
                filters.aiScoreMin !== undefined || filters.aiScoreMax !== undefined ? 'AIスコア' : null
              ].filter(Boolean).join(', ')}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}