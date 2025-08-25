'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Building2, 
  TrendingUp, 
  TrendingDown, 
  Star, 
  ExternalLink,
  ChevronUp,
  ChevronDown,
  Filter,
  ArrowUpDown,
  Target
} from 'lucide-react';

interface ThemeDetail {
  id: string;
  name: string;
  description: string;
  overview: string;
  detailed_description: string;
  category: string;
  stock_count: number;
  performance_1m: number;
  performance_3m: number;
  performance_1y: number;
  is_featured: boolean;
  is_trending: boolean;
  background_image?: string;
  follow_count: number;
  market_cap_total: number;
  top_stocks: string[];
  risk_level: 'Low' | 'Medium' | 'High';
  growth_stage: 'Early' | 'Growth' | 'Mature';
  created_at: string;
  updated_at: string;
}

interface Stock {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  market_cap: number;
  ai_score: number;
  theme_weight: number;
}

interface ThemeStockTableProps {
  theme: ThemeDetail;
  stocks: Stock[];
}

type SortField = 'theme_weight' | 'current_price' | 'change_percent' | 'market_cap' | 'ai_score' | 'symbol' | 'company_name';
type SortOrder = 'asc' | 'desc';

export default function ThemeStockTable({ theme, stocks }: ThemeStockTableProps) {
  const router = useRouter();
  const [sortField, setSortField] = useState<SortField>('theme_weight');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [filterScore, setFilterScore] = useState<number>(0);
  const [showOnlyTopPerformers, setShowOnlyTopPerformers] = useState(false);

  // フィルタリング・ソート済み銘柄リスト
  const filteredAndSortedStocks = useMemo(() => {
    let filtered = stocks.filter(stock => stock.ai_score >= filterScore);

    if (showOnlyTopPerformers) {
      filtered = filtered.filter(stock => stock.change_percent > 0);
    }

    return filtered.sort((a, b) => {
      let aVal: any = a[sortField];
      let bVal: any = b[sortField];

      if (sortField === 'symbol' || sortField === 'company_name') {
        return sortOrder === 'asc' 
          ? aVal.localeCompare(bVal) 
          : bVal.localeCompare(aVal);
      }

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
      }

      return 0;
    });
  }, [stocks, sortField, sortOrder, filterScore, showOnlyTopPerformers]);

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const handleStockClick = (symbol: string) => {
    // TODO: Navigate to stock detail page
    router.push(`/stocks/${symbol}`);
  };

  const formatPrice = (price: number) => {
    if (price > 1000) {
      return `¥${Math.round(price).toLocaleString('ja-JP')}`;
    }
    return `$${price.toFixed(2)}`;
  };

  const formatMarketCap = (marketCap: number) => {
    if (marketCap >= 1000000000000) {
      return `${(marketCap / 1000000000000).toFixed(1)}兆円`;
    } else if (marketCap >= 100000000) {
      return `${Math.round(marketCap / 100000000)}億円`;
    } else {
      return `${(marketCap / 100000000).toFixed(1)}億円`;
    }
  };

  const formatPerformance = (performance: number) => {
    const sign = performance >= 0 ? '+' : '';
    return `${sign}${performance.toFixed(2)}%`;
  };

  const getPerformanceColor = (performance: number) => {
    return performance >= 0 ? 'text-green-400' : 'text-red-400';
  };

  const getAIScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400 bg-green-900/20';
    if (score >= 60) return 'text-blue-400 bg-blue-900/20';
    if (score >= 40) return 'text-yellow-400 bg-yellow-900/20';
    return 'text-red-400 bg-red-900/20';
  };

  const getThemeWeightColor = (weight: number) => {
    if (weight >= 10) return 'text-purple-400 bg-purple-900/20';
    if (weight >= 5) return 'text-blue-400 bg-blue-900/20';
    return 'text-gray-400 bg-gray-900/20';
  };

  const SortButton = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center space-x-1 text-left hover:text-blue-400 transition-colors group"
    >
      <span>{children}</span>
      <div className="flex flex-col">
        <ChevronUp 
          className={`w-3 h-3 ${
            sortField === field && sortOrder === 'asc' 
              ? 'text-blue-400' 
              : 'text-gray-600 group-hover:text-gray-400'
          }`} 
        />
        <ChevronDown 
          className={`w-3 h-3 -mt-1 ${
            sortField === field && sortOrder === 'desc' 
              ? 'text-blue-400' 
              : 'text-gray-600 group-hover:text-gray-400'
          }`} 
        />
      </div>
    </button>
  );

  return (
    <div className="bg-gray-900/50 border border-gray-800/50 rounded-xl p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Building2 className="w-6 h-6 mr-3 text-green-400" />
          <div>
            <h2 className="text-xl font-bold text-white">関連銘柄</h2>
            <p className="text-sm text-gray-400">
              {theme.name}テーマの構成銘柄 ({filteredAndSortedStocks.length}/{stocks.length}銘柄)
            </p>
          </div>
        </div>

        <div className="text-sm text-gray-400">
          総時価総額: {formatMarketCap(theme.market_cap_total)}
        </div>
      </div>

      {/* フィルタ・コントロール */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
        <div className="flex items-center space-x-4">
          {/* AIスコアフィルタ */}
          <div className="flex items-center space-x-2">
            <Star className="w-4 h-4 text-yellow-400" />
            <span className="text-sm text-gray-400">AIスコア:</span>
            <select
              value={filterScore}
              onChange={(e) => setFilterScore(Number(e.target.value))}
              className="bg-gray-800/50 border border-gray-700/50 rounded px-2 py-1 text-sm text-white focus:outline-none focus:border-purple-500/50"
            >
              <option value={0}>全て</option>
              <option value={60}>60以上</option>
              <option value={70}>70以上</option>
              <option value={80}>80以上</option>
            </select>
          </div>

          {/* トップパフォーマーフィルタ */}
          <button
            onClick={() => setShowOnlyTopPerformers(!showOnlyTopPerformers)}
            className={`flex items-center space-x-1 px-3 py-1 rounded-lg text-sm transition-colors ${
              showOnlyTopPerformers 
                ? 'bg-green-600/20 text-green-400 border border-green-500/30' 
                : 'bg-gray-700/50 text-gray-300 hover:bg-gray-700/70'
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            <span>上昇銘柄のみ</span>
          </button>
        </div>

        <div className="text-sm text-gray-500">
          クリックで銘柄詳細ページに移動
        </div>
      </div>

      {/* テーブル */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="border-b border-gray-700/50">
            <tr className="text-sm text-gray-300">
              <th className="text-left p-3">
                <SortButton field="symbol">銘柄</SortButton>
              </th>
              <th className="text-right p-3">
                <SortButton field="current_price">株価</SortButton>
              </th>
              <th className="text-right p-3">
                <SortButton field="change_percent">変動率</SortButton>
              </th>
              <th className="text-right p-3">
                <SortButton field="market_cap">時価総額</SortButton>
              </th>
              <th className="text-center p-3">
                <SortButton field="ai_score">AIスコア</SortButton>
              </th>
              <th className="text-center p-3">
                <SortButton field="theme_weight">構成比重</SortButton>
              </th>
              <th className="text-center p-3">アクション</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/30">
            {filteredAndSortedStocks.length > 0 ? (
              filteredAndSortedStocks.map((stock) => (
                <tr 
                  key={stock.symbol}
                  className="hover:bg-gray-800/20 transition-colors cursor-pointer"
                  onClick={() => handleStockClick(stock.symbol)}
                >
                  {/* 銘柄情報 */}
                  <td className="p-3">
                    <div>
                      <div className="font-bold text-white text-lg">
                        {stock.symbol}
                      </div>
                      <div className="text-sm text-gray-400">
                        {stock.company_name}
                      </div>
                    </div>
                  </td>

                  {/* 株価 */}
                  <td className="p-3 text-right">
                    <div className="font-bold text-white text-lg">
                      {formatPrice(stock.current_price)}
                    </div>
                  </td>

                  {/* 変動率 */}
                  <td className="p-3 text-right">
                    <div className={`font-bold flex items-center justify-end ${getPerformanceColor(stock.change_percent)}`}>
                      {stock.change_percent >= 0 ? (
                        <TrendingUp className="w-4 h-4 mr-1" />
                      ) : (
                        <TrendingDown className="w-4 h-4 mr-1" />
                      )}
                      {formatPerformance(stock.change_percent)}
                    </div>
                  </td>

                  {/* 時価総額 */}
                  <td className="p-3 text-right">
                    <div className="text-white font-medium">
                      {formatMarketCap(stock.market_cap)}
                    </div>
                  </td>

                  {/* AIスコア */}
                  <td className="p-3 text-center">
                    <div className={`inline-flex items-center px-2 py-1 rounded-full text-sm font-medium ${getAIScoreColor(stock.ai_score)}`}>
                      {stock.ai_score}
                    </div>
                  </td>

                  {/* テーマ構成比重 */}
                  <td className="p-3 text-center">
                    <div className={`inline-flex items-center px-2 py-1 rounded-full text-sm font-medium ${getThemeWeightColor(stock.theme_weight)}`}>
                      {stock.theme_weight.toFixed(1)}%
                    </div>
                  </td>

                  {/* アクションボタン */}
                  <td className="p-3 text-center">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleStockClick(stock.symbol);
                      }}
                      className="text-purple-400 hover:text-purple-300 transition-colors"
                      title="銘柄詳細ページへ"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} className="p-8 text-center">
                  <Filter className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                  <div className="text-gray-400">条件に合う銘柄がありません</div>
                  <div className="text-sm text-gray-500 mt-1">
                    フィルタ条件を調整してください
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* テーブル説明 */}
      <div className="mt-6 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
        <div className="flex items-start space-x-3">
          <Target className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-blue-400 mb-1">指標について</h4>
            <div className="text-sm text-gray-300 space-y-1">
              <p>• AIスコア: 複数のAIモデルによる銘柄の総合評価（0-100）</p>
              <p>• 構成比重: テーマ指数における各銘柄の時価総額加重比率</p>
              <p>• 時価総額は最新の市場価格に基づいて計算されています</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}